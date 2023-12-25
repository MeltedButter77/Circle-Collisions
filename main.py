import sys
import pygame
import math
import random

areaRadius = 380
areaCenter = pygame.Vector2(400, 400)
newBallRadius = 20


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


class Ring(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        super().__init__()
        self.colour = pygame.Color(generate_color())

        self.radius = radius
        self.position = pygame.Vector2(x, y)
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

    def collide_balls(self, game):
        for other in game.balls.sprites():
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

    def update(self, game, *args, **kwargs):
        self.position += self.velocity

        self.collide_wall()
        self.collide_balls(game)

        if self.radius > areaRadius:
            print("KIL")
            self.kill()

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
        self.balls = pygame.sprite.Group()

    def run(self):
        while True:
            self.screen.fill((0, 0, 100))

            pygame.draw.circle(self.screen, "blue", (400, 400), areaRadius)
            for ring in self.balls:
                ring.update(self)
                ring.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.balls.add(Ring(400, 400, newBallRadius))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.balls.add(Ring(event.pos[0], event.pos[1], newBallRadius))

            pygame.display.update()
            self.clock.tick(60)


Game().run()
