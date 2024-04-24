import pygame
import random
from queue import PriorityQueue

pygame.init()

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Visualizer")

#define colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_YELLOW = (255, 255, 102)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False
"""
Calculate the Manhattan distance between two points.

Parameters:
    p1 (tuple): A tuple representing the coordinates of the first point.
    p2 (tuple): A tuple representing the coordinates of the second point.

Returns:
    int: The distance between the two points.
"""
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)
"""
Dijkstra's algorithm for finding the shortest path between two points on a grid.

Parameters:
- draw: A function to visualize the grid.
- grid: A 2D list representing the grid.
- start: The starting point on the grid.
- end: The ending point on the grid.

Returns:
- True if a path is found and visualized.
- False if no path is found.

Note:
- This algorithm uses a priority queue to explore the grid in the order of the lowest cost.
- The grid is represented by a 2D list, where each element represents a spot on the grid.
- The g_score dictionary keeps track of the cost from the start point to each spot on the grid.
- The came_from dictionary keeps track of the previous spot that leads to the current spot.
- The algorithm terminates when the end point is reached or when there are no more spots to explore.
- The draw function is used to visualize the grid at each step of the algorithm.
"""
def dijkstra_algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                if neighbor not in [item[2] for item in open_set.queue]:
                    count += 1
                    open_set.put((g_score[neighbor], count, neighbor))
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False
"""
A* algorithm implementation for pathfinding in a grid.

Parameters:
- draw: A function used to draw the grid and visualize the algorithm's progress.
- grid: A 2D list representing the grid where the algorithm will search for a path.
- start: The starting node for the pathfinding algorithm.
- end: The target node for the pathfinding algorithm.

Returns:
- True if a path from start to end is found, False otherwise.

The A* algorithm uses a priority queue to explore the grid nodes based on their estimated distance to the target node. It iteratively evaluates the neighbors of each node and updates their scores accordingly. The algorithm stops when the target node is reached or when there are no more nodes to explore.

Note: This implementation assumes the existence of the following helper functions:
- reconstruct_path(came_from, end, draw): Reconstructs the path from start to end based on the came_from dictionary and visualizes it using the draw function.
- h(pos1, pos2): Heuristic function that estimates the distance between two nodes.

"""
def a_star_algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in [item[2] for item in open_set.queue]:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False
"""
This function implements a brute-force algorithm to find a path from the start point to the end point in a given grid.

Parameters:
- draw (function): A function used to visualize the grid.
- grid (list): A 2D list representing the grid.
- start (Node): The starting node.
- end (Node): The ending node.

Returns:
- bool: True if a path is found, False otherwise.
"""
def brute_force_algorithm(draw, grid, start, end):
    visited = set()
    queue = [start]

    while queue:
        current = queue.pop(0)
        if current == end:
            reconstruct_path(visited, end, draw)
            end.make_end()
            return True
        visited.add(current)
        for neighbor in current.neighbors:
            if neighbor not in visited and not neighbor.is_barrier():
                queue.append(neighbor)
                neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()

    return False


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col
"""
This code defines a main function that creates a graphical user interface using the Pygame library. 
The user interface displays buttons for selecting different algorithms (A*, Dijkstra, and Brute Force) to solve a pathfinding problem on a grid.

The code initializes variables for the number of rows in the grid and the grid itself. 
It also initializes variables for the start and end positions on the grid.

The main loop of the program runs until the user closes the window. 
Within the loop, the code updates the display, draws the buttons and text, and handles user input events.

When the user clicks on a button, the code performs the corresponding algorithm. 
Each algorithm has its own loop that allows the user to interact with the grid. The grid is drawn on the screen, and the code handles user input events to modify the grid (e.g., selecting start and end positions, placing barriers). The algorithm is executed when the user presses the spacebar.

The code also includes functions for updating the neighbors of each spot on the grid, 
drawing the grid on the screen, and resetting the grid.

The program uses the Pygame library to create the graphical user interface and handle user input events.

Note: The code assumes that the necessary functions for the algorithms 
(e.g., a_star_algorithm, dijkstra_algorithm, brute_force_algorithm) and other helper functions (e.g., make_grid, draw, get_clicked_pos) are defined elsewhere.
"""
def main():
    ROWS = 50
    grid = make_grid(ROWS, WIDTH)

    start = None
    end = None

    run = True
    while run:
        WIN.fill(WHITE)
        
        font = pygame.font.SysFont(None, 36)
        text = font.render("Select Algorithm:", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, 50))
        WIN.blit(text, text_rect)

        a_star_button = pygame.Rect(100, 150, 200, 50)
        dijkstra_button = pygame.Rect(100, 250, 200, 50)
        brute_force_button = pygame.Rect(100, 350, 200, 50)
        button_colors = [LIGHT_BLUE, LIGHT_GREEN, LIGHT_YELLOW]

        pygame.draw.rect(WIN, button_colors[0], a_star_button)
        pygame.draw.rect(WIN, button_colors[1], dijkstra_button)
        pygame.draw.rect(WIN, button_colors[2], brute_force_button)

        text = font.render("A* Algorithm", True, BLACK)
        text_rect = text.get_rect(center=a_star_button.center)
        WIN.blit(text, text_rect)

        text = font.render("Dijkstra", True, BLACK)
        text_rect = text.get_rect(center=dijkstra_button.center)
        WIN.blit(text, text_rect)

        text = font.render("Brute Force", True, BLACK)
        text_rect = text.get_rect(center=brute_force_button.center)
        WIN.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if a_star_button.collidepoint(event.pos):
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    while True:
                        draw(WIN, grid, ROWS, WIDTH)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_c:
                                    start = None
                                    end = None
                                    grid = make_grid(ROWS, WIDTH)
                                    break
                                elif event.key == pygame.K_SPACE and start and end:
                                    for row in grid:
                                        for spot in row:
                                            spot.update_neighbors(grid)
                                    a_star_algorithm(lambda: draw(WIN, grid, ROWS, WIDTH), grid, start, end)
                                    break
                            if pygame.mouse.get_pressed()[0]:  # LEFT
                                pos = pygame.mouse.get_pos()
                                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                                spot = grid[row][col]
                                if not start and spot != end:
                                    start = spot
                                    start.make_start()
                                elif not end and spot != start:
                                    end = spot
                                    end.make_end()
                                elif spot != end and spot != start:
                                    spot.make_barrier()
                            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                                pos = pygame.mouse.get_pos()
                                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                                spot = grid[row][col]
                                spot.reset()
                                if spot == start:
                                    start = None
                                elif spot == end:
                                    end = None
                elif dijkstra_button.collidepoint(event.pos):
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    while True:
                        draw(WIN, grid, ROWS, WIDTH)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_c:
                                    start = None
                                    end = None
                                    grid = make_grid(ROWS, WIDTH)
                                    break
                                elif event.key == pygame.K_SPACE and start and end:
                                    for row in grid:
                                        for spot in row:
                                            spot.update_neighbors(grid)
                                    dijkstra_algorithm(lambda: draw(WIN, grid, ROWS, WIDTH), grid, start, end)
                                    break
                            if pygame.mouse.get_pressed()[0]:  # LEFT
                                pos = pygame.mouse.get_pos()
                                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                                spot = grid[row][col]
                                if not start and spot != end:
                                    start = spot
                                    start.make_start()
                                elif not end and spot != start:
                                    end = spot
                                    end.make_end()
                                elif spot != end and spot != start:
                                    spot.make_barrier()
                            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                                pos = pygame.mouse.get_pos()
                                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                                spot = grid[row][col]
                                spot.reset()
                                if spot == start:
                                    start = None
                                elif spot == end:
                                    end = None             
                elif brute_force_button.collidepoint(event.pos):
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    while True:
                        draw(WIN, grid, ROWS, WIDTH)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_c:
                                    start = None
                                    end = None
                                    grid = make_grid(ROWS, WIDTH)
                                    break
                                elif event.key == pygame.K_SPACE and start and end:
                                    for row in grid:
                                        for spot in row:
                                            spot.update_neighbors(grid)
                                    brute_force_algorithm(lambda: draw(WIN, grid, ROWS, WIDTH), grid, start, end)
                                    break
                            if pygame.mouse.get_pressed()[0]:  # LEFT
                                pos = pygame.mouse.get_pos()
                                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                                spot = grid[row][col]
                                if not start and spot != end:
                                    start = spot
                                    start.make_start()
                                elif not end and spot != start:
                                    end = spot
                                    end.make_end()
                                elif spot != end and spot != start:
                                    spot.make_barrier()
                            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                                pos = pygame.mouse.get_pos()
                                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                                spot = grid[row][col]
                                spot.reset()
                                if spot == start:
                                    start = None
                                elif spot == end:
                                    end = None

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
