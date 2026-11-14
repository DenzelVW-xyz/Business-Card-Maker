# Import Modules
import os
import platform
import shlex
import subprocess

import qrcode
from PIL import Image, ImageFont

# Clear command
if platform.system() == "Windows":
    clear = lambda: subprocess.run("cls", check=False)
else:
    clear = lambda: subprocess.run("clear", check=False)

# Set up Directory

root_dir = os.path.abspath(os.curdir)

try:
    os.mkdir("Results")
    os.chdir("Results")
except FileExistsError:
    os.chdir("Results")

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

less_than_4 = False
while less_than_4 == False:
    user_details = input("Enter Details (Separated by spaces): ")
    details = dict(item.split("=", 1) for item in shlex.split(user_details))
    if len(details) > 4:
        print("Please keep details under 5")
    else:
        less_than_4 = True

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
def draw_text(draw, text, x, y, max_width=550, font_size=65):
    font_path = os.path.join(root_dir, "fonts", "Caudex-Bold.ttf")

    font = ImageFont.truetype(font_path, font_size)

    while draw.textlength(text, font=font) > max_width and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)

    draw.text((x, y), text, fill=(0, 0, 0), font=font, anchor="mt")


# Add Logo to the top right of the card
try:
    logo = Image.open(logo).convert("RGBA")
except FileNotFoundError:
    try:
        logo = Image.open(os.path.join(root_dir, logo)).convert("RGBA")
    except FileNotFoundError:
        print("Image you provided does not exist.")
        raise SystemExit(1)

# Resize while maintaining aspect ratio
logo.thumbnail((250, 250), Image.Resampling.LANCZOS)

if remove_background:
    print("Removing Logo Background...")
    logo = remove(logo, session=session)

# Calculate top-right position dynamically
x = card_background.width - logo.width
y = 0

# Paste logo
card_background.paste(logo, (x, y), logo)

# Save and cleanup
card_background.save("Result.png")
