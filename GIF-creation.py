from PIL import Image, ImageDraw, ImageFont

def create_image(size, text):
    img = Image.new('RGB', (600, 50), "pink") # size and color of background
    draw = ImageDraw.Draw(img)
    draw.text((size[0], size[1]), text, font = fnt, fill="white") #font color 
    return img

frames = []

def roll(text):
    for i in range(len(text)+1):
        new_frame = create_image((0,0), text[:i])
        frames.append(new_frame)
# <<< ========== Customize font and text below ============== >>>>
fnt = ImageFont.truetype("arial", 36)

print("""Enter your text for your GIF. 
      For ending input enter 'end' """)

text_input = ""
input_array = []
while text_input != 'end':
    text_input = input('Enter your text for GIF : ')
    input_array.append(text_input)

[roll(text) for text in input_array]

frames[0].save('my_gif.gif', format='GIF', 
               append_images=frames[1:], save_all=True, duration=80, loop=0)
