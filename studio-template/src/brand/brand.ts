import * as serifF from "@remotion/google-fonts/BodoniModa";
import * as sansF from "@remotion/google-fonts/Inter";
import * as condF from "@remotion/google-fonts/Anton";
import * as typeF from "@remotion/google-fonts/CourierPrime";
import { gfont } from "../kit/fonts";

// Generated from channel.json by `new_channel.py brand demo`. Edit channel.json brand, not this file.
// Colour roles: deep/navy/navy2 = background ramp, gold/gold2/goldDeep = accent ramp (any hue), ivory = main text,
// paper = document cards, red = negative stamps, green = positive verdicts, dim = secondary text.
export const BRAND = {
  name: "Demo Channel",
  handle: "@demochannel",
  tagline: "We bring the story. And the receipts.",
  wordmark: "brand/wordmark.png",
  mono: "brand/mono.png",
  colors: {
    deep: "#030F20",
    navy: "#041B38",
    navy2: "#123258",
    gold: "#E9A82C",
    gold2: "#F6CB62",
    goldDeep: "#BE8617",
    ivory: "#F8F3E8",
    paper: "#EFE7D6",
    red: "#D7263D",
    green: "#2BB673",
    dim: "#9AA6BD",
  },
  fonts: {
    serif: gfont(serifF, ["500", "700", "900"]), serifI: gfont(serifF, ["500", "700"], "italic"),
    sans: gfont(sansF, ["500", "700", "800", "900"]), cond: gfont(condF, ["400"]), type: gfont(typeF, ["400", "700"]),
  },
};
