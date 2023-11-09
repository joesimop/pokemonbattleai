import tkinter
from tkinter import ttk
import time

from selenium import webdriver

from .driver import WebDriver


class GUI:
    
    window: tkinter.Tk
    driver: WebDriver | None
    _near_team_info_frame: ttk.Frame
    _near_team_info_subframes: list[ttk.Frame]
    _far_team_info_frame: ttk.Frame
    _far_team_info_subframes: list[ttk.Frame]
    _move_info_frame: ttk.Frame
    _move_info_subframes: list[ttk.Frame]
    
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
    
    def run(self) -> None:
        """Run the GUI."""
        self.window.mainloop()
    
    def hook(self, driver: WebDriver) -> None:
        """Hook the GUI to the driver."""
        self.driver = driver
    
    def _update_team_info_from_driver(self) -> None:
        """Update the info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        
        near_team_info = self.driver.get_my_team_info()
        near_team_info_strings = [info.display().split('\n') for info in near_team_info]
        self.update_info_frame(self._near_team_info_frame, self._near_team_info_subframes, near_team_info_strings)
        
        far_team_info = self.driver.get_enemy_team_info()
        far_team_info_strings = [info.display().split('\n') for info in far_team_info]
        self.update_info_frame(self._far_team_info_frame, self._far_team_info_subframes, far_team_info_strings)
    
    def _update_move_info_from_driver(self) -> None:
        """Update the info frame from the driver."""
        if self.driver is None:
            return
        # slight delay to wait for mouse movement to stop
        time.sleep(0.5)
        move_info = self.driver.get_available_moves()
        move_info_strings = [info.display().split('\n') for info in move_info]
        self.update_info_frame(self._move_info_frame, self._move_info_subframes, move_info_strings)
    
    def _add_buttons(self) -> None:
        """Add buttons to the window."""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tkinter.BOTTOM, pady=10)
        btn = ttk.Button(button_frame, text='Get Team Info', command=self._update_team_info_from_driver)
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
        btn = ttk.Button(button_frame, text='Get Move Info', command=self._update_move_info_from_driver)
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