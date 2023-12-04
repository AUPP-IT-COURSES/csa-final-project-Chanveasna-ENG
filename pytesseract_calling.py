"""
Code that calls pytesseract to read text from images
"""
import pytesseract


def convert_img2text(image):
    result = pytesseract.image_to_string(image)
    return result


def img2boxes(image):
    result = pytesseract.image_to_boxes(image)
    return result


def img2data(image):
    result = pytesseract.image_to_data(image)
    return result
