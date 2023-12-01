from dataclasses import dataclass
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


@dataclass
class ModifierInfo:
    atk: float
    def_: float
    spa: float
    spd: float
    spe: float
    evasion: float
    accuracy: float
    
    def display(self) -> str:
        """Return a string representation of the statbar."""
        return f'{self.atk}/{self.def_}/{self.spa}/{self.spd}/{self.spe}\n{self.evasion} Evasion\n{self.accuracy} Accuracy'

@dataclass
class MoveInfo:
    name: str
    type: str
    moves_left: int
    
    def display(self) -> str:
        """Return a string representation of the move."""
        return f'{self.name}\n{self.type}\n{self.moves_left} PP'

@dataclass
class PokemonInfo:
    name: str
    gender: str | None
    hp_percent: float
    abilities: list[str]
    speed: tuple[int, int]
    
    def display(self) -> str:
        """Return a string representation fo the pokemon."""
        ability_str = '\n'.join(f'- {ability}' for ability in self.abilities)
        return f'{self.name}: {self.gender}\nHP: {self.hp_percent}%\nAbilities:\n{ability_str}\nSpeed: {self.speed}'

@dataclass
class StartingPokemonInfo:
    name: str
    types: list[str]
    tera_type: str
    gender: str | None
    hp_percent: float
    total_hp: int
    ability: str
    item: str
    atk: int
    def_: int
    spa: int
    spd: int
    spe: int
    moves: list[str]
    
    def display(self) -> str:
        moves_str = '\n'.join(f'- {move}' for move in self.moves)
        lines = [
            f'{self.name}: {self.gender}',
            ', '.join(self.types),
            f'Tera Type: {self.tera_type}',
            f'HP: {self.total_hp} ({self.hp_percent}%)',
            f'Ability: {self.ability}',
            f'Item: {self.item}',
            f'{self.atk}/{self.def_}/{self.spa}/{self.spd}/{self.spe}',
            f'Moves:\n{moves_str}'
        ]
        return '\n'.join(lines)
    
def _parse_statbar(statbar: WebElement) -> ModifierInfo:
    """Parse a statbar string into a StatbarInfo object."""
    statuses = statbar.find_element(by=By.CLASS_NAME, value='status')
    temp_modifiers = {
        'Atk': 1.0,
        'Def': 1.0,
        'SpA': 1.0,
        'SpD': 1.0,
        'Spe': 1.0,
        'Evasion': 1.0,
        'Accuracy': 1.0,
    }
    after_buff: tuple[str, float] | None = None
    for modifier in [e.text for e in statuses.find_elements(by=By.TAG_NAME, value='span')]:
        if 'Protosynthesis' in modifier or 'Quark Drive' in modifier:
            affected = modifier.split(':')[1].strip()
            if affected == 'Spe':
                after_buff = (affected, 0.5)
            else:
                after_buff = (affected, 0.3)
        else:
            modifier_name = modifier.split()[0][:-1]
            modifier_value = float(modifier.split()[1].strip())
            temp_modifiers[modifier_name] = modifier_value
    
    temp_modifiers[after_buff[0]] += after_buff[1]
    
    return ModifierInfo(
        atk=temp_modifiers['Atk'],
        def_=temp_modifiers['Def'],
        spa=temp_modifiers['SpA'],
        spd=temp_modifiers['SpD'],
        spe=temp_modifiers['Spe'],
        evasion=temp_modifiers['Evasion'],
        accuracy=temp_modifiers['Accuracy'],
    )


