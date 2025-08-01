import os
import math
import random
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from colorama import Fore
from effects import VideoEffects
from text import TextGenerator
from utils import validate_media

class CharacterClips:
    @staticmethod
    def create_character_intro_clip(config, file1_path, file2_path, name1, name2, custom_text1,
                                   custom_text2, start_time, duration):
        clips = []
        text_regions = []

        for path, pos_y in [(file1_path, 0), (file2_path, config.FINAL_HEIGHT // 2)]:
            media_type = 'image' if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'

            if os.path.exists(path) and validate_media(path, media_type):
                is_static = media_type == 'image'
                clip = mp.ImageClip(path) if is_static else mp.VideoFileClip(path).set_fps(config.FPS)

                if not is_static and clip.duration < duration:
                    clip = clip.fx(vfx.loop, duration=duration)

                clip = clip.set_duration(duration)
                clip = VideoEffects.resize_clip(clip, config.FINAL_WIDTH, config.FINAL_HEIGHT // 2)

                if is_static:
                    clip = VideoEffects.apply_pulsate_effect(clip, duration)

                clip = VideoEffects.apply_dimming_effect(clip, config)
                clip = VideoEffects.apply_intro_effect(clip, duration, config)
                clip = clip.set_position((0, pos_y)).set_start(start_time)

                clips.apend(clip)

            else:
                print(f'[WARNING] Invalid media {path}, using placeholder ⚠️')

                clip = mp.ColorClip(
                    size=(config.FINAL_WIDTH, config.FINAL_HEIGHT // 2),
                    color=(0, 0, 0),
                    duration=duration
                )
                clip = clip.set_position((0, pos_y)).set_start(start_time)
                clips.append(clip)

        particle_clip = VideoEffects.create_particle_clip(
            duration, config.FINAL_WIDTH, config.FINAL_HEIGHT, text_regions, config
        )
        particle_clip = particle_clip.set_start(start_time)
        clips.append(particle_clip)

        vs_text = f'{name1.upper()}\nVS\n{name2.upper()}'

        text_clip, vs_text_regions = TextGenerator.create_text_clip(
            vs_text, start_time, duration, config, fontsize=0.14, position=('center', 'center'), is_intro=True
        )
        clips.append(text_clip)

        text_regions.extend(vs_text_regions)

        if custom_text1:
            custom_text1_clip, custom_text1_regions = TextGenerator.create_text_clip(
                custom_text1, start_time, duration, config, fontsize=0.06, position=('left', 'top'), is_intro=True
            )
            clips.append(custom_text1_clip)

            text_regions.extend(custom_text1_regions)

        if custom_text2:
            custom_text2_clip, custom_text2_regions = TextGenerator.create_text_clip(
                custom_text2, start_time, duration, config, fontsize=0.06, position=('right', 'bottom'), is_intro=True
            )
            clips.append(custom_text2_clip)

            text_regions.extend(custom_text2_regions)

        return (
            mp.CompositeVideoClip(clips, size=(config.FINAL_WIDTH, config.FINAL_HEIGHT))
            .fx(vfx.fadein, config.FADE_DURATION)
            .fx(vfx.fadeout, config.FADE_DURATION)
        )

    @staticmethod
    def create_stat_comparison_clip(file1_path, file2_path, stat_name, score1, score2,
                                   start_time, duration, winner, char1_name, char2_name, config):
        clips = []
        text_regions = []
        text_duration = 1.0
        file_duration = duration - text_duration

        for path, pos_y in [(file1_path, 0), (file2_path, config.FINAL_HEIGHT // 2)]:
            media_type = 'image' if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'

            if os.path.exists(path) and validate_media(path, media_type):
                is_static = media_type == 'image'
                clip = mp.ImageClip(path) if is_static else mp.VideoFileClip(path).set_fps(config.FPS)

                if not is_static and clip.duration < duration:
                    clip = clip.fx(vfx.loop, duration=duration)

                clip = clip.set_duration(duration)
                clip = VideoEffects.resize_clip(clip, config.FINAL_WIDTH, config.FINAL_HEIGHT // 2)

                if is_static:
                    clip = VideoEffects.apply_pulsate_effect(clip, duration)

                clip = VideoEffects.apply_dimming_effect(clip, config)
                clip = VideoEffects.apply_transition_effect(
                    clip, duration, config.TRANSITION_DURATION,
                    random.choice(['scale', 'zoom', 'slide-in', 'opacity', 'fade']), config
                )
                clip = clip.set_position((0, pos_y)).set_start(start_time)
                clips.append(clip)

            else:
                print(f'[WARNING] Invalid media {path}, using placeholder ⚠️')

                clip = mp.ColorClip(
                    size=(config.FINAL_WIDTH, config.FINAL_HEIGHT // 2),
                    color=(0, 0, 0),
                    duration=duration
                )
                clip = clip.set_position((0, pos_y)).set_start(start_time)
                clips.append(clip)

        particle_clip = VideoEffects.create_particle_clip(
            duration, config.FINAL_WIDTH, config.FINAL_HEIGHT, text_regions, config
        )
        particle_clip = particle_clip.set_start(start_time)
        clips.append(particle_clip)

        stat_text, stat_text_regions = TextGenerator.create_text_clip(
            stat_name.upper(), start_time, text_duration, config, fontsize=0.12, position=('center', 'center')
        )
        clips.append(stat_text)

        text_regions.extend(stat_text_regions)

        if winner is None:
            text = f'BOTH\n{score1} — {score2}'

            for path, pos_y in [(file1_path, 0), (file2_path, config.FINAL_HEIGHT // 2)]:
                media_type = 'image' if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'

                if os.path.exists(path) and validate_media(path, media_type):
                    is_static = media_type == 'image'
                    clip = mp.ImageClip(path) if is_static else mp.VideoFileClip(path).set_fps(config.FPS)

                    if not is_static and clip.duration < file_duration:
                        clip = clip.fx(vfx.loop, duration=file_duration)

                    clip = clip.set_duration(file_duration)
                    clip = VideoEffects.resize_clip(clip, config.FINAL_WIDTH, config.FINAL_HEIGHT // 2)

                    if is_static:
                        clip = VideoEffects.apply_pulsate_effect(clip, file_duration)

                    clip = VideoEffects.apply_dimming_effect(clip, config)
                    clip = VideoEffects.apply_transition_effect(
                        clip, file_duration, config.TRANSITION_DURATION,
                        random.choice(['scale', 'zoom', 'slide-in', 'opacity', 'fade']), config
                    )
                    clip = clip.set_position((0, pos_y)).set_start(start_time + text_duration)
                    clips.append(clip)

                else:
                    clip = mp.ColorClip(
                        size=(config.FINAL_WIDTH, config.FINAL_HEIGHT // 2),
                        color=(0, 0, 0),
                        duration=file_duration
                    )
                    clip = clip.set_position((0, pos_y)).set_start(start_time + text_duration)
                    clips.append(clip)

        else:
            path = file1_path if winner == 1 else file2_path
            name = char1_name if winner == 1 else char2_name

            text = f'{name.upper()}\n{score1} — {score2}'
            media_type = 'image' if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'

            if os.path.exists(path) and validate_media(path, media_type):
                is_static = media_type == 'image'
                clip = mp.ImageClip(path) if is_static else mp.VideoFileClip(path).set_fps(config.FPS)

                if not is_static and clip.duration < file_duration:
                    clip = clip.fx(vfx.loop, duration=file_duration)

                clip = clip.set_duration(file_duration)
                clip = VideoEffects.resize_clip(clip, config.FINAL_WIDTH, config.FINAL_HEIGHT)

                if is_static:
                    clip = VideoEffects.apply_pulsate_effect(clip, file_duration)

                clip = VideoEffects.apply_dimming_effect(clip, config)
                clip = VideoEffects.apply_transition_effect(
                    clip, file_duration, config.TRANSITION_DURATION,
                    random.choice(['scale', 'zoom', 'slide-in', 'opacity', 'fade']), config
                )
                clip = clip.set_position('center').set_start(start_time + text_duration)
                clips.append(clip)

            else:
                clip = mp.ColorClip(
                    size=(config.FINAL_WIDTH, config.FINAL_HEIGHT),
                    color=(0, 0, 0),
                    duration=file_duration
                )
                clip = clip.set_position('center').set_start(start_time + text_duration)
                clips.append(clip)

        score_text, score_text_regions = TextGenerator.create_text_clip(
            text, start_time + text_duration, file_duration, config, fontsize=0.12, position=('center', 'center')
        )
        clips.append(score_text)

        text_regions.extend(score_text_regions)

        return (
            mp.CompositeVideoClip(clips, size=(config.FINAL_WIDTH, config.FINAL_HEIGHT))
            .fx(vfx.fadein, config.FADE_DURATION)
            .fx(vfx.fadeout, config.FADE_DURATION)
        )

    @staticmethod
    def create_winner_screen_clip(winner_name, score1, score2, difficulty_label, winner_file,
                                 start_time, duration, char1_file, char2_file, config):
        print(f'[INFO] Creating winner screen for {winner_name}, start={start_time}s ⏱️')

        clips = []
        text_regions = []

        if winner_name != 'TIE':
            media_type = 'image' if winner_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'

            if os.path.exists(winner_file) and validate_media(winner_file, media_type):
                is_static = media_type == 'image'
                clip = mp.ImageClip(winner_file) if is_static else mp.VideoFileClip(winner_file).set_fps(config.FPS)

                if not is_static and clip.duration < duration:
                    clip = clip.fx(vfx.loop, duration=duration)

                clip = clip.set_duration(duration)
                clip = VideoEffects.resize_clip(clip, config.FINAL_WIDTH, config.FINAL_HEIGHT)

                if is_static:
                    clip = VideoEffects.apply_pulsate_effect(clip, duration)

                clip = VideoEffects.apply_dimming_effect(clip, config)
                clip = VideoEffects.apply_transition_effect(
                    clip, duration, config.TRANSITION_DURATION,
                    random.choice(['scale', 'zoom', 'slide-in', 'opacity', 'fade']), config
                )
                clip = clip.set_position('center').set_start(start_time)
                clips.append(clip)

            else:
                print(f'[WARNING] Invalid winner media {winner_file}, using placeholder ⚠️')

                clip = mp.ColorClip(
                    size=(config.FINAL_WIDTH, config.FINAL_HEIGHT),
                    color=(0, 0, 0),
                    duration=duration
                )
                clip = clip.set_position('center').set_start(start_time)
                clips.append(clip)

            text = f'{winner_name.upper()}\n{score1} — {score2}\n{difficulty_label.upper()}'

        else:
            text = f'BOTH\n{score1} — {score2}'

            for path, pos_y in [(char1_file, 0), (char2_file, config.FINAL_HEIGHT // 2)]:
                media_type = 'image' if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'

                if os.path.exists(path) and validate_media(path, media_type):
                    is_static = media_type == 'image'
                    clip = mp.ImageClip(path) if is_static else mp.VideoFileClip(path).set_fps(config.FPS)

                    if not is_static and clip.duration < duration:
                        clip = clip.fx(vfx.loop, duration=duration)

                    clip = clip.set_duration(duration)
                    clip = VideoEffects.resize_clip(clip, config.FINAL_WIDTH, config.FINAL_HEIGHT // 2)

                    if is_static:
                        clip = VideoEffects.apply_pulsate_effect(clip, duration)

                    clip = VideoEffects.apply_dimming_effect(clip, config)
                    clip = VideoEffects.apply_transition_effect(
                        clip,
                        duration,
                        config.TRANSITION_DURATION,
                        random.choice(['scale', 'zoom', 'slide-in', 'opacity', 'fade']),
                        config
                    )
                    clip = clip.set_position((0, pos_y)).set_start(start_time)
                    clips.append(clip)

                else:
                    clip = mp.ColorClip(
                        size=(config.FINAL_WIDTH, config.FINAL_HEIGHT // 2),
                        color=(0, 0, 0),
                        duration=duration
                    )
                    clip = clip.set_position((0, pos_y)).set_start(start_time)
                    clips.append(clip)

        particle_clip = VideoEffects.create_particle_clip(
            duration, config.FINAL_WIDTH, config.FINAL_HEIGHT, text_regions, config
        )
        particle_clip = particle_clip.set_start(start_time)
        clips.append(particle_clip)

        text_clip, text_regions = TextGenerator.create_text_clip(
            text, start_time, duration, config, fontsize=0.16, position=('center', 'center')
        )
        clips.append(text_clip)

        text_regions.extend(text_regions)

        return (
            mp.CompositeVideoClip(clips, size=(config.FINAL_WIDTH, config.FINAL_HEIGHT))
            .fx(vfx.fadein, config.FADE_DURATION)
            .fx(vfx.fadeout, config.FADE_DURATION)
        )

    @staticmethod
    def create_slideshow_intro_clip(config, color_scheme):
        print(f'{Fore.CYAN}Creating intro... ✨{Fore.RESET}')

        try:
            text_img = TextGenerator.create_stylish_text_image(
                config,
                config.INTRO_TEXT,
                color_scheme=color_scheme,
            )
            bg_gradient = VideoEffects.create_gradient_background(
                config.RESOLUTION,
                color_scheme['bg'],
                color_scheme['gradient'],
                'diagonal'
            )
            bg_array = np.array(bg_gradient)
            text_array = np.array(text_img.resize((config.RESOLUTION[0], 400)))
            intro_clip = mp.ImageClip(bg_array).set_duration(config.INTRO_DURATION)
            text_clip = (
                mp.ImageClip(text_array)
                .set_duration(config.INTRO_DURATION)
                .set_position(('center', config.RESOLUTION[1] * 0.4))
            )
            intro_final = mp.CompositeVideoClip([intro_clip, text_clip]).fx(vfx.fadein, 0.5).fx(vfx.fadeout, 0.5)

            print(f'{Fore.GREEN}Enhanced intro created ✅{Fore.RESET}')
        except Exception as e:
            print(f'{Fore.RED}Intro creation failed: {e} ❌{Fore.RESET}')

            return False

        return intro_final
