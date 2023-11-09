import tkinter
from tkinter import ttk


class GUI:
    
    window: tkinter.Tk
    _team_info_frame: ttk.Frame
    _team_info_subframes: list[ttk.Frame]
    _move_info_frame: ttk.Frame
    _move_info_subframes: list[ttk.Frame]
    
    """A GUI for the bot."""
    def __init__(self, window_name: str, geometry: str) -> None:
        """Initialize the GUI."""
        self.window = tkinter.Tk()
        self.window.title(window_name)
        self.window.geometry(geometry)
        
        self._add_buttons()
        self._team_info_frame, self._team_info_subframes = self._add_team_info()
        self._move_info_frame, self._move_info_subframes = self._add_move_info()
        
        self.window.mainloop()
    
    def run(self) -> None:
        """Run the GUI."""
        self.window.mainloop()
    
    def _add_buttons(self) -> None:
        """Add buttons to the window."""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tkinter.BOTTOM, pady=10)
        btn = ttk.Button(button_frame, text='Get Move Info', command=lambda: print('Call to driver for move info'))
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
        btn = ttk.Button(button_frame, text='Get Team Info', command=lambda: print('Call to driver for team info'))
        btn.pack(side=tkinter.LEFT, padx=5, pady=5)
    
    def _add_team_info(self) -> tuple[ttk.Frame, list[ttk.Frame]]:
        """Adds an area to display team info in a horizontal frame."""
        team_frame = ttk.Frame(self.window)
        team_frame.pack(side=tkinter.TOP, pady=10)
        
        team_label = ttk.Label(team_frame, text='Team Info')
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
    
    def update_info_frame(self, info: list[list[str]]) -> None:
        """Update the info frame with the given info."""
        for subframe in self._team_info_subframes:
            subframe.destroy()
        self._team_info_subframes.clear()
        for info_lines in info:
            subframe = ttk.Frame(self._team_info_frame)
            subframe.pack(side=tkinter.LEFT, padx=5)
            for line in info_lines:
                label = ttk.Label(subframe, text=line)
                label.pack(side=tkinter.TOP)
            self._team_info_subframes.append(subframe)
        self._team_info_frame.update()
    
    def test_info_update(self) -> None:
        """Test updating the info frame."""
        info = [
            ['Test 1', 'Test 2'],
            ['Test 3', 'Test 4'],
            ['Test 5', 'Test 6'],
            ['Test 7', 'Test 8'],
            ['Test 9', 'Test 10'],
            ['Test 11', 'Test 12'],
        ]
        self.update_info_frame(info)


def main() -> None:
    gui = GUI('Pokemon Showdown Bot', '500x500')
    gui.test_info_update()
    gui.run()

if __name__ == '__main__':
    main()
