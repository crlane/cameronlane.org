import os
import shutil


def copy_images_to_build(image_dir, build_dir):
    if os.path.exists(image_dir) and os.path.isdir(image_dir):
        shutil.copytree(image_dir, build_dir)


def resize_images():
    pass
