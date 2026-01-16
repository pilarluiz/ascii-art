"""
ASCII Art Converter

Converts images to ASCII art representation.
"""

from PIL import Image
# import numpy as np
from .constants import CHAR_SETS, DEFAULT_WIDTH, DEFAULT_CHAR_SET, ASPECT_RATIO_CORRECTION


class AsciiConverter:
    """
    Converts images to ASCII art.
    
    The converter takes an image, resizes it, converts to grayscale,
    and maps each pixel's brightness to an ASCII character.
    """
    
    def __init__(self, width: int = DEFAULT_WIDTH, char_set: str = DEFAULT_CHAR_SET) -> None:
        """
        Initialize the ASCII converter.
        
        Args:
            width: Width of the output ASCII art in characters
            char_set: Name of character set to use (from constants.CHAR_SETS)
        """
        self.width = width
        
        # Validate and store the character set
        if char_set not in CHAR_SETS:
            raise ValueError(f"Unknown character set '{char_set}'. Available: {list(CHAR_SETS.keys())}")
        
        self.char_set_name = char_set
        self.characters = CHAR_SETS[char_set]
        
        # Store aspect ratio correction for resizing
        self.aspect_ratio_correction = ASPECT_RATIO_CORRECTION
    
    
    def convert_image(self, image_path: str) -> str:
        """
        Convert an image file to ASCII art.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            String containing the ASCII art representation
        """
        # Load the image
        image = self._load_image(image_path)
        
        # Resize the image
        image = self._resize_image(image)
        
        # Convert to grayscale
        image = self._convert_to_grayscale(image)
        
        # Convert pixels to ASCII characters
        ascii_art = self._pixels_to_ascii(image)
        
        return ascii_art
    
    
    def _load_image(self, image_path: str) -> Image.Image:
        """
        Load an image from file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object
        """
        try:
            image = Image.open(image_path)
            return image
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise ValueError(f"Failed to load image '{image_path}': {e}")
    
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image to target ASCII dimensions.
        Maintains aspect ratio with correction for terminal character height.
        
        Args:
            image: PIL Image object
            
        Returns:
            Resized PIL Image object
        """
        # Get original dimensions
        original_width, original_height = image.size
        
        # Calculate aspect ratio
        aspect_ratio = original_height / original_width
        
        # Calculate new height based on width, with correction for terminal character height
        # Terminal characters are taller than wide (~2:1), so we adjust
        new_height = int(self.width * aspect_ratio * self.aspect_ratio_correction)
        
        # Resize the image
        resized_image = image.resize((self.width, new_height), Image.Resampling.LANCZOS)
        
        return resized_image
    
    
    def _convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """
        Convert image to grayscale.
        
        Args:
            image: PIL Image object
            
        Returns:
            Grayscale PIL Image object
        """
        # Convert to grayscale mode ('L' = Luminance)
        grayscale_image = image.convert('L')
        return grayscale_image
    
    
    def _pixels_to_ascii(self, image: Image.Image) -> str:
        """
        Convert image pixels to ASCII characters.
        Maps brightness values (0-255) to characters in the character set.
        
        Args:
            image: Grayscale PIL Image object
            
        Returns:
            String containing ASCII art
        """
        # Get image dimensions
        width, height = image.size
        
        # Get all pixel data as a flat list (brightness values 0-255)
        pixels = list(image.getdata())
        
        # Build ASCII art string row by row
        ascii_art = []
        num_chars = len(self.characters)
        
        for y in range(height):
            row = []
            for x in range(width):
                # Get pixel brightness (0-255)
                pixel_index = y * width + x
                brightness = pixels[pixel_index]
                
                # Map brightness (0-255) to character index (0 to num_chars-1)
                # Bright pixels (high brightness) → sparse characters (high index)
                # Dark pixels (low brightness) → dense characters (low index)
                char_index = int(brightness / 255 * (num_chars - 1))
                
                # Get the character from the character set
                char = self.characters[char_index]
                row.append(char)
            
            # Add row to ASCII art with newline
            ascii_art.append(''.join(row))
        
        # Join all rows with newlines
        return '\n'.join(ascii_art)

