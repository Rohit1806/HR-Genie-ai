import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  TextField,
  MenuItem,
  alpha,
  Paper,
  Divider,
} from '@mui/material';
import {
  TrendingUp as PromoteIcon,
  Warning as RiskIcon,
  Lightbulb as IdealIcon,
  Timeline as GrowthIcon,
} from '@mui/icons-material';
import { performanceApi } from '@/api/performance.api';
import PageHeader from '@/components/ui/PageHeader';
import ScoreGauge from '@/components/ui/ScoreGauge';
import AttritionRiskBadge from '@/components/ai/AttritionRiskBadge';
import PromotionScoreBadge from '@/components/ai/PromotionScoreBadge';

export default function AIInsights() {
  const [selectedCycleId, setSelectedCycleId] = useState('');

  // Query performance cycles
  const { data: cyclesData, isLoading: isLoadingCycles } = useQuery({
    queryKey: ['performance-cycles'],
    queryFn: () => performanceApi.listCycles(),
  });

  useEffect(() => {
    if (!selectedCycleId && cyclesData?.items && cyclesData.items.length > 0) {
      setSelectedCycleId(cyclesData.items[0].id);
    }
  }, [cyclesData, selectedCycleId]);

  // Query AI insights
  const { data: insights, isLoading: isLoadingInsights } = useQuery({
    queryKey: ['ai-performance-insights', selectedCycleId],
    queryFn: () => performanceApi.getAIInsights(selectedCycleId),
    enabled: !!selectedCycleId,
  });

  return (
    <Box>
      <PageHeader
        title="AI Performance Insights"
        subtitle="Analyze predictive analytics forecasts regarding career advancement, promotion readiness, and retention indicators."
      />

      {/* Select active cycle */}
      <Box sx={{ mb: 4, display: 'flex', gap: 2, alignItems: 'center' }}>
        <Typography variant="body1" sx={{ color: '#F8FAFC', fontWeight: 600 }}>
          Review Cycle:
        </Typography>
        {isLoadingCycles ? (
          <CircularProgress size={20} />
        ) : (
          <TextField
            select
            size="small"
            value={selectedCycleId}
            onChange={(e) => setSelectedCycleId(e.target.value)}
            sx={{ minWidth: 260, background: alpha('#1E293B', 0.6), borderRadius: '8px' }}
          >
            {(cyclesData?.items || []).map((c) => (
              <MenuItem key={c.id} value={c.id}>
                {c.name} ({c.cycle_type})
              </MenuItem>
            ))}
          </TextField>
        )}
      </Box>

      {isLoadingInsights ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
          <CircularProgress color="secondary" />
        </Box>
      ) : insights ? (
        <Grid container spacing={3}>
          {/* Main Gauges Row */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                border: '1px solid #334155',
                borderRadius: '16px',
                height: '100%',
                p: 2,
              }}
            >
              <CardContent sx={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                  <PromoteIcon sx={{ color: '#8B5CF6' }} />
                  <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                    Career Promotion Index
                  </Typography>
                </Box>

                <ScoreGauge score={insights.promotion_score} size="lg" label="" />
                
                <Box sx={{ mt: 3 }}>
                  <PromotionScoreBadge score={insights.promotion_score} />
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mt: 2, px: 2 }}>
                  Calculated based on objective target completions (OKRs) and manager feedback competencies.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card
              sx={{
                background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                border: '1px solid #334155',
                borderRadius: '16px',
                height: '100%',
                p: 2,
              }}
            >
              <CardContent sx={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                  <RiskIcon sx={{ color: '#EF4444' }} />
                  <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                    Retention Risk Forecast
                  </Typography>
                </Box>

                <ScoreGauge score={insights.attrition_risk} size="lg" label="" />

                <Box sx={{ mt: 3 }}>
                  <AttritionRiskBadge riskScore={insights.attrition_risk} />
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mt: 2, px: 2 }}>
                  Derived from daily attendance logs consistency, overtime shifts count, and review score deviation.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* AI Narrative and Recommendations */}
          <Grid item xs={12}>
            <Card
              sx={{
                background: 'linear-gradient(145deg, #1E293B, #0F172A)',
                border: '1px solid #334155',
                borderRadius: '16px',
                p: 3,
              }}
            >
              <CardContent sx={{ p: 0 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <GrowthIcon sx={{ color: '#8B5CF6' }} />
                  <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                    AI Predictive Assessment & Development Roadmap
                  </Typography>
                </Box>

                <Typography variant="body2" sx={{ color: '#94A3B8', mb: 4, lineHeight: 1.7, fontSize: '0.95rem' }}>
                  {insights.summary}
                </Typography>

                <Divider sx={{ borderColor: '#334155', mb: 3 }} />

                <Typography variant="subtitle2" sx={{ color: '#F8FAFC', mb: 2, fontWeight: 700 }}>
                  Tailored Actionable Training Recommendations
                </Typography>

                <Grid container spacing={2}>
                  {insights.recommendations.map((rec: string, idx: number) => (
                    <Grid item xs={12} md={6} key={idx}>
                      <Paper
                        elevation={0}
                        sx={{
                          p: 2,
                          background: '#0F172A',
                          border: '1px solid #1E293B',
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 2,
                        }}
                      >
                        <IdealIcon sx={{ color: '#F59E0B', mt: 0.2 }} />
                        <Typography variant="body2" sx={{ color: '#E2E8F0' }}>
                          {rec}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography color="text.secondary">Please select a cycle to retrieve AI career analytics.</Typography>
        </Box>
      )}
    </Box>
  );
}
