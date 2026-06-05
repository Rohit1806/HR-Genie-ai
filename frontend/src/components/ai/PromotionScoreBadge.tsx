import React from 'react';
import { Tooltip, Box, Typography } from '@mui/material';
import AIBadge from '@/components/ui/AIBadge';

interface PromotionScoreBadgeProps {
  score: number; // 0 to 100
}

export default function PromotionScoreBadge({ score }: PromotionScoreBadgeProps) {
  let color = '#22C55E'; // green > 80
  if (score < 60) {
    color = '#EF4444'; // red < 60
  } else if (score < 80) {
    color = '#EAB308'; // yellow 60-80
  }

  return (
    <Tooltip title={`Promotion Readiness Score: ${score}%`}>
      <Box display="inline-flex" alignItems="center" gap={1}>
        <Typography variant="body2" fontWeight={700} sx={{ color }}>
          {score}%
        </Typography>
        <AIBadge label="AI" tooltip="AI recommendation score using skills, performance trend, and peers metrics" />
      </Box>
    </Tooltip>
  );
}
