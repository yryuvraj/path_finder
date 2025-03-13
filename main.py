import pygame
import random
from queue import PriorityQueue
import math
import time

pygame.init()

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Visualizer")

# Define colours
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GREEN      = (0, 255, 0)
BLUE       = (0, 0, 255)
RED        = (255, 0, 0)
ORANGE     = (255, 165, 0)
YELLOW     = (255, 255, 0)
PURPLE     = (128, 0, 128)
GREY       = (128, 128, 128)
TURQUOISE = (64, 224, 208)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN= (144, 238, 144)
LIGHT_YELLOW = (255, 255, 102)

# Font for timer display
TIMER_FONT = pygame.font.SysFont(None, 36)

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

    # Returns the row and column indices of the spot as a tuple (row, col).    
    def get_pos(self):
        return self.row, self.col
    # Returns True if the spot is closed (colored red), indicating that it has been visited and evaluated during pathfinding.
    def is_closed(self):
        return self.color == RED
    #  Returns True if the spot is open (colored green), indicating that it is currently being considered for evaluation during pathfinding.
    def is_open(self):
        return self.color == GREEN
    # Returns True if the spot is a barrier (colored black), indicating that it is an obstacle and cannot be traversed
    def is_barrier(self):
        return self.color == BLACK
    # Returns True if the spot is the start point (colored orange).
    def is_start(self):
        return self.color == ORANGE
    # Returns True if the spot is the end point (colored turquoise).
    def is_end(self):
        return self.color == TURQUOISE
    # Resets the color of the spot to white, effectively clearing it.
    def reset(self):
        self.color = WHITE
    # Sets the color of the spot to orange, marking it as the start point.
    def make_start(self):
        self.color = ORANGE
    # Sets the color of the spot to red, indicating that it has been visited and evaluated during pathfinding.
    def make_closed(self):
        self.color = RED
    #  Sets the color of the spot to green, indicating that it is currently being considered for evaluation during pathfinding.
    def make_open(self):
        self.color = GREEN
    # Sets the color of the spot to black, indicating that it is an obstacle.
    def make_barrier(self):
        self.color = BLACK
    #  Sets the color of the spot to turquoise, marking it as the end point.
    def make_end(self):
        self.color = TURQUOISE
    # Sets the color of the spot to purple, indicating that it is part of the final path found by the algorithm.
    def make_path(self):
        self.color = PURPLE

    #Draws the spot on the Pygame window win with its current color, position, and size. 
    #This method is responsible for visually representing the spot on the grid.
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    """
    This method updates the list of neighbors for the current spot (self).
    It takes the grid as input, which is a 2D list representing the entire grid of spots. 
    It first clears the current list of neighbors (self.neighbors = []). Then, it checks the neighboring spots in four directions (up, down, left, right) to see if they are barriers.
    If a neighboring spot is not a barrier, it appends that spot to the list of neighbors.
    """
    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x2 - x1) + abs(y2 - y1)

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

def draw_with_timer(win, grid, rows, width, elapsed_time):
    """Redraws the grid with the elapsed time displayed in the top left."""
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    timer_text = TIMER_FONT.render(f"Time: {elapsed_time:.3f} s", True, BLACK)
    win.blit(timer_text, (10, 10))
    pygame.display.update()

def reconstruct_path(came_from, current, draw_func):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw_func()

