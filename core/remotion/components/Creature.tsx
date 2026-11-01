import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { ramp } from '../lib/lib';
import { SceneProps, Svg, Label } from './common';
import { KenBurnsBg } from './KenBurns';
import { creature, Grounded } from './registry';

// Một sinh vật đứng trên nền, chân chạm y (tâm ngang tại x). props: name, x, y, scale, flip, walk (px dịch chuyển), label, sub, bg (props KenBurns)
export const Creature: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const { name = 'trex', x = 960, y = 940, scale = 1, flip = false, walk = 0 } = props;
  const enter = ramp(f, 0, 24);
  const dx = walk * (f / dur);
  return (
    <AbsoluteFill>
      <KenBurnsBg asset={asset} dur={dur} p={props.bg} />
      <Svg>
        <ellipse cx={x + dx} cy={y + 4} rx={300 * scale} ry={24 * scale} fill="#000" opacity={0.25} filter="url(#soft6)" />
        <g transform={`translate(${x + dx},${y + (1 - enter) * 40}) scale(${flip ? -scale : scale},${scale})`} opacity={enter}>
          <Grounded>{creature(name, f, props)}</Grounded>
        </g>
      </Svg>
      {props.label ? <Label text={props.label} sub={props.sub} from={10} to={dur - 10} /> : null}
    </AbsoluteFill>
  );
};
