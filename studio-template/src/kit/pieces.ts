import { Easing, interpolate, spring } from "remotion";
import { FPS } from "./theme";

// Motion primitives shared by every kit component.
export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const pop = (f: number, at = 0, damping = 11) => spring({ frame: f - at, fps: FPS, config: { damping, stiffness: 190, mass: 0.7 } });
export const ease = (f: number, a: number, b: number, from = 0, to = 1) =>
  interpolate(f, [a, b], [from, to], { ...clamp, easing: Easing.bezier(0.2, 0.8, 0.2, 1) });
