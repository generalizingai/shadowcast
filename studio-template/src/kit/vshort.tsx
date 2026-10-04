import React, { useMemo } from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import { FPS } from "./theme";
import { resolveShots, ShotDef, Word } from "./timing";
import { Punch } from "./media";
import { SoundLayer } from "./audio";
import { L } from "./theme";
import { Bug, Flash, Glam } from "./stage";
import { Big, Kicker } from "./parts";
import { Captions, Fix } from "./captions";
import { BRAND } from "../brand/brand";

// Native 9:16 Short (1080x1920), cut from one VO section of an episode and re-laid out per beat.
// Native full-height 9:16 (never a boxed 16:9 frame); captions small, in their own band, never over content.
// Safe zones: keep content between y≈260 and y=1420; the caption band is y≈1440-1520; the Shorts UI covers below that.
export const LEAD = 0.25, TAIL = 0.3, END = 2.6;
export const VW = 1080, VH = 1920;
// Cut-outs end at y=1420, just above the caption band.
export const STAR_Y = (h: number) => VH - 500 - h;

type Sec = { name: string; s: number; e: number };
export const section = (sections: Sec[], prefix: string) => sections.find((x) => x.name.startsWith(prefix))!;
export const vFramesFor = (sections: Sec[], prefix: string) => { const s = section(sections, prefix); return Math.ceil((s.e - s.s + LEAD + TAIL + END) * FPS); };

const Cap: React.FC<{ w: Word[]; fixes: Fix[] }> = ({ w, fixes }) => {
  const f = useCurrentFrame();
  return <div style={{ position: "absolute", left: 0, right: 0, top: 1440 }}><Captions words={w} t={f / FPS} lead={LEAD} accent={L.gold2} fixes={fixes} size={58} /></div>;
};

export const VShort: React.FC<{ words: Word[]; sections: Sec[]; prefix: string; shots: ShotDef[]; fixes?: Fix[]; endLine?: string; top?: React.ReactNode }> =
  ({ words, sections, prefix, shots, fixes = [], endLine = `FULL VIDEO\nON *${BRAND.name.toUpperCase()}*`, top }) => {
    const s = section(sections, prefix);
    const w = useMemo(() => words.filter((x) => x.s >= s.s - 0.01 && x.s < s.e + 0.01).map((x) => ({ ...x, s: x.s - s.s, e: x.e - s.s })), [words, s]);
    const total = vFramesFor(sections, prefix);
    const endAt = total - Math.round(END * FPS);
    const res = useMemo(() => resolveShots(shots, w, FPS, LEAD, endAt), [shots, w, endAt]);
    return (
      <AbsoluteFill style={{ background: L.deep }}>
        <Audio src={staticFile("audio/vo_tight.wav")} startFrom={Math.round((s.s - LEAD) * FPS)} endAt={Math.round((s.e + TAIL) * FPS)} />
        <SoundLayer shots={res} words={w} fps={FPS} lead={LEAD} total={total} />
        {res.map((r, i) => <Sequence key={i} from={r.from} durationInFrames={r.dur}><Punch>{r.el({ dur: r.dur, m: r.m })}</Punch></Sequence>)}
        <Sequence from={endAt}><Glam><Big text={endLine} size={120} y={-120} /><Kicker text="SUBSCRIBE FOR MORE" y={150} size={40} /></Glam><Flash /></Sequence>
        <Sequence durationInFrames={endAt}><div style={{ position: "absolute", left: 0, right: 0, top: 70 }}>{top ?? <Bug n={null} />}</div><Cap w={w} fixes={fixes} /></Sequence>
      </AbsoluteFill>
    );
  };
