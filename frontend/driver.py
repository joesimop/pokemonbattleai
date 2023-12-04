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
    pokemon: str
    atk: int
    def_: int
    spa: int
    spd: int
    spe: int
    evasion: int
    accuracy: int
    confused: bool
    paralyzed: bool
    aqua_ring: bool
    taunt: bool
    frozen: bool
    toxic: bool
    endure: bool
    poison: bool
    
    def display(self) -> str:
        """Return a string representation of the statbar."""
        final_string = f'{self.pokemon}:\n'
        final_string += f'{self.atk}/{self.def_}/{self.spa}/{self.spd}/{self.spe}\n{self.evasion} Evasion\n{self.accuracy} Accuracy'
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
        if self.poison:
            final_string += '\nPoison'
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
    nickname: str | None
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
    nickname: str | None
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
        final_strings.append('My Other:' + ''.join(f'\n- {effect}' for effect in self.my_other))
        final_strings.append('Enemy Other:' + ''.join(f'\n- {effect}' for effect in self.enemy_other))
        final_strings.append('My Hazards:' + ''.join(f'\n- {effect}' for effect in self.my_hazards))
        final_strings.append('Enemy Hazards:' + ''.join(f'\n- {effect}' for effect in self.enemy_hazards))
        return final_strings

def _convert_stat_to_stage(raw: float, acc_eva: bool) -> int:
    """Convert a raw stat to a multiplier stage."""
    if acc_eva:
        conversions = [
            (9 / 3, 6),
            (8 / 3, 5),
            (7 / 3, 4),
            (6 / 3, 3),
            (5 / 3, 2),
            (4 / 3, 1),
            (3 / 3, 0),
            (3 / 4, -1),
            (3 / 5, -2),
            (3 / 6, -3),
            (3 / 7, -4),
            (3 / 8, -5),
            (3 / 9, -6),
        ]
    else:
        conversions = [
            (8 / 2, 6),
            (7 / 2, 5),
            (6 / 2, 4),
            (5 / 2, 3),
            (4 / 2, 2),
            (3 / 2, 1),
            (2 / 2, 0),
            (2 / 3, -1),
            (2 / 4, -2),
            (2 / 5, -3),
            (2 / 6, -4),
            (2 / 7, -5),
            (2 / 8, -6),
        ]
    
    return min(conversions, key=lambda x: abs(raw - x[0]))[1]

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
    poison = False

    for modifier in [e.text for e in statuses.find_elements(by=By.TAG_NAME, value='span')]:
        if 'Protosynthesis' in modifier or 'Quark Drive' in modifier:
            pass
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
        elif 'PZN' in modifier:
            poison = True
        else:
            modifier_name = modifier.split()[1].strip()
            modifier_value = float(modifier.split()[0][:-1])
            temp_modifiers[modifier_name] = modifier_value
    
    return ModifierInfo(
        pokemon=statbar.text.split('\n')[0].strip(),
        atk=_convert_stat_to_stage(temp_modifiers['Atk'], False),
        def_=_convert_stat_to_stage(temp_modifiers['Def'], False),
        spa=_convert_stat_to_stage(temp_modifiers['SpA'], False),
        spd=_convert_stat_to_stage(temp_modifiers['SpD'], False),
        spe=_convert_stat_to_stage(temp_modifiers['Spe'], False),
        evasion=_convert_stat_to_stage(temp_modifiers['Evasion'], True),
        accuracy=_convert_stat_to_stage(temp_modifiers['Accuracy'], True),
        confused=confused,
        paralyzed=paralyzed,
        aqua_ring=aqua_ring,
        taunt=taunt,
        frozen=frozen,
        toxic=toxic,
        endure=endure,
        poison=poison,
    )


class WebDriver(webdriver.Chrome):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_enemy_statbar(self) -> ModifierInfo:
        enemy_statbar = self.find_element(by=By.CLASS_NAME, value='lstatbar')
        return _parse_statbar(enemy_statbar)

    def get_my_statbar(self) -> ModifierInfo:
        my_statbar = self.find_element(by=By.CLASS_NAME, value='rstatbar')
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
    
    def _get_pokemon_type(self, pokemon_header: str) -> tuple[str, str | None]:
        pokemon_type = pokemon_header.strip()
        nickname = None
        if '(' in pokemon_header:
            pokemon_type = pokemon_header.split('(')[1].split(')')[0]
            nickname = pokemon_header.split('(')[0].strip()
        return (pokemon_type, nickname)

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
                pokemon_name, pokemon_nickname = self._get_pokemon_type(header.text)
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
                
                team.append(PokemonInfo(pokemon_name, pokemon_nickname, pokemon_gender, pokemon_hp, item, pokemon_abilities, pokemon_speed))
        
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
            name, nickname = self._get_pokemon_type(header.text.split('\n')[0])
            starting_info.append(StartingPokemonInfo(
                name=name,
                nickname=nickname,
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
                info.enemy_other.append(' '.join(effect_name.split(' ')[1:]))
            else:
                print(f'Unknown effect: {effect_name}')
        
        inner_battle_div = self.find_element(by=By.CLASS_NAME, value='innerbattle')
        children = inner_battle_div.find_elements(by=By.XPATH, value='./*')
        graphics_div = children[4]
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
                if 'Stealth Rock' not in info.enemy_hazards:
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
