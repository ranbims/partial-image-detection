from PIL import Image

import os


def list_files(folder_path: str):
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def rescale_images(folder_path: str, width: int, height: int, output_folder: str):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    files = list_files(folder_path)
    for file in files:
        im = Image.open(os.path.join(folder_path, file))
        scaled_im = im.resize((width, height))
        scaled_im.save(os.path.join(output_folder, file))

if __name__ == "__main__":
    rescale_images("raw", 256, 256, "scaled")