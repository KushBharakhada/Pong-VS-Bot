import pygame

pygame.init()

"""
Pong vs Bot
- Player and Bot have 5 Lives
- Game ends when one player has 0 lives
- Winner is presented to the screen at the end then game restarts
- Bot plays by looking at the vertical position of the puck
"""

# Setting up window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong VS Bot")

# Colors
BLUE = (25, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Fonts
SCORE_FONT = pygame.font.SysFont("comicsans", 30)
WINNER_FONT = pygame.font.SysFont("comicsans", 70)

FPS = 60
PADDLE_EDGE_SPACING = 10
INITIAL_LIVES = 5


class Paddle:
    # Paddle size
    PADDLE_WIDTH = 10
    PADDLE_HEIGHT = 70
    VELOCITY = 3

    def __init__(self, x, y, color, lives=INITIAL_LIVES):
        self.x = x
        self.y = self.initial_pos_y = y
        self.color = color
        self.lives = lives

    def draw(self, window):
        pygame.draw.rect(WINDOW, self.color,
                         (self.x, self.y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT))

    def move(self, up=True):
        if up:
            self.y -= self.VELOCITY
        else:
            self.y += self.VELOCITY

    def recenter(self):
        self.y = self.initial_pos_y


class Puck:
    RADIUS = 7
    MAX_VELOCITY = 5

    def __init__(self, x, y):
        self.x = self.initial_pos_x = x
        self.y = self.initial_pos_y = y
        self.x_velocity = self.MAX_VELOCITY
        self.y_velocity = self.initial_vel_y = 0

    def draw(self, window):
        pygame.draw.circle(WINDOW, WHITE, (self.x, self.y), self.RADIUS)

    def move(self):
        self.x += self.x_velocity
        self.y += self.y_velocity

    def recenter(self):
        self.x = self.initial_pos_x
        self.y = self.initial_pos_y
        self.y_velocity = self.initial_vel_y
        self.x_velocity *= -1


def puck_paddle_collision(puck, paddle):
    paddle_middle_y = paddle.y + Paddle.PADDLE_HEIGHT / 2
    # Find y difference between puck and center of paddle
    # Collision in top half of paddle gives positive and bottom gives negative difference
    y_difference = paddle_middle_y - puck.y
    # Calculate where on the paddle puck was hit
    proportion = y_difference / (Paddle.PADDLE_HEIGHT / 2)
    # Closer to the edge the puck hits paddle, higher the velocity
    vel = proportion * Puck.MAX_VELOCITY
    puck.y_velocity = -vel


def collision(puck, player, bot):
    # Puck hits top and bottom
    if puck.y + Puck.RADIUS >= WINDOW_HEIGHT:
        puck.y_velocity *= -1
    elif puck.y - Puck.RADIUS <= 0:
        puck.y_velocity *= -1

    # Check direction of puck (left or right)
    if puck.x_velocity < 0:
        # Check if puck is in front of panel vertically
        if puck.y >= player.y and puck.y <= player.y + Paddle.PADDLE_HEIGHT:
            # Check if left side of puck touches the left paddle
            if puck.x - Puck.RADIUS <= player.x + Paddle.PADDLE_WIDTH:
                # Change x direction and adjust y
                puck.x_velocity *= -1
                puck_paddle_collision(puck, player)
    else:
        if bot.y <= puck.y and puck.y <= bot.y + Paddle.PADDLE_HEIGHT:
            if puck.x + Puck.RADIUS >= bot.x:
                puck.x_velocity *= -1
                puck_paddle_collision(puck, bot)


def draw(window, player, bot, puck):
    window.fill(BLACK)
    player.draw(window)
    bot.draw(window)

    # Center vertical line
    pygame.draw.rect(window, WHITE, (WINDOW_WIDTH // 2, 0, 2, WINDOW_HEIGHT))

    # Lives text
    player_lives_text = SCORE_FONT.render(f"{player.lives}", 1, BLUE)
    bot_lives_text = SCORE_FONT.render(f"{bot.lives}", 1, RED)
    window.blit(player_lives_text, (WINDOW_WIDTH//4 - player_lives_text.get_width()/2, 15))
    window.blit(bot_lives_text, (WINDOW_WIDTH * 3/4 - bot_lives_text.get_width() / 2, 15))

    # Puck
    puck.draw(window)
    pygame.display.update()


def player_movement(keys, player):
    if keys[pygame.K_UP] and player.y - Paddle.VELOCITY > 0:
        player.move(up=True)
    if keys[pygame.K_DOWN] and \
            player.y + Paddle.PADDLE_HEIGHT + Paddle.VELOCITY < WINDOW_HEIGHT:
        player.move(up=False)


def bot_movement(puck, bot):
    # Only move bot when puck is heading towards the bot
    if puck.x_velocity >= 0:
        paddle_middle_y = bot.y + Paddle.PADDLE_HEIGHT / 2
        if puck.y <= paddle_middle_y and bot.y - Paddle.VELOCITY > 0:
            bot.move(up=True)
        if puck.y >= paddle_middle_y and \
                bot.y + Paddle.PADDLE_HEIGHT + Paddle.VELOCITY < WINDOW_HEIGHT:
            bot.move(up=False)

def round_reset(puck, player, bot):
    # Reset paddles and the puck
    player.recenter()
    bot.recenter()
    puck.recenter()


def reset(puck, player, bot):
    # Reset paddles, puck and lives
    round_reset(puck, player, bot)
    player.lives = INITIAL_LIVES
    bot.lives = INITIAL_LIVES


def check_lives(player, bot):
    if player.lives == 0:
        return "You LOSE!"
    elif bot.lives == 0:
        return "You WIN!"
    return ""


def pong():
    run = True
    clock = pygame.time.Clock()

    # Paddles - Start paddle at center vertically
    player_paddle = Paddle(PADDLE_EDGE_SPACING,
                           WINDOW_HEIGHT // 2 - Paddle.PADDLE_HEIGHT // 2, BLUE)
    bot_paddle = Paddle(WINDOW_WIDTH - Paddle.PADDLE_WIDTH - PADDLE_EDGE_SPACING,
                        WINDOW_HEIGHT // 2 - Paddle.PADDLE_HEIGHT // 2, RED)

    # Puck
    puck = Puck(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    while run:
        # Cap the while loop at a maximum FPS
        clock.tick(FPS)
        draw(WINDOW, player_paddle, bot_paddle, puck)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Check keys pressed by player
        keys_pressed = pygame.key.get_pressed()
        player_movement(keys_pressed, player_paddle)
        # Move bot according to puck position
        bot_movement(puck, bot_paddle)

        puck.move()
        collision(puck, player_paddle, bot_paddle)

        if puck.x < 0:
            player_paddle.lives -= 1
            round_reset(puck, player_paddle, bot_paddle)
        elif puck.x > WINDOW_WIDTH:
            bot_paddle.lives -= 1
            round_reset(puck, player_paddle, bot_paddle)

        text = check_lives(player_paddle, bot_paddle)
        if text:
            winner_text = WINNER_FONT.render(text, 1, YELLOW)
            WINDOW.blit(winner_text,
                        (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, WINDOW_HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(5000)
            reset(puck, player_paddle, bot_paddle)

    pygame.QUIT


if __name__ == "__main__":
    pong()
