import type React from "react";
import { BRAND } from "../brand/brand";

// Everything visual reads from src/brand/brand.ts (written by the brand-kit skill for each channel).
export const FPS = 30;
export const W = 1920;
export const H = 1080;
export const L = BRAND.colors;
export const LFF = BRAND.fonts;

// Accent-foil text fill (background-clip text) with a soft glow.
export const foil: React.CSSProperties = {
  background: `linear-gradient(175deg, ${L.gold2} 0%, ${L.gold} 45%, ${L.goldDeep} 70%, ${L.gold2} 100%)`,
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  color: "transparent",
  filter: `drop-shadow(0 4px 0 #0009) drop-shadow(0 0 24px ${L.gold}55)`,
};

// Every asset path is relative to the episode folder (rendered with --public-dir=<episode>).
export const A = (n: string) => `assets/${n}`;
