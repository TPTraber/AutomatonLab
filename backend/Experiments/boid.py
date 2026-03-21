import pygame
import random
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

boidNum  = 50
speed = 0

class Boid:
    def __init__(self, startingPos):
        self.pos = startingPos
        self.velocity = pygame.Vector2(random.random() * 10 - 5,random.random() * 10 - 5)
        self.neighbors = []
        self.cohesion = pygame.Vector2()

    def updatePos(self, speed):
        self.pos = self.pos + (self.velocity * speed)

    def isInRange(self, otherBoid, sightDistance):
        return math.dist(self.pos, otherBoid.pos) <= sightDistance
    
    def getNeighbours(self,boids, range):
        self.neighbors = []
        for boi in boids:
            if boi != self and self.isInRange(boi, range):
                self.neighbors.append(boi)
    
    def updateCohesion(self):
        neighborVectors = []
        if len(neighborVectors) == 0: return
        for boi in self.neighbors:
            neighborVectors += boi.pos - self.pos
        averageVector = pygame.Vector2
        for vector in neighborVectors:
            averageVector += vector
        self.cohesion = averageVector * (1 / len(neighborVectors))
        print(self.cohesion)
        
        
    def updateVelocity(self, cohesionM = 1):
        self.updateCohesion()
        sumVector = pygame.Vector2()
        sumVector += self.cohesion * cohesionM
        self.velocity = sumVector

boids=[]

for i in range(0,boidNum):
    startingX = random.randrange(0, screen.get_width())
    startingY = random.randrange(0, screen.get_width())
    boids.append(Boid(pygame.Vector2(startingX, startingY)))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    for boi in boids:
        boi.getNeighbours(boids, 30)
        boi.updateVelocity()
        boi.updatePos(1)
        pygame.draw.circle(screen, "white", boi.pos, 10)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()