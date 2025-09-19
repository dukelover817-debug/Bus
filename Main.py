import tkinter as tk
from tkinter import messagebox
import threading
import time
import math
from datetime import datetime
import tkintermapview

class Bus:
    def __init__(self, bus_number, route_coords, stop_names, map_widget, color, label_var, speed_var, all_buses):
        self.bus_number = bus_number
        self.route_coords = route_coords
        self.stop_names = stop_names
        self.map_widget = map_widget
        self.color = color
        self.label_var = label_var
        self.speed_var = speed_var
        self.bus_icon = None
        self.current_index = 0
        self.all_buses = all_buses
        self.distance_travelled = 0.0
        self.cumulative_distance = 0.0
        self.route_history = []
        self.start_time = datetime.now()

    def move_bus(self):
        for i in range(len(self.route_coords)-1):
            x1, y1 = self.route_coords[i]
            x2, y2 = self.route_coords[i+1]
            steps = 30
            for step in range(steps):
                t = step / steps
                new_x = x1 + (x2 - x1) * t
                new_y = y1 + (y2 - y1) * t

                distance_step = math.hypot((x2 - x1)/steps, (y2 - y1)/steps) * 0.1
                self.distance_travelled += distance_step
                self.cumulative_distance += distance_step

                for bus in self.all_buses:
                    if bus.bus_number != self.bus_number and bus.current_index == self.current_index:
                        new_speed = max(0.05, 0.5 - self.speed_var.get()/15)
                        time.sleep(new_speed)
                        break
                else:
                    time.sleep(max(0.03, 0.5 - self.speed_var.get()/10))

                self.map_widget.after(0, self.update_location, new_x, new_y, self.stop_names[i])
            self.current_index = i + 1
            self.route_history.append(self.stop_names[i])
        self.map_widget.after(0, self.update_location, *self.route_coords[-1], self.stop_names[-1])
        self.route_history.append(self.stop_names[-1])
        self.label_var.set(
            f"Bus {self.bus_number} completed. Trip: {self.distance_travelled:.2f} km | Total: {self.cumulative_distance:.2f} km"
        )

    def update_location(self, x, y, stop_name):
        if self.bus_icon:
            self.map_widget.delete(self.bus_icon)
        self.bus_icon = self.map_widget.set_marker(x, y, text=self.bus_number, color=self.color)
        self.bus_icon.tag_bind(self.bus_icon, "<Button-1>", lambda e: self.show_bus_info(stop_name))
        self.label_var.set(
            f"Bus {self.bus_number} at stop: {stop_name} | Trip: {self.distance_travelled:.2f} km | Total: {self.cumulative_distance:.2f} km"
        )

    def show_bus_info(self, stop_name):
        history_str = " -> ".join(self.route_history[-10:])
        messagebox.showinfo(
            f"Bus {self.bus_number} Details",
            f"Bus Number: {self.bus_number}\n"
            f"Current Stop: {stop_name}\n"
            f"Trip Distance: {self.distance_travelled:.2f} km\n"
            f"Cumulative Distance: {self.cumulative_distance:.2f} km\n"
            f"Route History (last stops): {history_str}\n"
            f"Details Link: https://fleet-tracker.example.com/{self.bus_number}"
        )

class FleetBusTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Fleet Bus Tracker")
        self.map_widget = tkintermapview.TkinterMapView(root, width=900, height=650)
        self.map_widget.pack()
        self.buses = []
        self.labels_frame = tk.Frame(root)
        self.labels_frame.pack()
        self.speed_var = tk.DoubleVar()
        self.speed_var.set(5)
        self.create_speed_slider()

    def create_speed_slider(self):
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Label(frame, text="Bus Speed:").pack(side=tk.LEFT)
        tk.Scale(frame, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.speed_var).pack(side=tk.LEFT)

    def add_bus(self, bus_number, route_coords, stop_names, color="red"):
        for i in range(len(route_coords)-1):
            x1, y1 = route_coords[i]
            x2, y2 = route_coords[i+1]
            self.map_widget.set_line(x1, y1, x2, y2, color="black", width=2)
        for (x, y), name in zip(route_coords, stop_names):
            self.map_widget.set_marker(x, y, text=name, color="yellow")
        label_var = tk.StringVar()
        label_var.set(f"Bus {bus_number} waiting...")
        tk.Label(self.labels_frame, textvariable=label_var).pack()
        bus = Bus(bus_number, route_coords, stop_names, self.map_widget, color, label_var, self.speed_var, self.buses)
        self.buses.append(bus)
        threading.Thread(target=bus.move_bus).start()

if __name__ == "__main__":
    # Example routes (latitude, longitude)
    route1 = [(12.9716, 77.5946), (12.9726, 77.5956), (12.9736, 77.5966), (12.9746, 77.5976)]
    stops1 = ["City Center", "Main Street", "Park", "Museum"]

    route2 = [(12.9716, 77.5946), (12.9706, 77.5936), (12.9696, 77.5926), (12.9686, 77.5916)]
    stops2 = ["Downtown", "Library", "University", "Market"]

    root = tk.Tk()
    tracker = FleetBusTracker(root)
    tracker.add_bus("101", route1, stops1, "red")
    tracker.add_bus("102", route2, stops2, "green")
    root.mainloop()
