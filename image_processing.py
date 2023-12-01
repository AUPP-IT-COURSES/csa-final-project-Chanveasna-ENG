"""
Class and functions for image processing and transformation
"""
import PIL.ImageTk
import PIL.ImageFilter
import PIL.Image
import PIL.ImageTransform
import cv2
import numpy as np


def convert_to_BW_pixels(image, buckets=100):
    pixels = list(image.getdata())
    return [pixel_value // buckets if pixel_value // buckets == 0 else 255 for pixel_value in pixels]


def convert_to_black_and_white(image, buckets=100, radius=0.):
    width, height = image.size
    image = image.filter(PIL.ImageFilter.GaussianBlur(radius=radius))
    bw_image = PIL.Image.new(mode="L", size=(width, height), color="white")
    bw_image.putdata(convert_to_BW_pixels(image.convert("L"), buckets))
    return bw_image


def resize(image, max_width_or_height):
    width, height = image.size
    ratio = max(width, height) / max_width_or_height
    new_width, new_height = width / ratio, height / ratio

    # if height > width:
    #     new_height = new_height
    #     new_width = width * new_height / height
    # elif width > height:
    #     new_width = new_width
    #     new_height = height * new_width / width
    # else:
    #     new_width = new_width
    #     new_height = new_height

    return image.resize((round(new_width), round(new_height)), PIL.Image.LANCZOS)


def transform_image(image, point1, point2, point3, point4):
    # image.transform((image.width, image.height), PIL.Image.QUAD, (point1, point2, point3, point4))
    imagez = resize(image, 850)
    image = np.array(image)
    pts1 = np.float32([point1, point2, point3, point4]) # type: ignore
    pts2 = np.float32([[0, 0], [imagez.height, 0], [0, imagez.width], [imagez.height, imagez.width]]) # type: ignore
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    image = cv2.warpPerspective(image, matrix, (850, 850))
    image = PIL.Image.fromarray(image)
    return image
    # imagez.show()
    # image.show()

# transform_image(PIL.Image.open("image/test.jpg"), (100, 100), (500, 100), (100, 200), (500, 200))