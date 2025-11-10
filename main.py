import moviepy.config as mp_config
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import numpy as np
import os
import re
import random
from PIL import Image, ImageFilter, ImageEnhance
from datetime import datetime
from pathlib import Path
from colorama import init, Fore
from config import VersusConfig, SlideshowConfig
from clips import CharacterClips
from effects import VideoEffects
from text import TextGenerator
from utils import validate_media

init(autoreset=True)


def configure_imagemagick():
    imagemagick_path = r'C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe'
   
    if os.path.exists(imagemagick_path):
        mp_config.IMAGEMAGICK_BINARY = imagemagick_path
        
        print(f'{Fore.GREEN}ImageMagick configured successfully at {imagemagick_path} ✅{Fore.RESET}')
    
    else:
        print(f'{Fore.RED}ImageMagick not found at {imagemagick_path} ❌{Fore.RESET}')
        print(f'{Fore.YELLOW}Falling back to default ImageMagick configuration{Fore.RESET}')

def generate_1v1_comparison(config=VersusConfig):
    print(f'{Fore.CYAN}Starting 1v1 comparison video generation for {config.CHARACTER1_DATA["name"]} vs {config.CHARACTER2_DATA["name"]} 🎬{Fore.RESET}')
    
    start_time = datetime.now()

    clips = []

    script_dir = Path(__file__).parent

    char1_files = {k: str(script_dir / v) for k, v in config.CHARACTER1_DATA['files'].items()}
    char2_files = {k: str(script_dir / v) for k, v in config.CHARACTER2_DATA['files'].items()}
    char1_name = config.CHARACTER1_DATA['name']
    char2_name = config.CHARACTER2_DATA['name']
    
    intro_clip = CharacterClips.create_character_intro_clip(
        config,
        char1_files['intro'],
        char2_files['intro'],
        char1_name,
        char2_name,
        config.CHARACTER1_DATA['custom_text'],
        config.CHARACTER2_DATA['custom_text'],
        0,
        config.INTRO_DURATION
    )

    clips.append(intro_clip)

    score1, score2 = 0, 0

    current_time = config.INTRO_DURATION

    for stat_name, (char1_has, char2_has) in config.CHARACTER_STATS.items():
        winner = None

        if char1_has and not char2_has:
            winner = 1
            score1 += 1

        elif char2_has and not char1_has:
            winner = 2
            score2 += 1

        elif char1_has and char2_has:
            score1 += 1
            score2 += 1

            winner = None

        stat_clip = CharacterClips.create_stat_comparison_clip(
            config,
            char1_files['main'],
            char2_files['main'],
            stat_name,
            score1,
            score2,
            start_time=current_time,
            duration=config.STAT_DURATION,
            winner=winner,
            char1_name=char1_name,
            char2_name=char2_name
        )

        clips.append(stat_clip)

        current_time += config.STAT_DURATION

    winner_text = TextGenerator.create_text_clip(
        'WINNER', current_time, 1.0, config, fontsize=0.16, position=('center', 'center')
    )[0]

    clips.append(winner_text)

    current_time += 1.0

    score_diff = abs(score1 - score2)
    num_stats = len(config.CHARACTER_STATS)

    if score_diff == 0:
        difficulty_label = ''
        winner_name = 'TIE'

    elif score_diff == 1:
        difficulty_label = 'extreme diff'
        winner_name = char1_name if score1 > score2 else char2_name
    
    elif score_diff <= num_stats * 0.2:
        difficulty_label = 'low diff'
        winner_name = char1_name if score1 > score2 else char2_name
    
    elif score_diff <= num_stats * 0.4:
        difficulty_label = 'mid diff'
        winner_name = char1_name if score1 > score2 else char2_name
    
    else:
        difficulty_label = 'high diff'
        winner_name = char1_name if score1 > score2 else char2_name
    
    winner_file = char1_files['win'] if score1 > score2 else char2_files['win'] if score2 > score1 else None

    winner_clip = CharacterClips.create_winner_screen_clip(
        config,
        winner_name,
        score1,
        score2,
        difficulty_label,
        winner_file,
        start_time=current_time,
        duration=config.OUTRO_DURATION,
        char1_file=char1_files['main'],
        char2_file=char2_files['main']
    )

    clips.append(winner_clip)

    final_clip = mp.CompositeVideoClip(clips, size=(config.RESOLUTION))

    try:
        music_path = str(script_dir / config.MUSIC_PATH)

        if os.path.exists(music_path) and validate_media(music_path, 'audio'):
            audio_clip = mp.AudioFileClip(music_path)
            
            if audio_clip.duration > 0:
                loops_needed = int(np.ceil(final_clip.duration / audio_clip.duration))
                audio_clip = mp.concatenate_audioclips([audio_clip] * loops_needed)
                audio_clip = audio_clip.set_duration(final_clip.duration)
                final_clip = final_clip.set_audio(audio_clip)
                audio_clip.close()

            print(f'{Fore.GREEN}Audio loaded: {music_path} 🎵{Fore.RESET}')
        
        else:
            print(f'{Fore.YELLOW}Audio file {music_path} invalid or missing, proceeding without audio ⚠️{Fore.RESET}')
    except Exception as e:
        print(f'{Fore.RED}Failed to add music: {e} ❌{Fore.RESET}')
    
    output_path = str(script_dir / config.OUTPUT_PATH)
    
    try:
        final_clip.write_videofile(
            output_path,
            fps=config.FPS,
            codec='libx264',
            audio_codec='aac',
            bitrate=config.BITRATE,
            preset='ultrafast',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads=8
        )

        print(f'{Fore.GREEN}1v1 comparison video saved at {output_path} in {(datetime.now() - start_time).total_seconds()}s ✅{Fore.RESET}')
    except Exception as e:
        print(f'{Fore.RED}Failed to save 1v1 video: {e} ❌{Fore.RESET}')
    finally:
        final_clip.close()

        for clip in clips:
            clip.close()


