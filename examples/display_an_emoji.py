import logging
import pygame
from random import choice
from pygame_emojis import load_emoji, logger

logging.basicConfig()

# Set logging to debug so we see what happens


logger.setLevel(logging.DEBUG)


if __name__ == "__main__":

    pygame.init()
    size = (640, 640)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    done = False

    pygame.font.init()

    emojis_list = [":red_heart:", "👍", "🫶", "🏳️‍🌈", "😍", "🗡️"]

    def change_emoji():
        screen.fill((0, 0, 0))

        surf = load_emoji(choice(emojis_list), size)
        screen.blit(surf, (0, 0))
        pygame.display.update()

    change_emoji()

    # print(dir(text_image))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                done = True
            elif event.type == pygame.KEYDOWN:

                change_emoji()

        clock.tick(20)