import React from 'react';
import { Card, CardContent, Typography, Box, Grid } from '@mui/material';
import ScoreGauge from '@/components/ui/ScoreGauge';
import AIBadge from '@/components/ui/AIBadge';

interface AIScoreCardProps {
  title: string;
  overallScore: number;
  subMetrics: { label: string; score: number }[];
  summary?: string;
}

export default function AIScoreCard({ title, overallScore, subMetrics, summary }: AIScoreCardProps) {
  return (
    <Card sx={{ bgcolor: 'background.paper', borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
      <CardContent sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight={700}>{title}</Typography>
          <AIBadge label="AI" tooltip="Calculated by HRGenie AI Analysis Model" />
        </Box>
        
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4} display="flex" justifyContent="center">
            <Box textAlign="center">
              <ScoreGauge score={overallScore} size="md" label="Overall Fit" />
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={8}>
            <Box display="flex" flexDirection="column" gap={1.5}>
              {subMetrics.map((metric) => {
                let color = '#22C55E';
                if (metric.score < 60) color = '#EF4444';
                else if (metric.score < 80) color = '#EAB308';
                
                return (
                  <Box key={metric.label} display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" color="text.secondary">{metric.label}</Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box sx={{ width: 100, height: 6, bgcolor: 'action.hover', borderRadius: 3, overflow: 'hidden' }}>
                        <Box sx={{ width: `${metric.score}%`, height: '100%', bgcolor: color, borderRadius: 3 }} />
                      </Box>
                      <Typography variant="body2" fontWeight={700} sx={{ color, minWidth: 35, textAlign: 'right' }}>
                        {metric.score}%
                      </Typography>
                    </Box>
                  </Box>
                );
              })}
            </Box>
          </Grid>
        </Grid>

        {summary && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'action.hover', borderRadius: 2, borderLeft: '3px solid #8B5CF6' }}>
            <Typography variant="caption" fontWeight={600} display="block" color="text.secondary" mb={0.5}>
              AI COPILOT SUMMARY
            </Typography>
            <Typography variant="body2" color="text.primary">
              {summary}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
