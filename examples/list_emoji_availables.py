from pygame_emojis import _EMOJIS_DIR, find_code, find_emoji

import emoji

# This will list all the files availabe for all the emojis known by emoji package
print(_EMOJIS_DIR)
ALL_EMOJIS = emoji.EMOJI_DATA.keys()

EMOJI_TO_SEARCH = ["❤️", "👍", "🫶", "🏳️‍🌈", "😍", "🗡️", "🐦‍⬛"]

for e in EMOJI_TO_SEARCH:

    try:
        print(e, emoji.EMOJI_DATA[e])
        code_list = find_code(e)
        print(e, code_list)
        file = find_emoji(e)
        print("File selected:", file)
        extension = file.suffix
    except Exception as err:
        print(f"[ERROR] {err}: Could not translate {e}")
        continue

    print(f_name := "{}*{}".format("-".join(code_list), extension))
    print("Files available: ", [f.name for f in _EMOJIS_DIR.rglob(f_name)])
