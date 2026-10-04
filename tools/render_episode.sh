#!/bin/zsh
# Render everything for one episode into episodes/<dir>/out/: long.mp4, short1.mp4, short2.mp4, thumb_A/B/C.jpg
#   render_episode.sh <slug> <ID> [long|shorts|thumbs ...]     (default: all)
set -e
SLUG=$1; ID=$2; shift 2; WHAT=${@:-long shorts thumbs}
HOMEF=${SHADOWCAST_HOME:-$HOME/Shadowcast}; ROOT="$HOMEF/$SLUG"; STUDIO="$ROOT/studio"; T=$(dirname "$0")
EP=$(python3 -c "import sys;sys.path.insert(0,'$T');from ep import find;print(find('$SLUG','$ID')['_dir'])")
mkdir -p "$EP/out"
comps=$(cd "$STUDIO" && npx remotion compositions src/index.ts --public-dir="$EP" --quiet 2>/dev/null | tr ' ' '\n')
for w in ${=WHAT}; do
  case $w in
    long) "$T/render.sh" "$STUDIO" "$ID" "$EP" "$EP/out/long.mp4" 4 ;;
    shorts) for k in 1 2; do echo "$comps" | grep -qx "${ID}Short$k" && "$T/render.sh" "$STUDIO" "${ID}Short$k" "$EP" "$EP/out/short$k.mp4" 2; done ;;
    thumbs) for x in A B C; do
      if echo "$comps" | grep -qx "${ID}Thumb$x"; then
        (cd "$STUDIO" && npx remotion still src/index.ts "${ID}Thumb$x" "$EP/out/thumb_$x.png" --public-dir="$EP" --log=error)
        python3 -c "from PIL import Image;Image.open('$EP/out/thumb_$x.png').convert('RGB').save('$EP/out/thumb_$x.jpg',quality=90)" && rm "$EP/out/thumb_$x.png"
      fi; done ;;
  esac
done
ls -la "$EP/out"
