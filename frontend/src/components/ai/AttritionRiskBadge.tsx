import React from 'react';
import { Tooltip, Box } from '@mui/material';
import AIBadge from '@/components/ui/AIBadge';
import StatusPill from '@/components/ui/StatusPill';

interface AttritionRiskBadgeProps {
  riskScore: number; // 0 to 100
}

export default function AttritionRiskBadge({ riskScore }: AttritionRiskBadgeProps) {
  let label = 'Low Risk';
  let status: 'success' | 'warning' | 'error' = 'success';

  if (riskScore >= 80) {
    label = 'Critical Risk';
    status = 'error';
  } else if (riskScore >= 50) {
    label = 'Medium Risk';
    status = 'warning';
  }

  return (
    <Tooltip title={`AI-computed Attrition Risk: ${riskScore}%`}>
      <Box display="inline-flex" alignItems="center" gap={1}>
        <StatusPill status={label.toLowerCase().replace(' ', '_')} />
        <AIBadge label="AI" tooltip="AI Model evaluation based on activity, tenure, and performance" />
      </Box>
    </Tooltip>
  );
}
