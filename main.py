import sys
import pygame
import math
import random

areaRadius = 380
areaCenter = pygame.Vector2(400, 400)
newBallRadius = 20

# Changeable Values
wall_bounce_increase = 0.7
collide_bounce_increase = 0.7
max_velocity = 20

deathColour = (0, 0, 100)

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

        self.radius = radius
        self.position = pygame.Vector2(center[0], center[1])
        self.velocity = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))

    def collide_wall(self):
        distance = math.sqrt((self.position.x - 400) ** 2 + (self.position.y - 400) ** 2)
        if distance + self.radius > areaRadius:

            angle = math.atan2(self.position.y - areaCenter.y, self.position.x - areaCenter.x)
            angle += random.uniform(-0.1, 0.1)  # Adjust the range as needed

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
        for other in game.collision_balls.sprites():
            if self == other:
                continue

            # Calculate the distance between the ball centers
            distance = self.position.distance_to(other.position)

            # Check if the distance is less than the sum of the radii (collision detected)
            if distance < self.radius + other.radius:
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
        pass

    def update(self, game, *args, **kwargs):
        self.position += self.velocity

        self.collide_wall()
        self.collide_balls(game)
        self.drag()

        if self.radius > areaRadius:
            self.kill()

        if self.velocity.length() > max_velocity:
            game.collision_balls.remove(self)
            self.colour = deathColour

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.position, self.radius)


class Game:
    def __init__(self):
        # Pygame Setup
        pygame.init()
        pygame.display.set_caption("Platformer!")
        self.screen = pygame.display.set_mode((800, 800))
        self.clock = pygame.time.Clock()

        # Sprite Groups
        self.collision_balls = pygame.sprite.Group()
        self.all_balls = pygame.sprite.Group()

    def run(self):
        while True:
            self.screen.fill((0, 0, 100))

            pygame.draw.circle(self.screen, "blue", (400, 400), areaRadius)

            self.collision_balls.update(self)
            for ball in self.all_balls:
                ball.draw(self.screen)

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
            self.clock.tick(60)


Game().run()
