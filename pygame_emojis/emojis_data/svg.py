try:
    import cairosvg
    cairo_installed = True
except (OSError, ModuleNotFoundError): 
    # OSError: no library called "cairo-2" was found
    # ModuleNotFoundError: cairosvg not installed
    cairo_installed = False
    cairosvg = None