import tkinter as tk
import tsp
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

        self.font = ("Verdana", 18)
        self.toggled = "city"

        self.solving_lock = threading.Lock()

        self.setup_rectangles()
        self.setup_manager()

    def setup_rectangles(self):
        self.rectangles = tk.Canvas(self.window, width=800, height=600, bd=0, borderwidth=0)
        self.rectangles_size = {}

        for i in range(300):
            col = i % 20
            row = i // 20

            x_pos = col * 40
            y_pos = row * 40
            
            x_size = x_pos+40
            y_size = y_pos+40

            self.rectangles.create_rectangle(x_pos, y_pos, x_size, y_size, fill="black", outline="white", tags=("clickable", str(i)))
            self.rectangles_size[i] = (x_pos, y_pos, x_size, y_size)

        self.rectangles.bind("<Button-1>", self.on_click)
        self.rectangles.bind("<Button-3>", self.on_declick)
        
        self.rectangles.pack()
    
    def setup_manager(self):
        manager_window = tk.Toplevel(bg="black")
    
        manager_window.resizable(width=False, height=False) 
        manager_window.title("Grid Manager")
        
        city_toggle = tk.Button(manager_window, text="CITY", font=self.font, fg="black", bg="white", command=lambda: self.toggle("city"))
        start_toggle = tk.Button(manager_window, text="START", font=self.font, fg="black", bg="white", command=lambda: self.toggle("start"))
        end_toggle = tk.Button(manager_window, text="END", font=self.font, fg="black", bg="white", command=lambda: self.toggle("end"))

        self.mode_text = tk.Label(manager_window, text="MODE: CITY", font=self.font, bg="black", fg="white")
        solve_button = tk.Button(manager_window, text="SOLVE", font=self.font, fg="black", bg="white", command=self.solve)
        clear_button = tk.Button(manager_window, text="CLEAR", font=self.font, fg="black", bg="white", command=self.clear)

        self.cur_distance_text = tk.Label(manager_window, text="DISTANCE: 0 TILES", font=self.font, bg="black", fg="white")

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

        overall_distance = self.mha_distance_for_overall_path(overall_path)

        self.cur_distance_text.config(text=f"DISTANCE: {overall_distance} TILES")

    def mha_distance_for_overall_path(self, overall_path):
        overall_distance = 0
        
        for i in range(len(overall_path)-1):
            overall_distance += tsp.mha_distance(overall_path[i], overall_path[i+1])

        return overall_distance

    def solve_path(self, overall_path):
        with self.solving_lock:
            for i in range(len(overall_path)-1):    
                path = tsp.walk(overall_path[i], overall_path[i+1])
                self.path_colorize(path)
    
    def path_colorize(self, path):
        for point in path:
            col, row = point
            id = ((row)*20)+col+1

            if self.rectangles.itemcget(id, "fill") == "black":
                self.rectangles.itemconfig(id, fill="blue")

            sleep(0.1)
            
    def on_declick(self, event):        
        if self.solving_lock.locked():
            self.warning("A solve is still ongoing!")
            return

        with self.solving_lock:
            col = event.x // 40
            row = event.y // 40
            
            id = ((row)*20)+col+1

            color = self.rectangles.itemcget(id, "fill")

            if color == "black":
                print("not clicked yet", id)
                return
            elif color == "blue":
                print("path can not be deleted", id)
                return
            
            if color == "green":
                self.start = None
                print("start:",self.start)
            elif color == "red":
                self.end = None
                print("end:",self.end)
            elif color == "white":
                self.cities.remove((col, row))
                self.change_city_text()

                print("cities:",self.cities)

            self.rectangles.itemconfig(id, fill="black")
            self.rectangles.itemconfig(id, outline="white")

            print("declicked", id)

    def on_click(self, event):
        if self.solving_lock.locked():
            self.warning("A solve is still ongoing!")
            return

        with self.solving_lock:
            col = event.x // 40
            row = event.y // 40
            
            id = ((row)*20)+col+1

            color = self.rectangles.itemcget(id, "fill")
            color_config = None

            if color != "black":
                print("already clicked", id)
                return

            if self.toggled == "city":
                color_config = "white"
                self.cities.append((col, row))

                print("cities:", self.cities)

                self.create_city_text(col, row, id-1)
            
            elif self.toggled == "start":
                color_config = "green"
                if self.start is None:
                    self.start = (col, row)
                    print("start:", self.start)
                else:
                    self.warning("Start point can only be one")
                    return
            elif self.toggled == "end":
                color_config = "red"
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

        self.rectangles.create_text((x+x_size)/2, (y+y_size)/2, text=str(index+1), tags="city_num", fill="blue")

    def change_city_text(self):
        self.rectangles.delete("city_num")
        
        for point in self.cities:
            col, row = point
            
            id = (row*20)+col

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
                if self.rectangles.itemcget(id, "fill") == "blue":
                    self.rectangles.itemconfig(id, fill="black")
                    self.rectangles.itemconfig(id, outline="white")

if __name__ == "__main__":
    window = tk.Tk()
    TSP(window)
    window.mainloop()