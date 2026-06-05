import React, { useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  RadioGroup,
  FormControlLabel,
  Radio,
  alpha,
} from '@mui/material';
import { DragIndicator as DragIcon } from '@mui/icons-material';
import { AIBadge } from '../ui/AIBadge';

interface Candidate {
  id: string;
  name: string;
  email: string;
  ai_score: number;
  applied_date: string;
  avatar?: string;
  current_stage: string;
}

interface CandidateKanbanProps {
  candidates?: Candidate[];
  onStageChange?: (candidateId: string, newStage: string) => void;
  onCandidateClick?: (candidate: Candidate) => void;
}

const stages = [
  'Applied',
  'AI Screening',
  'Shortlisted',
  'Interview',
  'Technical',
  'HR Round',
  'Offered',
];

const stageColors: Record<string, string> = {
  Applied: '#6B7280',
  'AI Screening': '#8B5CF6',
  Shortlisted: '#3B82F6',
  Interview: '#F59E0B',
  Technical: '#06B6D4',
  'HR Round': '#EC4899',
  Offered: '#22C55E',
};

function getScoreColor(score: number): string {
  if (score > 80) return '#22C55E';
  if (score >= 60) return '#EAB308';
  return '#EF4444';
}

const defaultCandidates: Candidate[] = [
  { id: '1', name: 'Sarah Chen', email: 'sarah@email.com', ai_score: 92, applied_date: '2026-05-28', current_stage: 'Interview' },
  { id: '2', name: 'James Wilson', email: 'james@email.com', ai_score: 87, applied_date: '2026-05-29', current_stage: 'AI Screening' },
  { id: '3', name: 'Priya Patel', email: 'priya@email.com', ai_score: 78, applied_date: '2026-05-30', current_stage: 'Shortlisted' },
  { id: '4', name: 'Michael Brown', email: 'michael@email.com', ai_score: 55, applied_date: '2026-05-27', current_stage: 'Applied' },
  { id: '5', name: 'Emily Davis', email: 'emily@email.com', ai_score: 95, applied_date: '2026-05-26', current_stage: 'Technical' },
  { id: '6', name: 'Alex Kim', email: 'alex@email.com', ai_score: 68, applied_date: '2026-05-25', current_stage: 'Applied' },
  { id: '7', name: 'Lisa Wang', email: 'lisa@email.com', ai_score: 83, applied_date: '2026-05-24', current_stage: 'HR Round' },
  { id: '8', name: 'David Lee', email: 'david@email.com', ai_score: 91, applied_date: '2026-05-23', current_stage: 'Offered' },
  { id: '9', name: 'Rachel Green', email: 'rachel@email.com', ai_score: 74, applied_date: '2026-05-31', current_stage: 'AI Screening' },
  { id: '10', name: 'Tom Harris', email: 'tom@email.com', ai_score: 42, applied_date: '2026-06-01', current_stage: 'Applied' },
];

