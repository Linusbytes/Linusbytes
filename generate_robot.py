from PIL import Image, ImageDraw
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'robot.gif'
W, H, SCALE = 160, 64, 4
FRAMES = 64
frames = []


def robot(draw, x, y, step, face_right=True):
    # All shapes are on a low-resolution canvas to preserve sharp pixel art.
    metal = '#64748b'
    dark = '#263445'
    light = '#a5b4c4'
    blue = '#72d7f4'
    def rect(a,b,c,d,color):
        if not face_right:
            a,c = -c,-a
        draw.rectangle((int(x+a),int(y+b),int(x+c),int(y+d)),fill=color)

    bob = int(round(abs(math.sin(step)) * 2))
    # Back leg first; phase-shifted motion creates a clear walk cycle.
    rear = int(round(math.sin(step + math.pi) * 4))
    front = int(round(math.sin(step) * 4))
    rect(-9, 15+bob, -4, 24+bob, dark)
    rect(-10+rear, 24+bob, -5+rear, 32+bob, metal)
    rect(-12+rear, 31+bob, -4+rear, 33+bob, dark)
    rect(4, 15+bob, 9, 24+bob, dark)
    rect(4+front, 24+bob, 9+front, 32+bob, light)
    rect(3+front, 31+bob, 12+front, 33+bob, dark)
    # Torso, side joint, neck.
    rect(-13, -4+bob, 12, 17+bob, dark)
    rect(-11, -3+bob, 10, 14+bob, metal)
    rect(-7, 0+bob, 7, 9+bob, light)
    rect(-5, 3+bob, 5, 6+bob, dark)
    rect(-3, 4+bob, 2, 5+bob, blue)
    rect(11, 3+bob, 15, 11+bob, dark)
    rect(12, 4+bob, 14, 9+bob, light)
    rect(-3, -15+bob, 3, -5+bob, dark)
    rect(-2, -14+bob, 2, -7+bob, metal)
    # Wide sensor head with distinctive two camera eyes.
    rect(-21, -27+bob, 20, -15+bob, dark)
    rect(-19, -26+bob, 18, -18+bob, metal)
    rect(-15, -24+bob, -9, -19+bob, '#101b28')
    rect(-13, -23+bob, -11, -21+bob, blue)
    rect(5, -24+bob, 11, -19+bob, '#101b28')
    rect(7, -23+bob, 9, -21+bob, blue)
    rect(19, -23+bob, 23, -21+bob, light)


for i in range(FRAMES):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    half = FRAMES // 2
    if i < half:
        progress = i / (half - 1)
        x = 24 + int(progress * (W - 48))
        facing = True
    else:
        progress = (i - half) / (half - 1)
        x = W - 24 - int(progress * (W - 48))
        facing = False
    robot(d, x, 29, i * math.pi / 4, facing)
    # Upscale using nearest-neighbour interpolation for crisp pixel edges.
    frames.append(im.resize((W * SCALE, H * SCALE), Image.Resampling.NEAREST))

# GIF transparency is encoded using a dedicated palette index.
converted = []
for im in frames:
    rgb = Image.new('RGB', im.size, (255, 0, 255))
    rgb.paste(im, mask=im.getchannel('A'))
    p = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = p.getpalette()
    # Reserve palette index 255 for transparent pixels.
    palette[255 * 3:255 * 3 + 3] = [255, 0, 255]
    p.putpalette(palette)
    transparent = Image.new('L', im.size, 255)
    p.paste(255, mask=im.getchannel('A').point(lambda a: 255 if a == 0 else 0))
    p.info['transparency'] = 255
    converted.append(p)

converted[0].save(OUT, save_all=True, append_images=converted[1:], duration=65, loop=0,
                  disposal=2, transparency=255, optimize=False)
print(f'Created {OUT}')
