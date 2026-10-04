import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { clamp, ease, pop } from "./pieces";
import { A, foil, L, LFF } from "./theme";
import { Star } from "./parts";
import { BRAND } from "../brand/brand";

// Data-driven graphics for story and countdown episodes. All positions are 1920x1080 unless a prop says otherwise.
// Layout rules learned the hard way: labels never wrap (nowrap + fixed heights), narrow segments stagger their labels,
// and nothing sits closer than ~60px to a frame edge.

// Chapter opener: "CHAPTER 3" kicker, big serif title, accent rule, faint numeral behind.
export const ChapterCard: React.FC<{ n: number; title: string }> = ({ n, title }) => {
  const f = useCurrentFrame();
  const p = pop(f, 0, 13), q = pop(f, 6, 14), r = ease(f, 8, 24);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", fontFamily: LFF.serif, fontWeight: 900, fontSize: 760, color: "#ffffff08", lineHeight: 1 }}>{n}</div>
      <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 36, letterSpacing: 18, color: L.gold2, opacity: p }}>CHAPTER {n}</div>
      <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 150, color: L.ivory, marginTop: 10, textAlign: "center", lineHeight: 1.02, maxWidth: 1500,
        transform: `translateY(${(1 - q) * 40}px)`, opacity: q, textShadow: "0 8px 0 #0008" }}>{title}</div>
      <div style={{ width: 700 * r, height: 5, marginTop: 34, background: `linear-gradient(90deg, transparent, ${L.gold}, transparent)` }} />
    </AbsoluteFill>
  );
};

// Chapter progress (top right), shown over every shot of a chapter.
export const ChapterTag: React.FC<{ n: number; titles: string[] }> = ({ n, titles }) => (
  <div style={{ position: "absolute", right: 44, top: 38, display: "flex", alignItems: "center", gap: 14 }}>
    <div style={{ display: "flex", gap: 6 }}>
      {titles.map((_, i) => <div key={i} style={{ width: i + 1 === n ? 34 : 12, height: 12, borderRadius: 6, background: i + 1 <= n ? L.gold : "rgba(255,255,255,0.2)" }} />)}
    </div>
    <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 20, letterSpacing: 4, color: L.ivory, textShadow: "0 2px 8px #000", whiteSpace: "nowrap" }}>{titles[n - 1]?.toUpperCase()}</div>
  </div>
);

// Episode title card: wordmark, kicker, big foil title, italic subline.
export const TitleCard: React.FC<{ kicker?: string; title: string; sub?: string }> = ({ kicker, title, sub }) => {
  const f = useCurrentFrame();
  const p = pop(f, 0, 12), q = pop(f, 10, 12);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <Img src={staticFile(A(BRAND.wordmark))} style={{ width: 380, opacity: ease(f, 0, 12), marginBottom: 26 }} />
      {kicker && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 40, letterSpacing: 16, color: L.gold2, opacity: p }}>{kicker}</div>}
      <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 190, lineHeight: 0.95, textAlign: "center", maxWidth: 1600, ...foil, transform: `scale(${0.7 + 0.3 * p})` }}>{title}</div>
      {sub && <div style={{ fontFamily: LFF.serifI, fontStyle: "italic", fontSize: 56, color: L.ivory, marginTop: 24, opacity: q }}>{sub}</div>}
    </AbsoluteFill>
  );
};

// End card: wordmark, tagline, subscribe pill. Works at 16:9 and 9:16.
export const EndCard: React.FC<{ line?: string }> = ({ line = BRAND.tagline }) => {
  const f = useCurrentFrame();
  const { width } = useVideoConfig();
  const p = pop(f, 0, 12), q = pop(f, 14, 10);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <Img src={staticFile(A(BRAND.wordmark))} style={{ width: width > 1200 ? 900 : 720, transform: `scale(${0.8 + 0.2 * p})`, opacity: p }} />
      <div style={{ fontFamily: LFF.serifI, fontStyle: "italic", fontSize: 60, color: L.ivory, marginTop: 30, opacity: ease(f, 8, 18), textAlign: "center", maxWidth: "86%" }}>{line}</div>
      <div style={{ marginTop: 50, background: L.gold, color: L.deep, fontFamily: LFF.sans, fontWeight: 900, fontSize: 44, letterSpacing: 6, padding: "18px 56px", borderRadius: 60,
        transform: `scale(${q})`, boxShadow: `0 0 40px ${L.gold}88` }}>SUBSCRIBE</div>
    </AbsoluteFill>
  );
};

