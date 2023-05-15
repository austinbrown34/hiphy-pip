#!/bin/bash

eval media=($MEDIA)
eval durs=($DURS)
eval starts=($STARTS)
song=$SONG
destination=$DESTINATION
format=$FORMAT

for i in "${!media[@]}"; do
  echo "$i"
  ffmpeg -y -hide_banner -nostats -re -ss "${starts[$i]}" -i "${media[$i]}" -t "${durs[$i]}" -c:v mpeg2video -f mpegts -
done | pv| ffmpeg -y -hide_banner -nostats -re -fflags +igndts -thread_queue_size 512 -i pipe:0 -fflags +genpts -i "$song" -map 0:0 -map 1:0 -s 640x360 -crf 30 -preset ultrafast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -vcodec libx264 -r 25 -b:v 500k -f "$format" "$destination"
