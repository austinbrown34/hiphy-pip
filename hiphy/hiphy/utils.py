import subprocess
from .aubio import source, tempo, onset
from numpy import median, diff
from pydub import AudioSegment
import shlex
import os
import requests
import boto3
import magic
from botocore.client import Config
import tempfile


session = boto3.Session()
s3 = session.resource('s3')
s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
converted_bucket = 'ffmpeg-parallel-converted'


def get_video_duration(file):
    """Get the duration of a video using ffprobe."""
    cmd = 'ffprobe -i "{}" -show_entries format=duration -v quiet -of csv="p=0"'.format(file)
    output = subprocess.check_output(
        cmd,
        shell=True,
        stderr=subprocess.STDOUT
    )

    return float(output)


def get_beats(path, params=None, detection_mode='onset', quality='high'):
    # do something with quality
    """ Calculate the beats per minute (bpm) of a given file.
        path: path to the file
        param: dictionary of parameters
    """
    if params is None:
        params = {}

    samplerate, win_s, hop_s = 44100, 1024, 512
    if 'mode' in params:
        if params['mode'] in ['super-fast']:
            # super fast
            samplerate, win_s, hop_s = 4000, 128, 64
        elif params['mode'] in ['fast']:
            # fast
            samplerate, win_s, hop_s = 8000, 512, 128
        elif params['mode'] in ['default']:
            pass

    if 'samplerate' in params:
        samplerate = params['samplerate']
    if 'win_s' in params:
        win_s = params['win_s']
    if 'hop_s' in params:
        hop_s = params['hop_s']

    source_path = path
    o, s = None, None
    if detection_mode == 'onset':
        song = AudioSegment.from_wav(path)
        new = song.low_pass_filter(500)
        new.set_frame_rate(samplerate).export("mashup.wav", format="wav")
        source_path = "mashup.wav"
        hop_s = int(win_s // 1.001)
        s = source(source_path, samplerate, hop_s)
        samplerate = s.samplerate
        o = onset("default", win_s, hop_s, samplerate)
    else:
        s = source(path, samplerate, hop_s)
        samplerate = s.samplerate
        o = tempo("specdiff", win_s, hop_s, samplerate)
    beats = []
    total_frames = 0

    while True:
        nsamples, nread = s()
        is_beat = o(nsamples)
        if is_beat:
            this_beat = o.get_last_s()
            beats.append(this_beat)
        total_frames += nread
        if nread < hop_s:
            break
    return beats


def get_file_bpm(path, params=None, quality='high'):
    # do something with quality
    """ Calculate the beats per minute (bpm) of a given file.
        path: path to the file
        param: dictionary of parameters
    """
    if params is None:
        params = {}
    samplerate, win_s, hop_s = 44100, 1024, 512
    if 'mode' in params:
        if params['mode'] in ['super-fast']:
            samplerate, win_s, hop_s = 4000, 128, 64
        elif params['mode'] in ['fast']:
            samplerate, win_s, hop_s = 8000, 512, 128
        elif params['mode'] in ['default']:
            pass

    if 'samplerate' in params:
        samplerate = params['samplerate']
    if 'win_s' in params:
        win_s = params['win_s']
    if 'hop_s' in params:
        hop_s = params['hop_s']

    s = source(path, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("specdiff", win_s, hop_s, samplerate)
    beats = []
    total_frames = 0

    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_s()
            if o.get_confidence() > .5:
                beats.append(this_beat)
        total_frames += read
        if read < hop_s:
            break

    def beats_to_bpm(beats, path):
        if len(beats) > 1:
            if len(beats) < 4:
                print("few beats found in {:s}".format(path))
            bpms = 60./diff(beats)
            return median(bpms)
        else:
            print("not enough beats found in {:s}".format(path))
            return 0

    return beats_to_bpm(beats, path)


def trim_video(video, start, duration, scale, output, quality):
    # do something with quality
    command = """
                ffmpeg -y -i "{}" -ss {} -t {} -an -map 0:0 -map 0:0?
                -vf
                "scale={}:force_original_aspect_ratio=decrease,pad={}:(ow-iw)/2:(oh-ih)/2"
                -c:v libx264 -pix_fmt yuv420p -video_track_timescale 60000 "{}"
            """.format(video, start, duration, scale, scale, output)
    subprocess.call(shlex.split(command))


def trim_song(song, duration, output):
    command = "ffmpeg -y -i {} -t {} {}".format(song, duration, output)
    subprocess.call(shlex.split(command))


def multimedia_merge(text_file, song, video, quality):
    # do something with quality
    # command = "ffmpeg -y -f concat -safe 0 -i {} -i {} -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -af aresample=async=1 -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k {}".format(
    #     text_file,
    #     song,
    #     video
    # )
    # command = "ffmpeg -y -f concat -safe 0 -i {} -i {} -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -af aresample=async=1 -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k {}".format(
    #     text_file,
    #     song,
    #     video
    # )
    # command = "ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i {} -i {} {}".format(
    #     text_file,
    #     song,
    #     video
    # )
    # command = "-map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -af aresample=async=1 -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "movie=/tmp/work/logo.png [watermark]; [in]scale=$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:(ow-iw)/2:(oh-ih)/2 [scale]; [scale][watermark] overlay=main_w-overlay_w-10:main_h-overlay_h-10 [out]" -f mp4"
    
    # with tempfile.TemporaryDirectory() as tmpdir:
    #     with open(text_file, 'r') as f:
    #         lines = f.readlines()
    #         for i, line in enumerate(lines):
    #             filename

    os.putenv('FILE', text_file)
    os.putenv('SONG', song)
    os.putenv('RESOLUTION', "1920X1080")
    os.putenv('VID', video)

    subprocess.call(['sh', 'out-ffmpeg.sh'])
    # print(quality)
    # subprocess.call(shlex.split(command))


def multimedia_serve(media, durs, starts, song, destination, format, preprocess, resolution, quality):
    # do something with quality
    if preprocess:
        # starts = [str(int(start)).zfill(2) for start in starts]
        command = "bash live-encoder.sh"
    else:
        command = "bash test-encoder.sh"
    os.putenv('MEDIA', ' '.join(tuple(media)))
    os.putenv('DURS', ' '.join(tuple(durs)))
    os.putenv('STARTS', ' '.join(tuple(starts)))
    subprocess.call(['ffmpeg', '-y', '-i', song, '{}.aac'.format(song)])
    os.putenv('SONG', '{}.aac'.format(song))
    os.putenv('DESTINATION', destination)
    os.putenv('FORMAT', format)
    os.putenv('RESOLUTION', resolution)
    print(starts)
    subprocess.call(shlex.split(command))


def multimedia_post(post_url, payload, quality, audio_upload=False):
    # do something with quality
    subprocess.call(['ffmpeg', '-y', '-i', payload['song'], '{}.aac'.format(payload['song'])])
    payload['song'] = os.path.abspath('{}.aac'.format(payload['song']))
    if audio_upload:
        key = 'out/song.aac'
        upload(payload['song'], converted_bucket, key)
        song_url = 'https://s3.amazonaws.com/{}/{}'.format(
                converted_bucket,
                key
            )
        payload['song'] = song_url

    print(payload)
    r = requests.post(post_url, json=payload)
    print(r.status_code)


def upload(local_file, bucket, s3_file):
    content_type = magic.from_file(local_file, mime=True)
    s3.meta.client.upload_file(
        local_file,
        bucket,
        s3_file,
        {'ACL': 'public-read', 'ContentType': content_type}
    )

def get_presigned_url(bucket, key):
    # Generate the URL to get 'key-name' from 'bucket-name'
    # URL expires in 604800 seconds (seven days)
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key
        },
        ExpiresIn=86400
    )
    return url
