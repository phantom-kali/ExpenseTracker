from PIL import Image

# Open the PNG image
png_image = Image.open('image.png')

# Convert and save as ICO
png_image.save('favicon.ico', format='ICO')
