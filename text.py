import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import SlideshowConfig
from effects import VideoEffects

class TextGenerator:
    @staticmethod
    def get_fancy_font():
        fancy_fonts = [
            'C:\Windows\Fonts\Candara\Candara.ttf'
        ]

        for font_name in fancy_fonts:
            try:
                ImageFont.truetype(font_name, 80)

                print(f'[INFO] Using font: {font_name} ✓')

                return font_name
            except Exception:
                continue

        print('[WARNING] Using default font ⚠️')

    @staticmethod
    def create_stylish_text_image(config, text, font_size=80, color_scheme=None, style='modern'):
        if not color_scheme:
            color_scheme = random.choice(config.COLOR_SCHEMES)

        font_name = TextGenerator.get_fancy_font()

        canvas_size = (1400, 500)

        img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))

        if style == 'modern':
            bg_gradient = VideoEffects.create_gradient_background(
                canvas_size,
                color_scheme['bg'],
                color_scheme['gradient'],
                'diagonal'
            )

        elif style == 'neon':
            bg_gradient = VideoEffects.create_gradient_background(
                canvas_size, (0, 0, 0), color_scheme['accent'], 'vertical'
            )

        else:
            bg_gradient = VideoEffects.create_gradient_background(
                canvas_size,
                color_scheme['bg'],
                tuple(min(255, c + 30) for c in color_scheme['bg']),
                'vertical'
            )

        bg_gradient = bg_gradient.convert('RGBA')
        bg_gradient.putalpha(200)
        bg_gradient = bg_gradient.filter(ImageFilter.GaussianBlur(radius=3))
        
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(font_name, font_size) if font_name else ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)

        x = (canvas_size[0] - text_width) // 2
        y = (canvas_size[1] - text_height) // 2

        for offset, shadow_color in [
            ((6, 6), (0, 0, 0, 240)),
            ((4, 4), (0, 0, 0, 160)),
            ((2, 2), (0, 0, 0, 80))
        ]:
            shadow_img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            shadow_draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_color)
            img = Image.alpha_composite(img, shadow_img)

        text_img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        outline_width = 4
        outline_color = color_scheme['accent']

        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx * dx + dy * dy <= outline_width * outline_width:
                    text_draw.text((x + dx, y + dy), text, font=font, fill=outline_color)

        text_draw.text((x, y), text, font=font, fill=color_scheme['text'])

        glow_img = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.text((x, y), text, font=font, fill=(*color_scheme['accent'], 150))
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=8))
        img = Image.alpha_composite(img, glow_img)
        img = Image.alpha_composite(img, text_img)

        return img

    @staticmethod
    def create_text_clip(text, start_time, duration, config, fontsize=0.1, position=('center', 'center'), is_intro=False):
        print(f'[INFO] Creating text clip: {text}, duration={duration}s ✍️')
        
        try:
            base_fontsize = int(fontsize * config.FINAL_HEIGHT)
            text_length = len(text.replace('\n', ''))
            fontsize = int(base_fontsize * (0.6 if text_length > 8 else 1))
            font = config.FONT
            color = config.CUSTOM_TEXT_COLOR if is_intro and position != ('center', 'center') else config.TEXT_COLOR
            stroke_width = (
                4 if not is_intro and position == ('center', 'center') else
                2 if is_intro and position != ('center', 'center') else
                int(0.005 * config.FINAL_HEIGHT)
            )

            stroke_color = config.STROKE_COLOR
            text_method = 'label' if not is_intro and position == ('center', 'center') else 'caption'
            text_size = (int(config.FINAL_WIDTH * 0.8), None) if text_method == 'caption' else None
            text_clip = mp.TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font=font,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method=text_method,
                size=text_size
            )

            text_w, text_h = text_clip.size

            if position == ('center', 'center'):
                text_x = (config.FINAL_WIDTH - text_w) // 2
                text_y = (config.FINAL_HEIGHT - text_h) // 2

            elif position == ('left', 'top'):
                text_x, text_y = 0, 10

            elif position == ('right', 'bottom'):
                text_x, text_y = config.FINAL_WIDTH - text_w, config.FINAL_HEIGHT - text_h - 10
            
            else:
                text_x, text_y = position if isinstance(position, tuple) and len(position) == 2 else (0, 0)
            
            text_region = (text_x, text_y, text_w, text_h)
            
            if is_intro and position != ('center', 'center'):
                if position == ('left', 'top'):
                    adjusted_position = (-20, 10)

                elif position == ('right', 'bottom'):
                    adjusted_position = (config.FINAL_WIDTH - text_clip.size[0] + 20, config.FINAL_HEIGHT - text_clip.size[1] - 10)
                
                else:
                    adjusted_position = position

                text_clip = (
                    text_clip.set_position(adjusted_position)
                    .set_duration(duration)
                    .set_start(start_time)
                )

                if is_intro:
                    text_clip = text_clip.fx(vfx.fadein, config.FADE_DURATION).fx(vfx.fadeout, config.FADE_DURATION)
                
                return text_clip, [text_region]
            
            else:
                text_clip = (
                    text_clip.set_position(position)
                    .set_duration(duration)
                    .set_start(start_time)
                )

                if is_intro:
                    text_clip = text_clip.fx(vfx.fadein, config.FADE_DURATION).fx(vfx.fadeout, config.FADE_DURATION)
                
                return text_clip, [text_region]
        except Exception as e:
            print(f'[ERROR] Text creation error: {e} ❌')

            fallback_clip = (
                mp.TextClip(
                    text,
                    fontsize=int(0.06 * config.FINAL_HEIGHT),
                    color=config.TEXT_COLOR,
                    font=config.FALLBACK_FONT
                )
                .set_position(position)
                .set_duration(duration)
                .set_start(start_time)
            )

            return fallback_clip, []

    @staticmethod
    def create_caption_overlay(config, text, duration, position_style='random', start_time=0):
        color_scheme = random.choice(config.COLOR_SCHEMES)
        font_size = random.randint(40, 80)
        style = random.choice(['modern', 'neon', 'classic'])
        text_img = TextGenerator.create_stylish_text_image(
            config,
            text,
            font_size=font_size,
            color_scheme=color_scheme,
            style=style
        )
        text_array = np.array(text_img.resize((config.RESOLUTION[0], 400)))
        
        if position_style == 'top':
            position = ('center', config.RESOLUTION[1] * 0.1)

        elif position_style == 'bottom':
            position = ('center', config.RESOLUTION[1] * 0.75)

        elif position_style == 'center':
            position = ('center', 'center')

        else:
            positions = [
                ('center', config.RESOLUTION[1] * 0.15),
                ('center', config.RESOLUTION[1] * 0.6),
                ('center', config.RESOLUTION[1] * 0.8),
                ('center', 'center')
            ]

            position = random.choice(positions)

        text_clip = (
            mp.ImageClip(text_array)
            .set_duration(duration)
            .set_position(position)
            .set_start(start_time)
        )

        entrance_effect = random.choice(['fadein', 'slide_up', 'zoom_in'])
        exit_effect = random.choice(['fadeout', 'slide_down', 'zoom_out'])
        
        if entrance_effect == 'fadein':
            text_clip = text_clip.fx(vfx.fadein, 0.8)

        elif entrance_effect == 'zoom_in':
            text_clip = text_clip.fx(vfx.resize, lambda t: 0.3 + 0.7 * min(1, t * 1.5))
        
        if exit_effect == 'fadeout':
            text_clip = text_clip.fx(vfx.fadeout, 0.8)

        elif exit_effect == 'zoom_out':
            text_clip = text_clip.fx(
                vfx.resize,
                lambda t: max(0.3, 1 - (t - duration + 0.8) * 1.5) if t > duration - 0.8 else 1
            )

        return text_clip
