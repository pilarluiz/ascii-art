"""
ASCII Art Converter - Command Line Interface

Convert images to ASCII art from the command line.
"""

import argparse
import sys
from PIL import Image
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
    
    parser.add_argument(
        "--render-image",
        action="store_true",
        help="Render ASCII art as an image file"
    )
    
    parser.add_argument(
        "--color",
        action="store_true",
        help="Enable color output (ANSI colors for terminal)"
    )
    
    args = parser.parse_args()
    
    # Auto-detect image width if not specified (use default for terminal, auto for images)
    width = args.width
    if args.width == DEFAULT_WIDTH and args.render_image:
        # For image rendering, auto-detect width from image
        from PIL import Image
        try:
            with Image.open(args.image_path) as img:
                # Use a percentage of image width, capped at reasonable max
                # This gives good detail without being excessive
                auto_width = min(int(img.width * 0.3), 500)  # 30% of image width, max 500
                width = auto_width
                print(f"Auto-detected width from image: {img.width}px → {width} characters")
        except Exception:
            # Fall back to default if we can't detect
            width = DEFAULT_WIDTH
    
    # Create converter with specified options
    try:
        converter = AsciiConverter(width=width, char_set=args.char_set, use_color=args.color)
        print(f"Converting {args.image_path}...")
        print(f"Width: {width} characters, Character set: {args.char_set}")
        
        # Check if input is an animated GIF
        is_animated_gif = converter.is_animated_gif(args.image_path)
        
        if is_animated_gif:
            # Count frames
            with Image.open(args.image_path) as img:
                frame_count = 0
                try:
                    while True:
                        frame_count += 1
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass
            print(f"Detected animated GIF with {frame_count} frames")
        else:
            print("-" * 50)
        
        # Convert the image or GIF
        if is_animated_gif:
            # Process all frames of the GIF
            frames = converter.convert_gif(args.image_path)
            print(f"Processed {len(frames)} frames")
            print("-" * 50)
            
            # Output result for GIF
            if args.render_image:
                # Render as animated GIF
                output_img_path = args.output or "ascii_output.gif"
                
                # Ensure output path has .gif extension
                if not output_img_path.endswith('.gif'):
                    output_img_path = output_img_path.rsplit('.', 1)[0] + '.gif'
                
                converter.render_gif_to_images(frames, output_path=output_img_path)
                print(f"\nAnimated GIF rendered: {output_img_path} ({len(frames)} frames, width: {width} chars)")
            elif args.output:
                # Save frames as separate text files
                base_name = args.output.rsplit('.', 1)[0] if '.' in args.output else args.output
                for frame in frames:
                    frame_filename = f"{base_name}_frame_{frame['frame_number']:04d}.txt"
                    with open(frame_filename, 'w', encoding='utf-8') as f:
                        f.write(frame['ascii_art'])
                print(f"\nASCII art saved to {len(frames)} files: {base_name}_frame_*.txt")
            else:
                # Print first frame to terminal
                print("\n" + frames[0]['ascii_art'])
                if len(frames) > 1:
                    print(f"\n(Showing first frame only. GIF has {len(frames)} total frames)")
        else:
            # Process regular image
            ascii_art = converter.convert_image(args.image_path)
            
            # Output result
            if args.render_image:
                # Render as image
                output_img_path = args.output or "ascii_output.png"
                
                # Pass color_data if color was enabled
                color_data = getattr(converter, '_last_color_data', None) if args.color else None
                
                # Use the width (auto-detected or specified)
                converter.render_to_image(ascii_art, output_path=output_img_path, color_data=color_data)
                print(f"\nASCII art rendered as image: {output_img_path} (width: {width} chars)")
            elif args.output:
                # Save as text file
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(ascii_art)
                print(f"\nASCII art saved to: {args.output}")
            else:
                # Print to terminal
                print("\n" + ascii_art)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

