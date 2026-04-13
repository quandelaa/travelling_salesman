import tkinter as tk
from tsp import Algos
import threading
from time import sleep
from tkinter import messagebox

class TSP:
    def __init__(self, window):
        self.window = window

        self.window.title("TSP Solver")
        self.window.geometry("800x600")
        self.window.resizable(False, False)

        self.cities = []
        self.end = None
        self.start = None

        self.tsp = Algos()

        self.BLACK = "black"
        self.WHITE = "white"
        self.GREEN = "green"
        self.RED = "red"
        self.BLUE = "blue"
        self.ORANGEISH = "#EFFF84"

        self.SIZE_XY = 40
        self.ROW_SIZE = 20

        self.TILE_ANIM_DELAY = 0.05
        
        self.font = ("Verdana", 18)
        self.toggled = "city"

        self.solving_lock = threading.Lock()

        self.setup_rectangles()
        self.setup_manager()

    def setup_rectangles(self):
        self.rectangles = tk.Canvas(self.window, width=800, height=600, bd=0, borderwidth=0)
        self.rectangles_size = {}

        for i in range(300):
            col = i % self.ROW_SIZE
            row = i // self.ROW_SIZE

            x_pos = col * self.SIZE_XY
            y_pos = row * self.SIZE_XY
            
            x_size = x_pos+self.SIZE_XY
            y_size = y_pos+self.SIZE_XY

            self.rectangles.create_rectangle(x_pos, y_pos, x_size, y_size, fill=self.BLACK, outline=self.WHITE, tags=("clickable", str(i)))
            self.rectangles_size[i+1] = (x_pos, y_pos, x_size, y_size)

        self.rectangles.bind("<Button-1>", self.on_click)
        self.rectangles.bind("<Button-3>", self.on_declick)
        
        self.rectangles.pack()
    
    def setup_manager(self):
        manager_window = tk.Toplevel(bg=self.BLACK)
    
        manager_window.resizable(width=False, height=False) 
        manager_window.title("Grid Manager")
        
        city_toggle = tk.Button(manager_window, text="CITY", font=self.font, fg=self.BLACK, bg=self.WHITE, command=lambda: self.toggle("city"))
        start_toggle = tk.Button(manager_window, text="START", font=self.font, fg=self.BLACK, bg=self.WHITE, command=lambda: self.toggle("start"))
        end_toggle = tk.Button(manager_window, text="END", font=self.font, fg=self.BLACK, bg=self.WHITE, command=lambda: self.toggle("end"))

        self.mode_text = tk.Label(manager_window, text="MODE: CITY", font=self.font, bg=self.BLACK, fg=self.WHITE)
        solve_button = tk.Button(manager_window, text="SOLVE", font=self.font, fg=self.BLACK, bg=self.WHITE, command=self.solve)
        clear_button = tk.Button(manager_window, text="CLEAR", font=self.font, fg=self.BLACK, bg=self.WHITE, command=self.clear)

        self.cur_distance_text = tk.Label(manager_window, text="DISTANCE: 0 TILES", font=self.font, bg=self.BLACK, fg=self.WHITE)

        start_toggle.pack(fill="x")
        end_toggle.pack(fill="x")
        city_toggle.pack(fill="x")
        solve_button.pack(fill="x")
        clear_button.pack(fill="x")

        self.mode_text.pack()
        self.cur_distance_text.pack()

    def solve(self):
        if self.solving_lock.locked():
            self.warning("A solve is still ongoing!")
            return

        if self.end == None or self.start == None:
            self.warning("Set a start and end point")
            return
        elif len(self.cities) < 1:
            self.warning("Place at least one city")
            return
            
        overall_path = [self.start]
        for city in self.cities:
            overall_path.append(city)
        overall_path.append(self.end)

        self.clear()

        solve_path_thread = threading.Thread(target=self.solve_path, args=(overall_path,), daemon=True)
        solve_path_thread.start()

        overall_distance = self.tsp.mha_distance_for_overall_path(overall_path)

        self.cur_distance_text.config(text=f"DISTANCE: {overall_distance} TILES")

    def solve_path(self, overall_path):
        with self.solving_lock:
            for i in range(len(overall_path)-1):    
                path = self.tsp.walk(overall_path[i], overall_path[i+1])
                self.path_colorize(path, overall_path)
    
    def path_colorize(self, path, overall_path):
        for point in path:
            col, row = point
            id = ((row)*self.ROW_SIZE)+col+1

            if self.rectangles.itemcget(id, "fill") == self.BLACK:
                self.rectangles.itemconfig(id, fill=self.BLUE)
            elif self.rectangles.itemcget(id, "fill") == self.WHITE:
                if point in overall_path:
                    i = overall_path.index(point)
                    
                    if i > 1:
                        col, row = overall_path[i-1]
                        cur_col, cur_row = overall_path[i]
                        id = ((row)*self.ROW_SIZE)+col+1
                        cur_id = ((cur_row)*self.ROW_SIZE)+cur_col+1

                        if self.rectangles.itemcget(id, "fill") == self.ORANGEISH:
                            self.rectangles.itemconfig(cur_id, fill=self.ORANGEISH)
                    else:
                        self.rectangles.itemconfig(id, fill=self.ORANGEISH)

            sleep(self.TILE_ANIM_DELAY)
            
    def on_declick(self, event):        
        if self.solving_lock.locked():
            self.warning("A solve is still ongoing!")
            return

        with self.solving_lock:
            col = event.x // self.SIZE_XY
            row = event.y // 40
            
            id = ((row)*self.ROW_SIZE)+col+1

            color = self.rectangles.itemcget(id, "fill")

            if color == self.BLACK:
                print(f"tile {id} not clicked yet")
                return
            elif color == self.BLUE:
                print("path can not be deleted")
                return
            
            if color == self.GREEN:
                self.start = None
                print("start:",self.start)
            elif color == self.RED:
                self.end = None
                print("end:",self.end)
            elif color == self.WHITE or color == self.ORANGEISH:
                self.cities.remove((col, row))

                print("cities:",self.cities)

            self.change_city_text()

            self.rectangles.itemconfig(id, fill=self.BLACK)
            self.rectangles.itemconfig(id, outline=self.WHITE)

            print("declicked", id)

    def on_click(self, event):
        if self.solving_lock.locked():
            self.warning("A solve is still ongoing!")
            return

        with self.solving_lock:
            col = event.x // self.SIZE_XY
            row = event.y // self.SIZE_XY
            
            id = ((row)*self.ROW_SIZE)+col+1

            color = self.rectangles.itemcget(id, "fill")
            color_config = None

            if color != self.BLACK:
                print("already clicked", id)
                return

            if self.toggled == "city":
                color_config = self.WHITE
                self.cities.append((col, row))

                print("cities:", self.cities)

                self.create_city_text(col, row, id)
            
            elif self.toggled == "start":
                color_config = self.GREEN
                if self.start is None:
                    self.start = (col, row)
                    print("start:", self.start)
                else:
                    self.warning("Start point can only be one")
                    return
            elif self.toggled == "end":
                color_config = self.RED
                if self.end is None:
                    self.end = (col, row)
                    print("end:", self.end)
                else:
                    self.warning("End point can only be one")                
                    return

            self.rectangles.itemconfig(id, fill=color_config)
            self.rectangles.itemconfig(id, outline="black")

            print("clicked", id)

    def create_city_text(self, col, row, id):
        index = self.cities.index((col, row))

        print(index)
        (x, y, x_size, y_size) = self.rectangles_size[id]

        self.rectangles.create_text((x+x_size)/2, (y+y_size)/2, text=str(index+1), tags="city_num", fill="black")

    def change_city_text(self):
        self.rectangles.delete("city_num")
        
        for point in self.cities:
            col, row = point
            
            id = (row*self.ROW_SIZE)+col+1

            self.create_city_text(col, row, id)

    def warning(self, message="Something went wrong!"):
        messagebox.showwarning(title="Warning", message=message)

    def toggle(self, toggle_text):
        self.toggled = toggle_text
        self.mode_text.config(text=f"MODE: {toggle_text.upper()}")

    def clear(self):        
        if self.solving_lock.locked():
            self.warning("A solve is still ongoing!")
            return

        with self.solving_lock:
            for id in range(1,301):
                if self.rectangles.itemcget(id, "fill") == self.BLUE:
                    self.rectangles.itemconfig(id, fill=self.BLACK)
                    self.rectangles.itemconfig(id, outline=self.WHITE)
                elif self.rectangles.itemcget(id, "fill") == self.ORANGEISH:
                    self.rectangles.itemconfig(id, fill=self.WHITE)
                    self.rectangles.itemconfig(id, outline=self.BLACK)    

if __name__ == "__main__":
    window = tk.Tk()
    TSP(window)
    window.mainloop()