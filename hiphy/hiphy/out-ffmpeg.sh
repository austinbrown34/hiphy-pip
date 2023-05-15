#!/bin/bash
echo "$FILE"
echo "$SONG"
echo "$RESOLUTION"
echo "$VID"
# echo "$RTMP"
# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -i "$SONG" -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "scale=$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:(ow-iw)/2:(oh-ih)/2" -f mp4 /tmp/out.mp4 -loglevel debug
rm -rf /tmp/work/song.aac
rm -rf /tmp/work/logo.png
rm -rf /tmp/work/out.mp4

ffmpeg -y -protocol_whitelist file,http,https,tcp,tls -i "$SONG" song.aac
# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -c copy /tmp/work/all.ts



# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -c copy -bsf:a aac_adtstoasc all.mp4

# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -c copy -bsf:a aac_adtstoasc /tmp/work/all.mp4



# ffmpeg -y -i /tmp/work/all.mp4 -i /tmp/work/song.wav -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "scale=$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:(ow-iw)/2:(oh-ih)/2" -f mp4 /tmp/work/out.mp4
# ffmpeg -y -i /tmp/work/all.mp4 -i /tmp/work/song.wav -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec copy -strict experimental -vcodec libx264 -r 25 -b:v 500k -vf "scale=$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:(ow-iw)/2:(oh-ih)/2" -f mp4 /tmp/work/out.mp4



# ffmpeg -y -i /tmp/work/all.mp4 -i /tmp/work/song.wav -map 0:0 -map 1:0 -c:v copy -c:a aac -b:a 256k -shortest /tmp/work/out.mp4

# ffmpeg -y -i /tmp/work/all.mp4 -i "$SONG" -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "scale=$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:(ow-iw)/2:(oh-ih)/2" -f mp4 /tmp/work/out.mp4




# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -i /tmp/work/song.aac -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -af aresample=async=1 -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "scale=$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:(ow-iw)/2:(oh-ih)/2" -f mp4 /tmp/work/out.mp4
ffmpeg -y -protocol_whitelist file,http,https,tcp,tls -i "https://s3.amazonaws.com/ffmpeg-parallel-converted/gifs/big.png" -vf "scale=200:200" logo.png


# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -i song.aac -map 0:0 -map 1:0 "$VID"

ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -i song.aac -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -af aresample=async=1 -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "movie=logo.png [watermark]; [in]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2 [scale]; [scale][watermark] overlay=main_w-overlay_w-10:main_h-overlay_h-10 [out]" -f mp4 "$VID"





# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -i "https://s3.amazonaws.com/ffmpeg-parallel-converted/gifs/big.png" -i /tmp/work/song.aac -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -af aresample=async=1 -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -filter_complex "[1]scale=200:200[b];[0][b]overlay=main_w-overlay_w-10:main_h-overlay_h-10" -f mp4 /tmp/work/out.mp4
# -filter_complex "[1]scale=200:200[b];[0][b]overlay=main_w-overlay_w-10:main_h-overlay_h-10"











# ffmpeg -y -i /tmp/work/all.mp4 -i /tmp/work/song.aac -map 0:0 -map 1:0 -c:v copy /tmp/work/out.mp4



# ffmpeg -y -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -an -map 0:0 -map 0:1? -c:v libx264 -profile baseline -video_track_timescale 60000 /tmp/work/all.ts

# ffmpeg -y -i /tmp/work/all.mp4 -i /tmp/work/song.aac -map 0:1 -map 1:0 -vcodec copy -acodec copy /tmp/work/out.mp4
# ffmpeg -y -i /tmp/work/all.mp4 -i /tmp/work/song.aac -c copy -map 0:v:0 1:a:0 /tmp/work/out.mp4
# ffmpeg -y -i /tmp/work/all.mp4 -i /tmp/work/song.aac -map 0:0 -map 1:0 -vcodec copy -vf "scale=$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:(ow-iw)/2:(oh-ih)/2" -acodec copy /tmp/work/out.mp4
# ffmpeg -y -nostdin -f concat -safe 0 -protocol_whitelist file,http,https,tcp,tls -i "$FILE" -i "$SONG" -vf scale=1280X720 -c:v libx264 "$VID"
