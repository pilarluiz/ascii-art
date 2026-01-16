"""
ASCII Art Converter

Converts images to ASCII art representation.
"""

from PIL import Image
import sys
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
        original_size = image.size
        
        # Resize the image
        image = self._resize_image(image)
        resized_size = image.size
        
        # TODO: Remove debug
        print(f"Debug: Original size: {original_size}, Resized to: {resized_size}, "
              f"Compression: {resized_size[1]/original_size[1]*100:.1f}% of original height", 
              file=sys.stderr)
        
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
        
        # Calculate uncorrected height (true aspect ratio)
        uncorrected_height = int(self.width * aspect_ratio)
        
        # Calculate new height with correction for terminal character aspect ratio
        # Terminal characters are taller than wide, so we reduce height to compensate
        new_height = int(self.width * aspect_ratio * self.aspect_ratio_correction)
        
        # Prevent excessive compression - ensure we keep at least 40% of original height
        # This prevents important details (like fins) from being lost
        min_height = max(1, int(uncorrected_height * 0.4))
        if new_height < min_height:
            new_height = min_height
        
        # Also ensure we don't compress too much - if the compression ratio is extreme,
        # it means the aspect ratio correction might be wrong for this image
        compression_ratio = new_height / uncorrected_height if uncorrected_height > 0 else 1.0
        if compression_ratio < 0.3:  # If we're compressing more than 70%, something's wrong
            # Use a more conservative correction
            new_height = int(uncorrected_height * 0.5)  # At least keep 50% of height
        
        # Resize the image
        resized_image = image.resize((self.width, new_height), Image.Resampling.LANCZOS)
        
        return resized_image
    
    
    def _convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """
        Convert image to grayscale with histogram equalization for better contrast.
        
        Args:
            image: PIL Image object
            
        Returns:
            Grayscale PIL Image object with enhanced contrast
        """
        # Convert to grayscale mode ('L' = Luminance)
        grayscale_image = image.convert('L')
        
        # Apply histogram equalization to improve local contrast
        # This spreads out brightness values and preserves relative differences
        from PIL import ImageOps
        equalized_image = ImageOps.equalize(grayscale_image)
        
        return equalized_image
    
    
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
        
        # Normalize brightness range for better contrast
        # Use actual min/max from image instead of 0-255 range
        min_brightness = min(pixels)
        max_brightness = max(pixels)
        brightness_range = max_brightness - min_brightness
        
        # Avoid division by zero
        if brightness_range == 0:
            brightness_range = 1
        
        # Build ASCII art string row by row
        ascii_art = []
        num_chars = len(self.characters)
        
        for y in range(height):
            row = []
            for x in range(width):
                # Get pixel brightness (0-255)
                pixel_index = y * width + x
                brightness = pixels[pixel_index]
                
                # Normalize brightness to 0-1 range using actual image min/max
                normalized = (brightness - min_brightness) / brightness_range
                
                # Map normalized brightness to character index (0 to num_chars-1)
                # Bright pixels (high brightness) → sparse characters (high index)
                # Dark pixels (low brightness) → dense characters (low index)
                char_index = int(normalized * (num_chars - 1))
                
                # Get the character from the character set
                char = self.characters[char_index]
                row.append(char)
            
            # Add row to ASCII art with newline
            ascii_art.append(''.join(row))
        
        # Join all rows with newlines
        return '\n'.join(ascii_art)
    
    
    def render_to_image(self, ascii_art: str, font_size: int = 10, output_path: str = "ascii_output.png") -> Image.Image:
        """
        Render ASCII art as an image file.
        Useful for debugging proportions without terminal rendering effects.
        
        Args:
            ascii_art: ASCII art string
            font_size: Font size for rendering (default: 10)
            output_path: Path to save the image
            
        Returns:
            PIL Image object of the rendered ASCII art
        """
        from PIL import ImageDraw, ImageFont
        
        # Split into lines
        lines = ascii_art.split('\n')
        if not lines:
            return None
        
        # Estimate dimensions (monospace font)
        # Characters are typically wider than tall in images
        char_width = font_size * 0.6  # Approximate character width
        char_height = font_size * 1.2  # Approximate line height
        
        width = int(max(len(line) for line in lines) * char_width)
        height = int(len(lines) * char_height)
        
        # Create image with white background
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a monospace font, fall back to default if not available
        try:
            # Try system monospace font
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Draw each line
        y = 0
        for line in lines:
            draw.text((0, y), line, fill='black', font=font)
            y += int(char_height)
        
        # Save the image
        img.save(output_path)
        return img

