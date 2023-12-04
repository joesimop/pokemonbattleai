from dataclasses import dataclass
import time
from typing import Literal

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
    confused: bool
    paralyzed: bool
    aqua_ring: bool
    taunt: bool
    frozen: bool
    toxic: bool
    endure: bool
    
    def display(self) -> str:
        """Return a string representation of the statbar."""
        final_string = f'{self.atk}/{self.def_}/{self.spa}/{self.spd}/{self.spe}\n{self.evasion} Evasion\n{self.accuracy} Accuracy'
        if self.confused:
            final_string += '\nConfused'
        if self.paralyzed:
            final_string += '\nParalyzed'
        if self.aqua_ring:
            final_string += '\nAqua Ring'
        if self.taunt:
            final_string += '\nTaunt'
        if self.frozen:
            final_string += '\nFrozen'
        if self.toxic:
            final_string += '\nToxic'
        if self.endure:
            final_string += '\nEndure'
        return final_string

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
    item: str | None
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

@dataclass
class BattlefieldInfo:
    weather: Literal['Sun', 'Sandstorm', 'Snow', 'Rain'] | None
    terrain: Literal['Electric', 'Psychic', 'Misty', 'Grassy'] | None
    my_other: list[Literal['Light Screen', 'Reflect', 'Mist', 'Aurora Veil', 'Safeguard']]
    enemy_other: list[Literal['Light Screen', 'Reflect', 'Mist', 'Aurora Veil', 'Safeguard']]
    my_hazards: list[Literal['Spikes', 'Toxic Spikes', 'Stealth Rock', 'Sticky Web']]
    enemy_hazards: list[Literal['Spikes', 'Toxic Spikes', 'Stealth Rock', 'Sticky Web']]

    def display_items(self) -> list[str]:
        """Return a string representation of the items."""
        final_strings: list[str] = []
        final_strings.append(f'Weather: {self.weather}\nTerrain: {self.terrain}')
        final_strings.append('My Other:\n' + '\n'.join(f'- {effect}' for effect in self.my_other))
        final_strings.append('Enemy Other:\n' + '\n'.join(f'- {effect}' for effect in self.enemy_other))
        final_strings.append('My Hazards:\n' + '\n'.join(f'- {effect}' for effect in self.my_hazards))
        final_strings.append('Enemy Hazards:\n' + '\n'.join(f'- {effect}' for effect in self.enemy_hazards))
        return final_strings

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
    confused = False
    paralyzed = False
    aqua_ring = False
    taunt = False
    frozen = False
    toxic = False
    endure = False

    after_buff: tuple[str, float] | None = None
    for modifier in [e.text for e in statuses.find_elements(by=By.TAG_NAME, value='span')]:
        if 'Protosynthesis' in modifier or 'Quark Drive' in modifier:
            affected = modifier.split(':')[1].strip()
            if affected == 'Spe':
                after_buff = (affected, 0.5)
            else:
                after_buff = (affected, 0.3)
        elif 'Confused' in modifier:
            confused = True
        elif 'PAR' in modifier:
            paralyzed = True
        elif 'Aqua' in modifier:
            aqua_ring = True
        elif 'Taunt' in modifier:
            taunt = True
        elif 'FRZ' in modifier:
            frozen = True
        elif 'TOX' in modifier:
            toxic = True
        elif 'Endure' in modifier:
            endure = True
        else:
            modifier_name = modifier.split()[0][:-1]
            modifier_value = float(modifier.split()[1].strip())
            temp_modifiers[modifier_name] = modifier_value
    
    if after_buff is not None:
        temp_modifiers[after_buff[0]] += after_buff[1]
    
    return ModifierInfo(
        atk=temp_modifiers['Atk'],
        def_=temp_modifiers['Def'],
        spa=temp_modifiers['SpA'],
        spd=temp_modifiers['SpD'],
        spe=temp_modifiers['Spe'],
        evasion=temp_modifiers['Evasion'],
        accuracy=temp_modifiers['Accuracy'],
        confused=confused,
        paralyzed=paralyzed,
        aqua_ring=aqua_ring,
        taunt=taunt,
        frozen=frozen,
        toxic=toxic,
        endure=endure,
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

    def _get_tooltip(self, element: WebElement) -> WebElement | None:
        ActionChains(self).move_to_element(element).perform()
        time.sleep(0.05)
        try:
            return self.find_element(by=By.CLASS_NAME, value='tooltip')
        except NoSuchElementException:
            return None
    
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
                if tooltip is None:
                    continue
                header = tooltip.find_element(by=By.TAG_NAME, value='h2')
                pokemon_name = header.text
                pokemon_gender = self._get_gender_from_header(header)
                pokemon_info = tooltip.find_elements(by=By.TAG_NAME, value='p')
                try:
                    pokemon_hp = float(pokemon_info[0].text.split(':')[1].split('%')[0])
                except ValueError:
                    pokemon_hp = 0.0
                pokemon_abilities = [a.strip() for a in pokemon_info[1].text.split(':')[1].split(',')]
                item = None
                line_3_raw = pokemon_info[2].text.split()
                if line_3_raw[0] == 'Spe':
                    pokemon_speed = (int(line_3_raw[1]), int(line_3_raw[3]))
                else:
                    item = pokemon_info[2].text.split(':')[1].strip()
                    if item.startswith('None'):
                        item = None
                    line_4_raw = pokemon_info[3].text.split()
                    pokemon_speed = (int(line_4_raw[1]), int(line_4_raw[1]))
                
                team.append(PokemonInfo(pokemon_name, pokemon_gender, pokemon_hp, item, pokemon_abilities, pokemon_speed))
        
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
            if tooltip is None:
                continue
            header = tooltip.find_element(by=By.TAG_NAME, value='h2')
            pokemon_types = self._get_types_from_header(header)
            pokemon_info = tooltip.find_elements(by=By.TAG_NAME, value='p')
            fainted = False
            hp_percent = 0.0
            total_hp = 0
            # this hp percent/fainted thing is incredibly scuffed
            # but it catches some stupid bugs i had
            try:
                pokemon_item = pokemon_info[1].text.split(':')[2].strip()
            except IndexError:
                pokemon_item = 'None'
            except ValueError:
                fainted = True
            try:
                hp_percent = float(pokemon_info[0].text.split(':')[1].split('%')[0])
                total_hp = int(pokemon_info[0].text.split('/')[1].split(')')[0])
            except ValueError:
                fainted = True
            starting_info.append(StartingPokemonInfo(
                name=self._get_pokemon_type(header.text.split('\n')[0]),
                gender=self._get_gender_from_header(header),
                types=pokemon_types[:-1],
                tera_type=pokemon_types[-1],
                hp_percent=0.0 if fainted else hp_percent,
                total_hp=total_hp,
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

    def get_battlefield_info(self) -> BattlefieldInfo:
        info = BattlefieldInfo(
            weather=None,
            terrain=None,
            my_other=[],
            enemy_other=[],
            my_hazards=[],
            enemy_hazards=[],
        )

        # it's called weather but it has everything else too
        effects_div = self.find_elements(by=By.CLASS_NAME, value='weather')[1]
        effects = effects_div.find_element(by=By.TAG_NAME, value='em').text.split('\n')
        for effect in effects:
            if effect == '':
                continue
            effect_name = effect.split('(')[0].strip()
            if effect_name in {'Sun', 'Sandstorm', 'Snow', 'Rain'}:
                info.weather = effect_name
            elif effect_name.split(' ')[0] in {'Electric', 'Psychic', 'Misty', 'Grassy'}:
                info.terrain = effect_name.split(' ')[0]
            elif effect_name in {'Light Screen', 'Reflect', 'Mist', 'Aurora Veil', 'Safeguard'}:
                info.my_other.append(effect_name)
            elif effect_name in {'Foe\'s Light Screen', 'Foe\'s Reflect', 'Foe\'s Mist', 'Foe\'s Aurora Veil', 'Foe\'s Safeguard'}:
                info.enemy_other.append(effect_name)
            else:
                print(f'Unknown effect: {effect_name}')
        
        inner_battle_div = self.find_element(by=By.CLASS_NAME, value='innerbattle')
        graphics_div = inner_battle_div.find_elements(by=By.TAG_NAME, value='div')[4]
        my_hazards = graphics_div.find_elements(by=By.TAG_NAME, value='div')[2].find_elements(by=By.TAG_NAME, value='img')
        enemy_hazards = graphics_div.find_elements(by=By.TAG_NAME, value='div')[1].find_elements(by=By.TAG_NAME, value='img')
        
        for hazard in my_hazards:
            hazard_name = hazard.get_attribute('src').split('/')[-1].split('.')[0]
            if hazard_name in {'rock1', 'rock2'}:
                if 'Stealth Rock' not in info.my_hazards:
                    info.my_hazards.append('Stealth Rock')
            elif hazard_name == 'caltrop':
                info.my_hazards.append('Spikes')
            elif hazard_name == 'poisoncaltrop':
                info.my_hazards.append('Toxic Spikes')
            elif hazard_name == 'web':
                info.my_hazards.append('Sticky Web')
            else:
                print(f'Unknown hazard: {hazard_name}')
        
        for hazard in enemy_hazards:
            hazard_name = hazard.get_attribute('src').split('/')[-1].split('.')[0]
            if hazard_name in {'rock1', 'rock2'}:
                info.enemy_hazards.append('Stealth Rock')
            elif hazard_name == 'caltrop':
                info.enemy_hazards.append('Spikes')
            elif hazard_name == 'poisoncaltrop':
                info.enemy_hazards.append('Toxic Spikes')
            elif hazard_name == 'web':
                info.enemy_hazards.append('Sticky Web')
            else:
                print(f'Unknown hazard: {hazard_name}')

        return info

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
