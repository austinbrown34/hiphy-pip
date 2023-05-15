#!/bin/bash

eval media=($MEDIA)
eval durs=($DURS)
eval starts=($STARTS)
song=$SONG
destination=$DESTINATION
format=$FORMAT
resolution=$RESOLUTION

# for i in "${!media[@]}"; do
#   echo "$i"
#   echo "00:00:${starts[$i]}"
#   echo "*************************************************"
#   ffmpeg -y -hide_banner -nostats -re -ss "${starts[$i]}" -i $(youtube-dl -g "${media[$i]}" -f bestvideo[ext=mp4]) -t "${durs[$i]}" -c:v mpeg2video -f mpegts -
# done | pv| ffmpeg -y -hide_banner -nostats -re -fflags +igndts -thread_queue_size 512 -i pipe:0 -fflags +genpts -i "$song" -map 0:0 -map 1:0 -s 640x360 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" -f "$format" "$destination"



# for i in "${!media[@]}"; do
#   echo "$i"
#   echo "00:00:${starts[$i]}"
#   echo "*************************************************"
#   ffmpeg -y -hide_banner -nostats -re -ss "${starts[$i]}" -i $(youtube-dl -g "${media[$i]}" -f bestvideo[ext=mp4]) -t "${durs[$i]}" -c:v copy -f mpegts -
# done | pv| ffmpeg -y -hide_banner -nostats -re -fflags +igndts -thread_queue_size 512 -i pipe:0 -fflags +genpts -i "$song" -map 0:0 -map 1:0 -s 640x360 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -f "$format" "$destination"


for i in "${!media[@]}"; do
  echo "$i"
  echo "00:00:${starts[$i]}"
  echo "*************************************************"
  ffmpeg -y -hide_banner -nostats -re -ss "${starts[$i]}" -i $(youtube-dl -g "${media[$i]}" -f bestvideo[ext=mp4]) -t "${durs[$i]}" -c:v mpeg2video -f mpegts -
done | ffmpeg -y -hide_banner -nostats -re -fflags +igndts -thread_queue_size 512 -i pipe:0 -fflags +genpts -i "$song" -map 0:0 -map 1:0 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -vf "scale=$resolution:force_original_aspect_ratio=decrease,pad=$resolution:(ow-iw)/2:(oh-ih)/2" -f "$format" "$destination"






# for i in "${!media[@]}"; do
#   echo "$i"
#   echo "00:00:${starts[$i]}"
#   echo "*************************************************"
#   ffmpeg -y -hide_banner -nostats -ss "${starts[$i]}" -i $(youtube-dl -g "${media[$i]}" -f bestvideo[ext=mp4]) -t "${durs[$i]}" -c:v copy -f mpegts -
# done | ffmpeg -y -hide_banner -nostats -fflags +igndts -thread_queue_size 512 -i pipe:0 -fflags +genpts -i "$song" -map 0:0 -map 1:0 -s 640x360 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -f "$format" "$destination"


# ffmpeg -ss 30 -i $(youtube-dl -g https://www.youtube.com/watch\?v\=ewufRwrayTI -f bestvideo[ext=mp4]) -t 5 -c:v copy t.ts

# for i in "${!media[@]}"; do
#     ffmpeg -ss "${starts[$i]}" -i $(youtube-dl -g "${media[$i]}"  -f bestvideo[ext=mp4]) -t 5 -c:v copy "$i".mp4
# done
