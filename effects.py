import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import numpy as np
import math
import random
from PIL import Image, ImageFilter, ImageEnhance
from config import SlideshowConfig

class VideoEffects:
    @staticmethod
    def custom_resize_image(image, target_width, target_height):
        try:
            return np.array(image.resize((target_width, target_height), Image.Resampling.LANCZOS))
        except Exception as e:
            print(f'[WARNING] LANCZOS unavailable, falling back to NEAREST: {e} ⚠️')
            
            return np.array(image.resize((target_width, target_height), Image.Resampling.NEAREST))

    @staticmethod
    def resize_clip(clip, width, height):
        def resizer(pic):
            if pic.dtype != np.uint8:
                pic = np.clip(pic * 255, 0, 255).astype(np.uint8)

            with Image.fromarray(pic) as pilim:
                return VideoEffects.custom_resize_image(pilim, width, height)
        
        return clip.fl_image(resizer)

    @staticmethod
    def apply_pulsate_effect(clip, duration):
        def get_scale(t):
            return 1.0 + 0.1 * np.sin(2 * np.pi * t / 2.0)

        return clip.fx(vfx.resize, get_scale)

    @staticmethod
    def apply_dimming_effect(clip, config):
        def dimming_effect(get_frame, t):
            frame = get_frame(t)
            
            return np.clip(frame * (1 - config.DIM_OPACITY), 0, 255).astype(np.uint8)
        
        return clip.fl(dimming_effect)

    @staticmethod
    def create_particle_clip(duration, width, height, text_regions, config):
        def make_frame(t):
            frame = np.zeros((height, width, 4), dtype=np.uint8)

            for _ in range(config.PARTICLE_COUNT):
                seed = int(t * 1000 + _)
                random.seed(seed)
                x = random.randint(0, width)
                y = random.randint(0, height)
                vx = random.uniform(-config.PARTICLE_SPEED, config.PARTICLE_SPEED)
                vy = random.uniform(-config.PARTICLE_SPEED, config.PARTICLE_SPEED)
                x = int(x + vx * t) % width
                y = int(y + vy * t) % height
                
                in_text = False

                for region in text_regions:
                    tx, ty, tw, th = region

                    if tx <= x <= tx + tw and ty <= y <= ty + th:
                        in_text = True

                        break

                if in_text:
                    continue

                for px in range(max(0, x - config.PARTICLE_SIZE // 2), min(width, x + config.PARTICLE_SIZE // 2)):
                    for py in range(max(0, y - config.PARTICLE_SIZE // 2), min(height, y + config.PARTICLE_SIZE // 2)):
                        if 0 <= px < width and 0 <= py < height:
                            frame[py, px] = [255, 255, 255, 100]

            return frame[:, :, :3]

        return mp.VideoClip(make_frame, duration=duration).set_opacity(0.4)

    @staticmethod
    def apply_transition_effect(clip, duration, transition_duration, transition_type, config):
        print(f'[INFO] Applying {transition_type} transition for {transition_duration}s ⚡️')
        
        if transition_type == 'scale':
            def get_scale(t):
                if t < transition_duration:
                    return 1.0 + 0.5 * (t / transition_duration)

                elif t > duration - transition_duration:
                    return 1.5 - 0.5 * ((t - (duration - transition_duration)) / transition_duration)
                
                return 1.5

            return clip.fx(vfx.resize, get_scale)

        elif transition_type == 'zoom':
            def get_scale(t):
                if t > duration - transition_duration:
                    progress = (t - (duration - transition_duration)) / transition_duration
                    
                    return 1.0 + 0.8 * progress

                return 1.0

            return clip.fx(vfx.resize, get_scale)

        elif transition_type == 'slide-in':
            def get_position(t):
                if t < transition_duration:
                    progress = t / transition_duration
                    
                    return (config.RESOLUTION[1] * (1 - progress), 'center')
                
                return (0, 'center')

            return clip.set_position(get_position)

        elif transition_type == 'opacity':
            def get_opacity(t):
                if t < transition_duration:
                    return t / transition_duration

                elif t > duration - transition_duration:
                    return 1.0 - ((t - (duration - transition_duration)) / transition_duration)
                
                return 1.0

            def opacity_effect(get_frame, t):
                frame = get_frame(t)

                return np.clip(frame * get_opacity(t), 0, 255).astype(np.uint8)
            
            return clip.fl(opacity_effect)

        else:
            return clip.fx(vfx.fadeout, transition_duration)

    @staticmethod
    def apply_intro_effect(clip, duration, config):
        print(f'[INFO] Applying intro zoom and blur effect for {duration}s ✨')
        
        def effect(get_frame, t):
            try:
                progress = t / duration
                blur = 15 * (1 - progress)
                scale = 1.5 - 0.5 * progress
                frame = get_frame(t)

                if blur > 0:
                    with Image.fromarray(frame) as img:
                        frame = np.array(img.filter(ImageFilter.GaussianBlur(blur)))
                
                return VideoEffects.custom_resize_image(
                    Image.fromarray(frame),
                    int(config.RESOLUTION[0] * scale),
                    int(config.RESOLUTION[1] * scale // 2)
                )
            except Exception as e:
                print(f'[ERROR] Intro effect error: {e}, returning unprocessed frame ⚠️')
                
                return get_frame(t)

        return clip.fl(effect)

    @staticmethod
    def create_gradient_background(size, color1, color2, direction='vertical'):
        width, height = size

        gradient = Image.new('RGB', (width, height))

        if direction == 'vertical':
            for y in range(height):
                ratio = y / height

                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)

                for x in range(width):
                    gradient.putpixel((x, y), (r, g, b))

        elif direction == 'diagonal':
            for y in range(height):
                for x in range(width):
                    ratio = (x + y) / (width + height)

                    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                    
                    gradient.putpixel((x, y), (r, g, b))

        return gradient

    @staticmethod
    def apply_advanced_transitions(config, clip1, clip2, transition_type, duration=0.5):
        try:
            if transition_type == 'slide_left':
                def slide_left_effect(t):
                    if t < duration:
                        progress = t / duration

                        offset = int(config.RESOLUTION[0] * (1 - progress))

                        frame1 = clip1.get_frame(min(t, clip1.duration - 0.01))
                        frame2 = clip2.get_frame(0)

                        result = np.zeros_like(frame1)
                        
                        if offset < config.RESOLUTION[0] and offset > 0:
                            result[:, offset:] = frame1[:, : config.RESOLUTION[0] - offset]
                            result[:, :offset] = frame2[:, config.RESOLUTION[0] - offset :]
                       
                        elif offset <= 0:
                            result = frame2

                        else:
                            result = frame1

                        return result
                    
                    return clip2.get_frame(min(t - duration, clip2.duration - 0.01))
                
                return mp.VideoClip(slide_left_effect, duration=clip1.duration + duration)
           
            elif transition_type == 'zoom_in':
                def zoom_in_effect(t):
                    if t < duration:
                        progress = t / duration
                        scale = 1 + progress * 0.5

                        frame = clip1.get_frame(min(t, clip1.duration - 0.01))
                        h, w = frame.shape[:2]

                        new_h, new_w = max(1, int(h / scale)), max(1, int(w / scale))
                        start_y = max(0, (h - new_h) // 2)
                        start_x = max(0, (w - new_w) // 2)
                        end_y = min(h, start_y + new_h)
                        end_x = min(w, start_x + new_w)

                        cropped = frame[start_y:end_y, start_x:end_x]

                        if cropped.size > 0:
                            pil_img = Image.fromarray(cropped)
                            resized = pil_img.resize((w, h), Image.LANCZOS)
                            
                            return np.array(resized)
                        
                        return frame

                    return clip2.get_frame(min(t - duration, clip2.duration - 0.01))
                
                return mp.VideoClip(zoom_in_effect, duration=clip1.duration + duration)
           
            elif transition_type == 'spin':
                def spin_effect(t):
                    if t < duration:
                        progress = t / duration
                        angle = progress * 180

                        frame = clip1.get_frame(min(t, clip1.duration - 0.01))
                        pil_img = Image.fromarray(frame)

                        rotated = pil_img.rotate(angle, expand=False, fillcolor=(0, 0, 0))
                        
                        return np.array(rotated)
                    
                    return clip2.get_frame(min(t - duration, clip2.duration - 0.01))
               
                return mp.VideoClip(spin_effect, duration=clip1.duration + duration)
            
            else:
                return clip1.crossfadeout(duration).set_duration(clip1.duration + duration)
        except Exception as e:
            print(f'[WARNING] Transition effect failed: {e}, using crossfade ⚠️')
            return clip1.crossfadeout(0.2).set_duration(clip1.duration + 0.2)


    @staticmethod
    def apply_advanced_effects(clip):
        effect_type = random.choice(['shake', 'color_shift', 'glitch', 'wave', 'none', 'none'])
       
        try:
            if effect_type == 'shake':
                def shake_effect(get_frame, t):
                    frame = get_frame(t)

                    intensity = 8 if random.random() < 0.3 else 4

                    x = int(intensity * math.sin(t * 50) * random.uniform(0.5, 1.5))
                    y = int(intensity * math.cos(t * 50 * 1.3) * random.uniform(0.5, 1.5))

                    new_frame = np.zeros_like(frame)
                    h, w = frame.shape[:2]

                    src_y_start = max(0, -y)
                    src_y_end = min(h, h - y)
                    src_x_start = max(0, -x)
                    src_x_end = min(w, w - x)
                    dst_y_start = max(0, y)
                    dst_y_end = min(h, dst_y_start + (src_y_end - src_y_start))
                    dst_x_start = max(0, x)
                    dst_x_end = min(w, dst_x_start + (src_x_end - src_x_start))
                   
                    if dst_y_end > dst_y_start and dst_x_end > dst_x_start and src_y_end > src_y_start and src_x_end > src_x_start:
                        new_frame[dst_y_start:dst_y_end, dst_x_start:dst_x_end] = frame[src_y_start:src_y_end, src_x_start:src_x_end]
                 
                    else:
                        new_frame = frame
                  
                    return new_frame

                return clip.fl(shake_effect)

            elif effect_type == 'color_shift':
                def color_shift_effect(get_frame, t):
                    frame = get_frame(t)

                    shift = int(20 * math.sin(t * 3))

                    new_frame = frame.copy()
                    h, w = frame.shape[:2]

                    if shift > 0 and shift < w:
                        new_frame[:, shift:, 0] = frame[:, :-shift, 0]
                        new_frame[:, :-shift, 2] = frame[:, shift:, 2]

                    elif shift < 0 and abs(shift) < w:
                        new_frame[:, :shift, 0] = frame[:, -shift:, 0]
                        new_frame[:, -shift:, 2] = frame[:, :shift, 2]

                    return new_frame

                return clip.fl(color_shift_effect)

            elif effect_type == 'glitch':
                def glitch_effect(get_frame, t):
                    frame = get_frame(t)

                    if random.random() < 0.1:
                        glitch_frame = frame.copy()
                        h, w = frame.shape[:2]

                        for _ in range(random.randint(3, 8)):
                            y = random.randint(0, max(1, h - 50))
                            height = min(random.randint(5, 30), h - y)
                            shift = random.randint(-min(20, w // 4), min(20, w // 4))

                            if shift > 0 and shift < w:
                                glitch_frame[y:y + height, shift:] = frame[y:y + height, :-shift]
                           
                            elif shift < 0 and abs(shift) < w:
                                glitch_frame[y:y + height, :shift] = frame[y:y + height, -shift:]
                        
                        return glitch_frame

                    return frame

                return clip.fl(glitch_effect)

            elif effect_type == 'wave':
                def wave_effect(get_frame, t):
                    frame = get_frame(t)
                    new_frame = np.zeros_like(frame)
                    h, w = frame.shape[:2]

                    for y in range(h):
                        shift = int(10 * math.sin(y * 0.02 + t * 5))

                        if abs(shift) < w:
                            src_start = max(0, -shift)
                            src_end = min(w, w - shift)
                            dst_start = max(0, shift)
                            dst_end = min(w, dst_start + (src_end - src_start))
                            
                            if dst_end > dst_start and src_end > src_start:
                                new_frame[y, dst_start:dst_end] = frame[y, src_start:src_end]
                           
                            else:
                                new_frame[y] = frame[y]

                        else:
                            new_frame[y] = frame[y]

                    return new_frame
                return clip.fl(wave_effect)
        except Exception as e:
            print(f'[WARNING] Failed to apply effect "{effect_type}": {e} ⚠️')
            
            return clip

        return clip
