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
    driver: WebDriver | None = None

    tree: ttk.Treeview | None = None
    _treeview_info_frame: ttk.Frame | None = None

    _near_team_info_frame: ttk.Frame | None = None
    _near_team_info_subframes: list[ttk.Frame] | None = None
    _far_team_info_frame: ttk.Frame | None = None
    _far_team_info_subframes: list[ttk.Frame] | None = None
    _move_info_frame: ttk.Frame | None = None
    _move_info_subframes: list[ttk.Frame] | None = None
    _status_info_frame: ttk.Frame | None = None
    _status_info_subframes: list[ttk.Frame] | None = None
    _battlefield_info_frame: ttk.Frame | None = None
    _battlefield_info_subframes: list[ttk.Frame] | None = None
    _prediction_frame: ttk.Frame | None = None
    _prediction_subframe: list[ttk.Frame] | None = None

    my_team: list[StartingPokemonInfo] | None = None
    enemy_team: list[PokemonInfo] | None = None
    moves: list[MoveInfo] | None = None
    my_status: ModifierInfo | None = None
    enemy_status: ModifierInfo | None = None
    battlefield: BattlefieldInfo | None = None
    
    """A GUI for the bot."""
    def __init__(self, window_name: str, geometry: str) -> None:
        """Initialize the GUI."""
        self.window = tkinter.Tk()
        self.window.title(window_name)
        self.window.geometry(geometry)

        info_frame = ttk.Frame(self.window)
        info_frame.pack(fill=tkinter.BOTH, expand=True)
        tree_frame = ttk.Frame(info_frame)
        tree_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.tree = self.create_treeview(tree_frame)
        self._treeview_info_frame = ttk.Frame(info_frame)
        self._treeview_info_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        
        # self._near_team_info_frame, self._near_team_info_subframes = self._add_team_info('Your Team')
        # self._far_team_info_frame, self._far_team_info_subframes = self._add_team_info('Enemy Team')
        # self._move_info_frame, self._move_info_subframes = self._add_move_info()
        # self._status_info_frame, self._status_info_subframes = self._add_status_info()
        # self._battlefield_info_frame, self._battlefield_info_subframes = self.add_battlefield_info()
        
        self._prediction_frame, self._prediction_subframe = self.add_prediction()

        self._add_buttons()
    
    def run(self) -> None:
        """Run the GUI."""
        self.window.mainloop()
    
    def hook(self, driver: WebDriver) -> None:
        """Hook the GUI to the driver."""
        self.driver = driver
    
    def create_treeview(self, frame: tkinter.Frame) -> ttk.Treeview:
        """Create a treeview for the given frame."""
        tree = ttk.Treeview(frame)
        tree.pack(side=tkinter.LEFT, fill=tkinter.Y)
        tree_scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree_scroll.pack(side=tkinter.LEFT, fill=tkinter.Y)
        tree.configure(yscrollcommand=tree_scroll.set)

        # add entries for the teams, moves, statuses, and battlefield
        tree.insert('', 'end', 'team', text='Team')
        tree.insert('team', 'end', 'near_team', text='Near Team')
        tree.insert('team', 'end', 'far_team', text='Far Team')
        tree.insert('', 'end', 'moves', text='Moves')
        tree.insert('', 'end', 'statuses', text='Statuses')
        tree.insert('', 'end', 'battlefield', text='Battlefield')

        # call update_selection_frame when the selection changes
        tree.bind('<<TreeviewSelect>>', lambda _: self.update_selection_frame())

        return tree

    def update_tree_teams(self) -> None:
        """Add the teams to the treeview."""
        for child in self.tree.get_children('near_team'):
            self.tree.delete(child)
        for child in self.tree.get_children('far_team'):
            self.tree.delete(child)
        if self.my_team is not None:
            for i, pokemon in enumerate(self.my_team):
                name = f'{pokemon.nickname} ({pokemon.name})' if pokemon.nickname is not None else pokemon.name
                self.tree.insert('near_team', 'end', f'near_pokemon_{i}', text=name)
        if self.enemy_team is not None:
            for i, pokemon in enumerate(self.enemy_team):
                name = f'{pokemon.nickname} ({pokemon.name})' if pokemon.nickname is not None else pokemon.name
                self.tree.insert('far_team', 'end', f'far_pokemon_{i}', text=name)
    
    def update_selection_frame(self) -> None:
        """Update the treeview info frame based on the current treeview selection."""
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        selection = selection[0]

        def write_to_frame(lines: list[str]) -> None:
            """Write the given lines to the info frame."""
            for child in self._treeview_info_frame.winfo_children():
                child.destroy()
            for line in lines:
                label = ttk.Label(self._treeview_info_frame, text=line)
                label.pack(side=tkinter.TOP, anchor=tkinter.W, pady=3)

        if selection == 'near_team':
            if self.my_team is None:
                write_to_frame(['No team info available.'])
            else:
                write_to_frame([f'{pokemon.name}: {pokemon.hp_percent:02}%' for pokemon in self.my_team])
        elif selection == 'far_team':
            if self.enemy_team is None:
                write_to_frame(['No team info available.'])
            else:
                write_to_frame([f'{pokemon.name}: {pokemon.hp_percent:02}%' for pokemon in self.enemy_team])
        elif selection == 'moves':
            if self.moves is None:
                write_to_frame(['No move info available.'])
            else:
                write_to_frame([f'{move.name}: {move.type} ({move.moves_left})' for move in self.moves])
        elif selection == 'statuses':
            if self.my_status is None or self.enemy_status is None:
                write_to_frame(['No status info available.'])
            else:
                write_to_frame([self.my_status.display(), self.enemy_status.display()])
        elif selection == 'battlefield':
            if self.battlefield is None:
                write_to_frame(['No battlefield info available.'])
            else:
                write_to_frame(self.battlefield.display_items())
        elif selection.startswith('near_pokemon_'):
            if self.my_team is None:
                write_to_frame(['No team info available.'])
            else:
                index = int(selection.split('_')[-1])
                write_to_frame([self.my_team[index].display()])
        elif selection.startswith('far_pokemon_'):
            if self.enemy_team is None:
                write_to_frame(['No team info available.'])
            else:
                index = int(selection.split('_')[-1])
                write_to_frame([self.enemy_team[index].display()])
    
    def _update_starting_team_info_from_driver(self) -> None:
        """Update the starting team info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        
        self.my_team = self.driver.get_starting_info()

        if self._near_team_info_frame is not None and self._near_team_info_subframes is not None:
            starting_team_info_strings = [info.display().split('\n') for info in self.my_team]
            self.update_info_frame(self._near_team_info_frame, self._near_team_info_subframes, starting_team_info_strings)
        
        if self.tree is not None:
            self.update_tree_teams()
            self.tree.selection_set('near_team')
            self.update_selection_frame()
    
    def _update_enemy_team_info_from_driver(self) -> None:
        """Update the enemy team info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        
        self.enemy_team = self.driver.get_enemy_team_info()

        if self._far_team_info_frame is not None and self._far_team_info_subframes is not None:
            far_team_info_strings = [info.display().split('\n') for info in self.enemy_team]
            self.update_info_frame(self._far_team_info_frame, self._far_team_info_subframes, far_team_info_strings)
        
        if self.tree is not None:
            self.update_tree_teams()
            self.tree.selection_set('far_team')
            self.update_selection_frame()
    
    def _update_move_info_from_driver(self) -> None:
        """Update the info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        self.moves = self.driver.get_available_moves()

        if self._move_info_frame is not None and self._move_info_subframes is not None:
            move_info_strings = [info.display().split('\n') for info in self.moves]
            self.update_info_frame(self._move_info_frame, self._move_info_subframes, move_info_strings)
        
        if self.tree is not None:
            self.tree.selection_set('moves')
            self.update_selection_frame()
    
    def _update_status_info_from_driver(self) -> None:
        """Update the status info frame from the driver."""
        if self.driver is None:
            return
        
        self.my_status = self.driver.get_my_statbar()
        self.enemy_status = self.driver.get_enemy_statbar()
        
        if self._status_info_frame is not None and self._status_info_subframes is not None:
            status_strings: list[list[str]] = []
            status_strings.append(self.my_status.display().split('\n'))
            status_strings.append(self.enemy_status.display().split('\n'))
            self.update_info_frame(self._status_info_frame, self._status_info_subframes, status_strings)
        
        if self.tree is not None:
            self.tree.selection_set('statuses')
            self.update_selection_frame()
    
    def _update_battlefield_info_from_driver(self) -> None:
        """Update the battlefield info frame from the driver."""
        if self.driver is None:
            return
        
        self.battlefield = self.driver.get_battlefield_info()

        if self._battlefield_info_frame is not None and self._battlefield_info_subframes is not None:
            battlefield_strings = [info.split('\n') for info in self.battlefield.display_items()]
            self.update_info_frame(self._battlefield_info_frame, self._battlefield_info_subframes, battlefield_strings)
        
        if self.tree is not None:
            self.tree.selection_set('battlefield')
            self.update_selection_frame()
    
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
        button_frame.pack(side=tkinter.BOTTOM, pady=5)
        btn = ttk.Button(button_frame, text='Get Status Info', command=self._update_status_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5)
        btn = ttk.Button(button_frame, text='Get Battlefield Info', command=self._update_battlefield_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5)

        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tkinter.BOTTOM, pady=5)
        btn = ttk.Button(button_frame, text='Get Starting Info', command=self._update_starting_team_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5)
        btn = ttk.Button(button_frame, text='Get Enemy Team Info', command=self._update_enemy_team_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5)
        btn = ttk.Button(button_frame, text='Get Move Info', command=self._update_move_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5)

        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tkinter.BOTTOM, pady=5)
        btn = ttk.Button(button_frame, text='Get All Info', command=self._update_all_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5)
        btn = ttk.Button(button_frame, text='Run Model', command=self._update_prediction)
        btn.pack(side=tkinter.LEFT, padx=5)
    
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
        
        prediction_label = ttk.Label(prediction_frame, text='Predictions')
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
        for pokemon in my_bench:
            nickname = pokemon.nickname if pokemon.nickname is not None else pokemon.name
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

        model = load_model('model.h5')
        df = pd.DataFrame([data])
        scaler = MinMaxScaler()
        df_to_scale = pd.read_csv('final_moves.csv')
        X_train = df_to_scale.drop(columns=['PlayerMove'])
        scaler.fit(X_train)
        df_scaled = scaler.transform(df)
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
        move_mapping['switch'] = 0
        reverse_move_mapping = {v: k for k, v in move_mapping.items()}

        # Assuming self.moves is a list of move names
        # Encode self.moves using the mapping
        encoded_moves = [move_mapping[move.name] for move in self.moves if move.name in move_mapping]

        # Filter the list to a list of valid moves
        valid_moves = [index for index in sorted_indices if index in encoded_moves or index == 0]

        # Format into a list of strings with the move name and probability
        move_probabilities = [f'{reverse_move_mapping[index]}: {(pred[0][index]*100):.2f}%' for index in valid_moves]

        if self._prediction_frame is not None and self._prediction_subframe is not None:
            self.update_info_frame(self._prediction_frame, self._prediction_subframe, [move_probabilities])
