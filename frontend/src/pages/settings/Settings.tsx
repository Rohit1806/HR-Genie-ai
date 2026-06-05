import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  alpha,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  SettingsSuggest as AdjustIcon,
  Business as CompanyIcon,
  NotificationsActive as NotificationIcon,
} from '@mui/icons-material';
import PageHeader from '@/components/ui/PageHeader';
import { useAuthStore } from '@/store/authStore';
import { toast } from 'react-hot-toast';

export default function Settings() {
  const currentUser = useAuthStore((s) => s.user);

  // Profile details
  const [profile, setProfile] = useState({
    name: currentUser?.full_name || 'Demo Administrator',
    email: currentUser?.email || 'admin@demo.hrgenie.ai',
    role: currentUser?.role || 'admin',
  });

  // Copilot Thresholds
  const [thresholds, setThresholds] = useState({
    late_threshold: '09:30',
    promotion_readiness: 80,
    attrition_caution: 50,
  });

  // Preferences Toggles
  const [preferences, setPreferences] = useState({
    websocket_notifications: true,
    email_digests: false,
    use_redis_caching: true,
  });

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('Profile configurations saved!');
  };

  const handleThresholdsSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('AI thresholds calibration updated!');
  };

  const handlePreferencesChange = (field: string) => {
    setPreferences((prev: any) => ({ ...prev, [field]: !prev[field] }));
    toast.success('Notification preferences updated.');
  };

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto' }}>
      <PageHeader
        title="Settings & System Configurations"
        subtitle="Manage personal settings, calibrating AI Copilot trigger scores, and toggle system notifications."
      />

      <Grid container spacing={4}>
        {/* Profile Card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ background: 'linear-gradient(135deg, #1E293B, #0F172A)', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC', mb: 3 }}>
                Profile Overview
              </Typography>
              <form onSubmit={handleProfileSave}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Full Name"
                      value={profile.name}
                      onChange={(e) => setProfile((p) => ({ ...p, name: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Email Address"
                      disabled
                      value={profile.email}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      size="small"
                      label="System Role"
                      disabled
                      value={profile.role.toUpperCase()}
                    />
                  </Grid>
                  <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                    <Button
                      type="submit"
                      variant="contained"
                      startIcon={<SaveIcon />}
                      sx={{
                        background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                        textTransform: 'none',
                        borderRadius: '8px',
                        '&:hover': { background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' },
                      }}
                    >
                      Save Profile
                    </Button>
                  </Grid>
                </Grid>
              </form>
            </CardContent>
          </Card>
        </Grid>

        {/* AI Copilot Threshold Calibrations */}
        <Grid item xs={12} md={6}>
          <Card sx={{ background: 'linear-gradient(135deg, #1E293B, #0F172A)', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <AdjustIcon sx={{ color: '#8B5CF6' }} />
                <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                  AI Copilot Calibrations
                </Typography>
              </Box>

              <form onSubmit={handleThresholdsSave}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      size="small"
                      type="time"
                      label="Shift Late Threshold (Late after)"
                      InputLabelProps={{ shrink: true }}
                      value={thresholds.late_threshold}
                      onChange={(e) => setThresholds((p) => ({ ...p, late_threshold: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      size="small"
                      type="number"
                      label="Promotion Score Floor"
                      value={thresholds.promotion_readiness}
                      onChange={(e) => setThresholds((p) => ({ ...p, promotion_readiness: parseInt(e.target.value) || 80 }))}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      size="small"
                      type="number"
                      label="Attrition Risk Ceiling"
                      value={thresholds.attrition_caution}
                      onChange={(e) => setThresholds((p) => ({ ...p, attrition_caution: parseInt(e.target.value) || 50 }))}
                    />
                  </Grid>
                  <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                    <Button
                      type="submit"
                      variant="contained"
                      startIcon={<SaveIcon />}
                      sx={{
                        background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                        textTransform: 'none',
                        borderRadius: '8px',
                        '&:hover': { background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' },
                      }}
                    >
                      Calibrate Thresholds
                    </Button>
                  </Grid>
                </Grid>
              </form>
            </CardContent>
          </Card>
        </Grid>

        {/* System Preferences */}
        <Grid item xs={12}>
          <Card sx={{ background: 'linear-gradient(135deg, #1E293B, #0F172A)', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <NotificationIcon sx={{ color: '#EF4444' }} />
                <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                  Preferences & Infrastructure toggles
                </Typography>
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12} sm={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={preferences.websocket_notifications}
                        onChange={() => handlePreferencesChange('websocket_notifications')}
                        color="secondary"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" sx={{ color: '#E2E8F0', fontWeight: 600 }}>
                          Real-time WebSockets
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Enable push alerts drawer
                        </Typography>
                      </Box>
                    }
                  />
                </Grid>

                <Grid item xs={12} sm={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={preferences.email_digests}
                        onChange={() => handlePreferencesChange('email_digests')}
                        color="secondary"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" sx={{ color: '#E2E8F0', fontWeight: 600 }}>
                          Weekly Email Digests
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Send reports to inbox
                        </Typography>
                      </Box>
                    }
                  />
                </Grid>

                <Grid item xs={12} sm={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={preferences.use_redis_caching}
                        onChange={() => handlePreferencesChange('use_redis_caching')}
                        color="secondary"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" sx={{ color: '#E2E8F0', fontWeight: 600 }}>
                          Enable Redis Caching
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Speed up dashboard loading queries
                        </Typography>
                      </Box>
                    }
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
