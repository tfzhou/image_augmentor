from skimage import transform
import re
import math

PREFIX = 'rot'
REGEX = re.compile(r"^" + PREFIX + "_(?P<angle>-?[0-9]+)")

def rotatedRectWithMaxArea(w, h, angle):
    """
    Given a rectangle of size wxh that has been rotated by 'angle' (in
    radians), computes the width and height of the largest possible
    axis-aligned rectangle (maximal area) within the rotated rectangle.
    """
    if w <= 0 or h <= 0:
        return 0,0

    width_is_longer = w >= h
    side_long, side_short = (w,h) if width_is_longer else (h,w)

    # since the solutions for angle, -angle and 180-angle are all the same,
    # if suffices to look at the first quadrant and the absolute values of sin,cos:
    sin_a, cos_a = abs(math.sin(angle)), abs(math.cos(angle))
    if side_short <= 2.*sin_a*cos_a*side_long:
        # half constrained case: two crop corners touch the longer side,
        # the other two corners are on the mid-line parallel to the longer line
        x = 0.5*side_short
        wr,hr = (x/sin_a,x/cos_a) if width_is_longer else (x/cos_a,x/sin_a)
    else:
        # fully constrained case: crop touches all 4 sides
        cos_2a = cos_a*cos_a - sin_a*sin_a
        wr,hr = (w*cos_a - h*sin_a)/cos_2a, (h*cos_a - w*sin_a)/cos_2a

    return wr,hr

def crop_around_center(img, w, h):
    img_size = (img.shape[1], img.shape[0])
    img_center = (int(img_size[0]*0.5), int(img_size[1]*0.5))

    if w > img_size[0]:
        w = img_size[0]
    if h > img_size[1]:
        h = img_size[1]

    x1 = int(img_center[0] - w * 0.5)
    x2 = int(img_center[0] + w * 0.5)
    y1 = int(img_center[1] - h * 0.5)
    y2 = int(img_center[1] + h * 0.5)

    return img[y1:y2, x1:x2]


class Rotate:
    def __init__(self, angle):
        self.angle = angle
        self.code = PREFIX + str(angle)

    def process(self, img):
        img = transform.rotate(img, -self.angle)

        wr, hr = rotatedRectWithMaxArea(img.shape[0], img.shape[1], -self.angle)
        return crop_around_center(img, wr, hr)

    @staticmethod
    def match_code(code):
        match = REGEX.match(code)
        if match:
            d = match.groupdict()
            return Rotate(int(d['angle']))
