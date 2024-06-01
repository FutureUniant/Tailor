from PIL import Image, ImageChops


def compare_images(image1_path, image2_path):
    """

    :param image1_path:
    :param image2_path:
    :return:
            0  : image1 and image2 are normal, but different
            1  : image1 and image2 are normal, and same
            -1 : image1 is damaged
            -2 : image2 is damaged
            -3 : image1 and image2 are all damaged
    """
    damaged_flag = 0
    try:
        image1 = Image.open(image1_path)
    except:
        damaged_flag -= 1
    try:
        image2 = Image.open(image2_path)
    except:
        damaged_flag -= 2
    if damaged_flag < 0:
        return damaged_flag

    diff = ImageChops.difference(image1, image2)
    if diff.getbbox() is None:
        return 1
    else:
        return 0
