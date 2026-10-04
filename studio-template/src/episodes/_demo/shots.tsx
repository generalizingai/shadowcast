import React from "react";
import { ShotDef } from "../../kit/timing";
import { Flash, Glam, Photo } from "../../kit/stage";
import { Big, Countdown, Stamp } from "../../kit/parts";
import { Climb, EndCard, LockGrid, TitleCard } from "../../kit/charts";
import { L } from "../../kit/theme";

// Long-video shot list. One entry per beat: `at` = first words of the beat, `marks` = later words that trigger reveals.
// Split into shots1.tsx / shots2.tsx when long; tools/audit_layout.py reads every shots*.tsx in file order.
export const SHOTS: ShotDef[] = [
  { at: "", sfx: "thud", el: () => <Glam><TitleCard kicker="SHADOWCAST" title="Demo Episode" sub="every graphic, word-synced" /><Flash /></Glam> },
  { at: "Number three", sfx: "click", marks: ["Watch"], el: ({ m }) => <Glam photo="web/b_demo.jpg"><Countdown n={3} name="THE CLIMB" role="chart demo" cut="cut/demo.png" m={m} /></Glam> },
  { at: "gold chart", marks: ["one", "four."], el: ({ m }) => (
    <Glam dim={0.1}><Climb title="DEMO · GROWTH" max={5} pts={[{ d: "START", v: 1, label: "1" }, { d: "END", v: 4, label: "4" }]} ats={[m[0], m[1]]} ticks={[{ v: 2, label: "2" }, { v: 4, label: "4" }]} /></Glam>) },
  { at: "Number two", sfx: "click", marks: ["receipt."], msfx: ["thud"], el: ({ dur, m }) => (
    <Photo src="web/b_demo.jpg" dur={dur} dark={0.6}><Big text="EVERY CLAIM NEEDS *A RECEIPT*" size={110} y={-120} /><Stamp text="SOURCED" at={m[0]} y={160} color={L.gold} /></Photo>) },
  { at: "Number one", sfx: "click", marks: ["opens."], el: ({ m }) => <Glam><LockGrid items={["ONE", "TWO", "THREE"]} owner="LOCKED" unlockAt={m[0]} unlockOwner="YOURS" /></Glam> },
  { at: "Thanks", sfx: "thud", el: () => <Glam><EndCard /><Flash /></Glam> },
];
