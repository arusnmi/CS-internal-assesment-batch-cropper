
from PIL import Image
from autocrop import Cropper


cropper = Cropper()

def crop_image(image_path):
    image= cropper.crop(image_path)

    cropped_image = Image.fromarray(image)

    return cropped_image


