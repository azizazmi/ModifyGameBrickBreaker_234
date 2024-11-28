import tkinter as tk
import random  # To generate random chances for power-ups

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 7
        self.direction = [1, -1]
        # increase the below value to increase the speed of ball
        self.speed = 8
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='#f51010')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#f7ee35')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#fc25b4', 2: '#fc8516', 3: '#4cf51a'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            if random.random() < 0.3:
                self.drop_powerup(game)
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])
            
    def drop_powerup(self, game):
        """Drop a power-up when the brick is destroyed."""
        coords = self.get_position()
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
        powerup_type = random.choice(list(PowerUp.TYPES.keys()))  # Randomly pick a power-up type
        powerup = PowerUp(self.canvas, x, y, powerup_type)
        game.powerups.append(powerup)

class PowerUp(GameObject):
    TYPES = {
        "enlarge_paddle": "green",
        "fast_ball": "blue",
        "extra_life": "white",
    }

    def __init__(self, canvas, x, y, type):
        self.type = type  # Type of the power-up
        self.width = 20
        self.height = 20
        color = PowerUp.TYPES[type]
        item = canvas.create_oval(x - self.width / 2, y - self.height / 2,
                                  x + self.width / 2, y + self.height / 2,
                                  fill=color, tags='powerup')
        super(PowerUp, self).__init__(canvas, item)

    def fall(self):
        """Make the power-up fall down the screen."""
        self.move(0, 5)  # Adjust the speed as needed



class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 780
        self.height = 600
        self.canvas = tk.Canvas(self, bg='#1b1b1b',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()
        self.powerups = []

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 450)
        self.initial_paddle_width = self.paddle.width
        self.enlarge_paddle_count = 0
        self.items[self.paddle.item] = self.paddle
        # First layer (closest to the paddle): Bricks with 1 hit value
        for x in range(5, self.width - 5, 65):  # Adjust the gap to fit bricks evenly
            self.add_brick(x + 30, 275, 1)
        for x in range(5, self.width - 5, 90):  # Adjust the gap to fit bricks evenly
            self.add_brick(x + 30, 245, 1)
        # Second layer: Mix of 1-hit and 3-hit bricks
        for x in range(5, self.width - 5, 65):
            if x % 130 == 5:  # Alternate pattern for hits = 1
                self.add_brick(x + 30, 200, 3)
            else:  # Hits = 2
                self.add_brick(x + 30, 175, 1)
        # Third layer:
        for x in range(5, self.width - 5, 130):
            self.add_brick(x + 30, 140, 2)
        # Fourth layer: Mix of 2-hit and 3-hit bricks
        for x in range(5, self.width - 5, 65):
            if x % 130 == 5:  # Alternate pattern for hits = 2
                self.add_brick(x + 30, 110, 2)
            else:  # Hits = 3
                self.add_brick(x + 30, 125, 3)
        # Fifth layer (topmost): Mix of 1-hit and 3-hit bricks
        for x in range(5, self.width - 5, 90):
            self.add_brick(x + 30, 80, 1)
        for x in range(5, self.width - 5, 65):
            self.add_brick(x + 30, 50, 3)


        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-13))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(13))

    def setup_game(self):
           self.add_ball()
           self.update_lives_text()
           self.text = self.draw_text(390, 500,
                                      'Press Space to start')
           self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 400)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40', color='#ffffff'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill=color)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        self.check_powerup_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(380, 300, '                 You win! \nYou are the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(380, 300, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.update_powerups()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

    def update_powerups(self):
        """Update the position of all falling power-ups."""
        for powerup in self.powerups:
            powerup.fall()
            # Remove power-ups that fall off the screen
            if powerup.get_position()[3] >= self.height:
                self.powerups.remove(powerup)
                powerup.delete()
    
    def reset_paddle_size(self):
        """Reset the paddle to its initial size."""
        self.paddle.width = self.initial_paddle_width
        x1, y1, x2, y2 = self.paddle.get_position()
        self.canvas.coords(self.paddle.item, x1, y1, x1 + self.initial_paddle_width, y2)

        # Reset the power-up counter so the player can enlarge the paddle again
        self.enlarge_paddle_count = 0

    
    def check_powerup_collisions(self):
        """Check for collisions between the paddle and power-ups."""
        paddle_coords = self.paddle.get_position()
        for powerup in self.powerups:
            powerup_coords = powerup.get_position()
            if (paddle_coords[0] < powerup_coords[2] and
                paddle_coords[2] > powerup_coords[0] and
                paddle_coords[1] < powerup_coords[3] and
                paddle_coords[3] > powerup_coords[1]):
                self.apply_powerup(powerup)
                self.powerups.remove(powerup)
                powerup.delete()

    def apply_powerup(self, powerup):
        """Apply the effect of a power-up."""
        if powerup.type == "enlarge_paddle":
            new_width = min(self.canvas.winfo_width(), self.paddle.width + 30)
            x1, y1, x2, y2 = self.paddle.get_position()
            self.paddle.width = new_width
            self.canvas.coords(self.paddle.item, x1, y1, x1 + new_width, y2)
            self.enlarge_paddle_count += 1
            if self.enlarge_paddle_count == 1:
                self.canvas.after(10000, self.reset_paddle_size)
        elif powerup.type == "fast_ball":
            self.ball.speed = min(16, max(8, self.ball.speed + 2))
        elif powerup.type == "extra_life":
            if self.lives < 5:
                self.lives += 1
                self.update_lives_text()
            else:
                self.draw_text(390, 550, "Max lives reached!", size="15", color="#ff0000")
                self.after(1000, lambda: self.canvas.delete("max_lives_message"))  # Remove message after 1 second

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()