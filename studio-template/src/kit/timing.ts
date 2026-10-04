// Word-anchored timing: every shot and in-shot event is pinned to a spoken phrase,
// resolved against ElevenLabs word timestamps (audio/words.json).
export type Word = { w: string; s: number; e: number };

const norm = (x: string) => x.toLowerCase().replace(/[^a-z0-9]/g, "");

export function makeCursor(words: Word[]) {
  const n = words.map((w) => norm(w.w));
  let cursor = 0;
  // Returns the start time (s) of the next occurrence of `phrase` at or after the cursor.
  return (phrase: string): number => {
    const toks = phrase.split(/\s+/).map(norm).filter(Boolean);
    for (let i = cursor; i < n.length; i++) {
      let ok = true;
      for (let j = 0; j < toks.length; j++) {
        if (n[i + j] !== toks[j]) {
          ok = false;
          break;
        }
      }
      if (ok) {
        cursor = i + 1;
        return words[i].s;
      }
    }
    throw new Error(`anchor not found: "${phrase}" after word #${cursor} (${words[cursor]?.w})`);
  };
}

export type ShotCtx = { dur: number; m: number[] };
export type ShotDef = {
  at: string; // phrase that starts the shot ("" = time 0)
  marks?: string[]; // phrases inside the shot, resolved to frames relative to shot start
  el: (c: ShotCtx) => React.ReactNode;
  sfx?: string; // SFX at the shot start
  msfx?: (string | null)[]; // SFX per mark (null = silent; marks are silent unless listed)
  noWhoosh?: boolean;
};
export type Resolved = { from: number; dur: number; m: number[]; el: ShotDef["el"]; sfx?: string; msfx?: (string | null)[]; noWhoosh?: boolean };

export function resolveShots(shots: ShotDef[], words: Word[], fps: number, lead: number, end: number): Resolved[] {
  const find = makeCursor(words);
  const starts: { from: number; m: number[] }[] = shots.map((s) => {
    const t = s.at === "" ? -lead : find(s.at);
    const from = Math.round((t + lead) * fps);
    const m = (s.marks ?? []).map((p) => Math.max(0, Math.round((find(p) + lead) * fps) - from));
    return { from, m };
  });
  return shots.map((s, i) => {
    const from = starts[i].from;
    const to = i + 1 < shots.length ? starts[i + 1].from : end;
    if (to <= from) throw new Error(`shot ${i} ("${s.at}") has non-positive duration`);
    return { from, dur: to - from, m: starts[i].m, el: s.el, sfx: s.sfx, msfx: s.msfx, noWhoosh: s.noWhoosh };
  });
}