// Three side-by-side people with a label each (one can be highlighted). cols[i].face is a cut-out path ("cut/x.png").
export const Trio: React.FC<{ cols: { face: string; who: string; what: string }[]; m: number[]; hot?: number }> = ({ cols, m, hot = cols.length - 1 }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      {cols.map((c, i) => {
        const at = m[i] ?? i * 20;
        if (f < at) return null;
        const h = i === hot;
        const p = pop(f, at, 13);
        return (
          <div key={i} style={{ position: "absolute", left: 340 + i * 620, top: 0, height: 1080, width: 560, transform: "translateX(-50%)" }}>
            <Star src={c.face} x={280} y={h ? 190 : 270} h={h ? 680 : 600} at={at} glow={h} />
            <div style={{ position: "absolute", left: 0, right: 0, top: 892, textAlign: "center", transform: `scale(${p})` }}>
              <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 30, letterSpacing: 6, color: h ? L.gold2 : L.dim, whiteSpace: "nowrap" }}>{c.who}</div>
              <div style={{ fontFamily: LFF.cond, fontSize: 96, lineHeight: 1, whiteSpace: "nowrap", ...(h ? foil : { color: L.ivory }) }}>{c.what}</div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Contract / document whose clauses highlight on their marks. Always labelled as a summary, never the original.
export const Contract: React.FC<{ head: string; sub?: string; clauses: { t: string; at: number }[]; note?: string; stamp?: { t: string; at: number; color?: string } }> =
  ({ head, sub, clauses, note = "SUMMARY · NOT THE ORIGINAL DOCUMENT", stamp }) => {
    const f = useCurrentFrame();
    const p = pop(f, 0, 14);
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", left: 360, right: 360, top: 140, bottom: 120, background: L.paper, boxShadow: "18px 22px 0 #000b", padding: "54px 70px",
          transform: `rotate(-1.5deg) translateY(${(1 - p) * 300}px)`, fontFamily: LFF.type, color: "#222" }}>
          <div style={{ fontWeight: 700, fontSize: 50, borderBottom: "3px solid #333", paddingBottom: 14 }}>{head}</div>
          {sub && <div style={{ fontSize: 30, color: "#666", marginTop: 10 }}>{sub}</div>}
          <div style={{ marginTop: 36 }}>
            {clauses.map((c, i) => {
              const s = ease(f, c.at, c.at + 16);
              return (
                <div key={i} style={{ fontSize: 46, lineHeight: 1.45, marginBottom: 14, opacity: f >= c.at - 12 ? 1 : 0.25 }}>
                  <span style={{ fontWeight: 700 }}>{i + 1}. </span>
                  <span style={{ background: `linear-gradient(90deg, ${L.gold2}cc ${s * 100}%, transparent ${s * 100}%)` }}>{c.t}</span>
                </div>
              );
            })}
          </div>
          <div style={{ position: "absolute", right: 30, bottom: 20, fontFamily: LFF.sans, fontWeight: 700, fontSize: 18, letterSpacing: 3, color: "#999" }}>{note}</div>
        </div>
        {stamp && f >= stamp.at && (
          <div style={{ position: "absolute", left: 1180, top: 700, transform: `translate(-50%,-50%) rotate(-12deg) scale(${interpolate(f - stamp.at, [0, 5], [2.2, 1], clamp)})`,
            border: `10px double ${stamp.color ?? L.red}`, color: stamp.color ?? L.red, fontFamily: LFF.cond, fontSize: 110, padding: "6px 34px", background: "rgba(239,231,214,0.85)", whiteSpace: "nowrap" }}>{stamp.t}</div>
        )}
      </AbsoluteFill>
    );
  };

