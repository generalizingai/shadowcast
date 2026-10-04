import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ease } from "./pieces";

// Every cut lands with a quick punch-in.
export const Punch: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ transform: `scale(${ease(f, 0, 7, 1.06, 1)})` }}>{children}</AbsoluteFill>;
};
