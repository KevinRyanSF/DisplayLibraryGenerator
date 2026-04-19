import os
import re
from .models import Sprite


def export_h_file(sprites, filepath, display_type="SSD1306", display_w=128, display_h=64):
    """
    Generates a .h file containing display metadata and sprite data arrays.
    """
    with open(filepath, 'w') as f:
        f.write("#ifndef SPRITES_H\n#define SPRITES_H\n\n")
        f.write("#include <stdint.h>\n\n")

        # Display metadata (Useful for C compilation and the Python importer)
        f.write(f"// META_DISPLAY_TYPE: {display_type}\n")
        f.write(f"#define DISPLAY_WIDTH {display_w}\n")
        f.write(f"#define DISPLAY_HEIGHT {display_h}\n\n")

        for sprite in sprites:
            # Macros defining the dimensions of each sprite to facilitate calls in the MCU code
            f.write(f"#define {sprite.name.upper()}_WIDTH {sprite.width}\n")
            f.write(f"#define {sprite.name.upper()}_HEIGHT {sprite.height}\n")
            f.write(f"const uint8_t {sprite.name}[] = {{\n  ")

            # Converts the 2D grid matrix into a 1D array of bytes
            for r in range(sprite.height):
                for c_block in range(0, sprite.width, 8):
                    byte_val = 0
                    for bit in range(8):
                        if c_block + bit < sprite.width:
                            if sprite.grid[r][c_block + bit]:
                                byte_val |= (1 << (7 - bit))
                    f.write(f"0x{byte_val:02X}, ")

                # Adds a line break after each sprite row to improve C code readability
                f.write("\n  ")

            f.write("\n};\n\n")
        f.write("#endif // SPRITES_H\n")


def import_h_file(filepath):
    """
    Reads a .h file, extracts display configurations, and reconstructs the sprites.
    """
    if not os.path.exists(filepath):
        return [], "SSD1306", 128, 64

    with open(filepath, 'r') as f:
        content = f.read()

    # Searches for display metadata at the top of the file
    type_match = re.search(r"// META_DISPLAY_TYPE:\s*(\w+)", content)
    display_type = type_match.group(1) if type_match else "SSD1306"

    w_match = re.search(r"#define DISPLAY_WIDTH\s+(\d+)", content)
    display_w = int(w_match.group(1)) if w_match else 128

    h_match = re.search(r"#define DISPLAY_HEIGHT\s+(\d+)", content)
    display_h = int(h_match.group(1)) if h_match else 64

    sprites = []

    # Regular expression to locate the byte arrays
    pattern = re.compile(r"const\s+uint8_t\s+(\w+)\[\]\s*=\s*\{([^}]+)\};")
    matches = pattern.findall(content)

    for name, data_str in matches:
        # Attempts to find the specific width and height macros for the current sprite
        sw_match = re.search(rf"#define {name.upper()}_WIDTH\s+(\d+)", content)
        sh_match = re.search(rf"#define {name.upper()}_HEIGHT\s+(\d+)", content)

        s_width = int(sw_match.group(1)) if sw_match else 16
        s_height = int(sh_match.group(1)) if sh_match else 16

        sprite = Sprite(name=name, width=s_width, height=s_height)

        # Extracts hexadecimal values and reconstructs the 2D drawing matrix
        hex_values = re.findall(r"0x([0-9A-Fa-f]{1,2})", data_str)
        byte_index = 0
        for r in range(s_height):
            for c_block in range(0, s_width, 8):
                if byte_index < len(hex_values):
                    byte_val = int(hex_values[byte_index], 16)
                    for bit in range(8):
                        if c_block + bit < s_width:
                            sprite.grid[r][c_block + bit] = (byte_val >> (7 - bit)) & 1
                    byte_index += 1
        sprites.append(sprite)

    return sprites, display_type, display_w, display_h