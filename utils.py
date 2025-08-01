import moviepy.editor as mp
import os
from PIL import Image
from colorama import Fore

def validate_media(path, media_type='image'):
    try:
        if media_type == 'image':
            with Image.open(path) as img:
                return img.format in ['GIF', 'PNG', 'JPEG', 'JPG']

        elif media_type == 'video':
            video = mp.VideoFileClip(path)
            valid = video.duration > 0
            video.close()

            return valid

        elif media_type == 'audio':
            audio = mp.AudioFileClip(path)
            valid = audio.duration > 0
            audio.close()

            return valid

        return False
    except Exception as e:
        print(f'{Fore.RED}Validation failed for {path} ({media_type}): {e} ❌{Fore.RESET}')

        return False
