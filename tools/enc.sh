#!/bin/bash
# 回のモジュールを書き出して、アップロード用(1080p)・確認用(720p)・380MBの分割・sha256 まで作る。
# 使い方: bash tools/enc.sh <モジュール名> <場面の数>   (途中で止まっても、続きから再開できる)
set -e
M=$1
cd /home/user/ushi-youtube/docu
N=$2
miss=$(for i in $(seq 0 $((N-1))); do f=$(printf ../output/segments_$M/%03d.mp4 $i); [ -s $f ] || echo $i; done | paste -sd,)
if [ -n "$miss" ]; then python3 film.py $M --jobs 3 --no-master --only $miss; else python3 film.py $M --jobs 1 --no-master --only 0; fi
cd ../output
E=enc_$M; mkdir -p $E upload
[ -s $E/audio.m4a ] || { ffmpeg -y -loglevel error -i ${M}_audio.wav -af loudnorm=I=-14:TP=-1.5:LRA=9 -ar 48000 -c:a aac -b:a 192k $E/a.tmp.m4a && mv $E/a.tmp.m4a $E/audio.m4a; }
: > $E/list.txt
for i in $(seq 0 $((N-1))); do
  b=$(printf %03d.mp4 $i)
  [ -s $E/$b ] || { ffmpeg -y -loglevel error -i segments_$M/$b -an -c:v libx264 -preset slow -crf 22 -maxrate 8M -bufsize 16M -pix_fmt yuv420p $E/tmp_$b && mv $E/tmp_$b $E/$b; }
  echo "file '$b'" >> $E/list.txt
done
ffmpeg -y -loglevel error -f concat -safe 0 -i $E/list.txt -i $E/audio.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart upload/${M}_1080p.mp4
ffmpeg -y -loglevel error -i upload/${M}_1080p.mp4 -vf scale=1280:720 -c:v libx264 -preset medium -crf 26 -c:a aac -b:a 128k -movflags +faststart ${M}_preview.mp4
cd upload && rm -f ${M}_1080p.mp4.part* && split -b 380M -d -a 1 ${M}_1080p.mp4 ${M}_1080p.mp4.part && sha256sum ${M}_1080p.mp4 ${M}_1080p.mp4.part* > ${M}_sha256.txt && cat ${M}_sha256.txt
