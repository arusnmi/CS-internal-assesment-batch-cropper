
from PIL import Image
from autocrop import Cropper




def crop_image(image_path, wgth, hght):
    cropper = Cropper(width=wgth, height=hght)
    image= cropper.crop(image_path)

    cropped_image = Image.fromarray(image)

    return cropped_image


