#!/bin/zsh
# Render one composition and master its audio to -14 LUFS (YouTube level).
#   render.sh <studio dir> <composition id> <episode dir> <out.mp4> [concurrency]
# Long videos default to concurrency 4; pass 2 for Shorts (they embed video and can eat several GB of swap).
set -e
STUDIO=$1; COMP=$2; EP=$3; OUT=$4; CONC=${5:-4}
free=$(df -g "$EP" | tail -1 | awk '{print $4}'); [ "$free" -lt ${SHADOWCAST_MIN_FREE_GB:-3} ] && { echo "only ${free} GB free; need ~3 GB to render" >&2; exit 1; }
RAW="${OUT%.mp4}.raw.mp4"
(cd "$STUDIO" && npx remotion render src/index.ts "$COMP" "$RAW" --public-dir="$EP" --codec=h264 --crf=20 --concurrency=$CONC --log=error) 2>&1 | grep -v "network requests" || true
[ -f "$RAW" ] || { echo "render failed" >&2; exit 1; }
J=$(ffmpeg -hide_banner -i "$RAW" -vn -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
read i tp lra th off <<< "$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")"
if [[ "$i" == "-inf" ]]; then  # silent track (test renders): nothing to normalise
  ffmpeg -v error -y -i "$RAW" -c:v copy -c:a aac -b:a 192k -ar 48000 "$OUT"
else
ffmpeg -v error -y -i "$RAW" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=${i}:measured_TP=${tp}:measured_LRA=${lra}:measured_thresh=${th}:offset=${off}:linear=true,alimiter=limit=0.75:attack=2:release=60:level=false" -ar 48000 -c:a aac -b:a 192k "$OUT"
fi
rm -f "$RAW"
ffprobe -v error -show_entries stream=width,height:format=duration,size -of compact "$OUT"
