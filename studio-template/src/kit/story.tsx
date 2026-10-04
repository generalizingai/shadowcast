import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { ease, pop } from "./pieces";
import { A, foil, L, LFF } from "./theme";
import { Big, Stamp, Star } from "./parts";

// Story beats used by countdown and documentary episodes. Faces are cut-out paths ("cut/name.png").

// A row of people sliding in along the bottom; silhouettes until revealAt (great for cold opens).
export const Lineup: React.FC<{ faces: string[]; at?: number; revealAt?: number }> = ({ faces, at = 0, revealAt = 1e9 }) => {
  const f = useCurrentFrame();
  const step = Math.min(180, 1620 / faces.length);
  return (
    <AbsoluteFill>
      {faces.map((k, i) => (
        <Star key={k + i} src={k} x={960 - (step * (faces.length - 1)) / 2 + i * step} y={520 + (i % 2) * 40} h={560 - (i % 2) * 40} at={at + i * 4} sil={f < revealAt} />
      ))}
    </AbsoluteFill>
  );
};

// One big line at a time, switching on marks ("PRISON CELLS" / "COURTROOMS" / ...).
export const Teasers: React.FC<{ items: string[]; m: number[]; size?: number }> = ({ items, m, size = 170 }) => {
  const f = useCurrentFrame();
  const cur = items.reduce((acc, _, i) => (f >= (m[i] ?? 0) ? i : acc), 0);
  return <Big key={cur} text={items[cur]} at={m[cur] ?? 0} size={items[cur].length > 22 ? Math.round(size * 0.8) : size} />;
};

// A stack of case folders with a stamp landing on top.
export const FileStack: React.FC<{ labels: string[]; stamp: string; stampAt?: number }> = ({ labels, stamp, stampAt = 12 }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      {labels.slice(0, 4).map((lab, i) => {
        const p = pop(f, i * 3, 14);
        return (
          <div key={i} style={{ position: "absolute", left: 560 + i * 26, top: 300 - i * 30, width: 800, height: 520, background: i % 2 ? "#D9C79E" : "#E6D5AC",
            borderRadius: 8, boxShadow: "10px 14px 0 #0008", transform: `rotate(${-6 + i * 4}deg) translateY(${(1 - p) * 500}px)` }}>
            <div style={{ position: "absolute", left: 30, top: -34, width: 230, height: 50, background: i % 2 ? "#D9C79E" : "#E6D5AC", borderRadius: "8px 8px 0 0" }} />
            <div style={{ position: "absolute", left: 50, top: 50, fontFamily: LFF.type, fontWeight: 700, fontSize: 34, color: "#5a4a2a" }}>{lab}</div>
          </div>
        );
      })}
      <Stamp text={stamp} at={stampAt} color={L.gold} size={130} y={40} />
    </AbsoluteFill>
  );
};

// A price tag that re-prices on a mark ($40 -> $15,000).
export const PriceTag: React.FC<{ from: string; fromSub: string; to?: string; toSub?: string; at?: number; swap?: number; x?: number; y?: number }> =
  ({ from, fromSub, to, toSub, at = 0, swap = 1e9, x = 360, y = 0 }) => {
    const f = useCurrentFrame();
    if (f < at) return null;
    const p = pop(f, at, 10), sw = !!to && f >= swap, q = sw ? pop(f, swap, 9) : 1;
    return (
      <div style={{ position: "absolute", left: 960 + x, top: 540 + y, transform: `translate(-50%,-50%) rotate(${sw ? 6 : -8}deg) scale(${p * (0.8 + 0.2 * q)})` }}>
        <div style={{ background: sw ? L.gold : L.ivory, padding: "40px 70px 40px 110px", clipPath: "polygon(18% 0, 100% 0, 100% 100%, 18% 100%, 0 50%)", boxShadow: "0 0 0 6px #000" }}>
          <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 150, color: L.navy, lineHeight: 1, whiteSpace: "nowrap" }}>{sw ? to : from}</div>
          <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 28, color: L.navy, letterSpacing: 5, whiteSpace: "nowrap" }}>{sw ? toSub : fromSub}</div>
        </div>
        <div style={{ position: "absolute", left: 40, top: "50%", width: 30, height: 30, marginTop: -15, borderRadius: 15, background: L.navy }} />
      </div>
    );
  };

