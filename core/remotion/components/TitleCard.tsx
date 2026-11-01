import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { SceneProps, BigText, useTheme, fontOf, fade } from './common';
import { KenBurnsBg } from './KenBurns';

// Tiêu đề chương. props: title, sub, kicker (dòng nhỏ phía trên)
export const TitleCard: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  return (
    <AbsoluteFill style={{ background: t.palette.bg }}>
      <KenBurnsBg asset={asset} dur={dur} p={{ z0: 1.0, z1: 1.08, filter: 'brightness(0.6)', ...props }} />
      {props.kicker ? (
        <div style={{ position: 'absolute', top: 330, width: '100%', textAlign: 'center', fontFamily: fontOf(t), fontSize: 36, letterSpacing: 12, color: t.palette.accent, opacity: fade(f, 4, dur - 6), textShadow: '2px 2px 0 #1c140e' }}>
          {props.kicker}
        </div>
      ) : null}
      <BigText text={props.title || ''} from={6} to={dur - 4} />
      {props.sub ? <BigText text={props.sub} from={16} to={dur - 4} y={540} size={46} /> : null}
    </AbsoluteFill>
  );
};
