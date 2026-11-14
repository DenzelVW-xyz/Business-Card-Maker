# Import Modules
import os
import shlex

import qrcode
from PIL import Image, ImageDraw, ImageFont


# Clear command
def clear():
    os.system("cls" if os.name == "nt" else "clear")


# Set up Directory

root_dir = os.path.dirname(os.path.abspath(__file__))

results_dir = os.path.join(root_dir, "Results")
os.makedirs(results_dir, exist_ok=True)

# Data User inputs
qrcode_data = input("Data for QRcode: ")
card_title = input("Title of the card: ")
logo = input("Path to your logo: ")
remove_background = (
    input("Would you like to remove logo background?\n(Y/N): ").strip().upper() == "Y"
)

# User Adds Details
clear()
print("Write each detail in this format (Max 4):\n'Phone Number:'='Example'")

while True:
    user_details = input("Enter Details (Separated by spaces): ")

    try:
        details = dict(item.split("=", 1) for item in shlex.split(user_details))
    except ValueError:
        print("Invalid format! Use key=value.")
        continue

    if len(details) > 4:
        print("Please keep details under 5.")
    else:
        break

# Prepare Background removal model.
if remove_background == True:
    print("Importing rembg module...", flush=True)
    from rembg import new_session, remove

    print("Preparing AI model...", flush=True)
    session = new_session("u2net")
    print("AI model ready!")


# Function that creates the qrcode and saves it as an image
def create_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )

    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="beige")
    return img


# Create an the background, add the qr_image.
card_background = Image.new("RGBA", (1050, 600), (245, 245, 220))
qr_image = create_qr_code(qrcode_data)
qr_image = qr_image.resize((250, 250), Image.Resampling.NEAREST)
card_background.paste(qr_image, (0, 0))  # Add qr_image


# Create a title and a dynamically scale to a textbox
draw = ImageDraw.Draw(card_background)


def draw_text(draw, text, x, y, max_width=550, font_size=65):
    font_path = os.path.join(root_dir, "fonts", "Caudex-Bold.ttf")

    font = ImageFont.truetype(font_path, font_size)

    while draw.textlength(text, font=font) > max_width and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)

    draw.text((x, y), text, fill=(0, 0, 0), font=font, anchor="mt")


draw_text(draw, card_title, x=525, y=10)


# Add Logo to the top right of the card
try:
    logo = Image.open(logo).convert("RGBA")
except FileNotFoundError:
    try:
        logo = Image.open(os.path.join(root_dir, logo)).convert("RGBA")
    except FileNotFoundError:
        print("Image you provided does not exist.")
        raise SystemExit(1)

if remove_background:
    print("Removing Logo Background...")
    logo = remove(logo, session=session)

# Resize while maintaining aspect ratio
logo.thumbnail((250, 250), Image.Resampling.LANCZOS)

# Calculate top-right position dynamically
x = card_background.width - logo.width
y = 0

# Paste logo
card_background.paste(logo, (x, y), logo)

# Add Details To Business card
for index, (key, value) in enumerate(details.items()):
    draw_text(
        draw, f"{key}: {value}", x=525, y=270 + index * 65, max_width=900, font_size=40
    )

# Save and cleanup
card_background.save(os.path.join(results_dir, "Result.png"))
