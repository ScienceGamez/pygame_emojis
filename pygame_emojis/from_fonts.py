"""This was un attempt to make emojis from fonts.

But I never managed to make it work.
"""
import pygame


def available_emojis_fonts() -> list[str]:
    fonts = pygame.sysfont.get_fonts()
    emojis = [font for font in fonts if "emoji" in font]
    return emojis


def default_emoji_font() -> str:
    emoji_fonts = available_emojis_fonts()
    if emoji_fonts:
        return emoji_fonts[0]
    else:
        raise ValueError("No Font could be find in the system.")


if __name__ == "__main__":
    # Code found online and a bit modified
    import pygame, emoji
    import pygame.freetype

    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    done = False
    print(available_emojis_fonts())

    pygame.font.init()
    font = pygame.font.SysFont(default_emoji_font(), 50)
    # font = pygame.font.SysFont("segoe-ui-symbol.ttf", 72)
    font_color = (255, 255, 255, 255)
    font_background = (0, 0, 0, 0)

    text_string = emoji.emojize(":smile:")
    # text_string = u'ujiHelloÁpQ|, World 👍😖'
    # text_string = u'ujiHelloÁpQ|\U0001f44d, World 😖'
    # print(emoji.emojize('Python is :thumbs_up_sign:'))
    # text = font.render("♛", True, font_color, (0, 0))
    # text = font.render(text_string, True, font_color, (0, 0, 0, 0))
    # text = font.render(text_string, True, "black")
    text = font.render("A", True, "black")

    image_size = list(text[0].get_size())
    text_image = pygame.Surface(image_size)
    text_image.fill(font_background)
    pygame.display.flip()

    text_image.blit(text[0], (0, 0))

    # print(dir(text_image))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                done = True

        screen.fill((0, 0, 0))
        # screen.blit(text,
        screen.blit(
            text_image,
            (320 - text[0].get_width() // 2, 240 - text[0].get_height() // 2),
        )

        pygame.display.flip()
        clock.tick(60)