class WebDriver(webdriver.Chrome):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_enemy_statbar(self) -> ModifierInfo:
        enemy_statbar = self.find_elements(by=By.CLASS_NAME, value='statbar')[0]
        return _parse_statbar(enemy_statbar)

    def get_my_statbar(self) -> ModifierInfo:
        my_statbar = self.find_elements(by=By.CLASS_NAME, value='statbar')[1]
        return _parse_statbar(my_statbar)

    def get_available_moves(self) -> list[MoveInfo]:
        """Return a list of available moves."""
        move_menu = self.find_element(by=By.CLASS_NAME, value='movemenu')
        moves: list[MoveInfo] = []
        for move_button in move_menu.find_elements(by=By.TAG_NAME, value='button'):
            button_info = move_button.text.split()
            move_name = ' '.join(button_info[:-2])
            move_type = button_info[-2]
            moves_left = int(button_info[-1].split('/')[0])
            moves.append(MoveInfo(move_name, move_type, moves_left))
        return moves

    def _get_tooltip(self, element: WebElement) -> WebElement:
        ActionChains(self).move_to_element(element).perform()
        time.sleep(0.05)
        return self.find_element(by=By.CLASS_NAME, value='tooltip')
    
    def _get_gender_from_header(self, header: WebElement) -> str | None:
        try:
            pokemon_gender = header.find_element(by=By.TAG_NAME, value='img').get_attribute('alt')
            return pokemon_gender if pokemon_gender in {'M', 'F'} else None
        except NoSuchElementException:
            return None
    
    def _get_types_from_header(self, header: WebElement) -> list[str]:
        types: list[str] = []
        for container in header.find_elements(by=By.CLASS_NAME, value='textaligned-typeicons'):
            types.extend([img.get_attribute('alt') for img in container.find_elements(by=By.TAG_NAME, value='img')])
        return types
    
    def _get_pokemon_type(self, pokemon_name: str) -> str:
        if '(' in pokemon_name:
            return pokemon_name.split('(')[1].split(')')[0]
        return pokemon_name.strip()

    def _get_team_info(self, side_name: str) -> list[PokemonInfo]:
        side = self.find_element(by=By.CLASS_NAME, value=side_name)
        icons = side.find_elements(by=By.CLASS_NAME, value='teamicons')
        team: list[PokemonInfo] = []
        for icon_set in icons:
            for icon in icon_set.find_elements(by=By.TAG_NAME, value='span'):
                tooltip = self._get_tooltip(icon)
                header = tooltip.find_element(by=By.TAG_NAME, value='h2')
                pokemon_name = header.text
                pokemon_gender = self._get_gender_from_header(header)
                pokemon_info = tooltip.find_elements(by=By.TAG_NAME, value='p')
                try:
                    pokemon_hp = float(pokemon_info[0].text.split(':')[1].split('%')[0])
                except ValueError:
                    pokemon_hp = 0.0
                pokemon_abilities = [a.strip() for a in pokemon_info[1].text.split(':')[1].split(',')]
                line_3_raw = pokemon_info[2].text.split()
                if line_3_raw[0] == 'Spe':
                    pokemon_speed = (int(line_3_raw[1]), int(line_3_raw[3]))
                else:
                    line_4_raw = pokemon_info[3].text.split()
                    pokemon_speed = (int(line_4_raw[1]), int(line_4_raw[1]))
                
                team.append(PokemonInfo(pokemon_name, pokemon_gender, pokemon_hp, pokemon_abilities, pokemon_speed))
        
        return team

    def get_my_team_info(self) -> list[PokemonInfo]:
        return self._get_team_info('trainer-near')

    def get_enemy_team_info(self) -> list[PokemonInfo]:
        return self._get_team_info('trainer-far')
    
    def get_starting_info(self) -> list[StartingPokemonInfo]:
        """Return a list of starting pokemon info."""
        starting_info: list[StartingPokemonInfo] = []
        switch_menu = self.find_element(by=By.CLASS_NAME, value='switchmenu')
        for button in switch_menu.find_elements(by=By.TAG_NAME, value='button'):
            tooltip = self._get_tooltip(button)
            header = tooltip.find_element(by=By.TAG_NAME, value='h2')
            pokemon_types = self._get_types_from_header(header)
            pokemon_info = tooltip.find_elements(by=By.TAG_NAME, value='p')
            try:
                pokemon_item = pokemon_info[1].text.split(':')[2].strip()
            except IndexError:
                pokemon_item = 'None'
            starting_info.append(StartingPokemonInfo(
                name=self._get_pokemon_type(header.text.split('\n')[0]),
                gender=self._get_gender_from_header(header),
                types=pokemon_types[:-1],
                tera_type=pokemon_types[-1],
                hp_percent=float(pokemon_info[0].text.split(':')[1].split('%')[0]),
                total_hp=int(pokemon_info[0].text.split('/')[1].split(')')[0]),
                ability=pokemon_info[1].text.split(':')[1].split('/')[0].strip(),
                item=pokemon_item,
                atk=int(pokemon_info[2].text.split('/')[0].strip().split()[1]),
                def_=int(pokemon_info[2].text.split('/')[1].strip().split()[1]),
                spa=int(pokemon_info[2].text.split('/')[2].strip().split()[1]),
                spd=int(pokemon_info[2].text.split('/')[3].strip().split()[1]),
                spe=int(pokemon_info[2].text.split('/')[4].strip().split()[1]),
                moves=[move[2:] for move in pokemon_info[3].text.split('\n')]
            ))
        return starting_info
    

    def testing(self) -> None:
        while True:
            # execute an input string in Python for testing purposes
            try:
                print(eval(input(">>> ")))
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)

def main() -> None:
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors-spki-list')
    driver = WebDriver(options=options)
    driver.get("https://play.pokemonshowdown.com/")
    driver.testing()
    driver.quit()

if __name__ == '__main__':
    main()