def generate_slideshow(config=SlideshowConfig):
    print(f'{Fore.CYAN}Starting enhanced slideshow video generation 📸{Fore.RESET}')

    script_dir = Path(__file__).parent
    image_dir = os.path.join(script_dir, config.IMAGE_DIR)

    if not os.path.exists(image_dir):
        os.makedirs(image_dir, exist_ok=True)

        print(f'{Fore.YELLOW}Created directory: {image_dir} 📁{Fore.RESET}')

        return False

    image_files = [
        os.path.join(image_dir, f) for f in os.listdir(image_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')) and validate_media(os.path.join(image_dir, f), 'image')
    ]

    if not image_files:
        print(f'{Fore.RED}No valid images found in {image_dir} ❌{Fore.RESET}')

        return False

    print(f'{Fore.GREEN}Found {len(image_files)} images 📸{Fore.RESET}')

    random.shuffle(image_files)
    image_files = image_files[:min(len(image_files), config.MAX_IMAGES)]

    print(f'{Fore.GREEN}Limited to {len(image_files)} images 📸{Fore.RESET}')

    color_scheme = random.choice(config.COLOR_SCHEMES)

    print(f'{Fore.GREEN}Using color scheme: {color_scheme} 🎨{Fore.RESET}')

    intro_clip = CharacterClips.create_slideshow_intro_clip(config, color_scheme)
    
    clips = []

    print(f'{Fore.CYAN}Processing images with advanced effects... 🖼️{Fore.RESET}')

    for idx, img_path in enumerate(image_files):
        print(f'{Fore.CYAN}Processing {idx+1}/{len(image_files)}: {os.path.basename(img_path)} 🖼️{Fore.RESET}')

        try:
            img = Image.open(img_path).convert('RGB')
            img.verify()

            img = Image.open(img_path).convert('RGB')
            img_width, img_height = img.size

            if img_width < 50 or img_height < 50:
                print(f'{Fore.YELLOW}Image too small ({img_width}x{img_height}): {os.path.basename(img_path)} ⚠️{Fore.RESET}')

                continue

            max_size = 4000

            if img_width > max_size or img_height > max_size:
                print(f'{Fore.YELLOW}Resizing large image ({img_width}x{img_height}) to fit max size {max_size}: {os.path.basename(img_path)} 📏{Fore.RESET}')

                scale_factor = min(max_size / img_width, max_size / img_height)
                img = img.resize((int(img_width * scale_factor), int(img_height * scale_factor)), Image.LANCZOS)
                img_width, img_height = img.size

                print(f'{Fore.GREEN}Image resized to ({img_width}x{img_height}) ✅{Fore.RESET}')

            aspect_ratio = img_width / img_height
            target_aspect_ratio = config.RESOLUTION[0] / config.RESOLUTION[1]

            if aspect_ratio < target_aspect_ratio:
                new_width = min(img_width, int(img_height * target_aspect_ratio))
                left = max(0, (img_width - new_width) // 2)
                right = min(img_width, left + new_width)
                img = img.crop((left, 0, right, img_height))

            else:
                new_height = min(img_height, int(img_width / target_aspect_ratio))
                top = max(0, (img_height - new_height) // 2)
                bottom = min(img_height, top + new_height)
                img = img.crop((0, top, img_width, bottom))

            img = img.resize(config.RESOLUTION, Image.LANCZOS)

            enhance_type = random.choice(['none', 'sharpen', 'contrast', 'brightness', 'color'])

            if enhance_type == 'sharpen':
                img = img.filter(ImageFilter.SHARPEN)

            elif enhance_type == 'contrast':
                img = ImageEnhance.Contrast(img).enhance(random.uniform(1.05, 1.25))

            elif enhance_type == 'brightness':
                img = ImageEnhance.Brightness(img).enhance(random.uniform(0.95, 1.05))

            elif enhance_type == 'color':
                img = ImageEnhance.Color(img).enhance(random.uniform(1.05, 1.3))

            duration = random.uniform(config.MIN_IMG_DURATION, config.MAX_IMG_DURATION)
            img_clip = mp.ImageClip(np.array(img)).set_duration(duration)
            img_clip = VideoEffects.apply_advanced_effects(img_clip)

            clips_to_composite = [img_clip]

            if random.random() < 0.1:
                caption = random.choice(config.CAPTIONS)
                position_style = random.choice(['top', 'bottom', 'center', 'random'])
                caption_clip = TextGenerator.create_caption_overlay(
                    config,
                    caption,
                    2.5,
                    position_style
                )

                if caption_clip:
                    clips_to_composite.append(caption_clip)

            if len(clips_to_composite) > 1:
                img_clip = mp.CompositeVideoClip(clips_to_composite)

            clips.append(img_clip)
        except Exception as e:
            print(f'{Fore.RED}Failed to process image {os.path.basename(img_path)}: {e} ❌{Fore.RESET}')

            continue
    
    if not clips:
        print(f'{Fore.RED}No valid image clips created ❌{Fore.RESET}')

        return False

    print(f'{Fore.GREEN}Created {len(clips)} enhanced image clips ✅{Fore.RESET}')
    print(f'{Fore.CYAN}Applying advanced transitions... 🎞️{Fore.RESET}')

    try:
        if len(clips) == 1:
            main_clip = clips[0]

        else:
            final_clips = [clips[0]]

            for i in range(1, len(clips)):
                transition_type = random.choice(config.TRANSITION_TYPES)
                transition_duration = min(0.5, clips[i - 1].duration * 0.2, clips[i].duration * 0.2)

                try:
                    if transition_type in ['slide_left', 'slide_right', 'zoom_in', 'spin']:
                        transitioned_clip = VideoEffects.apply_advanced_transitions(
                            config,
                            final_clips[-1],
                            clips[i],
                            transition_type,
                            transition_duration
                        )
                        final_clips[-1] = transitioned_clip

                    else:
                        prev_clip = final_clips[-1]

                        if transition_type == 'crossfade':
                            final_clips[-1] = prev_clip.crossfadeout(transition_duration)
                            final_clips.append(clips[i].crossfadein(transition_duration))

                        else:
                            final_clips.append(clips[i])
                except Exception as e:
                    print(f'{Fore.RED}Transition failed between clips {i-1} and {i}: {e} ❌{Fore.RESET}')

                    final_clips.append(clips[i])

            main_clip = mp.concatenate_videoclips(final_clips, method='compose')

        current_duration = main_clip.duration + config.INTRO_DURATION

        if current_duration > config.MAX_VIDEO_DURATION:
            speed_factor = current_duration / (config.MAX_VIDEO_DURATION - config.INTRO_DURATION)
            speed_factor = max(1.0, speed_factor)
            main_clip = main_clip.fx(vfx.speedx, speed_factor)

            print(f'{Fore.YELLOW}Applied speed factor: {speed_factor:.2f}x ⚡{Fore.RESET}')

        print(f'{Fore.GREEN}Main sequence created ✅{Fore.RESET}')
    except Exception as e:
        print(f'{Fore.RED}Failed to create main sequence: {e} ❌{Fore.RESET}')
    
    print(f'{Fore.CYAN}Creating captions... 💬{Fore.RESET}')

    try:
        total_video_duration = main_clip.duration + config.INTRO_DURATION
        num_captions = max(2, min(6, int(total_video_duration / 8)))
        caption_clips = []
        used_captions = set()

        for i in range(num_captions):
            available_captions = [c for c in config.CAPTIONS if c not in used_captions]

            if not available_captions:
                used_captions.clear()
                available_captions = config.CAPTIONS

            caption = random.choice(available_captions)
            used_captions.add(caption)
            duration = random.uniform(2.5, 4.5)
            base_start = (total_video_duration - duration - config.INTRO_DURATION) * i / max(1, num_captions - 1)
            start_time = max(0, min(total_video_duration - duration, base_start + random.uniform(-2, 2)))
            position_style = random.choice(['top', 'bottom', 'center', 'random'])

            try:
                caption_clip = TextGenerator.create_caption_overlay(
                    config,
                    caption,
                    duration,
                    position_style,
                    start_time
                )

                if caption_clip:
                    caption_clips.append(caption_clip)

                    print(f'{Fore.GREEN}Created caption "{caption}" at {start_time:.1f}s with duration {duration:.1f}s ✅{Fore.RESET}')
            except Exception as e:
                print(f'{Fore.RED}Failed to create caption: {e} ❌{Fore.RESET}')

        print(f'{Fore.GREEN}Created {len(caption_clips)} independent captions ✅{Fore.RESET}')
    except Exception as e:
        print(f'{Fore.RED}Failed to create captions: {e} ❌{Fore.RESET}')
        caption_clips = []
    
    print(f'{Fore.CYAN}Assembling final video... 🎬{Fore.RESET}')

    try:
        final_sequence = mp.concatenate_videoclips([intro_clip, main_clip])

        if caption_clips:
            all_clips = [final_sequence] + [c.set_start(c.start + config.INTRO_DURATION) for c in caption_clips]
            final_clip = mp.CompositeVideoClip(all_clips)

        else:
            final_clip = final_sequence
    except Exception as e:
        print(f'{Fore.RED}Failed to create final sequence: {e} ❌{Fore.RESET}')

        return False
    
    try:
        music_path = str(script_dir / config.MUSIC_PATH)

        if os.path.exists(music_path) and validate_media(music_path, 'audio'):
            audio_clip = mp.AudioFileClip(music_path)
            audio_clip = audio_clip.set_duration(final_clip.duration).volumex(0.4)
            final_clip = final_clip.set_audio(audio_clip)
            audio_clip.close()

            print(f'{Fore.GREEN}Background music added 🎵{Fore.RESET}')

        else:
            print(f'{Fore.YELLOW}Music file not found, proceeding without audio ⚠️{Fore.RESET}')
    except Exception as e:
        print(f'{Fore.RED}Failed to add music: {e} ❌{Fore.RESET}')
    
    output_path = str(config.OUTPUT_VIDEO_PATH)

    try:
        final_clip.write_videofile(
            output_path,
            fps=config.FPS,
            codec='libx264',
            audio_codec='aac',
            bitrate='10000k',
            preset='medium',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads=4
        )
        print(f'{Fore.GREEN}Slideshow video saved at {output_path} ✅{Fore.RESET}')
        print(f'{Fore.GREEN}Final video duration: {final_clip.duration:.2f} seconds 📊{Fore.RESET}')

        return True
    except Exception as e:
        print(f'{Fore.RED}Failed to save slideshow video: {e} ❌{Fore.RESET}')

        return False
    finally:
        final_clip.close()

        for clip in clips + [intro_clip] + caption_clips:
            clip.close()


configure_imagemagick()
generate_1v1_comparison()
generate_slideshow()
