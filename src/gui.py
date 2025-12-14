from constants import THEMES
from board import Board
from solver import Solver
import util, push
from tkinter import messagebox
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

class GameGUI:

    def __init__(self, master, root_dir, tile_size, font_size, initial_theme_name, delay_ms, auto_restart):
        self.master = master
        self.root_dir = root_dir
        self.tile_size = tile_size
        self.font_size = font_size
        self.theme_name = initial_theme_name
        self.theme = THEMES[initial_theme_name]
        self.settings = None
        self.delay_ms = delay_ms
        self.auto_restart = auto_restart
        self.selected_mode = tk.StringVar()


        self.board = Board(grid_size = 4)
        self.board.set_update_callback(self.update_gui)
        self.solver = Solver(self.board, self, delay = delay_ms)

        self.cells = [[None] * self.board.grid_size for _ in range(self.board.grid_size)]
        self.init_gui()
        self.update_gui()
        self.master.bind("<Key>", self.key_pressed)

    def init_gui(self):
        bg_colour = self.theme["BG_COLOUR"]
        self.master.configure(bg=bg_colour)

        # Settings bar
        self.top_frame = tk.Frame(self.master, bg=bg_colour)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        # Settings button
        try:
            gear_path = os.path.join(self.root_dir, "assets", "settings.png")
            gear_img = Image.open(gear_path) # CREDIT: https://www.flaticon.com/free-icons/options
            gear_size = int(self.tile_size * 0.25)
            gear_img = gear_img.resize((gear_size, gear_size), Image.Resampling.LANCZOS)
            gear_image = ImageTk.PhotoImage(gear_img)
            self.gear_button = tk.Button(
                self.top_frame,
                image=gear_image,
                bg=bg_colour,
                borderwidth=0,
                activebackground=bg_colour,
                command=self.open_settings
            )
            self.gear_button.image = gear_image
            self.gear_button.pack(side="right", padx=10)
        except Exception as e:
            print(f"Could not load settings icon: {e}")
            self.gear_button = tk.Button(self.top_frame, text="Settings", command=self.open_settings)
            self.gear_button.pack(side="right", padx=10)

        # Restart button
        self.restart_button = tk.Button(
            self.top_frame,
            text="Restart",
            bg=bg_colour,
            fg=self.theme["TILE_COLORS"][2][1],
            borderwidth=0,
            activebackground=bg_colour,
            command=self.restart_game
        )
        self.restart_button.pack(side="right", padx=10)

        # Autosolve option
        strategies = ["-","Random", "Corner","Max Merge"]

        self.auto_solve_dropdown = ttk.Combobox(
            self.top_frame,
            values = strategies,
            state = "readonly",
            textvariable=self.selected_mode
        )
        self.auto_solve_dropdown.current(0)
        self.auto_solve_dropdown.bind("<<ComboboxSelected>>", self.refresh_button_state)
        self.auto_solve_dropdown.pack(side="left", padx = 10)

        # Autosolve Button
        self.solve_button = tk.Button(
            self.top_frame,
            text = "Solve",
            bg = bg_colour,
            fg=self.theme["TILE_COLORS"][2][1],
            borderwidth=0,
            activebackground=bg_colour,
            state = "disabled",
            command=self.start_solve
        )
        self.solve_button.pack(side="left", padx=10)

        # Main board
        self.background = tk.Frame(self.master, bg=bg_colour)
        self.background.grid(row=1, column=0, padx=10, pady=10)

        for i in range(self.board.grid_size):
            for j in range(self.board.grid_size):
                cell_frame = tk.Frame(
                    self.background,
                    bg=self.theme["TILE_COLORS"][0][0],
                    width=self.tile_size,
                    height=self.tile_size
                )
                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                cell_label = tk.Label(
                    cell_frame,
                    text="",
                    bg=self.theme["TILE_COLORS"][0][0],
                    fg=self.theme["TILE_COLORS"][0][1],
                    font=("Helvetica", self.font_size, "bold"),
                    width=4,
                    height=2
                )
                cell_label.pack(expand=True, fill="both")
                self.cells[i][j] = cell_label

    def restart_game(self):
        self.solver.stop()
        self.board.restart()
        self.update_gui()

    def refresh_button_state(self, event):
        if self.auto_solve_dropdown.get() == "-":
            self.solve_button.config(state="disabled")
        else:
            self.solve_button.config(state="normal")
    
    def start_solve(self):
        if self.auto_solve_dropdown.get() == "Random":
            self.solver.random_strat()
            return
        if self.auto_solve_dropdown.get() == "Corner":
            self.solver.corner_strat()
            return
        if self.auto_solve_dropdown.get() == "Max Merge":
            self.solver.max_merge_strat()
            return

    def key_pressed(self, event): # Accepts both arrows and WSAD
        key = event.keysym.lower()
        if key in ['up', 'w', 'down', 's', 'left', 'a', 'right', 'd']:  # If user tries to interact
            self.solver.stop()

        grid = self.board.grid
        saved_grid = util.copy_grid(grid)

        # Should be moved to board
        if key in ['up', 'w']:
            push.push_up(grid)
        elif key in ['down', 's']:
            push.push_down(grid)
        elif key in ['left', 'a']:
            push.push_left(grid)
        elif key in ['right', 'd']:
            push.push_right(grid)
        
        if not util.grid_equal(saved_grid, grid):   # Only add a block if the grid has changed
            self.board.add_new_tile()

        self.make_move()

    def make_move(self):
        self.update_gui()
        grid = self.board.grid
        if util.check_won(grid):
            self.board.game_over = True
            messagebox.showinfo("2048", "You won!")
        elif util.check_lost(grid):
            self.board.game_over = True
            messagebox.showinfo("2048", "Game Over!")

    def update_theme(self, theme_name):
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        bg_colour = self.theme["BG_COLOUR"]
        self.master.configure(bg=bg_colour)
        self.top_frame.configure(bg=bg_colour)
        self.background.configure(bg=bg_colour)
        self.restart_button.configure(bg=bg_colour, fg=self.theme["TILE_COLORS"][2][1])
        self.solve_button.configure(bg=bg_colour, fg=self.theme["TILE_COLORS"][2][1])
        try:
            self.gear_button.configure(bg=bg_colour, activebackground=bg_colour)
        except Exception:
            pass
        self.update_gui()

    def update_gui(self):
        grid = self.board.get_grid()
        for i in range(self.board.grid_size):
            for j in range(self.board.grid_size):
                value = grid[i][j]
                # Get colors, using 'default' if value > 2048
                bg_color, fg_color = self.theme["TILE_COLORS"].get(value, self.theme["TILE_COLORS"]["default"])
                text = str(value) if value != 0 else ""
                label = self.cells[i][j]
                label.config(text=text, bg=bg_color, fg=fg_color)
                
                label.config(font=("Helvetica", self.font_size, "bold"))

        self.master.update_idletasks()

    def open_settings(self):
        if (self.settings == None) or (not self.settings.winfo_exists()):
            self.settings = SettingsWindow(self.master, self.theme_name, self.update_theme, self.delay_ms, self.auto_restart)
        else:
            self.settings.focus()


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, current_theme_name, theme_callback, delay_ms, auto_restart):
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.theme_callback = theme_callback
        self.parent = parent
        self.current_theme_name = tk.StringVar(value=current_theme_name)
        self.delay_ms = delay_ms
        self.auto_restart = auto_restart
        self.configure(bg=parent.cget("bg"))
        self.create_widgets()
        self.center_window()

        # Run as modal
        self.grab_set()
        self.wait_window(self)

    def create_widgets(self):
        bg_color = self.parent.cget("bg")

        # --- Theme Selection Frame ---
        theme_frame = tk.Frame(self, bg=bg_color)
        theme_frame.pack(pady=(10, 5), padx=20, anchor="w")

        tk.Label(theme_frame, text="Select Theme:", bg=bg_color, fg="#FFFFFF").pack(pady=(0, 5), anchor="w")
        for theme_name in THEMES.keys():
            rb = tk.Radiobutton(
                theme_frame,  
                bg=bg_color,
                activebackground=bg_color,
                fg="#FFFFFF",
                text=theme_name.title(),
                variable=self.current_theme_name,
                value=theme_name,
                selectcolor="#000000"
            )
            rb.pack(anchor="w", padx=20)

        # --- Delay Control Frame ---
        delay_frame = tk.Frame(self, bg=bg_color)
        delay_frame.pack(pady=10, padx=20, anchor="w")
        
        # Delay Label
        tk.Label(
            delay_frame, 
            text="Delay (ms):",
            bg=bg_color,
            fg="#FFFFFF",
            font=("Helvetica", 10)
        ).pack(side="left")

        # Delay Spinbox
        self.delay_spinbox = tk.Spinbox(
            delay_frame, 
            from_=0, 
            to=1000, 
            increment=50,
            textvariable=self.delay_ms, 
            width=5,
        )
        self.delay_spinbox.pack(side="left", padx=(5, 10))

        # --- Continuous Play Checkbox ---
        play_frame = tk.Frame(self, bg=bg_color)
        play_frame.pack(pady=(0, 10), padx=20, anchor="w")

        tk.Checkbutton(
            play_frame,
            text="Auto-Restart AI",
            variable=self.auto_restart,
            bg=bg_color,
            fg="#FFFFFF",
            selectcolor="#000000",
            activebackground=bg_color,
            offvalue=False,
            onvalue=True
        ).pack(anchor="w")

        # --- Button Frame ---
        button_frame = tk.Frame(self, bg=bg_color)
        button_frame.pack(pady=(5, 15), padx=15)

        # Revert Button (Left side of button_frame)
        tk.Button(
            button_frame,
            text="Revert",
            command=self.revert_settings, 
            width=8
        ).pack(side="left", padx=(0, 40))

        # OK Button (Right side of button_frame)
        tk.Button(
            button_frame,
            text="OK",
            command=self.apply_and_close, 
            width=8
        ).pack(side="right", padx=(10, 0))
        
        # Cancel Button (Right side, next to OK)
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_and_close, 
            width=8
        ).pack(side="right", padx=0)


    def apply_and_close(self):
        selected_theme = self.current_theme_name.get()
        self.theme_callback(selected_theme)


        self.grab_release()
        self.destroy()

    def cancel_and_close(self):
        # Close the window without applying the theme change
        self.grab_release()
        self.destroy()

    def revert_settings(self):
        self.theme_callback("colourful")
        

        self.grab_release()
        self.destroy()

    def center_window(self):
        self.parent.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()

        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")
