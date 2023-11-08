from dataclasses import dataclass
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


@dataclass
class StatbarInfo:
    name: str
    level: int
    hp_percent: int

@dataclass
class MoveInfo:
    name: str
    type: str
    moves_left: int

@dataclass
class PokemonInfo:
    name: str
    gender: str | None
    hp_percent: float
    abilities: list[MoveInfo]
    speed: tuple[int, int]


def _parse_statbar(statbar: str) -> StatbarInfo:
    """Parse a statbar string into a StatbarInfo object."""
    statbar_info = statbar.split()
    name = ' '.join(statbar_info[:-2])
    level = statbar_info[-2]
    hp_percent = int(statbar_info[-1])
    return StatbarInfo(name, level, hp_percent)

def get_enemy_statbar(driver: webdriver.Chrome) -> StatbarInfo:
    enemy_statbar = driver.find_elements(by=By.CLASS_NAME, value='statbar')[0]
    return _parse_statbar(enemy_statbar.text)

def get_my_statbar(driver: webdriver.Chrome) -> StatbarInfo:
    my_statbar = driver.find_elements(by=By.CLASS_NAME, value='statbar')[1]
    return _parse_statbar(my_statbar.text)

def get_available_moves(driver: webdriver.Chrome) -> list[MoveInfo]:
    """Return a list of available moves."""
    move_menu = driver.find_element(by=By.CLASS_NAME, value='movemenu')
    moves: list[MoveInfo] = []
    for move_button in move_menu.find_elements(by=By.TAG_NAME, value='button'):
        button_info = move_button.text.split()
        move_name = ' '.join(button_info[:-2])
        move_type = button_info[-2]
        moves_left = int(button_info[-1].split('/')[0])
        moves.append(MoveInfo(move_name, move_type, moves_left))
    return moves

def _get_team_info(driver: webdriver.Chrome, side_name: str) -> list[PokemonInfo]:
    side = driver.find_element(by=By.CLASS_NAME, value=side_name)
    icons = side.find_elements(by=By.CLASS_NAME, value='teamicons')
    team: list[PokemonInfo] = []
    for icon_set in icons:
        for icon in icon_set.find_elements(by=By.TAG_NAME, value='span'):
            ActionChains(driver).move_to_element(icon).perform()
            time.sleep(0.05)
            
            tooltip = driver.find_element(by=By.CLASS_NAME, value='tooltip')
            header = tooltip.find_element(by=By.TAG_NAME, value='h2')
            pokemon_name = header.text
            try:
                pokemon_gender = header.find_element(by=By.TAG_NAME, value='img').get_attribute('alt')
                if pokemon_gender not in {'M', 'F'}:
                    # there was no gender image
                    pokemon_gender = None
            except NoSuchElementException:
                pokemon_gender = None
            pokemon_info = tooltip.find_elements(by=By.TAG_NAME, value='p')
            pokemon_hp = float(pokemon_info[0].text.split(':')[1].split('%')[0])
            pokemon_abilities = [a.strip() for a in pokemon_info[1].text.split(':')[1].split(',')]
            pokemon_speed_raw = pokemon_info[2].text.split()
            pokemon_speed = (int(pokemon_speed_raw[1]), int(pokemon_speed_raw[3]))
            
            team.append(PokemonInfo(pokemon_name, pokemon_gender, pokemon_hp, pokemon_abilities, pokemon_speed))
    
    return team

def get_my_team(driver: webdriver.Chrome) -> list[PokemonInfo]:
    return _get_team_info(driver, 'trainer-near')

def get_enemy_team(driver: webdriver.Chrome) -> list[PokemonInfo]:
    return _get_team_info(driver, 'trainer-far')

def testing(driver: webdriver.Chrome) -> None:
    while True:
        # execute an input string in Python for testing purposes
        try:
            print(eval(input(">>> ")))
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)

def main() -> None:
    driver = webdriver.Chrome()
    driver.get("https://play.pokemonshowdown.com/")
    testing(driver)
    driver.quit()

if __name__ == '__main__':
    main()
