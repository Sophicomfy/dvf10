# run by: `fontforge -script /path/to/print_charset.pe`

# Open the font file
font = fontforge.open("/datasets/lttr_ext/00000.otf")

# Get the list of glyphs in the font
glyphs = font.glyphs()

# Print the character set
print("Character Set of the Font:")
for glyph in glyphs:
    if glyph.unicode != -1:  # Only consider glyphs with valid Unicode values
        print(chr(glyph.unicode), end=' ')
print()  # For a new line at the end

# Close the font file
font.close()
