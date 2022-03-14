import glob
from PIL import Image

file_index = 0
for filename in glob.glob('raw_tracks/*.png'):
    im = Image.open(filename)
    pix = im.convert("RGB")
    save_str = ""
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            save_str += "0" if pix.getpixel((x, y))[0] + pix.getpixel((x, y))[1] + pix.getpixel((x, y))[2] == 0 else "1"
            save_str += ","
    
    with open(f"ready_tracks/{file_index}.track", "w") as fp:
        fp.write(save_str)
    file_index += 1
            

