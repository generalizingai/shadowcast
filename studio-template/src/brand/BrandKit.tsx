import React from "react";
import { AbsoluteFill } from "remotion";
import { BRAND } from "./brand";
import { foil } from "../kit/theme";

// Typographic logos rendered from the brand font (exact spelling, transparent background). tools/wordmark.py renders these.
export const BrandWordmark: React.FC = () => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
    <div style={{ fontFamily: BRAND.fonts.serif, fontWeight: 900, fontSize: 150, letterSpacing: 6, whiteSpace: "nowrap", color: BRAND.colors.ivory,
      textShadow: "0 4px 18px #0008" }}>{BRAND.name}</div>
  </AbsoluteFill>
);

export const BrandMono: React.FC = () => {
  const initials = BRAND.name.split(/\s+/).filter(Boolean).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", borderRadius: 96, overflow: "hidden",
      background: `radial-gradient(circle at 35% 30%, ${BRAND.colors.navy2}, ${BRAND.colors.deep} 75%)`, boxShadow: `inset 0 0 0 14px ${BRAND.colors.gold}` }}>
      <div style={{ fontFamily: BRAND.fonts.serif, fontWeight: 900, fontSize: initials.length > 1 ? 250 : 330, lineHeight: 1, ...foil, filter: "none" }}>{initials}</div>
    </AbsoluteFill>
  );
};