// Horizontal timeline; stops light up on their marks, labels alternate above/below.
export const Timeline: React.FC<{ stops: { label: string; sub?: string; at: number }[]; y?: number; note?: string; noteAt?: number }> = ({ stops, y = 0, note, noteAt = 0 }) => {
  const f = useCurrentFrame();
  const n = stops.length, x0 = 300, x1 = 1620;
  const lit = stops.filter((s) => f >= s.at).length;
  const prog = lit <= 1 ? 0 : ease(f, stops[lit - 1].at, stops[lit - 1].at + 18, (lit - 2) / (n - 1), (lit - 1) / (n - 1));
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: x0, top: 540 + y, width: x1 - x0, height: 8, background: "rgba(255,255,255,0.15)", borderRadius: 4 }} />
      <div style={{ position: "absolute", left: x0, top: 540 + y, width: (x1 - x0) * prog, height: 8, background: L.gold, borderRadius: 4, boxShadow: `0 0 18px ${L.gold}` }} />
      {stops.map((s, i) => {
        const x = x0 + ((x1 - x0) * i) / Math.max(1, n - 1);
        const on = f >= s.at;
        return (
          <div key={i} style={{ position: "absolute", left: x, top: 544 + y, transform: "translate(-50%,-50%)", textAlign: "center" }}>
            <div style={{ width: 40, height: 40, borderRadius: 20, margin: "0 auto", background: on ? L.gold : L.navy, border: `5px solid ${L.gold}`, transform: `scale(${on ? pop(f, s.at) : 1})` }} />
            <div style={{ position: "absolute", left: "50%", top: i % 2 ? 60 : -150, transform: "translateX(-50%)", whiteSpace: "nowrap", opacity: on ? 1 : 0.25 }}>
              <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 60, color: L.ivory }}>{s.label}</div>
              {s.sub && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 26, letterSpacing: 4, color: L.gold2 }}>{s.sub}</div>}
            </div>
          </div>
        );
      })}
      {note && f >= noteAt && <div style={{ position: "absolute", left: 0, right: 0, top: 820 + y, textAlign: "center", fontFamily: LFF.serifI, fontStyle: "italic", fontSize: 54, color: L.ivory, opacity: ease(f, noteAt, noteAt + 10) }}>{note}</div>}
    </AbsoluteFill>
  );
};