// Two people side by side with "paid -> got" lines (B appears on m[0], B's result on m[1]).
type Side = { name: string; face: string; left: string; right: string };
export const Versus: React.FC<{ a: Side; b: Side; m: number[] }> = ({ a, b, m }) => {
  const f = useCurrentFrame();
  const col = (c: Side, x: number, at: number, gotAt: number) => (f < at ? null : (
    <div style={{ position: "absolute", left: x, top: 0, width: 960, height: 1080 }}>
      <Star src={c.face} x={480} y={210} h={560} at={at} name={c.name} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 830, textAlign: "center", opacity: ease(f, at + 6, at + 14), whiteSpace: "nowrap" }}>
        <span style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 100, ...foil }}>{c.left}</span>
        <span style={{ fontFamily: LFF.cond, fontSize: 90, color: L.ivory, margin: "0 26px" }}>→</span>
        <span style={{ fontFamily: LFF.cond, fontSize: 96, color: L.ivory, opacity: ease(f, gotAt, gotAt + 6) }}>{c.right}</span>
      </div>
    </div>
  ));
  return (
    <AbsoluteFill>
      {col(a, 0, 0, 6)}
      <div style={{ position: "absolute", left: 958, top: 140, width: 4, height: 800, background: `linear-gradient(180deg, transparent, ${L.gold}, transparent)` }} />
      {col(b, 960, m[0] ?? 0, m[1] ?? 0)}
    </AbsoluteFill>
  );
};

// Tear-off calendar page; ring draws an accent circle round the day.
export const Calendar: React.FC<{ month: string; day: string; at?: number; x?: number; ring?: number }> = ({ month, day, at = 0, x = 0, ring = 1e9 }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = pop(f, at, 12), r = ease(f, ring, ring + 14);
  return (
    <div style={{ position: "absolute", left: 960 + x, top: 540, transform: `translate(-50%,-50%) rotate(-4deg) scale(${p})`, width: 520, background: "#fff", boxShadow: "16px 20px 0 #000b" }}>
      <div style={{ background: L.red, color: "#fff", fontFamily: LFF.cond, fontSize: 90, textAlign: "center", padding: "10px 0", letterSpacing: 6 }}>{month}</div>
      <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 300, color: L.navy, textAlign: "center", lineHeight: 1.1 }}>{day}</div>
      <svg style={{ position: "absolute", left: 60, top: 140 }} width={400} height={340}>
        <ellipse cx={200} cy={170} rx={180} ry={150} fill="none" stroke={L.gold} strokeWidth={14} strokeDasharray={1100} strokeDashoffset={1100 * (1 - r)} strokeLinecap="round" />
      </svg>
    </div>
  );
};

// Respectful card for a person who died or was harmed: no photo, no SFX, slow fade.
export const Memorial: React.FC<{ name: string; line: string; at?: number }> = ({ name, line, at = 0 }) => {
  const f = useCurrentFrame();
  const o = ease(f, at, at + 20);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", background: "rgba(2,8,18,0.6)" }}>
      <div style={{ opacity: o, textAlign: "center" }}>
        <div style={{ width: 120, height: 3, background: L.dim, margin: "0 auto 30px" }} />
        <div style={{ fontFamily: LFF.serif, fontWeight: 700, fontSize: 96, color: L.ivory, letterSpacing: 4 }}>{name}</div>
        <div style={{ fontFamily: LFF.sans, fontWeight: 700, fontSize: 40, color: L.dim, letterSpacing: 8, marginTop: 18 }}>{line}</div>
        <div style={{ width: 120, height: 3, background: L.dim, margin: "30px auto 0" }} />
      </div>
    </AbsoluteFill>
  );
};

// Grid of up to 10 framed faces with rank badges (outro recap).
export const Grid: React.FC<{ items: { face: string; badge: string }[] }> = ({ items }) => {
  const f = useCurrentFrame();
  const cols = Math.min(5, items.length), rows = Math.ceil(items.length / cols);
  return (
    <AbsoluteFill>
      {items.map((it, i) => {
        const c = i % cols, r = Math.floor(i / cols), a = i * 2;
        if (f < a) return null;
        return (
          <div key={i} style={{ position: "absolute", left: 960 + (c - (cols - 1) / 2) * 360, top: 540 - (rows * 420) / 2 + 30 + r * 420, width: 300, height: 380, transform: `translate(-50%,0) scale(${pop(f, a, 12)})`,
            background: `radial-gradient(circle at 50% 30%, ${L.navy2}, ${L.deep})`, border: `3px solid ${L.gold}`, overflow: "hidden", boxShadow: "0 18px 40px #000b" }}>
            <Img src={staticFile(A(it.face))} style={{ position: "absolute", left: "50%", bottom: 0, height: 360, transform: "translateX(-50%)" }} />
            <div style={{ position: "absolute", left: 0, top: 0, background: L.gold, color: L.deep, fontFamily: LFF.serif, fontWeight: 900, fontSize: 40, padding: "2px 14px" }}>{it.badge}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
