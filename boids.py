import pygame
from pygame.locals import *
import random, math
import os.path

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900

BOID_NUMBER = 200
BOID_GROUP_DISTANCE = 150
BOID_LOCAL_DISTANCE = 50
BOID_MAX_SPEED = 6
BOID_COHESION_FACTOR = 0.0001
BOID_ALIGNMENT_FACTOR = 0.125
BOID_SEPARATION_DISTANCE = 20
BOID_SEPARATION_FACTOR = 0.02
BOID_MAX_NOISE = 0

BORDER_WIDTH = 40
BORDER_REPEL_FACTOR = 0.2

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    file = os.path.join(main_dir, 'data', file)
    try:
        image = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image')
    return image.convert_alpha()

class Boid(pygame.sprite.Sprite):
    images = []
    def __init__(self, pos=None):
        pygame.sprite.Sprite.__init__(self, self.container)
        self.image = self.images[0]
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(4, 13))
        if pos is not None:
            self.pos = pos
        else:
            self.pos = random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)
        self.angle = random.randint(0, 359)
        self.dir = self.angle
        self.velocity = (random.uniform(-BOID_MAX_SPEED, BOID_MAX_SPEED),
                         random.uniform(-BOID_MAX_SPEED, BOID_MAX_SPEED))

    def get_velocity(self):
        center_x, center_y = 0, 0
        separation_x, separation_y = 0, 0
        alignment_x, alignment_y = 0, 0
        group_count, local_count = 0, 0
        pos = self.pos
        for boid in self.container:
            dis = math.hypot(boid.pos[0] - pos[0], boid.pos[1] - pos[1])
            if dis <= BOID_GROUP_DISTANCE:
                center_x += boid.pos[0]
                center_y += boid.pos[1]
                group_count += 1
            if dis <= BOID_LOCAL_DISTANCE:
                alignment_x += boid.velocity[0]
                alignment_y += boid.velocity[1]
                local_count += 1
            if dis <= BOID_SEPARATION_DISTANCE:
                separation_x -= (boid.pos[0] - pos[0]) * BOID_SEPARATION_FACTOR
                separation_y -= (boid.pos[1] - pos[1]) * BOID_SEPARATION_FACTOR

        # Cohesion: Boids move towards the center of their group
        if group_count > 0:
            center_x /= group_count
            center_y /= group_count
        cohesion = ((center_x - pos[0]) * BOID_COHESION_FACTOR,
                    (center_y - pos[1]) * BOID_COHESION_FACTOR)

        # Alignment: Boids try to match the velocity of nearby boids
        if local_count > 0:
            alignment_x /= local_count
            alignment_y /= local_count
        alignment = ((alignment_x - self.velocity[0]) * BOID_ALIGNMENT_FACTOR,
                     (alignment_y - self.velocity[1]) * BOID_ALIGNMENT_FACTOR)

        # Separation: Boids try to move away from boids that are too close
        separation = separation_x, separation_y

        return tuple(sum(x) for x in zip(self.velocity, cohesion, separation, alignment))


    def update(self):
        self.velocity = self.get_velocity()

        # Repel boids when near border of screen
        if abs(WINDOW_WIDTH / 2 - self.pos[0]) > WINDOW_WIDTH / 2 - BORDER_WIDTH:
            repel = 1 if self.pos[0] < WINDOW_WIDTH / 2 else -1
            repel *= BOID_MAX_SPEED * BORDER_REPEL_FACTOR
            self.velocity = self.velocity[0] + repel, self.velocity[1]
        if abs(WINDOW_HEIGHT / 2 - self.pos[1]) > WINDOW_HEIGHT / 2 - BORDER_WIDTH:
            repel = 1 if self.pos[1] < WINDOW_HEIGHT / 2 else -1
            repel *= BOID_MAX_SPEED * BORDER_REPEL_FACTOR
            self.velocity = self.velocity[0], self.velocity[1] + repel

        # Add noise
        x_rand = random.uniform(-BOID_MAX_NOISE, BOID_MAX_NOISE)
        y_rand = random.uniform(-BOID_MAX_NOISE, BOID_MAX_NOISE)
        self.velocity = self.velocity[0] + x_rand, self.velocity[1] + y_rand

        # Clamp velocity
        self.velocity = tuple(max(min(x, BOID_MAX_SPEED), -BOID_MAX_SPEED) for x in self.velocity)

        self.pos = tuple(sum(x) for x in zip(self.pos, self.velocity))

        self.angle = math.degrees(math.atan2(self.velocity[1], self.velocity[0]))
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=(self.rect.center))
        self.rect.center = self.pos

def main():
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Boids')

    Boid.images = [load_image('boid.png')]
    icon = pygame.transform.scale(Boid.images[0], (32, 32))
    pygame.display.set_icon(icon)

    boids = pygame.sprite.Group()
    Boid.container = boids

    # Create boids
    for _ in range(BOID_NUMBER):
        Boid()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                Boid(pygame.mouse.get_pos())

        pygame.time.Clock().tick(60)
        screen.fill([0, 0, 0])
        boids.update()
        boids.draw(screen)
        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()
