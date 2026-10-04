import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { clamp, ease, pop } from "./pieces";
import { A, foil, L, LFF } from "./theme";

const hidden = (f: number, at: number) => f < at;

// Ivory sticker outline + gold glow for real-person cut-outs.
const OUTLINE = ["drop-shadow(4px 0 0 #F8F3E8)", "drop-shadow(-4px 0 0 #F8F3E8)", "drop-shadow(0 4px 0 #F8F3E8)", "drop-shadow(0 -4px 0 #F8F3E8)",
  `drop-shadow(0 0 28px ${L.gold}88)`, "drop-shadow(14px 18px 0 #000a)"].join(" ");

// Real person cut-out with a gold-edged serif name tag.
export const Star: React.FC<{
  src: string; x: number; y: number; h: number; at?: number; from?: "bottom" | "left" | "right"; rot?: number;
  name?: string; role?: string; flip?: boolean; glow?: boolean; sil?: boolean; tagAt?: number;
}> = ({ src, x, y, h, at = 0, from = "bottom", rot = 0, name, role, flip, glow, sil, tagAt }) => {
  const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
  if (hidden(f, at)) return null;
  const p = pop(f, at, 13);
  const off = (1 - p) * 760;
  const dx = from === "left" ? -off : from === "right" ? off : 0;
  const dy = from === "bottom" ? off : 0;
  const breathe = 1 + Math.sin((f - at) / 20) * 0.01;
  const ta = tagAt ?? at + 8;
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(-50%,0) translate(${dx}px,${dy}px) rotate(${rot}deg) scale(${breathe})`, transformOrigin: "50% 100%" }}>
      {glow && <div style={{ position: "absolute", left: "50%", top: "45%", width: h * 0.9, height: h * 0.9, transform: "translate(-50%,-50%)",
        background: `radial-gradient(circle, ${L.gold}66, transparent 65%)`, filter: "blur(10px)" }} />}
      <Img src={staticFile(A(src))} style={{ position: "relative", height: h, display: "block", transform: flip ? "scaleX(-1)" : undefined,
        filter: sil ? `brightness(0) drop-shadow(0 0 3px ${L.gold}) drop-shadow(0 0 22px ${L.gold}aa)` : OUTLINE }} />
      {name && f >= ta && (
        <div style={{ position: "absolute", left: "50%", bottom: 70, transform: `translateX(-50%) scale(${pop(f, ta)})`, textAlign: "center", whiteSpace: "nowrap" }}>
          <div style={{ background: L.navy, border: `3px solid ${L.gold}`, color: L.ivory, fontFamily: LFF.serif, fontWeight: 700, fontSize: 40, letterSpacing: 3,
            padding: "8px 28px", boxShadow: "0 10px 30px #000b" }}>{name}</div>
          {role && <div style={{ display: "inline-block", background: L.gold, color: L.deep, fontFamily: LFF.sans, fontWeight: 800, fontSize: 22, letterSpacing: 3,
            padding: "5px 16px", textTransform: "uppercase" }}>{role}</div>}
        </div>
      )}
    </div>
  );
};

// Countdown opener: giant gold numeral on the left, the star slides in on the right when named.
export const Countdown: React.FC<{ n: number; name: string; role: string; cut: string; m: number[]; h?: number }> = ({ n, name, role, cut, m, h = 860 }) => {
  const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
  const p = pop(f, 0, 12);
  const rule = ease(f, 4, 18);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: W > H ? 140 : 90, top: W > H ? 150 : 200, transform: `scale(${0.6 + 0.4 * p})`, transformOrigin: "left center", opacity: Math.min(1, p * 2) }}>
        <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 34, letterSpacing: 14, color: L.gold2 }}>NUMBER</div>
        <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: n === 1 ? 560 : 480, lineHeight: 0.92, ...foil }}>{n}</div>
        <div style={{ height: 5, width: 560 * rule, background: `linear-gradient(90deg, ${L.gold}, transparent)`, marginTop: 6 }} />
      </div>
      {W > H ? <Star src={cut} x={1300} y={1080 - h + 30} h={h} at={m[0] ?? 8} name={name} role={role} glow />
        : <Star src={cut} x={W / 2 + 60} y={H - 500 - 980} h={980} at={m[0] ?? 8} name={name} role={role} glow />}
    </AbsoluteFill>
  );
};

// Big statement text. Words wrapped in *asterisks* render in gold.
export const Big: React.FC<{ text: string; at?: number; size?: number; y?: number; x?: number; serif?: boolean; color?: string; rot?: number; maxW?: number; align?: "center" | "left" }> =
  ({ text, at = 0, size = 120, y = 0, x = 0, serif, color = L.ivory, rot = 0, maxW = 1600, align = "center" }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const p = pop(f, at, 12);
    const parts = text.split(/(\*[^*]+\*)/g);
    return (
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
        <div style={{ fontFamily: serif ? LFF.serif : LFF.cond, fontWeight: serif ? 900 : 400, fontSize: size, color, lineHeight: serif ? 1.02 : 1.05,
          textTransform: serif ? undefined : "uppercase", textAlign: align, maxWidth: maxW, whiteSpace: "pre-line", letterSpacing: serif ? 0 : 2,
          transform: `translate(${x}px,${y}px) rotate(${rot}deg) scale(${0.55 + 0.45 * p})`, opacity: Math.min(1, p * 2),
          textShadow: "0 6px 0 #0009, 0 0 40px #000a" }}>
          {parts.map((s, i) => (s.startsWith("*") ? <span key={i} style={{ ...foil, filter: "none", textShadow: "none" }}>{s.slice(1, -1)}</span> : <span key={i}>{s}</span>))}
        </div>
      </AbsoluteFill>
    );
  };

// Small gold kicker line with rules either side.
export const Kicker: React.FC<{ text: string; at?: number; y?: number; x?: number; size?: number }> = ({ text, at = 0, y = -300, x = 0, size = 34 }) => {
  const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
  if (hidden(f, at)) return null;
  const o = ease(f, at, at + 10);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 22, transform: `translate(${x}px,${y}px)`, opacity: o }}>
        <div style={{ width: 90 * o, height: 3, background: L.gold }} />
        <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: size, letterSpacing: size * 0.32, color: L.gold2, whiteSpace: "nowrap" }}>{text}</div>
        <div style={{ width: 90 * o, height: 3, background: L.gold }} />
      </div>
    </AbsoluteFill>
  );
};

// Rubber stamp that slams in (red by default, gold for good news).
export const Stamp: React.FC<{ text: string; at?: number; x?: number; y?: number; rot?: number; color?: string; size?: number; sub?: string }> =
  ({ text, at = 0, x = 0, y = 0, rot = -9, color = L.red, size = 110, sub }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const s = interpolate(f - at, [0, 5], [2.3, 1], { ...clamp, easing: Easing.in(Easing.quad) });
    const shake = f - at < 9 ? Math.sin((f - at) * 3) * (9 - (f - at)) : 0;
    return (
      <div style={{ position: "absolute", left: W / 2 + x + shake, top: H / 2 + y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${s})`,
        opacity: interpolate(f - at, [0, 2], [0, 1], clamp), textAlign: "center",
        border: `${Math.round(size / 11)}px double ${color}`, outline: `${Math.round(size / 26)}px solid ${color}`, outlineOffset: -size / 6,
        padding: `${size * 0.14}px ${size * 0.34}px`, background: "rgba(3,15,32,0.72)", borderRadius: 10 }}>
        <div style={{ fontFamily: LFF.cond, fontSize: size, color, letterSpacing: 4, lineHeight: 1, whiteSpace: "nowrap", textTransform: "uppercase" }}>{text}</div>
        {sub && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: size * 0.24, color, letterSpacing: 4, marginTop: 8, whiteSpace: "nowrap" }}>{sub}</div>}
      </div>
    );
  };

