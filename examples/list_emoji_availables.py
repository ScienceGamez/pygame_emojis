from pygame_emojis import _SVG_DIR, find_code, find_svg

import emoji

# This will list all the files availabe for all the emojis known by emoji package
print(_SVG_DIR)
ALL_EMOJIS = emoji.EMOJI_DATA.keys()

EMOJI_TO_SEARCH = ["❤️", "👍", "🫶", "🏳️‍🌈", "😍", "🗡️", "🐦‍⬛"]

for e in EMOJI_TO_SEARCH:

    try:
        print(e, emoji.EMOJI_DATA[e])
        code_list = find_code(e)
        print(e, code_list)
        print("File selected:", find_svg(e))
    except:
        print(f"[ERROR] {e}: Could not translate {e}")
        continue

    print(f_name := "{}*.svg".format("-".join(code_list)))
    print("Files available: ", [f.name for f in _SVG_DIR.rglob(f_name)])
