import React, { useEffect, useState } from 'react';
import { Box, Typography } from '@mui/material';

interface ScoreGaugeProps {
  score: number;
  label: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = {
  sm: { width: 64, strokeWidth: 4, fontSize: '0.875rem', labelSize: '0.6rem' },
  md: { width: 96, strokeWidth: 6, fontSize: '1.25rem', labelSize: '0.75rem' },
  lg: { width: 140, strokeWidth: 8, fontSize: '1.75rem', labelSize: '0.875rem' },
};

function getScoreColor(score: number): string {
  if (score > 80) return '#22C55E';
  if (score >= 60) return '#EAB308';
  return '#EF4444';
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  label,
  size = 'md',
}) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const config = sizeMap[size];
  const color = getScoreColor(score);
  const radius = (config.width - config.strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  useEffect(() => {
    const duration = 1200;
    const steps = 60;
    const increment = score / steps;
    let current = 0;
    let frame = 0;

    const timer = setInterval(() => {
      frame++;
      current = Math.min(score, increment * frame);
      setAnimatedScore(current);

      if (frame >= steps) {
        setAnimatedScore(score);
        clearInterval(timer);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 0.5,
      }}
    >
      <Box
        sx={{
          position: 'relative',
          width: config.width,
          height: config.width,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg
          width={config.width}
          height={config.width}
          viewBox={`0 0 ${config.width} ${config.width}`}
          style={{ transform: 'rotate(-90deg)', position: 'absolute' }}
        >
          {/* Background Circle */}
          <circle
            cx={config.width / 2}
            cy={config.width / 2}
            r={radius}
            fill="none"
            stroke="#334155"
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
          />
          {/* Score Circle */}
          <circle
            cx={config.width / 2}
            cy={config.width / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{
              transition: 'stroke-dashoffset 0.3s ease-out',
              filter: `drop-shadow(0 0 6px ${color}40)`,
            }}
          />
        </svg>

        {/* Score Number */}
        <Typography
          sx={{
            position: 'relative',
            color: '#F8FAFC',
            fontWeight: 800,
            fontSize: config.fontSize,
            lineHeight: 1,
            zIndex: 1,
          }}
        >
          {Math.round(animatedScore)}
        </Typography>
      </Box>

      <Typography
        sx={{
          color: '#94A3B8',
          fontSize: config.labelSize,
          fontWeight: 500,
          textAlign: 'center',
          mt: 0.5,
        }}
      >
        {label}
      </Typography>
    </Box>
  );
};

export default ScoreGauge;
