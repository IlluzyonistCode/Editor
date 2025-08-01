class VersusConfig:
    RESOLUTION = (720, 1080)
    FPS = 60
    INTRO_DURATION = 5
    OUTRO_DURATION = 10
    STAT_DURATION = 2.5
    TRANSITION_DURATION = 0.5
    FADE_DURATION = 0.15
    DIM_OPACITY = 0.3
    PARTICLE_COUNT = 20
    PARTICLE_SIZE = 5
    PARTICLE_SPEED = 100
    FONT = 'Trebuchet-MS-Bold'
    FALLBACK_FONT = 'Arial'
    TEXT_COLOR = '#FFFFFF'
    CUSTOM_TEXT_COLOR = '#FFFFFF'
    STROKE_COLOR = 'black'
    BITRATE = '3000k'
    MUSIC_PATH = 'versus/music.mp3'
    CHARACTER1_DATA = {
        'name': 'Not Alone',
        'custom_text': 'Soothing self-made messenger',
        'files': {
            'intro': 'versus/not-alone-intro.mp4',
            'main': 'versus/not-alone.jpg',
            'win': 'versus/connect-me-win.mp4'
        }
    }
    CHARACTER2_DATA = {
        'name': 'ConnectMe',
        'custom_text': 'Vibrant social network from HiSphere',
        'files': {
            'intro': 'versus/connect-me-intro.mp4',
            'main': 'versus/connect-me.jpg',
            'win': 'versus/connect-me-win.mp4'
        }
    }
    CHARACTER_STATS = {
        'EXISTENCE TIME': (True, False),
        'LINES OF CODE': (False, True),
        'DEVELOPMENT TIME': (False, True),
        'STABILITY': (True, False),
        'SOLO DEVELOPER': (True, True),
        'MESSENGER': (True, False)
    }


class SlideshowConfig:
    RESOLUTION = (720, 1080)
    FPS = 60
    INTRO_DURATION = 3
    MIN_IMG_DURATION = 0.1
    MAX_IMG_DURATION = 2
    MAX_VIDEO_DURATION = 90
    MAX_IMAGES = 100
    INTRO_TEXT = 'POV: You are a God'
    MUSIC_PATH = 'slideshow/music.mp3'
    OUTPUT_VIDEO_PATH = 'slideshow/output.mp4'
    IMAGE_DIR = 'slideshow'
    CAPTIONS = [
        'You\'re absolutely stunning',
        'Your smile lights up the world',
        'You\'re one of a kind',
        'Radiant beauty inside and out',
        'You\'re simply breathtaking',
        'Pure perfection',
        'Angel on Earth',
        'Absolutely gorgeous',
        'You\'re incredible'
    ]
    COLOR_SCHEMES = [
        {
            'bg': (20, 20, 40),
            'text': (255, 255, 255),
            'accent': (255, 105, 180),
            'gradient': (60, 40, 80)
        },
        {
            'bg': (40, 20, 20),
            'text': (255, 255, 255),
            'accent': (255, 69, 0),
            'gradient': (80, 40, 40)
        },
        {
            'bg': (20, 40, 20),
            'text': (255, 255, 255),
            'accent': (50, 205, 50),
            'gradient': (40, 80, 40)
        },
        {
            'bg': (40, 20, 40),
            'text': (255, 255, 255),
            'accent': (147, 0, 211),
            'gradient': (80, 40, 80)
        },
        {
            'bg': (30, 30, 60),
            'text': (255, 255, 255),
            'accent': (255, 20, 147),
            'gradient': (60, 60, 120)
        },
        {
            'bg': (60, 30, 30),
            'text': (255, 255, 255),
            'accent': (255, 140, 0),
            'gradient': (120, 60, 60)
        }
    ]
    TRANSITION_TYPES = [
        'fade',
        'slide_left',
        'slide_right',
        'slide_up',
        'slide_down',
        'zoom_in',
        'zoom_out',
        'crossfade',
        'spin',
        'flip'
    ]
