from hiphy.vidsnatch import S3Snatch, YTSnatch
from hiphy.utils import trim_song
from hiphy.engine import Engine
import os
import random
import itertools
import re


ACCEPTED_MEDIA_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png'],
    'video': ['mp4', 'mov', 'mkv']
}

HIPHY_ENGINE = {
    'media-preprocessor': {
        'mode': ['sequential', 'parallel'],
        'quality': ['low', 'medium', 'high']
    },
    'beat-processor': {
        'mode': ['onset', 'bpm'],
        'quality': ['low', 'medium', 'high']
    },
    'finisher': {
        'mode': ['video', 'stream', 'post'],
        'style': ['batch', 'live'],
        'quality': ['low', 'medium', 'high']
    }

}


class Hiphy:
    def __init__(self, **kwargs):
        self.song = kwargs.get('song', None)
        self.media_folder = kwargs.get('media_folder', '.')
        if None in [self.song]:
            raise Exception(
                """ A song must be specified along with the path to
                    the folder where your media resides. """
            )
        self.output_video = kwargs.get('output_video', 'final.mp4')
        self.mode = kwargs.get('mode', 'default')
        self.transition_min = int(kwargs.get('transition_min', 0))
        self.random_transition_prob = float(
            kwargs.get('random_transition_prob', 0.5)
        )
        self.max_length = int(kwargs.get('max_length', -1))
        self.resolution = kwargs.get('resolution', '1280:720')
        self.keywords = kwargs.get('keywords', None)
        self.max_keyword_videos = int(kwargs.get('max_keyword_videos', 20))
        self.beats = kwargs.get('beats', None)
        self.work_dir = kwargs.get('work_dir', 'work_dir')
        self.preprocess = kwargs.get('preprocess', True)
        self.audio_upload = kwargs.get('audio_upload', False)
        self.callback = kwargs.get('callback', None)
        self.rtmp = kwargs.get('rtmp', None)
        self.email = kwargs.get('email', None)
        self.post_url = kwargs.get('post_url', None)
        self.engine_config = {
            'media-preprocessor': {
                'mode': 'sequential',
                'quality': 'high'
            },
            'beat-processor': {
                'mode': 'onset',
                'quality': 'high'
            },
            'finisher': {
                'mode': 'video',
                'style': 'batch',
                'quality': 'high'
            }
        }

        self.configure_engine(
            kwargs.get('media-preprocessor', None),
            kwargs.get('beat-processor', None),
            kwargs.get('finisher', None)
        )

        self.engine = Engine(self.engine_config)
        if self.engine.finisher.config['mode'] == 'post':
            self.preprocess = False

        self.media = []
        self.beat_map = []
        self.urls = []
        self.url_durations = []


    def configure_engine(self, mp, bp, finisher):
        print("** Configuring engine **")
        configuration = {}
        if mp is not None:
            mpx = mp.split('-')
            configuration['media-preprocessor'] = {
                'mode': mpx[0],
                'quality': mpx[1]
            }
        if bp is not None:
            bpx = bp.split('-')
            configuration['beat-processor'] = {
                'mode': bpx[0],
                'quality': bpx[1]
            }
        if finisher is not None:
            finisherx = finisher.split('-')
            configuration['finisher'] = {
                'mode': finisherx[0],
                'style': finisherx[1],
                'quality': finisherx[2]
            }

        self.engine_config.update(configuration)
        print("** Engine configured as: **")
        print(self.engine_config)

    def handle_song(self):
        if 'http' in self.song:
            print("** Getting song from url **")
            YTSnatch.get_audio_from_url(self.song, 'song.wav')
            self.song = 'song.wav'
        if not '.wav' in self.song:
            print("** Getting song from keyword **")
            url = YTSnatch.get_audio_url_from_keyword(self.song)
            YTSnatch.get_audio_from_url(url, 'song.wav')
            self.song = 'song.wav'
        if self.max_length != -1:
            fname, ext = os.path.splitext(self.song)
            trimmed_song = '{}_{}{}'.format(fname, self.max_length, ext)
            trim_song(
                self.song,
                self.max_length,
                trimmed_song
            )
            self.song = trimmed_song

    def handle_keywords(self):
        if self.keywords is not None:
            print("** Getting videos for keywords **")
            if self.preprocess:
                YTSnatch.get_keyword_vids_v2(
                    self.keywords,
                    self.media_folder,
                    self.max_keyword_videos
                )
            else:
                self.urls, self.url_durations = YTSnatch.get_keyword_urls_durations_v2(
                    self.keywords,
                    self.max_keyword_videos
                )


    def handle_beats(self, clean=True):
        if clean or self.beats is None:
            print("** Finding beats **")
            self.get_beats()

    def handle_media(self, clean=True):
        if clean or self.media.length == 0:
            print("** Getting media files **")
            self.get_media()

    def handle_work_dir(self, clean=True):
        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)

    def handle_shuffle(self):
        if self.preprocess:
            print("** Shuffling media **")
            self.shuffle_media()

    def handle_beat_map(self, min_dur=None):
        print("** Creating beat mapping **")
        self.get_beat_map(min_dur=min_dur)

    def handle_write_beat_map(self, output_file):
        with open(output_file, 'w') as fp:
            fp.writelines(["{}\n".format(x) for x in self.beat_map])

    def handle_separate_beat_map(self):
        media, durs, starts = self.separate_beat_map()


    def handle_media(self, clean=True):
        if clean or self.media.length == 0:
            print("** Getting media files **")
            self.get_media()


    def handle_finisher(self, clean=True):
        kwargs = {}
        media, durs, starts = self.separate_beat_map()
        kwargs = {
            'media': media,
            'durs': durs,
            'starts': starts,
            'destination': '',
            'callback': self.callback,
            'rtmp': self.rtmp,
            'post_url': self.post_url,
            'preprocess': self.preprocess,
            'email': self.email,
            'resolution': self.resolution,
            'text_file': os.path.join(self.media_folder, 'images.txt'),
            'output_video': self.output_video,
            'audio_upload': self.audio_upload
        }
        if self.engine.finisher.config['style'] == 'batch':
            print("** Writing beat mapping **")
            self.write_beat_map()
            print("** Making final video **")
            self.engine.finisher.run(
                self.song,
                **kwargs
            )
        else:
            print("** Making final video **")
            self.engine.finisher.run(
                self.song,
                **kwargs
            )



    def run(self, clean=True):
        if 'http' in self.song:
            print("** Getting song from url **")
            YTSnatch.get_audio_from_url(self.song, 'song.wav')
            self.song = 'song.wav'
        if not '.wav' in self.song:
            print("** Getting song from keyword **")
            url = YTSnatch.get_audio_url_from_keyword(self.song)
            YTSnatch.get_audio_from_url(url, 'song.wav')
            self.song = 'song.wav'
        if self.max_length != -1:
            fname, ext = os.path.splitext(self.song)
            trimmed_song = '{}_{}{}'.format(fname, self.max_length, ext)
            trim_song(
                self.song,
                self.max_length,
                trimmed_song
            )
            self.song = trimmed_song
        if self.keywords is not None:
            print("** Getting videos for keywords **")
            if self.preprocess:
                YTSnatch.get_keyword_vids_v2(
                    self.keywords,
                    self.media_folder,
                    self.max_keyword_videos
                )
            else:
                self.urls, self.url_durations = YTSnatch.get_keyword_urls_durations(
                    self.keywords,
                    self.max_keyword_videos
                )
        if clean or self.beats is None:
            print("** Finding beats **")
            self.get_beats()
        if clean or self.media.length == 0:
            print("** Getting media files **")
            self.get_media()
        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)
        if self.preprocess:
            print("** Shuffling media **")
            self.shuffle_media()
        print("** Creating beat mapping **")
        self.get_beat_map()
        kwargs = {}
        media, durs, starts = self.separate_beat_map()
        kwargs = {
            'media': media,
            'durs': durs,
            'starts': starts,
            'destination': '',
            'callback': self.callback,
            'rtmp': self.rtmp,
            'post_url': self.post_url,
            'preprocess': self.preprocess,
            'email': self.email,
            'resolution': self.resolution,
            'text_file': os.path.join(self.media_folder, 'images.txt'),
            'output_video': self.output_video,
            'audio_upload': self.audio_upload
        }
        print(kwargs)

        if self.engine.finisher.config['style'] == 'batch':
            print("** Writing beat mapping **")
            self.write_beat_map()
            print("** Making final video **")
            self.engine.finisher.run(
                self.song,
                **kwargs
            )
        else:
            print("** Making final video **")
            self.engine.finisher.run(
                self.song,
                **kwargs
            )

    def get_beats(self):
        self.beats = self.engine.beat_processor.run(
            self.song, {'mode': self.mode}
        )


    def get_media(self):
        if self.preprocess:
            extensions = list(
                itertools.chain.from_iterable(
                    ACCEPTED_MEDIA_EXTENSIONS.values()
                )
            )
            for media_file in os.listdir(self.media_folder):
                if not media_file.startswith('.'):
                    _, ext = os.path.splitext(media_file)
                    if ext.strip('.').lower() in extensions:
                        self.media.append(os.path.join(self.media_folder, media_file))
        else:
            self.media = self.urls


    def shuffle_media(self):
        random.shuffle(self.media)


    def get_beat_map(self, min_dur=None):
        media_index = 0
        last_beat = float(0.000)
        for i, beat in enumerate(self.beats):
            if media_index >= len(self.media):
                media_index = 0
            media_file = self.media[media_index]
            fname, ext = os.path.splitext(media_file)
            duration = float("{0:.2f}".format(float(float(beat) - last_beat)))
            random_transition = random.choices(
                population=[True, False],
                weights=[
                    self.random_transition_prob,
                    1 - self.random_transition_prob
                ],
                k=1
            ).pop()
            if duration > self.transition_min or random_transition:
                last_beat = float(beat)
                if ext.strip('.').lower() in ACCEPTED_MEDIA_EXTENSIONS['video']:
                    if self.engine.finisher.config['style'] == 'batch':
                        self.beat_map.append(
                            self.engine.media_preprocessor.run(
                                media_file,
                                self.work_dir,
                                duration,
                                self.resolution,
                                i
                            )
                        )
                    else:
                        self.beat_map.append(
                            (
                                media_file,
                                duration,
                                self.engine.media_preprocessor.get_media_start(
                                    media_file,
                                    duration
                                )
                            )
                        )
                else:
                    if 'http' in media_file:
                        self.beat_map.append(
                            (
                                media_file,
                                duration,
                                self.engine.media_preprocessor.get_media_start(
                                    media_file,
                                    duration if min_dur is None else min_dur,
                                    self.url_durations[media_index]
                                )
                            )
                        )
                    else:
                        self.beat_map.append(
                            (
                                media_file,
                                duration,
                                0.00
                            )
                        )
            media_index += 1


    def separate_beat_map(self):
        media = []
        durs = []
        starts = []
        for group in self.beat_map:
            media.append(group[0])
            durs.append(str(group[1]))
            starts.append(str(group[2]))
        return media, durs, starts


    def write_beat_map(self):
        text_file_path = os.path.join(self.media_folder, 'images.txt')
        with open(text_file_path, 'w') as text_file:
            for pair in self.beat_map:
                text_file.write(
                    'file {}\noutpoint {}\n'.format(
                        os.path.relpath(pair[0], self.media_folder),
                        pair[1]
                    )
                )
