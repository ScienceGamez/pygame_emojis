# pygame_emojis
Load emojis in pygame.

The first time you use this package, it will download a svg database.
This contain open source emojis from https://openmoji.org/

![example of how it looks](emoji.png)


## usage

```python

from pygame_emojis import load_emoji

# Choos the size
size = (64, 64)

# Load the emoji as a pygame.Surface
surface = load_emoji('😍', size)

```

## Acknowledgements


Emojis come from https://openmoji.org/.

See also their repo https://github.com/hfg-gmuend/openmoji/.

Thanks a lot to the whole team: https://openmoji.org/about/#acknowledgement.
