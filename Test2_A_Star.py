import pygame
import sys
import random
from collections import deque
from heapq import heappop, heappush
import time

# Constants
WIDTH, HEIGHT = 600, 600
TILE_SIZE = WIDTH // 40
GAP_SIZE = 2
BG_COLOR = (0, 0, 0)
BLUE_COLOR = (83,41,110)
SNAKE_COLOR = (255, 0, 0)
BLACK_COLOR = (0, 0, 0)
FOOD_COLOR = (78, 128, 101)
BOMB_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 30

class Board:
    def __init__(self, current_run):
        self.tiles = self.create_tiles()
        self.foods = []
        self.current_run = current_run
        self.add_initial_foods()

    def create_tiles(self):
        tiles = {}
        for i in range(35):
            for j in range(35):
                tile_x = i * (TILE_SIZE + GAP_SIZE)
                tile_y = j * (TILE_SIZE + GAP_SIZE)
                tiles[i,j] = (tile_x, tile_y)
        return tiles
    
    def add_initial_foods(self):
        # Positions for the food
        positions = [
            [(3, 3), (6, 10), (20, 5), (15, 22), (8, 27),
             (30, 20), (25, 15), (19, 9), (12, 19), (5, 25),
             (10, 6), (24, 28), (18, 13), (7, 29), (21, 16),
             (26, 4), (9, 14), (13, 30), (4, 22), (31, 11)],
            [(4, 5), (7, 12), (21, 6), (16, 23), (9, 28),
             (31, 21), (26, 16), (20, 10), (13, 20), (6, 26),
             (11, 7), (25, 29), (19, 14), (8, 30), (22, 17),
             (27, 5), (10, 15), (14, 31), (5, 23), (32, 12)],
            [(5, 7), (8, 14), (22, 8), (17, 25), (10, 30),
             (32, 23), (27, 18), (21, 12), (14, 22), (7, 28),
             (12, 9), (26, 31), (20, 16), (9, 32), (23, 19),
             (28, 7), (11, 17), (15, 33), (6, 25), (33, 14)],
            [(6, 9), (9, 16), (23, 10), (18, 27), (11, 32),
             (33, 24), (28, 19), (22, 13), (15, 23), (8, 29),
             (13, 10), (27, 32), (21, 17), (10, 33), (24, 20),
             (29, 8), (12, 18), (16, 34), (7, 26), (34, 15)],
            [(7, 11), (10, 18), (24, 11), (19, 28), (12, 33),
             (34, 25), (29, 20), (23, 14), (16, 24), (9, 30),
             (14, 11), (28, 33), (22, 18), (11, 34), (25, 21),
             (30, 9), (13, 19), (17, 34), (8, 27), (34, 16)]
        ]
        
        for pos in positions[self.current_run - 1]:
            self.foods.append(self.tiles[pos])
    
    def add_food(self):
        empty_tiles = [tile for tile in self.tiles.values() if tile not in self.foods]
        if empty_tiles:
            food_position = random.choice(empty_tiles)
            self.foods.append(food_position)


class Snake:
    def __init__(self, position):
        self.head_position = position
        self.body = [position]
        self.tail = None
        self.grow_pending = False

    def move(self, new_position):
        self.head_position = new_position
        self.body.insert(0, new_position)
        if self.tail is None:
            self.tail = self.body[-1]
        else:
            self.tail = self.body.pop()
        if self.grow_pending:
            self.grow()
            self.grow_pending = False
    
    def grow(self):
        self.body.append(self.body[0])
        if len(self.body) > 0:
            self.tail = self.body[0]

