import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { A, foil, L, LFF } from "./theme";
import { BRAND } from "../brand/brand";

// Thumbnail grammar (tuned on the Top10 reference): tight real faces, huge condensed text in white + gold/red,
// red circle / arrow call-outs, small channel badge. 1280x720.
type Face = { src: string; x: number; y: number; h: number; flip?: boolean };
const OUT = "drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 18px 30px #000c)";

export const Thumb: React.FC<{
  faces: Face[]; l1: string; l2: string; l2c?: string; num?: string; photo: string;
  circle?: { x: number; y: number; r: number }; arrow?: { x: number; y: number; rot: number }; s1?: number; s2?: number; tx?: number;
}> = ({ faces, l1, l2, l2c = L.gold, num = "10", photo, circle, arrow, s1 = 120, s2 = 150, tx = 640 }) => (
  <AbsoluteFill style={{ background: L.deep, overflow: "hidden" }}>
    <Img src={staticFile(A(photo))} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", filter: "blur(6px) brightness(0.45) saturate(1.2)" }} />
    <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 40%, ${L.red}55, transparent 60%), radial-gradient(circle at 50% 100%, ${L.deep}, transparent 70%)` }} />
    {faces.map((f, i) => (
      <Img key={i} src={staticFile(A(f.src))} style={{ position: "absolute", left: f.x, top: f.y, height: f.h, transform: `translateX(-50%)${f.flip ? " scaleX(-1)" : ""}`, filter: OUT }} />
    ))}
    {circle && <div style={{ position: "absolute", left: circle.x - circle.r, top: circle.y - circle.r, width: circle.r * 2, height: circle.r * 2, borderRadius: "50%",
      border: `12px solid ${L.red}`, boxShadow: "0 0 0 4px #000, inset 0 0 0 4px #000" }} />}
    {arrow && (
      <svg style={{ position: "absolute", left: arrow.x, top: arrow.y, transform: `rotate(${arrow.rot}deg)`, transformOrigin: "0 0" }} width={220} height={120} viewBox="0 0 220 120">
        <path d="M0 45 H150 V10 L215 60 L150 110 V75 H0 Z" fill={L.red} stroke="#000" strokeWidth={8} strokeLinejoin="round" />
      </svg>
    )}
    <div style={{ position: "absolute", left: tx, bottom: 26, transform: "translateX(-50%)", textAlign: "center", whiteSpace: "nowrap" }}>
      <div style={{ fontFamily: LFF.cond, fontSize: s1, lineHeight: 0.95, color: "#fff", WebkitTextStroke: "10px #000", paintOrder: "stroke fill", textTransform: "uppercase" }}>{l1}</div>
      <div style={{ fontFamily: LFF.cond, fontSize: s2, lineHeight: 0.95, color: l2c, WebkitTextStroke: "12px #000", paintOrder: "stroke fill", textTransform: "uppercase" }}>{l2}</div>
    </div>
    <div style={{ position: "absolute", left: 22, top: 18, display: "flex", alignItems: "center", gap: 10 }}>
      <div style={{ fontFamily: LFF.serif, fontWeight: 900, fontSize: 92, lineHeight: 1, ...foil }}>{num}</div>
    </div>
    <div style={{ position: "absolute", right: 20, top: 20, background: L.navy, border: `3px solid ${L.gold}`, padding: "6px 14px",
      fontFamily: LFF.serif, fontWeight: 700, fontSize: 26, letterSpacing: 4, color: L.ivory }}>{BRAND.name.toUpperCase()}</div>
  </AbsoluteFill>
);

