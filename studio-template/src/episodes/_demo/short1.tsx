import React from "react";
import { ShotDef } from "../../kit/timing";
import { Photo } from "../../kit/stage";
import { Big, Money } from "../../kit/parts";
import { VShort } from "../../kit/vshort";
import { W_, S_ } from "./data";

// Native 9:16 Short cut from one VO section (prefix = the section name's start).
const SHOTS: ShotDef[] = [
  { at: "Number two", marks: ["receipt."], el: ({ dur, m }) => (
    <Photo src="web/b_demo.jpg" dur={dur} dark={0.6}><Big text={"EVERY CLAIM\nNEEDS *A RECEIPT*"} size={96} y={-560} /><Money to={100} fmt={(v) => `${Math.round(v)}%`} at={m[0]} y={-300} size={150} label="sourced" /></Photo>) },
];
export const PREFIX1 = "#2";
export const Short1: React.FC = () => <VShort words={W_} sections={S_} prefix="#2" shots={SHOTS} />;