class Bomb:
    def __init__(self, position):
        self.position = position
        self.direction = "down"
        self.move_delay = 200
        self.last_move_time = pygame.time.get_ticks()

    def move(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_delay:
            if self.direction == "down":
                if self.position[1] < 34 * (TILE_SIZE + GAP_SIZE):
                    self.position = (self.position[0], self.position[1] + TILE_SIZE + GAP_SIZE)
                else:
                    self.direction = "up"
            elif self.direction == "up":
                if self.position[1] > 0:
                    self.position = (self.position[0], self.position[1] - TILE_SIZE - GAP_SIZE)
                else:
                    self.direction = "down"
            self.last_move_time = current_time

class Game:
    def __init__(self):
        self.current_run = 1
        self.runs_completed = 0
        self.board = Board(self.current_run)
        self.snake = Snake(self.board.tiles[17, 17])
        self.food = None
        self.bomb = Bomb(self.board.tiles[5, 0])
        self.move_delay = 35
        self.last_move_time = pygame.time.get_ticks()
        self.move_sequence = []
        self.current_step = 0
        self.shortest_path = []
        self.foods_collected = 0
        self.win_counter = 0
        self.move_counter = 0
        self.bomb1 = Bomb(self.board.tiles[5, 0])
        self.bomb2 = Bomb(self.board.tiles[29, 0])
        self.search_method = "a_star_search"
        self.black_boxes = [self.bomb1, self.bomb2]
        

    def next_run(self):
        start_time = time.time()  # Record the start time
        self.current_run += 1
        self.runs_completed += 1
        if self.current_run > 5:
            print("Game over. All runs completed.")
            pygame.quit()
            sys.exit()
        print(f"Starting run {self.current_run}...")
        self.board = Board(self.current_run)
        self.snake = Snake(self.board.tiles[17, 17])
        self.food = None
        self.bomb = Bomb(self.board.tiles[5, 0])
        self.move_delay = 35
        self.last_move_time = pygame.time.get_ticks()
        self.move_sequence = []
        self.current_step = 0
        self.shortest_path = []
        self.foods_collected = 0
        self.move_counter = 0
        self.bomb1 = Bomb(self.board.tiles[5, 0])
        self.bomb2 = Bomb(self.board.tiles[29, 0])
        self.black_boxes = [self.bomb1, self.bomb2]
        self.board.add_initial_foods()
        

    def check_collision_with_black_boxes(self):
        for box in self.black_boxes:
            if self.snake.head_position == box.position:
                return True
        for segment in self.snake.body[1:]:
            for box in self.black_boxes:
                if segment == box.position:
                    return True
        return False  # Return False if no collision is detected
                
    def apply_penalty(self, next_tile):
        for box in self.black_boxes:
            if next_tile == box.position:
                self.move_counter += 5
                print("Penalty applied: +5 to move counter")

    def bfs_search_with_obstacles(self, start, goal, max_depth=None):
        visited = set()
        queue = deque([(start, [])])
        while queue:
            current_tile, path = queue.popleft()
            if current_tile == goal:
                return path + [goal]
            if current_tile in visited:
                continue
            visited.add(current_tile)
            for neighbor in self.adjacent_tiles(current_tile):
                if neighbor not in visited and neighbor not in self.snake_body_as_tiles() and neighbor not in [box.position for box in self.black_boxes]:
                    queue.append((neighbor, path + [current_tile]))
        return []
    
    def a_star_search(self, start, goal, max_depth=None):
        visited = set()
        pq = [(0 + self.heuristic_distance(start, goal), 0, start, [])]
        while pq:
            _, cost, current_tile, path = heappop(pq)
            if current_tile == goal:
                return path + [goal]
            if current_tile in visited:
                continue
            visited.add(current_tile)
            for neighbor in self.adjacent_tiles(current_tile):
                if neighbor not in visited and neighbor not in self.snake_body_as_tiles():
                    new_cost = cost + 1
                    priority = new_cost + self.heuristic_distance(neighbor, goal)
                    heappush(pq, (priority, new_cost, neighbor, path + [current_tile]))
        return []
    
    def heuristic_distance(self, start, target):
        return abs(start[0] - target[0]) + abs(start[1] - target[1])
    
    def iddfs_search_with_obstacles(self, start, goal, max_depth):
        for depth in range(max_depth):
            visited = set()
            stack = [(start, 0, [])]
            while stack:
                current_tile, current_depth, path = stack.pop()
                if current_tile == goal:
                    return path + [goal]
                if current_depth < depth:
                    if current_tile in visited:
                        continue
                    visited.add(current_tile)
                    for neighbor in self.adjacent_tiles(current_tile):
                        if neighbor not in visited and neighbor not in self.snake_body_as_tiles() and neighbor not in [box.position for box in self.black_boxes]:
                            stack.append((neighbor, current_depth + 1, path + [current_tile]))
        return []

    def generate_path_to_food_with_obstacles(self):
        #print("Generating path to food...")
        if not self.board.foods:
            return

        snake_tile = self.tile_from_position(self.snake.head_position)
        closest_food = None
        min_distance = float('inf')

        for food_pos in self.board.foods:
            food_tile = self.tile_from_position(food_pos)
            distance = abs(snake_tile[0] - food_tile[0]) + abs(snake_tile[1] - food_tile[1])
            if distance < min_distance:
                min_distance = distance
                closest_food = food_tile

        if closest_food:
            future_black_box_positions = []  # Predicted future positions of black boxes
            for i in range(len(self.black_boxes)):
                future_black_box_positions.append(self.black_boxes[i].position)
                for j in range(3):  # Predict 3 steps into the future for each black box
                    self.black_boxes[i].move()
                    future_black_box_positions.append(self.black_boxes[i].position)
        
            # Generate path considering future black box positions
            self.shortest_path = self.a_star_search(snake_tile, closest_food, max_depth=100)
        
            # Check if the path intersects with future black box positions
            intersects_future_position = any(tile in future_black_box_positions for tile in self.shortest_path)
        
            # If the path intersects with future positions, find an alternative path
            if intersects_future_position:
                print("Path intersects with future black box position, finding alternative path...")
                self.shortest_path = []
                for possible_food_tile in self.board.foods:
                    alternative_path = self.a_star_search(snake_tile, possible_food_tile, max_depth=100)
                    if alternative_path:
                        self.shortest_path = alternative_path
                        break
            
                if not self.shortest_path:
                    print("No alternative path found for current food item, skipping...")
                    return
                else:
                    print("Alternative path found:", self.shortest_path)

    def generate_path_to_food(self):
        #print("Generating path to food...")
        if not self.board.foods:
            return

        snake_tile = self.tile_from_position(self.snake.head_position)
        closest_food = None
        min_distance = float('inf')

        for food_pos in self.board.foods:
            food_tile = self.tile_from_position(food_pos)
            distance = abs(snake_tile[0] - food_tile[0]) + abs(snake_tile[1] - food_tile[1])
            if distance < min_distance:
                min_distance = distance
                closest_food = food_tile

        #print("Closest food:", closest_food)
        if closest_food:
            self.shortest_path = self.a_star_search(snake_tile, closest_food)
            #print("Shortest path:", self.shortest_path)

            for tile in self.shortest_path:
                if tile in [box.position for box in self.black_boxes]:
                    #print("Collision detected with black box, finding alternative path...")
                    self.shortest_path = []
                    alternative_path_found = False
                    for possible_food_tile in self.board.foods:
                        alternative_path = self.a_star_search(snake_tile, possible_food_tile)
                        if alternative_path:
                            self.shortest_path = alternative_path
                            alternative_path_found = True
                            break
                
                    if not alternative_path_found:
                        print("No alternative path found, stopping temporarily...")
                        return
                    else:
                        print("Alternative path found:", self.shortest_path)
                        break

    def adjacent_tiles(self, position):
        return [(position[0] + x, position[1] + y) for x, y in [(0, 1), (0, -1), (1, 0), (-1, 0)] if
                (position[0] + x, position[1] + y) in self.board.tiles]

    def tile_from_position(self, position):
        for tile, pos in self.board.tiles.items():
            if pos == position:
                return tile
        return None

    def position_from_tile(self, tile):
        return self.board.tiles[tile]

    def snake_body_as_tiles(self):
        return [self.tile_from_position(segment) for segment in self.snake.body]

    def update(self):
        # Check if the move delay time has passed to move the snake
        current_time = pygame.time.get_ticks()

        if current_time - self.last_move_time > self.move_delay:
            # Move the snake based on the move sequence
            if self.move_sequence:
                #print("move_sequence before: ",self.move_sequence)
                next_tile = self.move_sequence[0]  # Get the next move from the sequence
                # Try moving the snake according to the next move
                self.snake.move(self.position_from_tile(next_tile))
                # Check if the snake successfully moved to the next tile
                if self.snake.head_position == self.position_from_tile(next_tile):
                    # If successful, remove the move from the sequence
                    self.move_sequence.pop(0)
                    self.move_counter += 1
                    self.apply_penalty(next_tile)
                    # Check if the snake eats food
                    if self.snake.head_position in self.board.foods:
                        self.snake.grow_pending = True
                        self.foods_collected += 1
                        self.board.foods.remove(self.snake.head_position)
                        print("Food eaten! Total foods collected:", self.foods_collected)
                        #print("Remaining foods:", self.board.foods)  # Add this line for debugging
                        # Check if the snake has collected enough food to go to the next run
                        if self.foods_collected == 20:
                            self.win_counter +=1
                            print("Win1: ", self.win_counter)
                            print("Move Counter: ", self.move_counter)
                            print("Snake collected 20 food. Moving to next run...")
                            self.next_run()
                    # Check if the snake collided with black boxes
                    if self.check_collision_with_black_boxes():
                        print("Win2: ", self.win_counter)
                        print("Move Counter: ", self.move_counter)
                        print("Snake collided with a black box. Moving to next run...")
                        self.next_run()
            else:
                # Generate new move sequence
                self.generate_path_to_food_with_obstacles()
                if self.shortest_path:
                    self.move_sequence = self.shortest_path.copy()
                    if self.move_sequence:
                        if len(self.move_sequence) == 1:
                            self.foods_collected -= 1
                        #print("Applying first move...")
                        next_tile = self.move_sequence.pop(0)
                        self.snake.move(self.position_from_tile(next_tile))
                        self.move_counter += 1
                        self.apply_penalty(next_tile)

                        if self.snake.head_position in self.board.foods:
                            self.snake.grow_pending = True
                            self.foods_collected += 1
                            self.board.foods.remove(self.snake.head_position)
                            print("Food eaten! Total foods collected:", self.foods_collected)

                            if self.foods_collected == 20:
                                self.win_counter +=1
                                print("Win3: ", self.win_counter)
                                print("Move Counter: ", self.move_counter)
                                print("Snake collected 20 food. Moving to next run...")
                                self.next_run()
                        if self.check_collision_with_black_boxes():
                            print("Win4: ", self.win_counter)
                            print("Move Counter: ", self.move_counter)
                            print("Snake collided with a black box. Moving to next run...")
                            self.next_run()

            # Update positions of black boxes
            for box in self.black_boxes:
                box.move()

            # Check for collisions with black boxes
            if self.check_collision_with_black_boxes():
                print("Win5: ", self.win_counter)
                print("Move Counter: ", self.move_counter)
                print("Snake collided with a black box. Moving to next run...")
                self.next_run()

            self.last_move_time = current_time

    def draw(self, screen):
        screen.fill(BG_COLOR)
        self.draw_tiles(screen)
        self.draw_snake(screen)
        self.draw_food(screen)
        self.draw_black_boxes(screen)
        self.draw_text(screen, f"Run: {self.current_run}", (10, 10))
        self.draw_text(screen, f"Run completed: {self.runs_completed}", (10, 50))
        self.draw_text(screen, f"Food collected: {self.foods_collected}", (10, 90))
        self.draw_text(screen, f"Move counter: {self.move_counter}", (10, 130))
        pygame.display.flip()

    def draw_tiles(self, screen):
        for tile_x, tile_y in self.board.tiles.values():
            pygame.draw.rect(screen, BLUE_COLOR, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))

    def draw_snake(self, screen):
        for i, segment in enumerate(self.snake.body):
            # Calculate the position of the curved square
            x, y = segment[0] + TILE_SIZE // (5/2), segment[1] + TILE_SIZE // (5/2)
            # Define the radius of the curved square
            radius = TILE_SIZE * 2 // 4

            # Draw the four sides of the curved square
            pygame.draw.rect(screen, (209, 0, 0), (x - radius, y - radius, radius, radius))
            pygame.draw.rect(screen, (209, 0, 0), (x - radius, y - radius, radius, radius))
            pygame.draw.rect(screen, (209, 0, 0), (x, y - radius, radius, radius))
            pygame.draw.rect(screen, (209, 0, 0), (x - radius, y, radius, radius))
            pygame.draw.rect(screen, (209, 0, 0), (x, y, radius, radius))


    def draw_food(self, screen):
        # Load the image for the food
        food_image = pygame.image.load("Food-Coin.png")
        # Scale the image to match the tile size
        food_image = pygame.transform.scale(food_image, (TILE_SIZE * 5 // 3, TILE_SIZE * 5 // 3))

        for food_position in self.board.foods:
            # Blit the image onto the screen at the food's position
            screen.blit(food_image, food_position)

    def draw_black_boxes(self, screen):
        for box in self.black_boxes:
            # Load the image for the black box
            black_box_image = pygame.image.load("Bomb1.png")
            # Scale the image to match the tile size
            black_box_image = pygame.transform.scale(black_box_image, (TILE_SIZE * 2, TILE_SIZE * 2))
            # Blit the image onto the screen at the box's position
            screen.blit(black_box_image, box.position)


    def draw_text(self, screen, text, position):
        font = pygame.font.Font(None, FONT_SIZE)
        text_surface = font.render(text, True, TEXT_COLOR)
        screen.blit(text_surface, position)


def main():
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    game = Game()
    total_time = 0  # Initialize total time
    last_run_count = 0  # Initialize last run count
    running = True
    while running:
        start_time = time.time()  # Record the start time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update()
        game.draw(screen)
        clock.tick(60)
        
        # Check if a new run has started
        if game.runs_completed > last_run_count:
            print("Total time for all runs:", round(total_time, 10), "seconds")
            last_run_count = game.runs_completed  # Update last run count
        
        # Check if the game has ended
        if not running:
            break
        
        # Calculate the duration of the current run
        end_time = time.time()  # Record the end time
        run_duration = end_time - start_time
        total_time += run_duration  # Accumulate the total time

    # Print the total time for all runs after the loop ends
    print("Total time for all runs:", round(total_time, 10), "seconds")

    pygame.quit()
    sys.exit()
    


if __name__ == "__main__":
    main()