from PIL import Image


def fix_transparency(input_path, output_path):
    img = Image.open(input_path)

    img = img.convert("RGBA")

    # Get the alpha channel
    alpha = img.split()[3]

    # Create a new image with a transparent background
    new_img = Image.new("RGBA", img.size, (0, 0, 0, 0))

    # Paste the original image, using the alpha channel as a mask
    new_img.paste(img, (0, 0), alpha)

    new_img.save(output_path, "PNG")


if __name__ == "__main__":
    input_file = "jslib_minimalist_logo_no_background_cut_resized.png"
    output_file = "logo_no_bg_resized_fixed.png"

    fix_transparency(input_file, output_file)
    print(f"Fixed transparency in {input_file} and saved as {output_file}")
