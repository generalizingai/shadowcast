import React, { useMemo } from "react";
import { Audio, Sequence, staticFile } from "remotion";
import { Resolved, Word } from "./timing";

// Sound layer: a few deliberate SFX on key beats, plus an optional music bed that ducks under the voice (off by default;
// pass music="assets/audio/music.wav" only if the reference channel uses music and you have a licensed track).
// SFX files live in the episode public dir under assets/audio/: whoosh pop click thud thunder ding typing riser tick.
export const SFX_GAIN: Record<string, number> = {
  whoosh: 0.12, pop: 0.18, click: 0.22, thud: 0.38, thunder: 0.5, ding: 0.24, typing: 0.18, riser: 0.25, tick: 0.15,
};
const SFX_LEN: Record<string, number> = { whoosh: 14, pop: 6, click: 3, thud: 14, thunder: 96, ding: 42, typing: 27, riser: 33, tick: 2 };

export const SoundLayer: React.FC<{
  shots: Resolved[]; words: Word[]; fps: number; lead: number; total: number;
  music?: string | null; musicSpeech?: number; musicGap?: number;
}> = ({ shots, words, fps, lead, total, music = null, musicSpeech = 0.092, musicGap = 0.16 }) => {
  // Per-frame music gain: ducked while any word is being spoken (+ short hang), smoothed with attack/release.
  const gain = useMemo(() => {
    const speaking = new Uint8Array(total);
    for (const w of words) {
      const a = Math.max(0, Math.floor((w.s + lead - 0.05) * fps)), b = Math.min(total, Math.ceil((w.e + lead + 0.25) * fps));
      for (let i = a; i < b; i++) speaking[i] = 1;
    }
    const g = new Float32Array(total); let v = musicGap;
    for (let i = 0; i < total; i++) {
      const target = speaking[i] ? musicSpeech : musicGap;
      v += (target - v) * (target < v ? 0.35 : 0.06); // fast duck, slow release
      g[i] = v;
    }
    return g;
  }, [words, fps, lead, total, musicSpeech, musicGap]);

  const hits: { at: number; name: string }[] = [];
  // SFX are opt-in: nothing plays unless the shot asks for it. Use them sparingly (a few per minute).
  shots.forEach((s) => {
    if (s.sfx) hits.push({ at: s.from, name: s.sfx });
    s.m.forEach((mm, k) => {
      const name = s.msfx ? s.msfx[k] : null;
      if (name) hits.push({ at: s.from + mm, name });
    });
  });

  return (
    <>
      {music && <Audio src={staticFile(music)} volume={(f) => gain[Math.min(total - 1, f)]} />}
      {hits.map((h, i) => (
        <Sequence key={i} from={h.at} durationInFrames={(SFX_LEN[h.name] ?? 30) + 6}>
          <Audio src={staticFile(`assets/audio/${h.name}.wav`)} volume={SFX_GAIN[h.name] ?? 0.25} />
        </Sequence>
      ))}
    </>
  );
};
