import tkinter as tk
from tkinter import messagebox
import random
import json
from pathlib import Path

class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Snake Game")
        self.window.resizable(False, False)

        # Constants
        self.GAME_WIDTH = 700
        self.GAME_HEIGHT = 500
        self.SPEED = 100
        self.SPACE_SIZE = 20
        self.BODY_SIZE = 2
        self.SNAKE_COLOR = "#00FF00"
        self.FOOD_COLOR = "#FF0000"
        self.BACKGROUND_COLOR = "#000000"

        # Game variables
        self.direction = 'right'
        self.score = 0
        self.high_score = self.load_high_score()

        # Create score label
        self.label = tk.Label(self.window, text=f"Score: {self.score} High Score: {self.high_score}", 
                            font=('consolas', 20))
        self.label.pack()

        # Create game canvas
        self.canvas = tk.Canvas(self.window, 
                              bg=self.BACKGROUND_COLOR,
                              height=self.GAME_HEIGHT,
                              width=self.GAME_WIDTH)
        self.canvas.pack()

        # Initialize game
        self.window.update()
        self.window_width = self.window.winfo_width()
        self.window_height = self.window.winfo_height()
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        # Center the window
        x = int((self.screen_width/2) - (self.window_width/2))
        y = int((self.screen_height/2) - (self.window_height/2))
        self.window.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        # Bind keys
        self.window.bind('<Left>', lambda event: self.change_direction('left'))
        self.window.bind('<Right>', lambda event: self.change_direction('right'))
        self.window.bind('<Up>', lambda event: self.change_direction('up'))
        self.window.bind('<Down>', lambda event: self.change_direction('down'))

        # Initialize snake and food
        self.snake = []
        self.food = None
        self.food_pos = None
        self.create_snake()
        self.create_food()
        
        # Start game
        self.next_turn()

    def load_high_score(self):
        try:
            with open('snake_high_score.json', 'r') as f:
                return json.load(f)['high_score']
        except:
            return 0

    def save_high_score(self):
        with open('snake_high_score.json', 'w') as f:
            json.dump({'high_score': self.high_score}, f)

    def create_snake(self):
        for x in range(self.BODY_SIZE):
            body_part = self.canvas.create_rectangle(
                x * self.SPACE_SIZE, 0,
                (x * self.SPACE_SIZE) + self.SPACE_SIZE,
                self.SPACE_SIZE,
                fill=self.SNAKE_COLOR,
                tag="snake"
            )
            self.snake.append(body_part)

    def create_food(self):
        def random_pos(limit):
            return random.randint(0, (limit - self.SPACE_SIZE) // self.SPACE_SIZE) * self.SPACE_SIZE

        x = random_pos(self.GAME_WIDTH)
        y = random_pos(self.GAME_HEIGHT)

        # Check if food spawns on snake
        while any(self.canvas.coords(body_part)[:2] == [x, y] for body_part in self.snake):
            x = random_pos(self.GAME_WIDTH)
            y = random_pos(self.GAME_HEIGHT)

        if self.food:
            self.canvas.delete(self.food)

        self.food = self.canvas.create_oval(
            x, y,
            x + self.SPACE_SIZE,
            y + self.SPACE_SIZE,
            fill=self.FOOD_COLOR,
            tag="food"
        )
        self.food_pos = (x, y)

    def next_turn(self):
        # Get head position
        head = self.snake[-1]
        head_pos = self.canvas.coords(head)

        # Calculate new head position
        if self.direction == 'left':
            new_head_pos = [head_pos[0] - self.SPACE_SIZE, head_pos[1]]
        elif self.direction == 'right':
            new_head_pos = [head_pos[0] + self.SPACE_SIZE, head_pos[1]]
        elif self.direction == 'up':
            new_head_pos = [head_pos[0], head_pos[1] - self.SPACE_SIZE]
        elif self.direction == 'down':
            new_head_pos = [head_pos[0], head_pos[1] + self.SPACE_SIZE]

        # Move snake
        new_head = self.canvas.create_rectangle(
            new_head_pos[0], new_head_pos[1],
            new_head_pos[0] + self.SPACE_SIZE,
            new_head_pos[1] + self.SPACE_SIZE,
            fill=self.SNAKE_COLOR
        )
        self.snake.append(new_head)

        # Check if food is eaten
        if new_head_pos[0] == self.food_pos[0] and new_head_pos[1] == self.food_pos[1]:
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.label.config(text=f"Score: {self.score} High Score: {self.high_score}")
            self.create_food()
        else:
            # Remove tail
            del_part = self.snake.pop(0)
            self.canvas.delete(del_part)

        # Check for collisions
        if (self.check_collisions(new_head_pos)):
            self.game_over()
        else:
            # Adjust speed based on score
            speed = max(50, self.SPEED - (self.score * 2))
            self.window.after(speed, self.next_turn)

    def check_collisions(self, pos):
        # Wall collisions
        if (pos[0] < 0 or
            pos[0] >= self.GAME_WIDTH or
            pos[1] < 0 or
            pos[1] >= self.GAME_HEIGHT):
            return True

        # Self collisions
        for body_part in self.snake[:-1]:  # Exclude head
            if pos == self.canvas.coords(body_part)[:2]:
                return True

        return False

    def change_direction(self, new_direction):
        if (new_direction == 'left' and self.direction != 'right' or
            new_direction == 'right' and self.direction != 'left' or
            new_direction == 'up' and self.direction != 'down' or
            new_direction == 'down' and self.direction != 'up'):
            self.direction = new_direction

    def game_over(self):
        self.canvas.delete(tk.ALL)
        self.canvas.create_text(
            self.canvas.winfo_width()/2,
            self.canvas.winfo_height()/2,
            font=('consolas', 70),
            text="GAME OVER",
            fill="red",
            tag="gameover"
        )
        
        # Show final score
        self.canvas.create_text(
            self.canvas.winfo_width()/2,
            self.canvas.winfo_height()/2 + 80,
            font=('consolas', 20),
            text=f"Final Score: {self.score}",
            fill="white",
            tag="score"
        )
        
        # Add play again button
        play_again_btn = tk.Button(
            self.window,
            text="Play Again",
            command=self.reset_game,
            font=('consolas', 15)
        )
        play_again_btn.pack(pady=10)

    def reset_game(self):
        # Clear canvas and remove play again button
        self.canvas.delete(tk.ALL)
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        # Reset game variables
        self.direction = 'right'
        self.score = 0
        self.snake = []
        self.food = None
        self.label.config(text=f"Score: {self.score} High Score: {self.high_score}")

        # Restart game
        self.create_snake()
        self.create_food()
        self.next_turn()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()