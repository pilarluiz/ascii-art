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
    
    "blocks-simple": "█▓▒░*+=-:. ",  # Combines blocks (dense) with simple characters (light)
}

# Default configuration
DEFAULT_WIDTH = 100
DEFAULT_CHAR_SET = "simple"
DEFAULT_HEIGHT = None  # None means auto-calculate based on aspect ratio

# Aspect ratio correction factor
# Terminal characters are typically taller than they are wide (~2:1 ratio)
# This factor helps maintain the original image proportions
# Lower values = more height compression to compensate for tall terminal chars
# Typical values: 0.4-0.6 for most terminals
ASPECT_RATIO_CORRECTION = 0.5

