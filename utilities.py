from typing import Tuple
from PIL import Image

import os
import random
import shutil
import uuid


def list_files(folder_path: str):
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def task_rescale_images(folder_path: str, width: int, height: int, output_folder: str):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    files = list_files(folder_path)
    for file in files:
        im = Image.open(os.path.join(folder_path, file))
        scaled_im = im.resize((width, height))
        scaled_im.save(os.path.join(output_folder, file))

def check_crop_valid(img: Image) -> bool:
    img.load()
    pre_pixel: Tuple = None
    for i in range(10):
        pixel = img.getpixel((random.randint(0, img.width - 1), random.randint(0, img.height - 1)))
        if (pre_pixel == None):
            pre_pixel = pixel
        if (pixel != pre_pixel):
            return True
    return False


def make_crop(file_path: str, output_folder: str, count: int):
    min_crop_size = 50
    print("Handling {}...".format(file_path))
    im = Image.open(file_path)
    file_name = os.path.basename(file_path)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    file_croped_folder = os.path.join(output_folder, file_name)
    if not os.path.exists(file_croped_folder):
        os.mkdir(file_croped_folder)
    for i in range(count):
        get_valid_crop = False
        while not get_valid_crop:
            p1 = (random.randint(0, im.width - min_crop_size), random.randint(0, im.height - min_crop_size))
            p2 = (random.randint(p1[0] + min_crop_size, im.width), random.randint(p1[1] + min_crop_size, im.height))
            croped_im: Image = im.crop((min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1])))
            if (check_crop_valid(croped_im)):
                get_valid_crop = True
                croped_im.save(os.path.join(file_croped_folder, "{}.png".format(uuid.uuid1())), format="png")

def task_make_crops(folder_path: str, scaled_width: int, scaled_height: int, output_folder: str):
    files = list_files(folder_path)
    for file in files:
        make_crop(os.path.join(folder_path, file), output_folder, 100)

def read_file_tree(raw_image_folder: str, croped_image_folder: str):
    images = list_files(raw_image_folder)
    image_dict = {}
    for image in images:
        crop_set = [os.path.join(croped_image_folder, image, croped) for croped in list_files(os.path.join(croped_image_folder, image))]
        image_dict[os.path.join(raw_image_folder, image)] = crop_set
    return image_dict

def save_composed_image(file1: str, file2: str, output_path: str):
    img = Image.open(file1)
    composed_image = Image.new('RGB', (512, 256))
    composed_image.paste(img.resize((256, 256)), (0, 0, 256, 256), mask=0)
    croped_image = Image.open(file2)
    composed_image.paste(croped_image.resize((256, 256)), (256, 0, 512, 256), mask=0)
    composed_image.save(os.path.join(output_path, "{}.png".format(uuid.uuid1())), format="png")

def task_generate_data_set(raw_image_folder: str, croped_image_folder: str, output_folder: str):
    images = read_file_tree(raw_image_folder, croped_image_folder)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    positive_path = os.path.join(output_folder, "positive")
    if not os.path.exists(positive_path):
        os.mkdir(positive_path)
    negative_path = os.path.join(output_folder, "negative")
    if not os.path.exists(negative_path):
        os.mkdir(negative_path)

    for file in images.keys():
        # generate positive
        for croped_file in images[file]:
            save_composed_image(file, croped_file, positive_path)
        
        # generate negative
        for file_oth in images.keys():
            if (file_oth != file):
                croped_files = images[file_oth]
                # randomly select 5 images
                size = len(croped_files)
                index = random.randint(0, size - 1)
                for i in range(5):
                    croped_file = croped_files[(index + i) % size]
                    save_composed_image(file, croped_file, negative_path)

def clean():
    if (os.path.exists("scaled")):
        shutil.rmtree("scaled")
    if (os.path.exists("crops")):
        shutil.rmtree("crops")

if __name__ == "__main__":
    #read_file_tree("raw", "crops")
    task_generate_data_set("raw", "crops", "generated_dataset")
    #clean()
    #task_make_crops("raw", 256, 256, "crops")
    # rescale_images("raw", 256, 256, "scaled")