def a_star_algorithm_timer(draw_func, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    start_time = time.time()

    while not open_set.empty():
        elapsed = time.time() - start_time
        draw_func(elapsed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        if current == end:
            reconstruct_path(came_from, end, lambda: draw_with_timer(WIN, grid, len(grid), WIDTH, time.time()-start_time))
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

        if current != start:
            current.make_closed()

    return False

def dijkstra_algorithm_timer(draw_func, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    # Dictionary to store the cost of getting from the start node to any given node.
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    while not open_set.empty():
        elapsed = time.time() - start_time
        draw_func(elapsed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        if current == end:
            reconstruct_path(came_from, end, lambda: draw_with_timer(WIN, grid, len(grid), WIDTH, time.time()-start_time))
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

        if current != start:
            current.make_closed()

    return False

def brute_force_algorithm_timer(draw_func, grid, start, end):
    queue = [start]
    came_from = {}
    start_time = time.time()
    while queue:
        elapsed = time.time() - start_time
        draw_func(elapsed)
        current = queue.pop(0)
        if current == end:
            reconstruct_path(came_from, end, lambda: draw_with_timer(WIN, grid, len(grid), WIDTH, time.time()-start_time))
            end.make_end()
            return True

        for neighbor in current.neighbors:
            if neighbor not in came_from and not neighbor.is_barrier():
                came_from[neighbor] = current
                queue.append(neighbor)
                neighbor.make_open()

        if current != start:
            current.make_closed()

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def main():
    # Set the number of rows in the grid
    ROWS = 50
    
    # Create the grid with the specified number of rows and window width
    grid = make_grid(ROWS, WIDTH)

    start = None
    end = None

    # Main loop: runs as long as the 'run' variable is True
    run = True
    while run:
        # Fill the window with a white background
        WIN.fill(WHITE)
        
        font = pygame.font.SysFont(None, 36)
        title_text = font.render("Select Algorithm:", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 50))
        WIN.blit(title_text, title_rect)

        a_star_button = pygame.Rect(100, 150, 200, 50)
        dijkstra_button = pygame.Rect(100, 250, 200, 50)
        brute_force_button = pygame.Rect(100, 350, 200, 50)
        button_colors = [LIGHT_BLUE, LIGHT_GREEN, LIGHT_YELLOW]

        # Draw algorithm selection buttons and labels
        pygame.draw.rect(WIN, button_colors[0], a_star_button)
        pygame.draw.rect(WIN, button_colors[1], dijkstra_button)
        pygame.draw.rect(WIN, button_colors[2], brute_force_button)

        a_star_text = font.render("A* Algorithm", True, BLACK)
        a_star_rect = a_star_text.get_rect(center=a_star_button.center)
        WIN.blit(a_star_text, a_star_rect)

        dijkstra_text = font.render("Dijkstra", True, BLACK)
        dijkstra_rect = dijkstra_text.get_rect(center=dijkstra_button.center)
        WIN.blit(dijkstra_text, dijkstra_rect)

        brute_text = font.render("Brute Force", True, BLACK)
        brute_rect = brute_text.get_rect(center=brute_force_button.center)
        WIN.blit(brute_text, brute_rect)

        # Event handling loop: handles user input events
        for event in pygame.event.get():
            # Check if the user closes the window
            if event.type == pygame.QUIT:
                run = False

            # Check if the user clicks the mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if a_star_button.collidepoint(event.pos):
                    # Reset start and end nodes, and create a new grid
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    
                    # Loop for handling user input until algorithm execution or window closure
                    while True:
                        draw(WIN, grid, ROWS, WIDTH)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if event.type == pygame.KEYDOWN:
                                # Reset grid if 'C' is pressed
                                if event.key == pygame.K_c:
                                    start = None
                                    end = None
                                    grid = make_grid(ROWS, WIDTH)
                                    break
                                # Start A* when SPACE is pressed and start/end are set
                                elif event.key == pygame.K_SPACE and start and end:
                                    for row in grid:
                                        for spot in row:
                                            spot.update_neighbors(grid)
                                    a_star_algorithm_timer(lambda t: draw_with_timer(WIN, grid, ROWS, WIDTH, t), grid, start, end)
                                    time.sleep(1)
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
                    # (Same process as for A* Algorithm button, but with Dijkstra's algorithm)
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    while True:
                        draw_with_timer(WIN, grid, ROWS, WIDTH, 0)
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
                                    dijkstra_algorithm_timer(lambda t: draw_with_timer(WIN, grid, ROWS, WIDTH, t), grid, start, end)
                                    time.sleep(1)
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
                    # (Same process as for A* Algorithm button, but with Brute Force algorithm)
                    start = None
                    end = None
                    grid = make_grid(ROWS, WIDTH)
                    while True:
                        draw_with_timer(WIN, grid, ROWS, WIDTH, 0)
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
                                    brute_force_algorithm_timer(lambda t: draw_with_timer(WIN, grid, ROWS, WIDTH, t), grid, start, end)
                                    time.sleep(1)
                                    break
                        if pygame.mouse.get_pressed()[0]:
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
                        elif pygame.mouse.get_pressed()[2]:
                            pos = pygame.mouse.get_pos()
                            row, col = get_clicked_pos(pos, ROWS, WIDTH)
                            spot = grid[row][col]
                            spot.reset()
                            if spot == start:
                                start = None
                            elif spot == end:
                                end = None
                        pygame.display.update()

        # Update the display
        pygame.display.update()

    # Quit Pygame when the main loop exits
    pygame.quit()

# Check if the script is being run as the main module
if __name__ == "__main__":
    main()

