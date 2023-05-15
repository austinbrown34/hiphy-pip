import os, sys, time, re, operator, csv
import requests
from bs4 import BeautifulSoup
import youtube_dl
import json
import boto3
import shlex
import subprocess
from pytube import YouTube, Search


class S3Snatch(object):
    @staticmethod
    def get_matching_s3_keys(bucket, prefix=''):
        s3 = boto3.resource('s3')
        s3_bucket = s3.Bucket(bucket)
        keys = []
        for o in s3_bucket.objects.filter(Prefix=prefix):
            if o.key.endswith('mp4'):
                keys.append(o.key)
        return keys

    @staticmethod
    def cdn_urls(bucket, prefix=''):
        keys = S3Snatch.get_matching_s3_keys(bucket, prefix)
        urls = []
        for key in keys:
            urls.append('https://{}.s3.amazonaws.com/{}'.format(
                bucket,
                key
            ))
        return urls


class YTSnatch(object):
    @staticmethod
    def can_get_streams(result):
        try:
            streams = result.streams
            return True
        except:
            return False

    @staticmethod
    def get_keyword_urls_v2(keywords, max_keyword_videos, fmt='mp4'):
        results = []
        for keyword in keywords:
            s = Search(keyword)
            while len(s.results) < max_keyword_videos:
                s.get_next_results()
            kw_results = [x.watch_url for x in s.results if YTSnatch.can_get_streams(x)][:max_keyword_videos]
            results += kw_results
        return results

    @staticmethod
    def get_keyword_vids_v2(keywords, folder, max_keyword_videos):
        ytlinks = YTSnatch.get_keyword_urls_v2(keywords, max_keyword_videos)
        for page_url in ytlinks:
            print("Trying {}".format(page_url))
            video = YouTube(page_url)
            print(folder)
            stream = video.streams.filter(file_extension='mp4').get_highest_resolution()
            stream.download(folder)

    @staticmethod
    def get_keyword_urls_durations_v2(keywords, max_keyword_videos, fmt='mp4'):
        urls = YTSnatch.get_keyword_urls_v2(keywords, max_keyword_videos)
        durations = []
        for url in urls:
            duration = YTSnatch.duration(url)
            durations.append(duration)
        return urls, durations

    @staticmethod
    def get_keyword_vids(keywords, folder, max_keyword_videos):
        ytlinks = YTSnatch.get_keyword_urls(keywords, max_keyword_videos)
        for page_url in ytlinks:
            print("Trying {}".format(page_url))
            # page_response = requests.get(page_url)
            ydl_opts = {
                'outtmpl': os.path.join(folder, '%(id)s.%(ext)s'),
                'external_downloader': 'ffmpeg',
                'external_downloader_args': ['-t', '60'],
                'ignore_errors': True,
                'format': 'bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            }
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([page_url])
            except Exception as e:
                print(str(e))
                pass


    @staticmethod
    def get_audio_url_from_keyword(keyword):
        base_url = 'https://www.youtube.com'
        song_url = []
        formatted_keyword = keyword.replace(' ', '+')
        url = 'https://www.youtube.com/results?search_query={}'.format(
            formatted_keyword
        )
        print("Trying {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [
            link.find(href=True)['href'] for link in soup.find_all(
                'h3',
                class_='yt-lockup-title'
            ) if (
                link.find(href=True)['href'].startswith('/watch') and
                'list=' not in link.find(href=True)['href']
                )
        ]
        song_url = '{}{}'.format(
            base_url,
            links[0]
        )
        return song_url


    @staticmethod
    def get_keyword_urls(keywords, max_keyword_videos, fmt='mp4'):
        base_url = 'https://www.youtube.com'
        ytlinks = []
        for keyword in keywords:
            results = YTSnatch.get_keyword_results(keyword, max_keyword_videos, fmt)
            ytlinks += [
                result["url"]
                for result in results
            ]
            # formatted_keyword = keyword.replace(' ', '+')
            # url = 'https://www.youtube.com/results?search_query={}'.format(
            #     formatted_keyword
            # )
            # print("Trying {}".format(url))
            # response = requests.get(url)
            # soup = BeautifulSoup(response.content, 'html.parser')
            # links = [
            #     link.find(href=True)['href'] for link in soup.find_all(
            #         'h3',
            #         class_='yt-lockup-title'
            #     ) if (
            #         link.find(href=True)['href'].startswith('/watch') and
            #         'list=' not in link.find(href=True)['href']
            #         )
            # ]
            # ytlinks += [
            #     '{}{}'.format(
            #         base_url,
            #         link
            #     ) for link in links if YTSnatch.has_format(
            #         '{}{}'.format(base_url, link),
            #         'mp4'
            #     )
            # ][:max_keyword_videos]
        return ytlinks

    @staticmethod
    def get_keyword_results(keyword, max_keyword_videos, fmt='mp4'):
        YDL_OPTIONS = {'format': fmt, 'noplaylist':'True', 'ignore_errors': True}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                requests.get(keyword)
            except:
                video = ydl.extract_info(f"ytsearch{max_keyword_videos}:{keyword}", download=False)['entries']
            else:
                video = ydl.extract_info(keyword, download=False)

        return video

    @staticmethod
    def get_keyword_urls_durations(keywords, max_keyword_videos, fmt='mp4'):
        base_url = 'https://www.youtube.com'
        ytlinks = []
        durations = []
        for keyword in keywords:
            results = YTSnatch.get_keyword_results(keyword, max_keyword_videos, fmt)
            ytlinks += [
                result["url"]
                for result in results
                if result["duration"] > 0
            ]
            durations += [
                result["duration"]
                for result in results
                if result["duration"] > 0
            ]
        #     formatted_keyword = keyword.replace(' ', '+')
        #     url = 'https://www.youtube.com/results?search_query={}'.format(
        #         formatted_keyword
        #     )
        #     print("Trying {}".format(url))
        #     response = requests.get(url)
        #     soup = BeautifulSoup(response.content, 'html.parser')
        #     links = [
        #         link.find(href=True)['href'] for link in soup.find_all(
        #             'h3',
        #             class_='yt-lockup-title'
        #         ) if link.find(href=True)['href'].startswith('/watch')
        #     ]
        #     ytlinks += [
        #         '{}{}'.format(
        #             base_url,
        #             link
        #         ) for link in links if YTSnatch.has_format(
        #             '{}{}'.format(base_url, link),
        #             'mp4'
        #         )
        #     ][:max_keyword_videos]
        # durations = [YTSnatch.duration(l) for l in ytlinks]
        return ytlinks, durations

    @staticmethod
    def duration(url):
        with youtube_dl.YoutubeDL() as ydl:
            video_data = ydl.extract_info(url, download=False)
            return video_data.get('duration')
        return 0

    @staticmethod
    def has_format(url, fmt):
        try:
            with youtube_dl.YoutubeDL() as ydl:
                video_data = ydl.extract_info(url, download=False)
                for format in video_data.get('formats', []):
                    if format.get('ext') == 'mp4':
                        return True
                return False
        except:
            return False

    @staticmethod
    def get_audio_from_url(url, song):
        command = "ffmpeg -y -i $(youtube-dl -f bestaudio -g {}) {}".format(
            url,
            song
        )
        subprocess.call(command, shell=True)
