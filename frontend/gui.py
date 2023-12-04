import tkinter
from tkinter import ttk
import time

import pandas as pd
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from .driver import WebDriver, PokemonInfo, MoveInfo, ModifierInfo, StartingPokemonInfo, BattlefieldInfo
from .conversion import serialize_data, load_pokemon_table


class GUI:
    
    window: tkinter.Tk
    driver: WebDriver | None
    _near_team_info_frame: ttk.Frame
    _near_team_info_subframes: list[ttk.Frame]
    _far_team_info_frame: ttk.Frame
    _far_team_info_subframes: list[ttk.Frame]
    _move_info_frame: ttk.Frame
    _move_info_subframes: list[ttk.Frame]
    _status_info_frame: ttk.Frame
    _status_info_subframes: list[ttk.Frame]
    _battlefield_info_frame: ttk.Frame
    _battlefield_info_subframes: list[ttk.Frame]
    _prediction: ttk.Frame
    _prediction_subframe: list[ttk.Frame]
    my_team: list[StartingPokemonInfo]
    enemy_team: list[PokemonInfo]
    moves: list[MoveInfo]
    my_status: ModifierInfo
    enemy_status: ModifierInfo
    battlefield: BattlefieldInfo
    
    """A GUI for the bot."""
    def __init__(self, window_name: str, geometry: str) -> None:
        """Initialize the GUI."""
        self.window = tkinter.Tk()
        self.window.title(window_name)
        self.window.geometry(geometry)
        
        self._add_buttons()
        self._near_team_info_frame, self._near_team_info_subframes = self._add_team_info('Your Team')
        self._far_team_info_frame, self._far_team_info_subframes = self._add_team_info('Enemy Team')
        self._move_info_frame, self._move_info_subframes = self._add_move_info()
        self._status_info_frame, self._status_info_subframes = self._add_status_info()
        self._battlefield_info_frame, self._battlefield_info_subframes = self.add_battlefield_info()
        self._prediction, self._prediction_subframe = self.add_prediction()
    
    def run(self) -> None:
        """Run the GUI."""
        self.window.mainloop()
    
    def hook(self, driver: WebDriver) -> None:
        """Hook the GUI to the driver."""
        self.driver = driver
    
    def _update_starting_team_info_from_driver(self) -> None:
        """Update the starting team info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        
        starting_team_info = self.driver.get_starting_info()
        starting_team_info_strings = [info.display().split('\n') for info in starting_team_info]
        self.update_info_frame(self._near_team_info_frame, self._near_team_info_subframes, starting_team_info_strings)
        
        self.my_team = starting_team_info
    
    def _update_enemy_team_info_from_driver(self) -> None:
        """Update the enemy team info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        
        far_team_info = self.driver.get_enemy_team_info()
        far_team_info_strings = [info.display().split('\n') for info in far_team_info]
        self.update_info_frame(self._far_team_info_frame, self._far_team_info_subframes, far_team_info_strings)
        
        self.enemy_team = far_team_info
    
    def _update_move_info_from_driver(self) -> None:
        """Update the info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        move_info = self.driver.get_available_moves()
        move_info_strings = [info.display().split('\n') for info in move_info]
        self.update_info_frame(self._move_info_frame, self._move_info_subframes, move_info_strings)
        
        self.moves = move_info
    
    def _update_status_info_from_driver(self) -> None:
        """Update the status info frame from the driver."""
        if self.driver is None:
            return
        
        status_strings: list[list[str]] = []
        
        my_status_info = self.driver.get_my_statbar()
        status_strings.append(my_status_info.display().split('\n'))
        
        enemy_status_info = self.driver.get_enemy_statbar()
        status_strings.append(enemy_status_info.display().split('\n'))
        
        self.update_info_frame(self._status_info_frame, self._status_info_subframes, status_strings)

        self.my_status = my_status_info
        self.enemy_status = enemy_status_info
    
    def _update_battlefield_info_from_driver(self) -> None:
        """Update the battlefield info frame from the driver."""
        if self.driver is None:
            return
        
        battlefield_info = self.driver.get_battlefield_info()
        battlefield_strings = [info.split('\n') for info in battlefield_info.display_items()]
        
        self.update_info_frame(self._battlefield_info_frame, self._battlefield_info_subframes, battlefield_strings)

        self.battlefield = battlefield_info
    
    def _update_all_info_from_driver(self) -> None:
        """Update all info frames from the driver."""
        self._update_starting_team_info_from_driver()
        self._update_enemy_team_info_from_driver()
        self._update_move_info_from_driver()
        self._update_status_info_from_driver()
        self._update_battlefield_info_from_driver()
    
    def _add_buttons(self) -> None:
        """Add buttons to the window."""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tkinter.BOTTOM, pady=10)
        btn = ttk.Button(button_frame, text='Get Starting Info', command=self._update_starting_team_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
        btn = ttk.Button(button_frame, text='Get Enemy Team Info', command=self._update_enemy_team_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
        btn = ttk.Button(button_frame, text='Get Move Info', command=self._update_move_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
        btn = ttk.Button(button_frame, text='Get Status Info', command=self._update_status_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
        btn = ttk.Button(button_frame, text='Get Battlefield Info', command=self._update_battlefield_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)

        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tkinter.BOTTOM, pady=10)
        btn = ttk.Button(button_frame, text='Get All Info', command=self._update_all_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
        btn = ttk.Button(button_frame, text='Run Model', command=self._update_prediction)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
    
    def _add_team_info(self, team_name: str) -> tuple[ttk.Frame, list[ttk.Frame]]:
        """Adds an area to display team info in a horizontal frame."""
        team_frame = ttk.Frame(self.window)
        team_frame.pack(side=tkinter.TOP, pady=10)
        
        team_label = ttk.Label(team_frame, text=f'Team Info: {team_name}')
        team_label.pack(side=tkinter.TOP)
        
        team_info_frame = ttk.Frame(team_frame)
        team_info_frame.pack(side=tkinter.TOP)
        
        subframes: list[ttk.Frame] = []
        for _ in range(6):
            pokemon_frame = ttk.Frame(team_info_frame)
            pokemon_frame.pack(side=tkinter.LEFT, padx=5)
            name_label = ttk.Label(pokemon_frame, text='Unknown')
            name_label.pack(side=tkinter.TOP)
            subframes.append(pokemon_frame)
        
        return team_info_frame, subframes

    def _add_move_info(self) -> tuple[ttk.Frame, list[ttk.Frame]]:
        """Adds an area to display move info in a horizontal frame."""
        move_frame = ttk.Frame(self.window)
        move_frame.pack(side=tkinter.TOP, pady=10)
        
        move_label = ttk.Label(move_frame, text='Move Info')
        move_label.pack(side=tkinter.TOP)
        
        move_info_frame = ttk.Frame(move_frame)
        move_info_frame.pack(side=tkinter.TOP)
        
        subframes: list[ttk.Frame] = []
        for _ in range(4):
            move_frame = ttk.Frame(move_info_frame)
            move_frame.pack(side=tkinter.LEFT, padx=5)
            name_label = ttk.Label(move_frame, text='Unknown')
            name_label.pack(side=tkinter.TOP)
            subframes.append(move_frame)
        
        return move_info_frame, subframes

    def _add_status_info(self) -> tuple[ttk.Frame, list[ttk.Frame]]:
        """Adds an area to display status info for each team in a horizontal frame."""
        status_frame = ttk.Frame(self.window)
        status_frame.pack(side=tkinter.TOP, pady=10)
        
        status_label = ttk.Label(status_frame, text='Status Info')
        status_label.pack(side=tkinter.TOP)
        
        status_info_frame = ttk.Frame(status_frame)
        status_info_frame.pack(side=tkinter.TOP)
        
        subframes: list[ttk.Frame] = []
        
        for _ in range(2):
            status_frame = ttk.Frame(status_info_frame)
            status_frame.pack(side=tkinter.LEFT, padx=5)
            name_label = ttk.Label(status_frame, text='Unknown')
            name_label.pack(side=tkinter.TOP)
            subframes.append(status_frame)
        
        return status_info_frame, subframes

    def add_battlefield_info(self) -> tuple[ttk.Frame, list[ttk.Frame]]:
        """Adds an area to display battlefield info in a horizontal frame."""
        battlefield_frame = ttk.Frame(self.window)
        battlefield_frame.pack(side=tkinter.TOP, pady=10)
        
        battlefield_label = ttk.Label(battlefield_frame, text='Battlefield Info')
        battlefield_label.pack(side=tkinter.TOP)
        
        battlefield_info_frame = ttk.Frame(battlefield_frame)
        battlefield_info_frame.pack(side=tkinter.TOP)
        
        subframes: list[ttk.Frame] = []
        
        for _ in range(3):
            battlefield_frame = ttk.Frame(battlefield_info_frame)
            battlefield_frame.pack(side=tkinter.LEFT, padx=5)
            name_label = ttk.Label(battlefield_frame, text='Unknown')
            name_label.pack(side=tkinter.TOP)
            subframes.append(battlefield_frame)
        
        return battlefield_info_frame, subframes

    def add_prediction(self) -> tuple[ttk.Frame, list[ttk.Frame]]:
        """Adds an area to display the prediction."""
        prediction_frame = ttk.Frame(self.window)
        prediction_frame.pack(side=tkinter.TOP, pady=10)
        
        prediction_label = ttk.Label(prediction_frame, text='Prediction')
        prediction_label.pack(side=tkinter.TOP)
        
        prediction_info_frame = ttk.Frame(prediction_frame)
        prediction_info_frame.pack(side=tkinter.TOP)
        
        subframes: list[ttk.Frame] = []
        
        prediction_frame = ttk.Frame(prediction_info_frame)
        prediction_frame.pack(side=tkinter.LEFT, padx=5)
        name_label = ttk.Label(prediction_frame, text='Unknown')
        name_label.pack(side=tkinter.TOP)
        subframes.append(prediction_frame)

        return prediction_info_frame, subframes
    
    def update_info_frame(self, frame: ttk.Frame, subframes: list[ttk.Frame], info: list[list[str]]) -> None:
        """Update the info frame with the given info."""
        for subframe in subframes:
            subframe.destroy()
        subframes.clear()
        for info_lines in info:
            subframe = ttk.Frame(frame)
            subframe.pack(side=tkinter.LEFT, padx=5)
            for line in info_lines:
                label = ttk.Label(subframe, text=line)
                label.pack(side=tkinter.TOP)
            subframes.append(subframe)
        frame.update()
    
    def format_data(self) -> dict[str, int | float]:
        """Format the data into a dictionary."""
        table = load_pokemon_table('pkmn_data.csv')

        my_onfield: StartingPokemonInfo | None = None
        my_bench = self.my_team.copy()
        active_pokemon_name = self.my_status.pokemon
        print(active_pokemon_name)
        for pokemon in my_bench:
            nickname = pokemon.nickname if pokemon.nickname is not None else pokemon.name
            print(f'\t{nickname}')
            if nickname == active_pokemon_name:
                my_onfield = pokemon
                my_bench.remove(pokemon)
                break
        if my_onfield is None:
            raise ValueError('Could not find active pokemon in team.')
        
        enemy_onfield: PokemonInfo | None = None
        enemy_bench = self.enemy_team.copy()
        active_pokemon_name = self.enemy_status.pokemon
        for pokemon in enemy_bench:
            nickname = pokemon.nickname if pokemon.nickname is not None else pokemon.name
            if nickname == active_pokemon_name:
                enemy_onfield = pokemon
                enemy_bench.remove(pokemon)
                break
        if enemy_onfield is None:
            raise ValueError('Could not find active pokemon in team.')
        
        return serialize_data(
            pokemon_table=table,
            player_pokemon=my_onfield,
            player_bench=my_bench,
            player_status=self.my_status,
            enemy_pokemon=enemy_onfield,
            enemy_bench=enemy_bench,
            enemy_status=self.enemy_status,
            battlefield=self.battlefield,
        )
    
    def _update_prediction(self) -> None:
        """Update the prediction."""
        if self.driver is None:
            return

        data = self.format_data()
        print(data)

        model = load_model('model.h5')
        df = pd.DataFrame([data])
        scaler = MinMaxScaler()
        df_scaled = scaler.fit_transform(df)
        pred = model.predict(df_scaled)

        # sort the moves based on their probabilities in descending order
        sorted_indices = np.argsort(-pred[0])
        if sorted_indices.ndim > 1:
            sorted_indices = sorted_indices.flatten()
        
        # load all the moves' data from the excel file
        moves_data = pd.ExcelFile('move_data.xlsx')
        df_moves = pd.read_excel(moves_data, sheet_name=0)

        # Create a dictionary mapping from move name to a numerical value or index
        # Assuming the Excel file has columns 'move_name' and 'move_value'
        move_mapping = pd.Series(df_moves['id'].values, index=df_moves['name']).to_dict()

        # Assuming self.moves is a list of move names
        # Encode self.moves using the mapping
        encoded_moves = [move_mapping[move.name] for move in self.moves if move.name in move_mapping]

        # Find the highest probability move that is in the user's list of available moves
        highest_valid_move_index = next((index for index in sorted_indices if index in encoded_moves), None)

        reverse_move_mapping = {v: k for k, v in move_mapping.items()}
        print([reverse_move_mapping[i] for i in sorted_indices[:5]])
        move_name = reverse_move_mapping[highest_valid_move_index]

        self.update_info_frame(self._prediction, self._prediction_subframe, [[move_name]])
