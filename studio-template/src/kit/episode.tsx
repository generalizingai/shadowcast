import React, { useMemo } from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import { FPS, L } from "./theme";
import { resolveShots, ShotDef, Word } from "./timing";
import { Punch } from "./media";
import { SoundLayer } from "./audio";
import { Bug } from "./stage";
import { ChapterTag } from "./charts";

// One long-form episode: VO (audio/vo_tight.wav in the episode folder), word-anchored shots, SFX, and a corner overlay.
// rail "countdown": section names like "#7 NAME" drive the #10..#1 rail. rail "chapters": "CHAPTER n: TITLE" drives the chapter tag.
export type Section = { name: string; s: number; e: number };
export const LEAD = 0.4, END_HOLD = 3;
export const episodeFrames = (words: Word[]) => Math.ceil((words[words.length - 1].e + LEAD + END_HOLD) * FPS);

export const makeEpisode = (o: { words: Word[]; sections: Section[]; shots: ShotDef[]; rail?: "countdown" | "chapters" | "none"; total?: number }) => {
  const total = episodeFrames(o.words);
  const titles = o.sections.filter((s) => /^CHAPTER \d+/i.test(s.name)).map((s) => s.name.replace(/^CHAPTER \d+:\s*/i, ""));
  const marks = o.sections.map((x) => ({
    from: Math.round((x.s + LEAD + (o.rail === "chapters" ? 3 : 0)) * FPS),
    n: o.rail === "countdown" ? (/^#(\d+)/.exec(x.name)?.[1] ? Number(/^#(\d+)/.exec(x.name)![1]) : null)
      : o.rail === "chapters" ? (/^CHAPTER (\d+)/i.exec(x.name)?.[1] ? Number(/^CHAPTER (\d+)/i.exec(x.name)![1]) : null) : null,
  }));
  const Overlay: React.FC = () => {
    const f = useCurrentFrame();
    if (f > total - Math.round((END_HOLD + 2) * FPS)) return null;
    const cur = [...marks].reverse().find((c) => f >= c.from);
    if (o.rail === "chapters") return <><Bug n={null} />{cur?.n ? <ChapterTag n={cur.n} titles={titles} /> : null}</>;
    return <Bug n={o.rail === "countdown" ? cur?.n ?? null : null} total={o.total ?? 10} />;
  };
  const Episode: React.FC = () => {
    const shots = useMemo(() => resolveShots(o.shots, o.words, FPS, LEAD, total), []);
    return (
      <AbsoluteFill style={{ background: L.deep }}>
        <Sequence from={Math.round(LEAD * FPS)}><Audio src={staticFile("audio/vo_tight.wav")} /></Sequence>
        <SoundLayer shots={shots} words={o.words} fps={FPS} lead={LEAD} total={total} />
        {shots.map((s, i) => <Sequence key={i} from={s.from} durationInFrames={s.dur}><Punch>{s.el({ dur: s.dur, m: s.m })}</Punch></Sequence>)}
        <Overlay />
      </AbsoluteFill>
    );
  };
  return { Episode, frames: total };
};
