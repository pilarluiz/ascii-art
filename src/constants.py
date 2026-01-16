"""
Constants and character sets for ASCII art conversion.

Character sets are ordered from darkest to lightest (dense to sparse).
The converter will map pixel brightness values to these characters.
"""

# Character sets ordered from dark to light
CHAR_SETS = {
    "simple": "@%#*+=-:. ",
    
    "standard": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    
    "detailed": "@%#*+=-:. ",  # Can be expanded with more characters
    
    "blocks": "█▓▒░ ",  # Unicode block characters (dark to light)
}

# Default configuration
DEFAULT_WIDTH = 100
DEFAULT_CHAR_SET = "standard"
DEFAULT_HEIGHT = None  # None means auto-calculate based on aspect ratio

# Aspect ratio correction factor
# Terminal characters are typically taller than they are wide (~2:1 ratio)
# This factor helps maintain the original image proportions
ASPECT_RATIO_CORRECTION = 0.55