// Gold count-up figure with label.
export const Money: React.FC<{ to: number; fmt?: (v: number) => string; label?: string; at?: number; dur?: number; x?: number; y?: number; size?: number; note?: string }> =
  ({ to, fmt = (v) => `$${Math.round(v).toLocaleString("en-US")}`, label, at = 0, dur = 22, x = 0, y = 0, size = 220, note }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const v = ease(f, at, at + dur) * to;
    const p = pop(f, at);
    return (
      <div style={{ position: "absolute", left: W / 2 + x, top: H / 2 + y, transform: `translate(-50%,-50%) scale(${0.6 + 0.4 * p})`, textAlign: "center", whiteSpace: "nowrap" }}>
        <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: size, lineHeight: 1, ...foil }}>{fmt(v)}</div>
        {label && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: size * 0.17, letterSpacing: 6, color: L.ivory, marginTop: 14, textTransform: "uppercase", textShadow: "0 3px 10px #000" }}>{label}</div>}
        {note && <div style={{ fontFamily: LFF.serifI, fontStyle: "italic", fontSize: size * 0.15, color: L.dim, marginTop: 8 }}>{note}</div>}
      </div>
    );
  };

// Film / show / book title as a typographic card (never artwork).
export const TitleChip: React.FC<{ t: string; yr?: string; kind?: string; at?: number; x?: number; y?: number; rot?: number; size?: number }> =
  ({ t, yr, kind, at = 0, x = 0, y = 0, rot = -3, size = 96 }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const p = pop(f, at, 12);
    return (
      <div style={{ position: "absolute", left: W / 2 + x, top: H / 2 + y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${p})`,
        background: L.ivory, padding: `${size * 0.3}px ${size * 0.6}px`, border: `4px solid ${L.gold}`, boxShadow: "12px 16px 0 #000a", textAlign: "center", whiteSpace: "nowrap" }}>
        {kind && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: size * 0.26, letterSpacing: 5, color: L.goldDeep, textTransform: "uppercase" }}>{kind}</div>}
        <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontStyle: "normal", fontSize: size, color: L.navy, lineHeight: 1.05 }}>{t}</div>
        {yr && <div style={{ fontFamily: LFF.serifI, fontStyle: "italic", fontSize: size * 0.42, color: L.navy2 }}>{yr}</div>}
      </div>
    );
  };

// Verdict / charge board: rows land on their marks.
export type Row = { k: string; v: string; c?: string; at: number };
export const Verdict: React.FC<{ title?: string; rows: Row[]; y?: number; w?: number; size?: number }> = ({ title = "THE VERDICT", rows, y = 0, w = 1500, size = 62 }) => {
  const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
  const p = pop(f, 0, 14);
  return (
    <div style={{ position: "absolute", left: (W - w) / 2, top: 230 + y, width: w, transform: `scale(${0.9 + 0.1 * p})`, opacity: p,
      background: "linear-gradient(180deg, rgba(18,50,88,0.95), rgba(4,27,56,0.95))", border: `3px solid ${L.gold}`, boxShadow: "0 30px 80px #000c" }}>
      <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 28, letterSpacing: 10, color: L.gold2, padding: "22px 40px", borderBottom: `2px solid ${L.gold}55` }}>{title}</div>
      {rows.map((r, i) => {
        if (f < r.at) return null;
        const q = pop(f, r.at, 12);
        return (
          <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 30, padding: "24px 40px", borderBottom: i < rows.length - 1 ? "1px solid #ffffff1c" : undefined,
            transform: `translateX(${(1 - q) * -60}px)`, opacity: q }}>
            <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: size, color: L.ivory, textTransform: "uppercase", letterSpacing: 1 }}>{r.k}</div>
            <div style={{ fontFamily: LFF.cond, fontSize: size * 0.92, color: L.deep, background: r.c ?? L.gold, padding: "4px 22px", letterSpacing: 3, whiteSpace: "nowrap",
              transform: `scale(${pop(f, r.at + 6)})` }}>{r.v}</div>
          </div>
        );
      })}
    </div>
  );
};

// Pull quote in italic serif with big gold marks.
export const QuoteCard: React.FC<{ q: string; who: string; at?: number; size?: number; left?: number; right?: number; top?: number }> =
  ({ q, who, at = 0, size = 76, left = 220, right = 220, top = 280 }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const n = Math.floor((f - at) * 2.2);
    const done = at + q.length / 2.2;
    return (
      <div style={{ position: "absolute", left, right, top }}>
        <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 240, lineHeight: 0.55, ...foil }}>“</div>
        <div style={{ fontFamily: LFF.serifI, fontStyle: "italic", fontWeight: 500, fontSize: size, color: L.ivory, lineHeight: 1.2, textShadow: "0 4px 18px #000" }}>{q.slice(0, n)}</div>
        <div style={{ fontFamily: LFF.sans, fontWeight: 700, fontSize: 30, letterSpacing: 4, color: L.gold2, marginTop: 34, opacity: ease(f, done, done + 8), textTransform: "uppercase" }}>{who}</div>
      </div>
    );
  };

// Fact card: kicker + big serif lines (dates, places, ages).
export const Fact: React.FC<{ kick?: string; lines: string[]; at?: number; x?: number; y?: number; size?: number; ats?: number[]; align?: "center" | "left" }> =
  ({ kick, lines, at = 0, x = 0, y = 0, size = 96, ats = [], align = "center" }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    const st = Math.max(at, ats[0] ?? at);
    if (hidden(f, st)) return null;
    const p = pop(f, st, 13);
    return (
      <div style={{ position: "absolute", left: W / 2 + x, top: H / 2 + y, transform: `translate(-50%,-50%) scale(${0.85 + 0.15 * p})`, opacity: p, textAlign: align,
        background: "rgba(3,15,32,0.82)", borderLeft: `8px solid ${L.gold}`, padding: "30px 50px", boxShadow: "0 24px 60px #000b", whiteSpace: "nowrap" }}>
        {kick && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: size * 0.3, letterSpacing: 8, color: L.gold2, marginBottom: 6 }}>{kick}</div>}
        {lines.map((l, i) => {
          const a = ats[i] ?? at;
          if (f < a) return null;
          return <div key={i} style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: size, color: L.ivory, lineHeight: 1.08, opacity: ease(f, a, a + 6) }}>{l}</div>;
        })}
      </div>
    );
  };

// Rebuilt news headline: white card, outlet slab, exact headline, gold highlighter sweep.
export const News: React.FC<{ outlet: string; title: string; date: string; color?: string; hl?: string; hlAt?: number; at?: number; rot?: number; y?: number; inset?: number; fs?: number }> =
  ({ outlet, title, date, color = "#B4182D", hl, hlAt = 9999, at = 0, rot = -1.5, y = 0, inset = 200, fs = 70 }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const p = pop(f, at, 14);
    const i = hl ? title.indexOf(hl) : -1;
    const s = ease(f, hlAt, hlAt + 14);
    const body = i < 0 ? title : (<>{title.slice(0, i)}<span style={{ background: `linear-gradient(90deg, ${L.gold2} ${s * 100}%, transparent ${s * 100}%)` }}>{hl}</span>{title.slice(i + hl!.length)}</>);
    return (
      <div style={{ position: "absolute", left: inset, right: inset, top: 250 + y, background: "#fff", padding: "46px 60px", boxShadow: "16px 20px 0 #000c", borderTop: `10px solid ${color}`,
        transform: `rotate(${rot}deg) scale(${0.85 + 0.15 * p})`, opacity: p }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ background: color, color: "#fff", fontFamily: LFF.sans, fontWeight: 900, fontSize: 32, padding: "6px 18px", letterSpacing: 1 }}>{outlet}</div>
          <div style={{ fontFamily: LFF.sans, fontWeight: 500, fontSize: 28, color: "#666" }}>{date}</div>
        </div>
        <div style={{ fontFamily: LFF.serif, fontWeight: 700, fontSize: fs, color: "#111", lineHeight: 1.12, marginTop: 24 }}>{body}</div>
      </div>
    );
  };

// Recreated document (police report etc.) on paper with a highlighter sweep; labelled as a recreation.
export const Doc: React.FC<{ head: string; sub?: string; lines: string[]; hlLine?: number; hlAt?: number; at?: number; rot?: number; note?: string; box?: [number, number, number, number]; fs?: number }> =
  ({ head, sub, lines, hlLine = -1, hlAt = 9999, at = 0, rot = 2, note = "RECREATED FOR ILLUSTRATION", box = [260, 260, 110, 90], fs = 54 }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const p = pop(f, at, 14);
    const s = ease(f, hlAt, hlAt + 18);
    return (
      <div style={{ position: "absolute", left: box[0], right: box[1], top: box[2], bottom: box[3], background: L.paper, boxShadow: "18px 22px 0 #000b", padding: "50px 64px",
        transform: `rotate(${rot}deg) translateY(${(1 - p) * 300}px)`, fontFamily: LFF.type, color: "#222" }}>
        <div style={{ fontWeight: 700, fontSize: 44, letterSpacing: 2, borderBottom: "3px solid #333", paddingBottom: 12 }}>{head}</div>
        {sub && <div style={{ fontSize: 30, marginTop: 10, color: "#555" }}>{sub}</div>}
        <div style={{ marginTop: 30 }}>
          {lines.map((l, i) => (
            <div key={i} style={{ fontSize: fs, lineHeight: 1.45 }}>
              <span style={i === hlLine ? { background: `linear-gradient(90deg, ${L.gold2}cc ${s * 100}%, transparent ${s * 100}%)` } : undefined}>{l}</span>
            </div>
          ))}
        </div>
        <div style={{ position: "absolute", right: 30, bottom: 20, fontFamily: LFF.sans, fontWeight: 700, fontSize: 18, letterSpacing: 3, color: "#999" }}>{note}</div>
      </div>
    );
  };

// Row of small gold-outlined chips (film titles, prison names) that pop in on marks.
export const Chips: React.FC<{ items: string[]; ats: number[]; y?: number; size?: number }> = ({ items, ats, y = 330, size = 54 }) => {
  const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", gap: 24, transform: `translateY(${y}px)` }}>
        {items.map((t, i) => {
          const a = ats[i] ?? 0;
          if (f < a) return null;
          return <div key={i} style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: size, letterSpacing: 3, color: L.ivory, background: "rgba(3,15,32,0.85)",
            border: `3px solid ${L.gold}`, padding: `${size * 0.2}px ${size * 0.55}px`, transform: `scale(${pop(f, a)}) rotate(${i % 2 ? 2 : -2}deg)`, whiteSpace: "nowrap" }}>{t}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

// Big red X slashed over a word.
export const Slash: React.FC<{ at: number; x?: number; y?: number; w?: number; h?: number }> = ({ at, x = 0, y = 0, w = 900, h = 260 }) => {
  const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
  if (hidden(f, at)) return null;
  const a = ease(f, at, at + 5), b = ease(f, at + 4, at + 9);
  const len = Math.hypot(w, h), ang = (Math.atan2(h, w) * 180) / Math.PI;
  const bar = (p: number, r: number) => <div style={{ position: "absolute", left: -len / 2, top: -14, width: len * p, height: 28, background: L.red, borderRadius: 14,
    transform: `rotate(${r}deg)`, transformOrigin: `${len / 2}px 14px`, boxShadow: "0 0 0 5px #0008" }} />;
  return <div style={{ position: "absolute", left: W / 2 + x, top: H / 2 + y }}>{bar(a, ang)}{bar(b, -ang)}</div>;
};

export const Pic: React.FC<{ src: string; x: number; y: number; w: number; h: number; at?: number; rot?: number; cap?: string; pos?: string; mono?: boolean }> =
  ({ src, x, y, w, h, at = 0, rot = 3, cap, pos = "center", mono }) => {
    const f = useCurrentFrame();
    const { width: W, height: H } = useVideoConfig();
    if (hidden(f, at)) return null;
    const p = pop(f, at, 13);
    return (
      <div style={{ position: "absolute", left: x, top: y, width: w, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${p})`, background: L.ivory, padding: 16, paddingBottom: cap ? 12 : 16, boxShadow: "16px 20px 0 #000b" }}>
        <Img src={staticFile(A(src))} style={{ width: w - 32, height: h, objectFit: "cover", objectPosition: pos, display: "block", filter: mono ? "grayscale(1)" : undefined }} />
        {cap && <div style={{ fontFamily: LFF.sans, fontWeight: 800, fontSize: 24, letterSpacing: 3, color: L.navy, marginTop: 10, textAlign: "center", textTransform: "uppercase" }}>{cap}</div>}
      </div>
    );
  };
