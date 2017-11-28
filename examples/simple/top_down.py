import sys

import pygame

import examples.simple.extend.entities as extend
import systems


def main():
    # screen setup
    pygame.init()
    size = 0, 0
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    width, height = screen.get_size()

    # colour constants
    WHITE = (255, 255, 255)

    # group setup
    colliders = pygame.sprite.Group()
    non_colliders = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    player = extend.Player(width / 2, height / 2,
                           {"base": "examples/simple/assets/player.png",
                            "hurt": "examples/simple/assets/player-hurt.png"})
    main_cam = systems.camera.Camera(systems.camera.simple_camera, (width, height))
    clock = pygame.time.Clock()

    level = [
        "###############################",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "#.............................#",
        "###############################"
    ]

    # parse level list and add walls and floors to groups
    x, y = 0, 0
    for row in level:
        for col in row:
            if col == ".":
                extend.Floor(x, y).add(non_colliders, all_sprites)
            elif col == "#":
                extend.Wall(x, y).add(colliders, all_sprites)
            x += 32
        y += 32
        x = 0

    player.add(colliders, all_sprites)  # add player to groups

    # setup basic enemy and add to groups
    follower = extend.Follower(100, 100, {"base": "examples/simple/assets/enemy.png",
                                          "hurt": "examples/simple/assets/enemy-hurt.png"},
                               player)
    follower.add(colliders, all_sprites)

    # game loop
    while True:
        clock.tick(60)
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # handle events and move player
        player.rotate_to_mouse()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move(0, -player.speed, colliders)
        if keys[pygame.K_s]:
            player.move(0, player.speed, colliders)
        if keys[pygame.K_a]:
            player.move(-player.speed, 0, colliders)
        if keys[pygame.K_d]:
            player.move(player.speed, 0, colliders)

        if keys[pygame.K_ESCAPE]:
            sys.exit()

        if pygame.mouse.get_pressed()[0]:
            shake = player.attack()  # TODO: Offset camera by increments from shake generator

        main_cam.update(player)  # tell camera to follow player

        for sprite in all_sprites:
            if isinstance(sprite, systems.entities.LivingSprite):  # check if sprite is living
                if sprite.health > 0:
                    try:
                        for bullet in sprite.projectiles:
                            screen.blit(bullet.image, main_cam.apply(bullet))  # draw projectiles to screen
                    except AttributeError:  # will be raised if sprite has no projectiles group
                        pass
                    screen.blit(sprite.image, main_cam.apply(sprite))  # draw living sprites if they have health
            else:
                screen.blit(sprite.image, main_cam.apply(sprite))  # draw other sprites

        all_sprites.update(colliders, screen, main_cam)  # update sprites(kill dead sprites, update damage timers)

        pygame.display.flip()  # update display


if __name__ == "__main__":
    main()
