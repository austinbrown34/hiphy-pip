#!/bin/bash
echo "$START"
echo "$VID"
echo "$DUR"
# echo "$REVERSE"
echo "$OUT"
# echo $(youtube-dl -f bestvideo[ext=mp4] -g "$VID")
# ffmpeg -y -ss "$START" -i $(youtube-dl -f bestvideo[ext=mp4] -g "$VID" --geo-bypass -i -c --no-cache-dir) -t "$DUR" -an -map 0:0 -map 0:1? -c:a aac -ar 48000 -ac 2 -vf scale=1280X720 -c:v libx264 -profile baseline -video_track_timescale 60000 /tmp/out.ts
# rm -rf /tmp/preout.ts
# rm -rf /tmp/out.ts


 ffmpeg -y -ss "$START" -i $(youtube-dl -f bestvideo[ext=mp4] -g "$VID" --geo-bypass -i -c --no-cache-dir) -t "$DUR" -an -map 0:0 -map 0:1? -c:a aac -ar 48000 -ac 2 -vf scale=1920:1080 -c:v libx264 -profile baseline -video_track_timescale 60000 "$OUT"


# if [ "$REVERSE" -eq "TRUE" ]; then
#     ffmpeg -y -ss "$START" -i $(youtube-dl -f bestvideo[ext=mp4] -g "$VID" --geo-bypass -i -c --no-cache-dir) -t "$DUR" -an -map 0:0 -map 0:1? -c:a aac -ar 48000 -ac 2 -vf scale=1920:1080 -c:v libx264 -profile baseline -video_track_timescale 60000 /tmp/preout.ts
#     ffmpeg -y -i /tmp/preout.ts -vf reverse /tmp/out.ts
# else
#     ffmpeg -y -ss "$START" -i $(youtube-dl -f bestvideo[ext=mp4] -g "$VID" --geo-bypass -i -c --no-cache-dir) -t "$DUR" -an -map 0:0 -map 0:1? -c:a aac -ar 48000 -ac 2 -vf scale=1920:1080 -c:v libx264 -profile baseline -video_track_timescale 60000 /tmp/out.ts
#     # ffmpeg -y -i /tmp/preout.ts -vf reverse /tmp/out.ts
# fi


# ffmpeg -y -ss "$START" -i $(youtube-dl -f bestvideo[ext=mp4] -g "$VID" --geo-bypass -i -c --no-cache-dir) -t "$DUR" -c copy -bsf h264_mp4toannexb -video_track_timescale 60000 /tmp/out.ts


# ffmpeg -y -hide_banner -nostats -re -ss "$START" -i $(youtube-dl -g "$VID" -f bestvideo[ext=mp4] --geo-bypass -i -c --no-cache-dir) -t "$DUR" -c:v mpeg2video /tmp/out.ts