export const CandidateKanban: React.FC<CandidateKanbanProps> = ({
  candidates = defaultCandidates,
  onStageChange,
  onCandidateClick,
}) => {
  const [moveDialog, setMoveDialog] = useState<{
    candidate: Candidate;
    targetStage: string;
  } | null>(null);

  const getCandidatesForStage = (stage: string) =>
    candidates.filter((c) => c.current_stage === stage);

  const handleCardClick = (candidate: Candidate) => {
    if (onCandidateClick) {
      onCandidateClick(candidate);
    }
  };

  const handleMoveClick = (e: React.MouseEvent, candidate: Candidate) => {
    e.stopPropagation();
    setMoveDialog({ candidate, targetStage: candidate.current_stage });
  };

  const handleMoveConfirm = () => {
    if (moveDialog && onStageChange) {
      onStageChange(moveDialog.candidate.id, moveDialog.targetStage);
    }
    setMoveDialog(null);
  };

  return (
    <>
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          overflowX: 'auto',
          pb: 2,
          '&::-webkit-scrollbar': { height: 6 },
          '&::-webkit-scrollbar-thumb': {
            background: '#334155',
            borderRadius: 3,
          },
        }}
      >
        {stages.map((stage) => {
          const stageCandidates = getCandidatesForStage(stage);
          const stageColor = stageColors[stage];

          return (
            <Box
              key={stage}
              sx={{
                minWidth: 260,
                maxWidth: 280,
                flex: '0 0 260px',
                background: alpha('#0F172A', 0.5),
                borderRadius: '14px',
                border: '1px solid',
                borderColor: alpha('#334155', 0.5),
                display: 'flex',
                flexDirection: 'column',
                maxHeight: 600,
              }}
            >
              {/* Column Header */}
              <Box
                sx={{
                  px: 2,
                  py: 1.5,
                  borderBottom: '1px solid',
                  borderColor: alpha('#334155', 0.3),
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                }}
              >
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: stageColor,
                    boxShadow: `0 0 8px ${alpha(stageColor, 0.5)}`,
                  }}
                />
                <Typography
                  variant="body2"
                  sx={{ color: '#F8FAFC', fontWeight: 600, flex: 1, fontSize: '0.8rem' }}
                >
                  {stage}
                </Typography>
                <Chip
                  label={stageCandidates.length}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    background: alpha(stageColor, 0.15),
                    color: stageColor,
                    border: `1px solid ${alpha(stageColor, 0.3)}`,
                  }}
                />
              </Box>

              {/* Cards */}
              <Box
                sx={{
                  p: 1.5,
                  flex: 1,
                  overflowY: 'auto',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 1,
                  '&::-webkit-scrollbar': { width: 3 },
                  '&::-webkit-scrollbar-thumb': {
                    background: '#334155',
                    borderRadius: 2,
                  },
                }}
              >
                {stageCandidates.map((candidate) => {
                  const scoreColor = getScoreColor(candidate.ai_score);
                  return (
                    <Box
                      key={candidate.id}
                      onClick={() => handleCardClick(candidate)}
                      sx={{
                        p: 2,
                        background: alpha('#1E293B', 0.8),
                        borderRadius: '10px',
                        border: '1px solid',
                        borderColor: alpha('#334155', 0.5),
                        borderLeft: `3px solid ${scoreColor}`,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          background: alpha('#1E293B', 1),
                          transform: 'translateY(-1px)',
                          boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
                          borderColor: alpha(stageColor, 0.3),
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                        <Avatar
                          sx={{
                            width: 30,
                            height: 30,
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            background: `linear-gradient(135deg, ${stageColor}, ${alpha(stageColor, 0.6)})`,
                          }}
                        >
                          {candidate.name.split(' ').map((n) => n[0]).join('')}
                        </Avatar>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography
                            variant="body2"
                            sx={{
                              color: '#F8FAFC',
                              fontWeight: 600,
                              fontSize: '0.8rem',
                              lineHeight: 1.2,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {candidate.name}
                          </Typography>
                        </Box>
                      </Box>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Box
                            sx={{
                              px: 1,
                              py: 0.2,
                              borderRadius: '6px',
                              background: alpha(scoreColor, 0.12),
                              border: `1px solid ${alpha(scoreColor, 0.25)}`,
                            }}
                          >
                            <Typography
                              variant="caption"
                              sx={{ color: scoreColor, fontWeight: 700, fontSize: '0.7rem' }}
                            >
                              {candidate.ai_score}
                            </Typography>
                          </Box>
                          {candidate.ai_score > 80 && (
                            <AIBadge label="Top" tooltip="AI ranked in top tier" />
                          )}
                        </Box>
                        <Typography
                          variant="caption"
                          sx={{ color: '#64748B', fontSize: '0.65rem' }}
                        >
                          {new Date(candidate.applied_date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                          })}
                        </Typography>
                      </Box>

                      {/* Move Button */}
                      <Box
                        onClick={(e) => handleMoveClick(e, candidate)}
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: 0.5,
                          mt: 1.5,
                          pt: 1,
                          borderTop: '1px solid',
                          borderColor: alpha('#334155', 0.3),
                          color: '#64748B',
                          fontSize: '0.7rem',
                          cursor: 'pointer',
                          transition: 'color 0.2s',
                          '&:hover': { color: '#8B5CF6' },
                        }}
                      >
                        <DragIcon sx={{ fontSize: 14 }} />
                        <Typography variant="caption" sx={{ fontWeight: 500 }}>
                          Move Stage
                        </Typography>
                      </Box>
                    </Box>
                  );
                })}

                {stageCandidates.length === 0 && (
                  <Box
                    sx={{
                      py: 4,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{ color: '#475569', fontStyle: 'italic' }}
                    >
                      No candidates
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>
          );
        })}
      </Box>

      {/* Stage Move Dialog */}
      <Dialog
        open={Boolean(moveDialog)}
        onClose={() => setMoveDialog(null)}
        PaperProps={{
          sx: {
            background: '#1E293B',
            border: '1px solid #334155',
            borderRadius: '16px',
            minWidth: 360,
            boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          },
        }}
      >
        <DialogTitle sx={{ color: '#F8FAFC', fontWeight: 700, pb: 1 }}>
          Move {moveDialog?.candidate.name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: '#94A3B8', mb: 2 }}>
            Select the new stage for this candidate:
          </Typography>
          <RadioGroup
            value={moveDialog?.targetStage || ''}
            onChange={(e) =>
              setMoveDialog((prev) =>
                prev ? { ...prev, targetStage: e.target.value } : null
              )
            }
          >
            {stages.map((stage) => (
              <FormControlLabel
                key={stage}
                value={stage}
                control={
                  <Radio
                    sx={{
                      color: '#475569',
                      '&.Mui-checked': { color: stageColors[stage] },
                    }}
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: stageColors[stage],
                      }}
                    />
                    <Typography variant="body2" sx={{ color: '#E2E8F0' }}>
                      {stage}
                    </Typography>
                  </Box>
                }
                sx={{
                  mb: 0.5,
                  borderRadius: '8px',
                  mx: 0,
                  px: 1,
                  '&:hover': { background: alpha('#334155', 0.3) },
                }}
              />
            ))}
          </RadioGroup>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2.5 }}>
          <Button
            onClick={() => setMoveDialog(null)}
            sx={{
              color: '#94A3B8',
              textTransform: 'none',
              '&:hover': { background: alpha('#334155', 0.3) },
            }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleMoveConfirm}
            sx={{
              background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
              textTransform: 'none',
              borderRadius: '10px',
              px: 3,
              '&:hover': {
                background: 'linear-gradient(135deg, #7C3AED, #5B21B6)',
              },
            }}
          >
            Move
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CandidateKanban;
