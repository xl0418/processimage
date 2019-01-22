# -*- coding: UTF-8 -*-

import os
from PIL import Image
import imageio


def analyseImage(path):
    '''
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode 
    before processing all frames.
    '''
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def processImage(path):
    '''
    Iterate the GIF, extracting each frame.
    '''
    mode = analyseImage(path)['mode']

    im = Image.open(path)

    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')

    try:
        while True:
            print("saving %s (%s) frame %d, %s %s" % (path, mode, i, im.size, im.tile))

            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.putpalette(p)

            new_frame = Image.new('RGBA', im.size)

            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert('RGBA'))
            new_frame.save('%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i), 'PNG')

            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass


def main():
    processImage('giphy.gif')

path = 'giphy.gif'

if __name__ == "__main__":
    main()

def transparent_back(img):
    img = img.convert('RGBA')
    L, H = img.size
    color_0 = img.getpixel((0,0))
    for h in range(H):
        for l in range(L):
            dot = (l,h)
            color_1 = img.getpixel(dot)
            c1,c2,c3,_ = color_1
            # print(color_1)
            if abs(c1-50)<30 and abs(c2-150)<30 and abs(c3-155)<80:
                color_1 = (0,0,0,0)
                img.putpixel(dot,color_1)
    return img



def create_gif(image_list, gif_name):
    frames = []
    for image_name in image_list:
        frames.append(imageio.imread(image_name))
    # Save them as frames into a gif
    imageio.mimsave(gif_name, frames, 'GIF', duration=0.1)


touming = []
for i in range(75):
    imagename = 'giphy-%i.png' % i
    img = Image.open(imagename)
    img = img.convert('RGBA')

    tranimg = transparent_back(img)
    tranimg = tranimg.resize((360,360))
    toumingname = 'touming%i.png' % i
    touming.append(toumingname)
    tranimg.save(toumingname)


touming = []
for i in range(75):
    toumingname = 'touming%i.png' % i
    touming.append(toumingname)



gif_name = 'touming.gif'
giftran_name = 'truetouming.gif'
create_gif(touming,gif_name)

toumingim = Image.open(gif_name)
transparency = toumingim.info['transparency']
toumingim.save(giftran_name, transparency=0)

imgfirst = Image.open('touming0.png')

images = []

for n in touming:
    frame = Image.open(n)
    frame.convert('RGBA')
    images.append(frame)

images[0].save('truetouming1.gif', save_all=True, append_images=images[1:],loop=0,duration=100)
