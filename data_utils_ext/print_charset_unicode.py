import fontforge
import sys
import getopt

def usage():
    print("Usage: fontforge -script print_charset.pe --font /path/to/font/file.ttf --glyph uni|id|charname|char")
    sys.exit(2)

def main(argv):
    font_path = None
    glyph_types = []

    try:
        opts, args = getopt.getopt(argv, "", ["font=", "glyph="])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt == "--font":
            font_path = arg
        elif opt == "--glyph":
            glyph_types = arg.split()
    
    if not font_path or not glyph_types:
        usage()

    # Open the font file
    font = fontforge.open(font_path)

    # Get the list of glyphs in the font
    glyphs = font.glyphs()

    # Print the character set
    print("Character Set of the Font:")
    for glyph in glyphs:
        if glyph.unicode != -1:  # Only consider glyphs with valid Unicode values
            output = []
            if "uni" in glyph_types: # Unicode Identifier
                output.append(f"U{glyph.unicode:04X}")
            if "id" in glyph_types: # Decimal Value
                output.append(str(glyph.unicode))
            if "charname" in glyph_types: # Character Name
                output.append(glyph.glyphname)
            if "char" in glyph_types: # Character
                output.append(chr(glyph.unicode))
            print(", ".join(output))
    print()  # For a new line at the end

    # Close the font file
    font.close()

if __name__ == "__main__":
    main(sys.argv[1:])