// A grid of locked tiles with an owner line; unlockAt turns them accent-gold and hands them to unlockOwner.
export const LockGrid: React.FC<{ items: string[]; owner: string; ownerAt?: number; unlockAt?: number; unlockOwner?: string; y?: number; scale?: number; cols?: number }> =
  ({ items, owner, ownerAt = 0, unlockAt = 1e9, unlockOwner = "", y = 0, scale = 1, cols = 3 }) => {
    const f = useCurrentFrame();
    const open = f >= unlockAt;
    return (
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div style={{ transform: `translateY(${y}px) scale(${scale})`, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 360px)`, gap: 26 }}>
            {items.map((t, i) => {
              const p = pop(f, i * 3, 13);
              const u = open ? pop(f, unlockAt + i * 3, 11) : 0;
              return (
                <div key={t + i} style={{ height: 200, position: "relative", transform: `scale(${p})`, background: open ? `linear-gradient(160deg, ${L.gold2}, ${L.gold} 55%, ${L.goldDeep})` : `linear-gradient(160deg, ${L.navy2}, ${L.navy})`,
                  border: `4px solid ${open ? L.gold2 : `${L.gold}55`}`, boxShadow: open ? `0 0 ${30 * u}px ${L.gold}` : "0 14px 30px #000a", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: t.length > 9 ? 44 : 60, color: open ? L.deep : L.ivory, textAlign: "center", padding: 12 }}>{t}</div>
                  <svg style={{ position: "absolute", right: 14, top: 10, transform: `rotate(${open ? -25 * u : 0}deg) translateY(${open ? -12 * u : 0}px)` }} width={40} height={46} viewBox="0 0 40 46">
                    <path d={open ? "M10 20 V12 a10 10 0 0 1 20 0" : "M10 20 V12 a10 10 0 0 1 20 0 V20"} fill="none" stroke={open ? L.deep : L.gold} strokeWidth={5} />
                    <rect x={4} y={20} width={32} height={24} rx={4} fill={open ? L.deep : L.gold} />
                  </svg>
                </div>
              );
            })}
          </div>
          {f >= ownerAt && (
            <div style={{ marginTop: 40, display: "flex", alignItems: "center", gap: 20, transform: `scale(${pop(f, ownerAt)})`, whiteSpace: "nowrap" }}>
              <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 32, letterSpacing: 8, color: L.dim }}>OWNED BY</div>
              <div style={{ fontFamily: LFF.cond, fontSize: 84, color: open ? L.gold2 : L.red, letterSpacing: 3 }}>{open ? unlockOwner : owner}</div>
            </div>
          )}
        </div>
      </AbsoluteFill>
    );
  };

// Two-row "this → that" comparison; the second row is the highlighted one. strikeAt crosses out the first row's result.
export const Switch: React.FC<{ header: string; rows: [{ label: string; to: string }, { label: string; to: string; at: number }]; strikeAt?: number }> = ({ header, rows, strikeAt = 1e9 }) => {
  const f = useCurrentFrame();
  const row = (label: string, to: string, at: number, hot: boolean, y: number) => (f < at ? null : (
    <div style={{ position: "absolute", left: 260, right: 260, top: y, display: "flex", alignItems: "center", gap: 40, transform: `translateX(${(1 - pop(f, at, 13)) * -200}px)`, opacity: pop(f, at) }}>
      <div style={{ flex: 1, background: hot ? L.gold : "rgba(255,255,255,0.08)", border: `4px solid ${hot ? L.gold2 : "#ffffff33"}`, padding: "26px 36px", fontFamily: LFF.serif, fontWeight: 900, fontSize: 64, color: hot ? L.deep : L.ivory, whiteSpace: "nowrap" }}>{label}</div>
      <svg width={170} height={60}><path d="M0 30 H140 M115 8 L160 30 L115 52" stroke={hot ? L.gold : L.dim} strokeWidth={10} fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
      <div style={{ width: 520, fontFamily: LFF.cond, fontSize: 82, color: hot ? L.gold2 : L.dim, whiteSpace: "nowrap", textDecoration: !hot && f >= strikeAt ? "line-through" : undefined }}>{to}</div>
    </div>
  ));
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 0, right: 0, top: 150, textAlign: "center", fontFamily: LFF.sans, fontWeight: 800, fontSize: 34, letterSpacing: 12, color: L.gold2 }}>{header}</div>
      {row(rows[0].label, rows[0].to, 0, false, 330)}
      {row(rows[1].label, rows[1].to, rows[1].at, true, 600)}
    </AbsoluteFill>
  );
};

// Vertical bar comparison (2-6 bars). The last bar is highlighted unless hot says otherwise. Labels sit on one baseline.
export const Bars: React.FC<{ title: string; data: { t: string; v: number; sub?: string }[]; ats: number[]; fmt?: (v: number) => string; hot?: number }> =
  ({ title, data, ats, fmt = (v) => Math.round(v).toLocaleString("en-US"), hot = data.length - 1 }) => {
    const f = useCurrentFrame();
    const max = Math.max(...data.map((d) => d.v)), H0 = 470, gap = Math.min(360, 1400 / data.length);
    const x0 = 960 - (gap * (data.length - 1)) / 2;
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", left: 0, right: 0, top: 110, textAlign: "center", fontFamily: LFF.sans, fontWeight: 800, fontSize: 32, letterSpacing: 10, color: L.gold2 }}>{title}</div>
        {data.map((d, i) => {
          const at = ats[i] ?? 0, g = ease(f, at, at + 22);
          return (
            <div key={d.t} style={{ position: "absolute", left: x0 + i * gap, bottom: 150, width: gap - 20, transform: "translateX(-50%)", display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
              <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 56, color: L.ivory, opacity: f >= at ? 1 : 0, marginBottom: 12, whiteSpace: "nowrap" }}>{f >= at ? fmt(d.v * g) : ""}</div>
              <div style={{ width: Math.min(230, gap - 60), height: (H0 * d.v * g) / max, background: i === hot ? `linear-gradient(180deg, ${L.gold2}, ${L.goldDeep})` : `linear-gradient(180deg, ${L.ivory}, #b9b2a3)`, boxShadow: i === hot ? `0 0 30px ${L.gold}88` : undefined }} />
              <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 38, color: L.ivory, marginTop: 16, whiteSpace: "nowrap", height: 48 }}>{d.t}</div>
              {d.sub && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 20, letterSpacing: 4, color: L.gold2, whiteSpace: "nowrap" }}>{d.sub}</div>}
            </div>
          );
        })}
      </AbsoluteFill>
    );
  };

