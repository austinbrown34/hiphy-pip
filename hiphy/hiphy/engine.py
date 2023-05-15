import random
import re
import os
from  hiphy.utils import (
    get_video_duration, trim_video, get_beats,
    multimedia_merge, multimedia_serve, multimedia_post
)


class MediaPreProcessor:
    def __init__(self, config):
        self.config = config

    def run(self, media_file, work_dir, duration, resolution, i=0):
        fname, ext = os.path.splitext(media_file)
        start = self.get_media_start(media_file, duration)
        clean_name = re.sub(r'[\W_]+', '', fname)
        output_name = '{}-{}{}'.format(
            i, clean_name, '.mp4').replace(' ', '-')
        output_path = os.path.join(work_dir, output_name)
        if self.config['mode'] == 'sequential':
            trim_video(
                media_file,
                start,
                duration,
                resolution,
                output_path,
                self.config['quality']
            )
        else:
            trim_video(
                media_file,
                start,
                duration,
                resolution,
                output_path,
                self.config['quality']
            )
        return (output_path, duration, start)


    def get_media_start(self, media_file, duration, video_duration=None):
        if video_duration is None:
            video_duration = get_video_duration(media_file)
        setpts = duration / video_duration
        latest_start = video_duration - duration
        return round(random.uniform(0, latest_start), 2)


class BeatProcessor:
    def __init__(self, config):
        self.config = config

    def run(self, song, params):
        beats = []
        if self.config['mode'] == 'onset':
            beats = get_beats(
                song, params, self.config['mode'], self.config['quality']
            )
        else:
            beats = get_beats(
                song, params, self.config['mode'], self.config['quality']
            )
        return beats


class Finisher:
    def __init__(self, config):
        self.config = config

    def run(self, song, **kwargs):
        if self.config['mode'] == 'video':
            if self.config['style'] == 'batch':
                multimedia_merge(
                    kwargs['text_file'],
                    song,
                    kwargs['output_video'],
                    self.config['quality']
                )
            else:
                multimedia_serve(
                    kwargs['media'],
                    kwargs['durs'],
                    kwargs['starts'],
                    song,
                    kwargs['output_video'],
                    'mp4',
                    kwargs['preprocess'],
                    kwargs['resolution'],
                    self.config['quality']
                )
        elif self.config['mode'] == 'stream':
            multimedia_serve(
                kwargs['media'],
                kwargs['durs'],
                kwargs['starts'],
                song,
                kwargs['destination'],
                'flv',
                kwargs['preprocess'],
                kwargs['resolution'],
                self.config['quality']
            )
        else:
            payload = {
                'urls': kwargs['media'],
                'starts': kwargs['starts'],
                'durs': kwargs['durs'],
                'song': song,
                'callback': kwargs['callback'],
                'resolution': kwargs['resolution'],
                'rtmp': kwargs['rtmp'],
                'email': kwargs['email']
            }
            multimedia_post(
                kwargs['post_url'],
                payload,
                self.config['quality'],
                audio_upload=kwargs['audio_upload']
            )


class Engine:
    def __init__(self, config):
        self.config = config
        self.media_preprocessor = MediaPreProcessor(config['media-preprocessor'])
        self.beat_processor = BeatProcessor(config['beat-processor'])
        self.finisher = Finisher(config['finisher'])
