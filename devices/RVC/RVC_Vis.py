# This file is to visualize the RVC's position, 
# the way it does it now is a temporary solution before the frontend for it is implemented.

import matplotlib.pyplot as plt

class RVCVisualizer:
    def __init__(self, grid_size):
        self.fig, self.ax = None, None
        self.scatter = None
        self.grid_size = grid_size

    def initialize_plot(self, rvc_name):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, self.grid_size)
        self.ax.set_ylim(0, self.grid_size)

        self.ax.set_title(f"{rvc_name} Position: (0, 0)")
        self.ax.grid(True)

        self.scatter = self.ax.scatter([], [], color='red', s=100, label=rvc_name)
        self.ax.legend()

        plt.ion()
        plt.show(block=False)

    def update_plot(self, position, rvc_name):
        if self.fig is None:
            self.initialize_plot(rvc_name)

        x, y = position
        self.scatter.set_offsets([[x, y]])

        self.ax.set_title(f"{rvc_name} Position: {position}")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
