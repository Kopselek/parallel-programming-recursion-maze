import numpy as np
import random
import threading
import time
import matplotlib.pyplot as plt

class Maze:
    def __init__(self, width, height, start=(0, 0)):
        random.seed(time.time())
        self.maze = -np.ones((height, width))
        self.start = start
        self.end = (height - 1, width - 1)
        self.locks = [[threading.Lock() for _ in range(width)] for _ in range(height)]
        self.guard = threading.Lock()
        self.init_maze()
    
    def position_is_free(self, x, y) -> bool:
        if x < 0 or x >= self.maze.shape[0] or y < 0 or y >= self.maze.shape[1]:
            return False
        self.locks[x][y].acquire()
        value = self.maze[x, y]
        self.locks[x][y].release()
        return value == 0

    def update_position(self, x, y, value):
        self.guard.acquire()
        self.maze[x, y] = value
        self.guard.release()
        
    def can_generate(self, x, y) -> bool:
        if 0 <= x < self.maze.shape[0] and 0 <= y < self.maze.shape[1]:
            self.locks[x][y].acquire()
            value = self.maze[x, y]
            self.locks[x][y].release()
            neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                            if 0 <= x + dx < self.maze.shape[0] and 0 <= y + dy < self.maze.shape[1] and self.maze[x + dx, y + dy] == 0)
            return value == -1 and neighbors <= 1
        return False
        
    def init_maze(self):
        x, y = self.start
        self.maze[x, y] = 0
        stack = [(x, y)]
        while stack:
            x, y = stack[-1]
            directions = [(dx, dy) for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)] if self.can_generate(x + dx, y + dy)]
            if directions:
                dx, dy = random.choice(directions)
                x, y = x + dx, y + dy
                self.maze[x, y] = 0
                stack.append((x, y))
            else:
                stack.pop()

def traverse_maze(maze: Maze, x=0, y=0, threadId=1):
    if x == maze.end[0] and y == maze.end[1]:
        return
    
    maze.update_position(x, y, threadId)

    directions = [(0, 1), (0, -1), (-1, 0)]
    threads = []

    for dx, dy in directions:
        newX, newY = x + dx, y + dy
        if maze.position_is_free(newX, newY):
            new_thread_id = threadId + 1
            t = threading.Thread(target=traverse_maze, args=(maze, newX, newY, new_thread_id))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    if maze.position_is_free(x + 1, y):
        traverse_maze(maze, x + 1, y, threadId)

def display_maze(maze: Maze, title = ""):
    plt.rcParams['figure.figsize'] = (12, 12)
    if title != "": plt.title(title)
    plt.imshow(maze.maze)
    plt.show()

def generate_maze_time_measured(maze_height, maze_width):
    start = time.time()
    maze = Maze(maze_height, maze_width)
    traverse_maze(maze)
    end = time.time()
    title = "Generation time: {0}".format(end - start)
    display_maze(maze, title)

generate_maze_time_measured(300, 300)