import os
from PIL import Image
from django.conf import settings


def resize_image(image_path: str, resize_to: tuple = (500,500), resize_to_width: int = None):
    """Convert image to bytes"""
    try:
        with Image.open(image_path) as img:
            if resize_to_width:
                aspect_ratio = img.size[1] / img.size[0]
                img = img.resize((resize_to_width, int(resize_to_width*aspect_ratio)))
            elif resize_to:
                img = img.resize(resize_to)
            img.save(image_path)
            return (0, f"Image ({image_path}) resized and saved successfully")
    except Exception as e:
        return (1, e)

def delete_image(image_path: str):
    try:
        os.remove(image_path)
        return (0, f"Old profile image ({image_path}) has been removed!")
    except Exception as e:
        return (1, e)

def delete_model_image(caller: object, model: object, defaultImagePath: str):
    try:
        old = model.objects.get(id=caller.id)
        default_image_path = os.path.join(settings.MEDIA_ROOT, defaultImagePath)
        if old.image.path != default_image_path and old.image.path != caller.image.path:
            delete_image(old.image.path)
    except: pass