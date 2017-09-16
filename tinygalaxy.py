
import pygame
import sys
import pygame.gfxdraw
import random
from infra import Vector
from collections import namedtuple
# from math import sin, cos, pi
# import wordgen

rand = random.Random()


Env = namedtuple("Env", ['name', 'color', 'mask'])
Attrs = namedtuple("Attrs", ['metals', 'stones', 'gazes', 'oils', 'flora', 'fauna', 'climate'])
NUM_ATTRS = 7

DESERT = Env("Desert", (224, 201, 143), '1111111')
TERRAN = Env("Terran", (159, 196, 43), '1111111')
OCEANIC = Env("Oceanic", (0, 132, 255), '1111111')
GAIA = Env("Gaia", (0, 182, 0), '1111111')
BARREN = Env("Barren", (168, 150, 109), '1101000')
GAZGIANT = Env("Gaz Giant", (255, 48, 132), '1111000')

ENVS = DESERT, TERRAN, OCEANIC, GAIA, BARREN, GAZGIANT


def distribute_attributes(limit=10, mask='1111111'):
    values = [0 for i in range(NUM_ATTRS)]
    max_points = limit * mask.count('1')
    min_points = max_points // 2
    remain = rand.randint(min_points, max_points)
    while remain > 0:
        index = rand.randint(0, NUM_ATTRS - 1)
        if values[index] < limit and int(mask[index]):
            values[index] += 1
            remain -= 1

    return Attrs(*values)


def lerp(a, b, r):
    return a + (b - a) * r


def draw_pixel(position, color, r=1):
    x, y = position
    if r <= 1:
        pygame.draw.aaline(pygame.display.get_surface(), color, (x - 1, y), (x + 2, y), True)
        pygame.draw.aaline(pygame.display.get_surface(), color, (x, y - 1), (x, y + 2), True)
    else:
        pygame.gfxdraw.aacircle(pygame.display.get_surface(), x, y, r, color)


def draw_cluster(position, numStars, radius):
    layer = 0
    pop = 1
    nStars = 0
    while nStars < numStars:
        for i in range(pop):
            r = layer * radius
            rad = lerp(r, r + radius, rand.rand())
            angle = rand.rand() * 360.0
            point = Vector.scaledNormal(angle, rad) + position
            nStars += 1
            draw_pixel(point.immutable, (240, 240, 240), 3)
        layer += 1
        pop += 2


def has_collision(a, b, radius):
    return a.distance(b) <= radius * 2


def choose_color():
    colors = [(224, 201, 143), (159, 196, 43), (0, 132, 255), (0, 182, 0)]
    return colors[rand.choice([0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 0, 1, 2])]


def get_environment(color):
    m = {
        (224, 201, 143): "Desert",
        (159, 196, 43): "Terran",
        (0, 132, 255): "Oceanic",
        (0, 182, 0): "Gaia"
    }

    if color in m:
        return m[color]
    return "Undefined"


def generate_map(mapCenter=(350000, 350000), numStars=210, layerRad=17500, starSystemRad=16000, filename='GalaxyMap.txt', seed=1412):
    with open(filename, 'w') as mapfile:
        rand.seed(seed)

        stcol = {True: (255, 255, 0), False: (64, 64, 0)}

        orbits = [0, 1, 0, 2, 0, 4, 0, 3, 0, 5, 0, 6, 0, 7, 0, 7, 0, 7]
        planetRads = [4000, 6000, 8000]
        locations = []
        left = mapCenter[0]
        top = mapCenter[1]
        right = mapCenter[0]
        bottom = mapCenter[1]
        halfLayer = (layerRad * 0.5)

        currentLayer = 0
        systemsOnLayer = 1

        while len(locations) < numStars:
            innerRadius = currentLayer * layerRad
            addedOnLayer = []

            while len(addedOnLayer) < int(systemsOnLayer):
                radius = innerRadius + halfLayer
                angle = rand.random() * 360.0
                point = Vector.scaledNormal(angle, radius) + mapCenter

                collides = False
                for p in addedOnLayer:
                    if has_collision(point, p, starSystemRad):
                        collides = True
                        break

                if collides:
                    continue

                planets = rand.choice(orbits)
                mapfile.write("\nSTARSYSTEM: ({}, {}) {}\n".format(point.x, point.y, "??"))  # wordgen.new_word('Onk')))
                for i in [0, 1, 2]:
                    bit = 2 ** i
                    rad = planetRads[i]
                    ang = rand.randint(0, 359)
                    if bit & planets == bit:
                        pp = Vector.scaledNormal(ang, rad) + point
                        x, y = pp.rounded
                        env = rand.choice(ENVS)
                        attrs = distribute_attributes(5, env.mask)
                        # color = choose_color()
                        mapfile.write("PLANET: ({}, {}) {} {} {}\n".format(x, y, tuple(attrs), env.name, ['I', 'II', 'III'][i]))
                        draw_pixel((pp * 0.001).rounded, env.color, 1)

                left = int(min(point.x - halfLayer, left))
                right = int(max(point.x + halfLayer, right))
                top = int(min(point.y - halfLayer, top))
                bottom = int(max(point.y + halfLayer, bottom))
                locations.append(point.rounded)
                addedOnLayer.append(point)
                draw_pixel((point * 0.001).rounded, stcol[planets > 0], 2)

            systemsOnLayer += 2
            currentLayer += 1.25

    return [left, top, right - left, bottom - top], locations


def main():
    width = 700
    height = 700
    displaymode = (width, height)
    pygame.display.set_mode(displaymode)
    pygame.display.set_caption('Starfield')
    # an array of colors for the stars. probability is determined by the amount of times a color is mentioned
    # colors = [THECOLORS["white"],THECOLORS["yellow"], THECOLORS["white"],THECOLORS["red"],THECOLORS["white"]]

    # draw_cluster((350,350), 70, 30)
    print(generate_map()[0])

    pygame.display.update()

    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            sys.exit()


if __name__ == "__main__":
    main()
