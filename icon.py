import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_reddit_icon(size=512, output_path=None):
    """
    Create a Reddit-themed icon for the Screddit application
    
    Args:
        size: Size of the icon in pixels (default: 512)
        output_path: Path to save the icon (default: app_icon.ico in current directory)
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")

    # Reddit colors
    reddit_orange = (255, 69, 0)  # #FF4500
    reddit_blue = (0, 121, 211)   # #0079D3
    white = (255, 255, 255)
    dark_gray = (26, 26, 27)      # #1A1A1B

    # Create a base image with padding
    padding = int(size * 0.1)
    img_size = size + 2 * padding
    img = Image.new('RGB', (img_size, img_size), dark_gray)
    draw = ImageDraw.Draw(img)
    
    # Create the main circular background
    circle_center = (img_size // 2, img_size // 2)
    circle_radius = size // 2
    
    # Draw circle with Reddit orange
    draw.ellipse(
        (
            circle_center[0] - circle_radius,
            circle_center[1] - circle_radius,
            circle_center[0] + circle_radius,
            circle_center[1] + circle_radius
        ),
        fill=reddit_orange
    )    # Create a more Reddit-styled "S" character
    # Reddit uses a custom font called "Reddit Sans" but we'll mimic it with our drawing
    
    # Draw the "S" character using custom shapes to match Reddit's style
    # The "S" in Reddit's style is slightly rounded and has variable thickness
    
    # Calculate the size for our custom "S"
    s_width = int(size * 0.45)
    s_height = int(size * 0.65)
    s_thickness = int(size * 0.12)  # Thickness of the S curves
    
    # Calculate the position (centered in the circle)
    s_left = circle_center[0] - s_width // 2
    s_top = circle_center[1] - s_height // 2
    
    # Define the curve points for an "S" shape
    # Top curve
    top_curve_center = (s_left + s_width // 2, s_top + s_thickness // 2)
    top_curve_radius = s_width // 2
    
    # Bottom curve
    bottom_curve_center = (s_left + s_width // 2, s_top + s_height - s_thickness // 2)
    bottom_curve_radius = s_width // 2
    
    # Draw the top half of the "S" (filled semicircle)
    draw.pieslice(
        (
            top_curve_center[0] - top_curve_radius,
            top_curve_center[1] - top_curve_radius,
            top_curve_center[0] + top_curve_radius,
            top_curve_center[1] + top_curve_radius
        ),
        180, 0, fill=white
    )
    
    # Draw the bottom half of the "S" (filled semicircle)
    draw.pieslice(
        (
            bottom_curve_center[0] - bottom_curve_radius,
            bottom_curve_center[1] - bottom_curve_radius,
            bottom_curve_center[0] + bottom_curve_radius,
            bottom_curve_center[1] + bottom_curve_radius
        ),
        0, 180, fill=white
    )
    
    # Draw the middle connecting part of the "S"
    middle_rect = [
        s_left + s_width - s_thickness,  # Right edge of the top curve
        s_top + s_thickness // 2,        # Bottom of top curve
        s_left + s_width,                # Right edge of the S
        s_top + s_height - s_thickness // 2  # Top of bottom curve
    ]
    draw.rectangle(middle_rect, fill=white)
    
    # Draw the left edge of the "S"
    left_rect = [
        s_left,                          # Left edge of the S
        s_top + s_thickness // 2,        # Bottom of top curve
        s_left + s_thickness,            # Left edge + thickness
        s_top + s_height - s_thickness // 2  # Top of bottom curve
    ]
    draw.rectangle(left_rect, fill=white)
    
    # Create a small blue pill shape at the bottom for the "reddit" theme
    pill_width = int(size * 0.5)
    pill_height = int(size * 0.15)
    pill_radius = pill_height // 2
    pill_top = circle_center[1] + int(size * 0.15)
    
    # Draw the pill shape
    pill_left = circle_center[0] - pill_width // 2
    pill_rect = [
        pill_left, 
        pill_top, 
        pill_left + pill_width, 
        pill_top + pill_height
    ]
    
    # Draw rounded rectangle for the pill
    draw.rectangle(pill_rect, fill=reddit_blue)
    
    # Round the left edge
    left_circle_center = (pill_left + pill_radius, pill_top + pill_radius)
    left_circle_bbox = [
        left_circle_center[0] - pill_radius,
        left_circle_center[1] - pill_radius,
        left_circle_center[0] + pill_radius,
        left_circle_center[1] + pill_radius
    ]
    draw.ellipse(left_circle_bbox, fill=reddit_blue)
    
    # Round the right edge
    right_circle_center = (pill_left + pill_width - pill_radius, pill_top + pill_radius)
    right_circle_bbox = [
        right_circle_center[0] - pill_radius,
        right_circle_center[1] - pill_radius,
        right_circle_center[0] + pill_radius,
        right_circle_center[1] + pill_radius
    ]
    draw.ellipse(right_circle_bbox, fill=reddit_blue)
    
    # Apply slight blur to make it look more polished
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Crop to remove padding for the final icon
    crop_box = (padding, padding, size + padding, size + padding)
    img = img.crop(crop_box)
    
    # Resize to standard icon sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []
    
    for icon_size in icon_sizes:
        icons.append(img.resize(icon_size, Image.Resampling.LANCZOS))
      # Save as ICO if output path is provided
    if output_path:
        img.save(output_path, format="ICO", sizes=icon_sizes)
        print(f"Icon saved to {output_path}")
        return output_path
    else:
        return img

def create_favicon():
    """Create a smaller favicon version"""
    output_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
    create_reddit_icon(size=256, output_path=output_path)
    print(f"Favicon saved to {output_path}")

def create_png_versions():
    """Create PNG versions of the icon at different sizes"""
    output_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(output_dir, exist_ok=True)
    
    sizes = [16, 32, 48, 64, 128, 256, 512]
    for size in sizes:
        img_path = os.path.join(output_dir, f"screddit_icon_{size}.png")
        
        # Create a new icon of this specific size
        temp_path = os.path.join(os.path.dirname(__file__), f"temp_{size}.ico")
        create_reddit_icon(size=size, output_path=temp_path)
        
        # Open the icon and convert to PNG
        img = Image.open(temp_path)
        img.save(img_path, format="PNG")
        
        # Remove temp file
        os.remove(temp_path)
        
        print(f"PNG icon ({size}px) saved to {img_path}")

if __name__ == "__main__":
    # Create the main icon
    create_reddit_icon()
    
    # Create additional versions
    create_favicon()
    create_png_versions()