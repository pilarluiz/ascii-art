"""
ASCII Art Converter

Converts images to ASCII art representation.
"""

from PIL import Image
from .constants import CHAR_SETS, DEFAULT_WIDTH, DEFAULT_CHAR_SET, ASPECT_RATIO_CORRECTION


class AsciiConverter:
    """
    Converts images to ASCII art.
    """
    
    def __init__(self, width: int = DEFAULT_WIDTH, char_set: str = DEFAULT_CHAR_SET, use_color: bool = False) -> None:
        """
        Initialize the ASCII converter.
        
        Args:
            width: Width of the output ASCII art in characters
            char_set: Name of character set to use (from constants.CHAR_SETS)
            use_color: Whether to use color output (ANSI colors for terminal)
        """
        self.width = width
        self.use_color = use_color
        
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
        
        # Initialize color_data
        color_data = None
        
        # Enhance the image before capturing colors
        if self.use_color:
            from PIL import ImageEnhance
            
            # Enhance brightness and sharpness to make colors pop
            brightened_image = ImageEnhance.Brightness(image).enhance(1.2)  # 20% brighter
            sharpened_image = ImageEnhance.Sharpness(brightened_image).enhance(1.5)  # 50% sharper
            
            # Capture colors from the enhanced image
            color_data = self._capture_color_data(sharpened_image)
            
            # Boost saturation using HSV
            color_data = self._boost_saturation(color_data, multiplier=3.0)
            
            # Use the enhanced image for character mapping
            image = sharpened_image
        else:
            # Convert to grayscale for B&W image
            image = self._convert_to_grayscale(image)

        # Convert pixels to ASCII characters
        # For terminal: apply ANSI codes if color enabled
        # For image rendering: color_data will be passed separately to render_to_image
        ascii_art = self._pixels_to_ascii(image, color_data)
        
        # Store color_data for potential image rendering (even if ANSI wasn't applied)
        self._last_color_data = color_data
        
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
        resized_image = image.resize((self.width, new_height), Image.Resampling.NEAREST)
        
        return resized_image
    
    
    def _capture_color_data(self, image: Image.Image) -> list:
        """
        Capture RGB color data from image before grayscale conversion.
        
        Args:
            image: PIL Image object (RGB/RGBA)
            
        Returns:
            List of (R, G, B) tuples, one per pixel
        """
        # Ensure image is in RGB mode
        if image.mode != 'RGB':
            rgb_image = image.convert('RGB')
        else:
            rgb_image = image
        
        # Get all pixel data as a flat list of (R, G, B) tuples
        pixels = list(rgb_image.getdata())
        return pixels

        
    def _boost_saturation(self, color_data: list, multiplier: float = 1.5) -> list:
        """
        Boost saturation of RGB colors by converting to HSV, increasing S, and converting back.
        
        Args:
            color_data: List of (R, G, B) tuples
            multiplier: Saturation multiplier (1.0 = no change, 1.5 = 50% boost, 2.0 = 100% boost)
            
        Returns:
            List of (R, G, B) tuples with boosted saturation
        """
        import colorsys
        
        boosted_colors = []
        
        for r, g, b in color_data:
            # Convert RGB (0-255) to normalized RGB (0.0-1.0)
            r_norm = r / 255.0
            g_norm = g / 255.0
            b_norm = b / 255.0
            
            # Convert to HSV
            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
            
            # Boost saturation (clamp to 0.0-1.0)
            s_boosted = min(1.0, s * multiplier)
            
            # Convert back to RGB
            r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s_boosted, v)
            
            # Convert back to 0-255 range and round
            r_int = int(round(r_new * 255))
            g_int = int(round(g_new * 255))
            b_int = int(round(b_new * 255))
            
            # Clamp to valid range
            r_int = max(0, min(255, r_int))
            g_int = max(0, min(255, g_int))
            b_int = max(0, min(255, b_int))
            
            boosted_colors.append((r_int, g_int, b_int))
        
        return boosted_colors
    
    
    def _rgb_to_ansi(self, r: int, g: int, b: int) -> str:
        """
        Convert RGB values to ANSI 256-color escape code.
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            
        Returns:
            ANSI escape code string for the color
        """
        # Map RGB (0-255) to ANSI 256-color palette (216 colors from 16-231)
        # Formula: 16 + 36*R + 6*G + B where R,G,B are 0-5
        r6 = int(r / 255 * 5)
        g6 = int(g / 255 * 5)
        b6 = int(b / 255 * 5)
        color_code = 16 + 36 * r6 + 6 * g6 + b6
        return f"\033[38;5;{color_code}m"
    
    
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
    
    
    def _pixels_to_ascii(self, image: Image.Image, color_data: list = None) -> str:
        """
        Convert image pixels to ASCII characters.
        Maps brightness values (0-255) to characters in the character set.
        Optionally applies color using ANSI escape codes.
        
        Args:
            image: Grayscale PIL Image object
            color_data: Optional list of (R, G, B) tuples for color (one per pixel)
            
        Returns:
            String containing ASCII art (with ANSI color codes if color_data provided)
        """
        # Get image dimensions
        width, height = image.size
        
        # Convert to grayscale for brightness calculation (even if we have color_data)
        # This ensures we get single brightness values, not RGB tuples
        if image.mode != 'L':
            grayscale_image = image.convert('L')
        else:
            grayscale_image = image
        
        # Get all pixel data as a flat list (brightness values 0-255)
        pixels = list(grayscale_image.getdata())
        
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
                
                # Apply color if color_data is provided
                if color_data and pixel_index < len(color_data):
                    r, g, b = color_data[pixel_index]
                    ansi_color = self._rgb_to_ansi(r, g, b)
                    reset_code = "\033[0m"
                    char = f"{ansi_color}{char}{reset_code}"
                
                row.append(char)
            
            # Add row to ASCII art with newline
            ascii_art.append(''.join(row))
        
        # Join all rows with newlines
        return '\n'.join(ascii_art)
    
    
    def render_to_image(self, ascii_art: str, font_size: int = 10, output_path: str = "ascii_output.png", color_data: list = None) -> Image.Image:
        """
        Render ASCII art as an image file.
        Useful for debugging proportions without terminal rendering effects.
        Supports colored rendering if color_data is provided.
        
        Args:
            ascii_art: ASCII art string (may contain ANSI codes if color was used)
            font_size: Font size for rendering (default: 10)
            output_path: Path to save the image
            color_data: Optional list of (R, G, B) tuples for colored rendering
            
        Returns:
            PIL Image object of the rendered ASCII art
        """
        from PIL import ImageDraw, ImageFont
        import re
        
        # Strip ANSI escape codes from ASCII art string for rendering
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        clean_ascii = ansi_escape.sub('', ascii_art)
        
        # Split into lines
        lines = clean_ascii.split('\n')
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
        
        # Draw each character with its color if color_data is provided
        if color_data:
            pixel_index = 0
            char_width_px = int(char_width)
            char_height_px = int(char_height)
            
            for line_idx, line in enumerate(lines):
                x = 0
                for char in line:
                    if pixel_index < len(color_data):
                        r, g, b = color_data[pixel_index]
                        color = (r, g, b)
                    else:
                        color = 'black'  # Fallback to black if color_data is insufficient
                    
                    # Draw each character individually with its color
                    draw.text((x, line_idx * char_height_px), char, fill=color, font=font)
                    x += char_width_px
                    pixel_index += 1
        else:
            # Draw each line without color (original behavior)
            y = 0
            for line in lines:
                draw.text((0, y), line, fill='black', font=font)
                y += int(char_height)
        
        # Save the image
        img.save(output_path)
        return img

