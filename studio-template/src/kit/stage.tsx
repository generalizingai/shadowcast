import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { clamp, ease } from "./pieces";
import { ClearStage } from "./ctx";
import { A, L, LFF } from "./theme";
import { BRAND } from "../brand/brand";

// Twinkling four-point glints scattered over the frame.
const Glitter: React.FC<{ n?: number; op?: number }> = ({ n = 46, op = 0.8 }) => {
  const f = useCurrentFrame();
  const { width: GW, height: GH } = useVideoConfig();
  return (
    <>
      {Array.from({ length: n }, (_, i) => {
        const x = (i * 397 + 113) % GW, y0 = (i * 233 + 41) % GH, sp = 0.15 + (i % 5) * 0.07;
        const y = ((y0 - f * sp) % (GH + 20) + GH + 20) % (GH + 20);
        const tw = 0.25 + 0.75 * Math.max(0, Math.sin((f + i * 17) / (9 + (i % 4) * 3)));
        const s = 6 + (i % 4) * 5;
        return (
          <div key={i} style={{ position: "absolute", left: x, top: y, width: s, height: s, opacity: tw * op,
            background: i % 3 ? L.gold2 : L.ivory, clipPath: "polygon(50% 0, 60% 40%, 100% 50%, 60% 60%, 50% 100%, 40% 60%, 0 50%, 40% 40%)",
            filter: `drop-shadow(0 0 6px ${L.gold})`, transform: `rotate(${(f + i * 30) * 0.4}deg)` }} />
        );
      })}
    </>
  );
};

// Navy glamour stage: deep gradient, two sweeping spotlights, glitter, optional blurred photo underneath.
export const Glam: React.FC<{ children?: React.ReactNode; photo?: string; photoOp?: number; dim?: number; glitter?: boolean; pos?: string }> =
  ({ children, photo, photoOp = 0.3, dim = 0, glitter = true, pos = "center" }) => {
    const f = useCurrentFrame();
    const { width: SW } = useVideoConfig();
    return (
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 35%, ${L.navy2} 0%, ${L.navy} 45%, ${L.deep} 100%)`, overflow: "hidden" }}>
        {photo && <Img src={staticFile(A(photo))} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", objectPosition: pos,
          opacity: photoOp, filter: "blur(12px) saturate(0.9)", transform: `scale(${1.12 + f * 0.0004})` }} />}
        {[0, 1].map((i) => (
          <div key={i} style={{ position: "absolute", left: i ? SW * 0.7 : SW * 0.17, top: -260, width: 300, height: 1700,
            background: "linear-gradient(180deg, rgba(255,236,190,0.16), transparent 72%)", filter: "blur(22px)",
            transform: `rotate(${(i ? 18 : -18) + Math.sin((f + i * 60) / 70) * 6}deg)`, transformOrigin: "top center" }} />
        ))}
        {glitter && <Glitter />}
        {dim > 0 && <AbsoluteFill style={{ background: `rgba(3,15,32,${dim})` }} />}
        <AbsoluteFill style={{ background: "radial-gradient(circle, transparent 50%, rgba(1,6,14,0.8) 100%)" }} />
        <ClearStage.Provider value={true}>{children}</ClearStage.Provider>
      </AbsoluteFill>
    );
  };

// Full-bleed real photo with a slow push, navy grade and gold light leak.
export const Photo: React.FC<{
  src: string; dur: number; dark?: number; blur?: number; zoom?: [number, number]; pan?: [number, number]; pos?: string; children?: React.ReactNode; mono?: boolean;
}> = ({ src, dur, dark = 0.55, blur = 0, zoom = [1.04, 1.15], pan = [0, -24], pos = "center", children, mono }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [0, Math.max(1, dur)], [0, 1], clamp);
  const s = zoom[0] + (zoom[1] - zoom[0]) * t;
  return (
    <AbsoluteFill style={{ background: L.deep, overflow: "hidden" }}>
      <Img src={staticFile(A(src))} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", objectPosition: pos,
        transform: `scale(${s}) translate(${pan[0] * t}px, ${pan[1] * t}px)`, filter: `blur(${blur}px) ${mono ? "grayscale(1) contrast(1.15)" : "saturate(1.05) contrast(1.05)"}` }} />
      <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(3,15,32,${(dark * 0.7).toFixed(2)}) 0%, rgba(3,15,32,${dark.toFixed(2)}) 100%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 78% 18%, ${L.gold}38, transparent 55%)`, mixBlendMode: "screen" }} />
      <AbsoluteFill style={{ background: "radial-gradient(circle, transparent 55%, rgba(1,6,14,0.85) 100%)" }} />
      <ClearStage.Provider value={true}>{children}</ClearStage.Provider>
    </AbsoluteFill>
  );
};

// Paparazzi flashbulb: a white burst that fades over ~8 frames.
export const Flash: React.FC<{ at?: number; strength?: number }> = ({ at = 0, strength = 0.85 }) => {
  const f = useCurrentFrame();
  const o = interpolate(f - at, [0, 1, 9], [0, strength, 0], clamp);
  if (o <= 0) return null;
  return <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 45%, #fff, #fff8 50%, ${L.gold2}55)`, opacity: o, pointerEvents: "none" }} />;
};

// Channel bug (monogram + name, top left) and an optional countdown rail (top right), drawn over every shot.
export const Bug: React.FC<{ n: number | null; total?: number }> = ({ n, total = 10 }) => {
  const f = useCurrentFrame();
  return (
    <>
      <div style={{ position: "absolute", left: 44, top: 36, display: "flex", alignItems: "center", gap: 14, opacity: 0.92 }}>
        <Img src={staticFile(A(BRAND.mono))} style={{ width: 54, height: 54, borderRadius: 10 }} />
        <div style={{ fontFamily: LFF.serif, fontWeight: 700, fontSize: 30, letterSpacing: 6, color: L.ivory, textShadow: "0 2px 10px #000c" }}>{BRAND.name.toUpperCase()}</div>
      </div>
      {n !== null && (
        <div style={{ position: "absolute", right: 44, top: 34, display: "flex", gap: 7, alignItems: "center", opacity: ease(f, 0, 10) }}>
          {Array.from({ length: total }, (_, i) => total - i).map((k) => (
            <div key={k} style={{ width: k === n ? 54 : 30, height: 30, borderRadius: 15, display: "flex", alignItems: "center", justifyContent: "center",
              background: k === n ? L.gold : k > n ? `${L.gold}66` : "rgba(255,255,255,0.14)", color: L.deep, fontFamily: LFF.sans, fontWeight: 900, fontSize: 17,
              boxShadow: k === n ? `0 0 18px ${L.gold}` : undefined }}>{k === n ? `#${k}` : ""}</div>
          ))}
        </div>
      )}
    </>
  );
};
