"""
ASCII Art Converter - Command Line Interface

Convert images to ASCII art from the command line.
"""

import argparse
import sys
from src.converter import AsciiConverter
from src.constants import CHAR_SETS, DEFAULT_WIDTH, DEFAULT_CHAR_SET


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert images, GIFs, and videos to ASCII art",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python main.py samples/image.jpg
  python main.py samples/image.jpg --width 150
  python main.py samples/image.jpg --char-set simple
  python main.py samples/image.jpg --width 80 --char-set blocks

Available character sets: {', '.join(CHAR_SETS.keys())}
        """
    )
    
    parser.add_argument(
        "image_path",
        help="Path to the image file to convert"
    )
    
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"Width of ASCII art in characters (default: {DEFAULT_WIDTH})"
    )
    
    parser.add_argument(
        "--char-set",
        choices=list(CHAR_SETS.keys()),
        default=DEFAULT_CHAR_SET,
        help=f"Character set to use (default: {DEFAULT_CHAR_SET})"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (if not specified, prints to terminal)"
    )
    
    args = parser.parse_args()
    
    # Create converter with specified options
    try:
        converter = AsciiConverter(width=args.width, char_set=args.char_set)
        print(f"Converting {args.image_path}...")
        print(f"Width: {args.width} characters, Character set: {args.char_set}")
        print("-" * 50)
        
        # Convert the image
        ascii_art = converter.convert_image(args.image_path)
        
        # Output result
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(ascii_art)
            print(f"\nASCII art saved to: {args.output}")
        else:
            print(ascii_art)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

