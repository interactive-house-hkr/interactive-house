import math
import pygame

from floorplan import (
    ROOMS,
    FURNITURE,
    ALL_ROOM_CELLS,
    WALKABLE_CELLS,
    DOORS,
    ENTRY_DOOR,
    room_name,
)


class RVCVisualizer:
    def __init__(self, grid_size, cell_size=78):
        self.grid_size = grid_size
        self.cell_size = cell_size

        self.margin = 26
        self.side_panel_width = 300
        self.bottom_panel_height = 92

        self.grid_width = self.grid_size * self.cell_size
        self.grid_height = self.grid_size * self.cell_size

        self.width = self.margin * 2 + self.grid_width + self.side_panel_width
        self.height = self.margin * 2 + self.grid_height + self.bottom_panel_height

        self.screen = None
        self.clock = None
        self.font_title = None
        self.font_body = None
        self.font_small = None
        self.font_tiny = None
        self.running = False

        self.path = []
        self.cleaned_cells = set()
        self.frame = 0

    def initialize_plot(self, rvc_name):
        if not pygame.get_init():
            pygame.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(f"{rvc_name} Visualization")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arial", 30, bold=True)
        self.font_body = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 16)
        self.font_tiny = pygame.font.SysFont("arial", 13)

        self.running = True

    def _handle_events(self):
        actions = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                actions.append("quit")
                pygame.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    actions.append("toggle_clean")
                elif event.key == pygame.K_d:
                    actions.append("dock")
                elif event.key == pygame.K_s:
                    actions.append("stop")
                elif event.key == pygame.K_x:
                    actions.append("reset")

        return actions

    def _grid_to_screen(self, position):
        x, y = position
        screen_x = self.margin + x * self.cell_size + self.cell_size // 2
        screen_y = self.margin + (self.grid_size - 1 - y) * self.cell_size + self.cell_size // 2
        return screen_x, screen_y

    def _cell_rect(self, x, y):
        screen_x = self.margin + x * self.cell_size
        screen_y = self.margin + (self.grid_size - 1 - y) * self.cell_size
        return pygame.Rect(screen_x, screen_y, self.cell_size, self.cell_size)

    def _draw_base(self):
        outer = pygame.Rect(self.margin, self.margin, self.grid_width, self.grid_height)
        pygame.draw.rect(self.screen, (247, 249, 251), outer, border_radius=18)
        pygame.draw.rect(self.screen, (171, 179, 189), outer, 3, border_radius=18)

    def _draw_rooms(self):
        room_colors = {
            "Kitchen": (232, 238, 248),
            "Living Room": (247, 240, 226),
            "Bedroom": (239, 232, 245),
            "Hall": (234, 239, 232),
            "Bathroom": (232, 240, 244),
        }

        for room, cells in ROOMS.items():
            for x, y in cells:
                pygame.draw.rect(self.screen, room_colors[room], self._cell_rect(x, y))

        # Subtle cleaned overlay
        for x, y in self.cleaned_cells.intersection(WALKABLE_CELLS):
            overlay = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            overlay.fill((80, 190, 120, 48))
            rect = self._cell_rect(x, y)
            self.screen.blit(overlay, rect.topleft)

    def _draw_room_labels(self):
        label_positions = {
            "Kitchen": (1, 6),
            "Living Room": (5, 6),
            "Bedroom": (1, 4),
            "Hall": (3, 2),
            "Bathroom": (6, 1),
        }

        for room, cell in label_positions.items():
            x, y = self._grid_to_screen(cell)
            text = self.font_small.render(room, True, (88, 94, 102))
            bg = text.get_rect(center=(x, y)).inflate(14, 8)

            bg_surface = pygame.Surface((bg.width, bg.height), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 165))
            self.screen.blit(bg_surface, bg.topleft)

            self.screen.blit(text, text.get_rect(center=(x, y)))

    def _draw_furniture(self):
        # Counter
        counter_cells = FURNITURE["counter"]
        xs = [c[0] for c in counter_cells]
        ys = [c[1] for c in counter_cells]
        left = min(xs)
        right = max(xs)
        bottom = min(ys)
        rect = pygame.Rect(
            self.margin + left * self.cell_size + 10,
            self.margin + (self.grid_size - 1 - bottom) * self.cell_size + 14,
            (right - left + 1) * self.cell_size - 20,
            18,
        )
        pygame.draw.rect(self.screen, (165, 174, 184), rect, border_radius=9)

        # Sofa
        sofa_cells = FURNITURE["sofa"]
        xs = [c[0] for c in sofa_cells]
        ys = [c[1] for c in sofa_cells]
        left = min(xs)
        right = max(xs)
        bottom = min(ys)
        rect = pygame.Rect(
            self.margin + left * self.cell_size + 10,
            self.margin + (self.grid_size - 1 - bottom) * self.cell_size + 10,
            (right - left + 1) * self.cell_size - 20,
            self.cell_size - 20,
        )
        pygame.draw.rect(self.screen, (187, 150, 119), rect, border_radius=14)

        # Table
        x, y = next(iter(FURNITURE["table"]))
        rect = self._cell_rect(x, y).inflate(-18, -18)
        pygame.draw.rect(self.screen, (160, 132, 101), rect, border_radius=12)

        # Bed
        bed_cells = FURNITURE["bed"]
        xs = [c[0] for c in bed_cells]
        ys = [c[1] for c in bed_cells]
        left = min(xs)
        right = max(xs)
        bottom = min(ys)
        rect = pygame.Rect(
            self.margin + left * self.cell_size + 12,
            self.margin + (self.grid_size - 1 - bottom) * self.cell_size + 12,
            (right - left + 1) * self.cell_size - 24,
            self.cell_size - 24,
        )
        pygame.draw.rect(self.screen, (184, 164, 214), rect, border_radius=14)

        pillow1 = pygame.Rect(rect.x + 10, rect.y + 8, 28, 18)
        pillow2 = pygame.Rect(rect.x + 44, rect.y + 8, 28, 18)
        pygame.draw.rect(self.screen, (247, 247, 247), pillow1, border_radius=8)
        pygame.draw.rect(self.screen, (247, 247, 247), pillow2, border_radius=8)

        # Sink
        x, y = next(iter(FURNITURE["sink"]))
        rect = self._cell_rect(x, y).inflate(-22, -24)
        pygame.draw.rect(self.screen, (177, 205, 218), rect, border_radius=12)

    def _draw_grid_lines(self):
        for i in range(self.grid_size + 1):
            x = self.margin + i * self.cell_size
            y = self.margin + i * self.cell_size

            pygame.draw.line(
                self.screen, (224, 228, 234),
                (x, self.margin),
                (x, self.margin + self.grid_height),
                1
            )
            pygame.draw.line(
                self.screen, (224, 228, 234),
                (self.margin, y),
                (self.margin + self.grid_width, y),
                1
            )

    def _draw_walls(self):
        wall_color = (123, 131, 141)
        wall_width = 8

        def draw_edge(cell, direction):
            x, y = cell
            rect = self._cell_rect(x, y)

            if direction == "east":
                pygame.draw.line(self.screen, wall_color, rect.topright, rect.bottomright, wall_width)
            elif direction == "north":
                pygame.draw.line(self.screen, wall_color, rect.topleft, rect.topright, wall_width)
            elif direction == "west":
                pygame.draw.line(self.screen, wall_color, rect.topleft, rect.bottomleft, wall_width)
            elif direction == "south":
                pygame.draw.line(self.screen, wall_color, rect.bottomleft, rect.bottomright, wall_width)

        def needs_wall(a, b):
            if b not in ALL_ROOM_CELLS:
                return True
            if frozenset((a, b)) in DOORS:
                return False
            return room_name(a) != room_name(b)

        for cell in ALL_ROOM_CELLS:
            x, y = cell

            east = (x + 1, y)
            north = (x, y + 1)

            if needs_wall(cell, east):
                draw_edge(cell, "east")

            if needs_wall(cell, north):
                draw_edge(cell, "north")

            if x == 0:
                draw_edge(cell, "west")

            if y == 0 and ENTRY_DOOR != ("south", cell):
                draw_edge(cell, "south")

        # Entry opening threshold
        entry_cell = ENTRY_DOOR[1]
        rect = self._cell_rect(*entry_cell)
        door_rect = pygame.Rect(rect.x + 18, rect.bottom - 8, self.cell_size - 36, 18)
        pygame.draw.rect(self.screen, (110, 83, 58), door_rect, border_radius=8)

        mat = pygame.Rect(rect.x + 12, rect.bottom + 6, self.cell_size - 24, 14)
        pygame.draw.rect(self.screen, (70, 70, 78), mat, border_radius=7)

        entry_text = self.font_tiny.render("Entry", True, (88, 92, 98))
        self.screen.blit(entry_text, (rect.x + 16, rect.bottom + 24))

    def _draw_door_markers(self):
        for pair in DOORS:
            a, b = tuple(pair)
            ax, ay = self._grid_to_screen(a)
            bx, by = self._grid_to_screen(b)

            center_x = (ax + bx) // 2
            center_y = (ay + by) // 2

            if a[0] != b[0]:  # vertical wall crossing
                rect = pygame.Rect(center_x - 8, center_y - 22, 16, 44)
            else:  # horizontal wall crossing
                rect = pygame.Rect(center_x - 22, center_y - 8, 44, 16)

            pygame.draw.rect(self.screen, (173, 138, 102), rect, border_radius=6)

    def _draw_dock(self):
        dock_x, dock_y = self._grid_to_screen((0, 0))

        shadow = pygame.Rect(0, 0, self.cell_size - 4, self.cell_size - 12)
        shadow.center = (dock_x + 4, dock_y + 5)
        pygame.draw.rect(self.screen, (173, 180, 194), shadow, border_radius=14)

        outer = pygame.Rect(0, 0, self.cell_size - 8, self.cell_size - 16)
        outer.center = (dock_x, dock_y)
        pygame.draw.rect(self.screen, (54, 100, 176), outer, border_radius=14)

        inner = pygame.Rect(0, 0, self.cell_size - 24, self.cell_size - 30)
        inner.center = (dock_x, dock_y)
        pygame.draw.rect(self.screen, (92, 142, 220), inner, border_radius=12)

        dock_text = self.font_tiny.render("DOCK", True, (255, 255, 255))
        self.screen.blit(dock_text, dock_text.get_rect(center=outer.center))

    def _draw_path(self):
        if len(self.path) > 1:
            visible_path = self.path[-60:]
            points = [self._grid_to_screen(p) for p in visible_path]
            pygame.draw.lines(self.screen, (120, 134, 146), False, points, 4)

    def _draw_robot(self, position, status):
        x, y = self._grid_to_screen(position)

        color_map = {
            "idle": (218, 78, 78),
            "cleaning": (57, 167, 96),
            "paused": (228, 165, 44),
            "returning_to_base": (70, 123, 216),
        }
        body_color = color_map.get(status, (218, 78, 78))
        radius = self.cell_size // 3

        if status == "cleaning":
            pulse = 4 + int(3 * math.sin(self.frame * 0.18))
            pygame.draw.circle(self.screen, (202, 239, 212), (x, y), radius + pulse)

        pygame.draw.circle(self.screen, (184, 190, 199), (x + 4, y + 5), radius)
        pygame.draw.circle(self.screen, body_color, (x, y), radius)
        pygame.draw.circle(self.screen, (43, 43, 43), (x, y), radius, 4)
        pygame.draw.circle(self.screen, (245, 245, 245), (x, y), radius - 11, 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + 10, y - 9), 6)

    def _draw_side_panel(self, rvc_name, position, status, battery_level):
        panel_x = self.margin * 2 + self.grid_width
        panel_rect = pygame.Rect(panel_x, self.margin, self.side_panel_width, self.grid_height)
        pygame.draw.rect(self.screen, (252, 252, 253), panel_rect, border_radius=18)
        pygame.draw.rect(self.screen, (179, 186, 196), panel_rect, 2, border_radius=18)

        title = self.font_title.render(rvc_name, True, (29, 35, 40))
        self.screen.blit(title, (panel_x + 22, self.margin + 20))

        status_colors = {
            "idle": (218, 78, 78),
            "cleaning": (57, 167, 96),
            "paused": (228, 165, 44),
            "returning_to_base": (70, 123, 216),
        }
        pill_color = status_colors.get(status, (120, 120, 120))
        pill_rect = pygame.Rect(panel_x + 22, self.margin + 76, 210, 40)
        pygame.draw.rect(self.screen, pill_color, pill_rect, border_radius=20)

        pill_text = self.font_small.render(status.replace("_", " ").title(), True, (255, 255, 255))
        self.screen.blit(pill_text, pill_text.get_rect(center=pill_rect.center))

        coverage = int((len(self.cleaned_cells.intersection(WALKABLE_CELLS)) / len(WALKABLE_CELLS)) * 100)
        location_label = "Dock station" if position == (0, 0) and status == "idle" else room_name(position)

        battery_state = "Charging" if position == (0, 0) and status == "idle" and battery_level < 100 else \
                        "Low battery" if battery_level <= 20 else \
                        "Ready"

        # Overview
        card1 = pygame.Rect(panel_x + 18, self.margin + 138, self.side_panel_width - 36, 148)
        pygame.draw.rect(self.screen, (245, 247, 249), card1, border_radius=16)
        pygame.draw.rect(self.screen, (220, 225, 231), card1, 1, border_radius=16)

        overview_title = self.font_small.render("Overview", True, (50, 56, 62))
        self.screen.blit(overview_title, (card1.x + 16, card1.y + 12))

        overview_lines = [
            f"Location: {location_label}",
            f"Position: {position}",
            f"Docked: {'Yes' if position == (0, 0) and status == 'idle' else 'No'}",
            f"Coverage: {coverage}%",
            f"Battery state: {battery_state}",
        ]

        for i, line in enumerate(overview_lines):
            text = self.font_small.render(line, True, (72, 78, 86))
            self.screen.blit(text, (card1.x + 16, card1.y + 38 + i * 20))

        # Battery
        card2 = pygame.Rect(panel_x + 18, self.margin + 298, self.side_panel_width - 36, 96)
        pygame.draw.rect(self.screen, (245, 247, 249), card2, border_radius=16)
        pygame.draw.rect(self.screen, (220, 225, 231), card2, 1, border_radius=16)

        battery_title = self.font_small.render("Battery", True, (50, 56, 62))
        self.screen.blit(battery_title, (card2.x + 16, card2.y + 12))

        battery_value = self.font_body.render(f"{battery_level}%", True, (72, 78, 86))
        self.screen.blit(battery_value, (card2.x + 16, card2.y + 32))

        bar_x = card2.x + 16
        bar_y = card2.y + 62
        bar_w = card2.width - 32
        bar_h = 18

        pygame.draw.rect(self.screen, (229, 233, 238), (bar_x, bar_y, bar_w, bar_h), border_radius=9)
        fill_w = int((max(0, min(100, battery_level)) / 100) * bar_w)
        fill_color = (57, 167, 96) if battery_level > 60 else (228, 165, 44) if battery_level > 30 else (218, 78, 78)
        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_w, bar_h), border_radius=9)
        pygame.draw.rect(self.screen, (170, 178, 188), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=9)

        # Stats
        card3 = pygame.Rect(panel_x + 18, self.margin + 408, self.side_panel_width - 36, 92)
        pygame.draw.rect(self.screen, (245, 247, 249), card3, border_radius=16)
        pygame.draw.rect(self.screen, (220, 225, 231), card3, 1, border_radius=16)

        stats_title = self.font_small.render("Simulation stats", True, (50, 56, 62))
        self.screen.blit(stats_title, (card3.x + 16, card3.y + 12))

        stats_lines = [
            f"Visited cells: {len(self.cleaned_cells)}",
            f"Path points: {len(self.path)}",
            f"Auto-return: 20%",
        ]

        for i, line in enumerate(stats_lines):
            text = self.font_small.render(line, True, (72, 78, 86))
            self.screen.blit(text, (card3.x + 16, card3.y + 36 + i * 18))

        # Legend
        card4 = pygame.Rect(panel_x + 18, self.margin + 514, self.side_panel_width - 36, 84)
        pygame.draw.rect(self.screen, (245, 247, 249), card4, border_radius=16)
        pygame.draw.rect(self.screen, (220, 225, 231), card4, 1, border_radius=16)

        legend_title = self.font_small.render("Legend", True, (50, 56, 62))
        self.screen.blit(legend_title, (card4.x + 16, card4.y + 10))

        legend_items = [
            ((57, 167, 96), "Cleaning"),
            ((228, 165, 44), "Paused"),
            ((70, 123, 216), "Returning"),
            ((218, 78, 78), "Idle"),
            ((54, 100, 176), "Dock"),
            ((173, 138, 102), "Door"),
        ]

        for i, (color, label) in enumerate(legend_items):
            col = i % 2
            row = i // 2
            x = card4.x + 18 + col * 120
            y = card4.y + 34 + row * 18

            pygame.draw.circle(self.screen, color, (x, y), 7)
            text = self.font_tiny.render(label, True, (72, 78, 86))
            self.screen.blit(text, (x + 14, y - 8))

    def _draw_bottom_bar(self):
        rect = pygame.Rect(
            self.margin,
            self.margin * 2 + self.grid_height,
            self.grid_width + self.side_panel_width,
            self.bottom_panel_height - self.margin
        )
        pygame.draw.rect(self.screen, (252, 252, 253), rect, border_radius=16)
        pygame.draw.rect(self.screen, (179, 186, 196), rect, 2, border_radius=16)

        title = self.font_small.render(
            "Interactive demo controls",
            True,
            (58, 64, 70)
        )
        controls = self.font_small.render(
            "Space = start/pause/resume   |   D = dock   |   S = stop   |   X = reset",
            True,
            (88, 94, 102)
        )

        self.screen.blit(title, (rect.x + 18, rect.y + 12))
        self.screen.blit(controls, (rect.x + 18, rect.y + 36))

    def update_plot(self, position, rvc_name, status="idle", battery_level=100):
        if self.screen is None:
            self.initialize_plot(rvc_name)

        if not self.running:
            return []

        actions = self._handle_events()
        if not self.running:
            return actions

        self.frame += 1

        if not self.path or self.path[-1] != position:
            self.path.append(position)

        self.cleaned_cells.add(position)

        self.screen.fill((232, 236, 241))
        self._draw_base()
        self._draw_rooms()
        self._draw_grid_lines()
        self._draw_furniture()
        self._draw_walls()
        self._draw_door_markers()
        self._draw_dock()
        self._draw_path()
        self._draw_room_labels()
        self._draw_robot(position, status)
        self._draw_side_panel(rvc_name, position, status, battery_level)
        self._draw_bottom_bar()

        pygame.display.flip()
        self.clock.tick(60)
        return actions

    def wait_until_closed(self, rvc):
        while self.running:
            self.update_plot(
                rvc.position,
                rvc.name,
                rvc.status,
                rvc.battery_level
            )

    def reset_traces(self):
        self.path = []
        self.cleaned_cells = set()