// Stacked bar breakdown (2-5 segments) whose labels stagger onto a second row when segments get narrow.
export const Stacked: React.FC<{ title: string; segs: { t: string; v: number; label: string; color?: string }[]; ats: number[]; note?: string }> = ({ title, segs, ats, note }) => {
  const f = useCurrentFrame();
  const total = segs.reduce((a, s) => a + s.v, 0), W0 = 1500;
  const palette = [L.gold, L.gold2, "#d9cfb8", "#8fa4c4", L.dim];
  let x = 210, lastRowEnd = [0, 0];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 210, top: 250, fontFamily: LFF.sans, fontWeight: 800, fontSize: 32, letterSpacing: 10, color: L.gold2 }}>{title}</div>
      {segs.map((s, i) => {
        const w = (W0 * s.v) / total, at = ats[i] ?? 0, g = ease(f, at, at + 16), left = x;
        x += w;
        const row = left < lastRowEnd[0] + 20 ? 1 : 0; // drop a row if the label would collide with the previous one
        lastRowEnd[row] = left + 280;
        const c = s.color ?? palette[i % palette.length];
        return (
          <React.Fragment key={s.t}>
            <div style={{ position: "absolute", left, top: 360, width: w * g, height: 170, background: c, borderRight: `4px solid ${L.deep}` }} />
            {f >= at && <div style={{ position: "absolute", left: left + 8, top: row ? 720 : 560, width: 270, whiteSpace: "nowrap", opacity: ease(f, at + 6, at + 16) }}>
              <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 64, color: L.ivory }}>{s.label}</div>
              <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 22, letterSpacing: 3, color: c }}>{s.t}</div>
            </div>}
          </React.Fragment>
        );
      })}
      {note && <div style={{ position: "absolute", left: 210, top: 880, fontFamily: LFF.serifI, fontStyle: "italic", fontSize: 40, color: L.dim, opacity: ease(f, (ats[segs.length - 1] ?? 0) + 20, (ats[segs.length - 1] ?? 0) + 34) }}>{note}</div>}
    </AbsoluteFill>
  );
};

// Growth line (2-5 points) with optional dashed reference line. Value above each point, date below it.
export const Climb: React.FC<{ title: string; pts: { d: string; v: number; label: string }[]; ats: number[]; max: number; ticks?: { v: number; label: string }[]; ref?: { v: number; label: string; at: number } }> =
  ({ title, pts, ats, max, ticks = [], ref }) => {
    const f = useCurrentFrame();
    const X = (i: number) => 520 + (i * 1120) / Math.max(1, pts.length - 1), Y = (v: number) => 880 - (v / max) * 620;
    const lit = pts.filter((_, i) => f >= (ats[i] ?? 0)).length;
    const path = pts.slice(0, Math.max(1, lit)).map((p, i) => `${i ? "L" : "M"} ${X(i)} ${Y(p.v)}`).join(" ");
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", left: 200, top: 120, fontFamily: LFF.sans, fontWeight: 800, fontSize: 32, letterSpacing: 10, color: L.gold2 }}>{title}</div>
        <svg style={{ position: "absolute", left: 0, top: 0 }} width={1920} height={1080}>
          {ticks.map((t) => <g key={t.v}><line x1={330} x2={1760} y1={Y(t.v)} y2={Y(t.v)} stroke="#ffffff1a" strokeWidth={2} /><text x={190} y={Y(t.v) + 10} fill={L.dim} fontSize={26} fontFamily="sans-serif">{t.label}</text></g>)}
          {ref && f >= ref.at && <g opacity={ease(f, ref.at, ref.at + 12)}><line x1={330} x2={1760} y1={Y(ref.v)} y2={Y(ref.v)} stroke={L.red} strokeWidth={4} strokeDasharray="16 12" />
            <text x={340} y={Y(ref.v) - 16} fill={L.red} fontSize={30} fontWeight={800} fontFamily="sans-serif">{ref.label}</text></g>}
          <path d={path} fill="none" stroke={L.gold} strokeWidth={10} strokeLinejoin="round" strokeLinecap="round" />
        </svg>
        {pts.map((p, i) => f >= (ats[i] ?? 0) && (
          <div key={p.d} style={{ position: "absolute", left: X(i), top: Y(p.v), transform: `translate(-50%,-50%) scale(${pop(f, ats[i] ?? 0)})` }}>
            <div style={{ width: 34, height: 34, borderRadius: 17, background: L.gold, border: `5px solid ${L.deep}` }} />
            <div style={{ position: "absolute", left: "50%", top: -112, transform: "translateX(-50%)", whiteSpace: "nowrap", fontFamily: LFF.serif, fontWeight: 900, fontSize: 70, ...foil }}>{p.label}</div>
            <div style={{ position: "absolute", left: "50%", top: 48, transform: "translateX(-50%)", whiteSpace: "nowrap", fontFamily: LFF.sans, fontWeight: 800, fontSize: 24, letterSpacing: 4, color: L.ivory }}>{p.d}</div>
          </div>
        ))}
      </AbsoluteFill>
    );
  };

