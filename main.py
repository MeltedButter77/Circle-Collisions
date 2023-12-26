import sys
import pygame
import math
import random

# Changeable Values
screen_width = 600

wall_bounce_increase = 0
collide_bounce_increase = 0
drag_multiplier = 1
death_velocity = 10

angle_random = 0.01
balls_collide = True

velocity_random = 2

newBallRadius = 15
deathColour = (0, 0, 100)

# Dependant & Fixed Values
window_size = pygame.Vector2(screen_width, screen_width)
areaRadius = window_size[0] / 2 - 20
areaCenter = pygame.Vector2(window_size*0.5)
simulation_fps = 60
fps = 60

def generate_color():
    """
    Generates a random vibrant color with reduced chances of being grey or white.
    This is achieved by ensuring that not all the color components are too close to each other or too high.
    """
    while True:
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)

        # Checking if the colors are not too close to each other (which would make them greyish)
        # and not all of them are too high (which would make them whitish)
        if abs(r - g) > 30 and abs(r - b) > 30 and abs(g - b) > 30 and not (r > 200 and g > 200 and b > 200):
            return r, g, b


class Ball(pygame.sprite.Sprite):
    def __init__(self, game, center, radius):
        super().__init__()
        self.colour = pygame.Color(generate_color())

        game.all_balls.add(self)
        game.collision_balls.add(self)

        self.last_collision_time = 0
        self.collision_cooldown = 50  # cooldown time in milliseconds

        self.radius = radius
        self.position = pygame.Vector2(center[0], center[1])
        self.velocity = pygame.Vector2(random.uniform(-velocity_ran, velocity_ran), random.uniform(-velocity_ran, velocity_ran))

    def collide_wall(self):
        distance = math.sqrt((self.position.x - areaCenter.x) ** 2 + (self.position.y - areaCenter.y) ** 2)
        if distance + self.radius > areaRadius:

            angle = math.atan2(self.position.y - areaCenter.y, self.position.x - areaCenter.x)
            angle += random.uniform(-angle_ran, angle_ran)  # Adjust the range as needed

            # Calculate the normal vector components
            normal_x = math.cos(angle)
            normal_y = math.sin(angle)

            # Calculate the dot product of velocity and normal
            dot_product = self.velocity.x * normal_x + self.velocity.y * normal_y

            # Reflect the ball's velocity
            self.velocity.x -= 2 * dot_product * normal_x
            self.velocity.y -= 2 * dot_product * normal_y

            velocity_direction = self.velocity.normalize()
            increase = pygame.Vector2(velocity_direction.x, velocity_direction.y) * wall_bounce_increase
            self.velocity += increase

    def collide_balls(self, game):
        if not balls_collide:
            return

        current_time = pygame.time.get_ticks()

        for other in game.collision_balls.sprites():
            if self == other:
                continue

            # Calculate the distance between the ball centers
            distance = self.position.distance_to(other.position)

            # Check if the distance is less than the sum of the radii (collision detected)
            if distance < self.radius + other.radius:
                # Check if the cooldown period has passed
                if current_time - self.last_collision_time > self.collision_cooldown:
                    self.last_collision_time = current_time
                    # Calculate the overlap
                    overlap = self.radius + other.radius - distance

                    # Calculate the normal vector
                    normal = (self.position - other.position).normalize()

                    # Adjust positions based on the overlap
                    self.position += normal * (overlap / 2)
                    other.position -= normal * (overlap / 2)

                    # Reflect the velocities
                    self.velocity.reflect_ip(normal)
                    other.velocity.reflect_ip(normal)

                    # increase velocity
                    velocity_direction = self.velocity.normalize()
                    increase = pygame.Vector2(velocity_direction.x, velocity_direction.y) * collide_bounce_increase
                    self.velocity += increase

    def drag(self):
        self.velocity *= drag_multiplier

    def update(self, game, *args, **kwargs):
        self.position += self.velocity

        self.collide_wall()
        self.collide_balls(game)
        self.drag()

        if self.radius > areaRadius:
            self.kill()

        if self.velocity.length() > death_velocity:
            game.collision_balls.remove(self)
            self.colour = deathColour

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.position, self.radius)


class Game:
    def __init__(self):
        # Pygame Setup
        pygame.init()
        pygame.display.set_caption("Game")
        self.screen = pygame.display.set_mode(window_size)
        self.clock = pygame.time.Clock()
        self.last_update_time = pygame.time.get_ticks()
        self.update_interval = 1/simulation_fps

        # Sprite Groups
        self.collision_balls = pygame.sprite.Group()
        self.all_balls = pygame.sprite.Group()

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()

            # This is consistent time between runs
            if current_time - self.last_update_time >= self.update_interval:
                self.last_update_time = current_time

                self.collision_balls.update(self)

            # Draw sequence
            self.screen.fill((0, 0, 100))

            pygame.draw.circle(self.screen, "blue", areaCenter, areaRadius)

            for ball in [ball for ball in self.all_balls if ball not in self.collision_balls]:
                ball.draw(self.screen)
            for ball in self.collision_balls:
                ball.draw(self.screen)

            # Handle events
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[2]:
                Ball(self, pygame.mouse.get_pos(), newBallRadius)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        Ball(self, (400, 400), newBallRadius)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    Ball(self, event.pos, newBallRadius)

            pygame.display.update()
            # small delay to reduce CPU usage
            pygame.time.delay(1)
            self.clock.tick(fps)

            # Display fps
            real_fps = self.clock.get_fps()
            pygame.display.set_caption(f"Current FPS: {real_fps:.2f}")

Game().run()
