# run by: `fontforge -script /path/to/print_charset.pe`

# Open the font file
font = fontforge.open("/datasets/lttr_ext/00000.otf")

# Get the list of glyphs in the font
glyphs = font.glyphs()

# Print the character set in Newline-Delimited Unicode format
print("Character Set of the Font:")
for glyph in glyphs:
    if glyph.unicode != -1:  # Only consider glyphs with valid Unicode values
        unicode_hex = f"{glyph.unicode:04X}"
        print(f"uni{unicode_hex}")

# Close the font file
font.close()