// Ranked horizontal bars with round face badges (face optional: monogram fallback). Row 0 is highlighted.
export const Leaderboard: React.FC<{ title: string; rows: { name: string; v: number; label: string; face?: string }[]; ats: number[] }> = ({ title, rows, ats }) => {
  const f = useCurrentFrame();
  const max = Math.max(...rows.map((r) => r.v)), step = Math.min(168, 840 / rows.length);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 160, top: 110, fontFamily: LFF.sans, fontWeight: 800, fontSize: 32, letterSpacing: 10, color: L.gold2 }}>{title}</div>
      {rows.map((r, i) => {
        const at = ats[i] ?? i * 20;
        if (f < at) return null;
        const g = ease(f, at, at + 20), hot = i === 0;
        return (
          <div key={r.name} style={{ position: "absolute", left: 160, top: 190 + i * step, display: "flex", alignItems: "center", gap: 26, opacity: Math.min(1, g * 2) }}>
            <div style={{ width: 140, height: 140, borderRadius: 70, overflow: "hidden", border: `5px solid ${hot ? L.gold : "#ffffff55"}`, background: L.navy2, position: "relative" }}>
              {r.face ? <Img src={staticFile(A(r.face))} style={{ position: "absolute", left: "50%", top: 0, height: 300, transform: "translateX(-50%)" }} />
                : <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: LFF.serif, fontWeight: 900, fontSize: 60, color: L.gold2 }}>{r.name.split(" ").map((w) => w[0]).join("").slice(0, 2)}</div>}
            </div>
            <div>
              <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 30, letterSpacing: 4, color: hot ? L.gold2 : L.ivory, whiteSpace: "nowrap" }}>{r.name.toUpperCase()}</div>
              <div style={{ display: "flex", alignItems: "center", gap: 20, marginTop: 6 }}>
                <div style={{ width: 1180 * (r.v / max) * g, height: 56, background: hot ? `linear-gradient(90deg, ${L.goldDeep}, ${L.gold2})` : "#c9c2b2", boxShadow: hot ? `0 0 28px ${L.gold}88` : undefined }} />
                <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 58, whiteSpace: "nowrap", ...(hot ? foil : { color: L.ivory }) }}>{r.label}</div>
              </div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Comment-bait voting grid (2-4 choices, lettered A-D).
export const Choices: React.FC<{ question: string; items: string[]; ats: number[] }> = ({ question, items, ats }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 0, right: 0, top: 130, textAlign: "center", fontFamily: LFF.serif, fontWeight: 900, fontSize: 90, color: L.ivory }}>{question}</div>
      {items.map((t, i) => {
        const at = ats[i] ?? i * 10;
        if (f < at) return null;
        return (
          <div key={t} style={{ position: "absolute", left: i % 2 ? 990 : 250, top: 340 + Math.floor(i / 2) * 260, width: 680, height: 210, display: "flex", alignItems: "center", gap: 26,
            background: "rgba(3,15,32,0.85)", border: `4px solid ${L.gold}`, padding: "0 34px", transform: `scale(${pop(f, at)})` }}>
            <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 90, ...foil }}>{String.fromCharCode(65 + i)}</div>
            <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 38, letterSpacing: 2, color: L.ivory }}>{t}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
