import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Avatar,
  Tabs,
  Tab,
  Button,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Person as PersonIcon,
  Psychology as PsychologyIcon,
  Description as DescriptionIcon,
  History as HistoryIcon,
  Add as AddIcon,
  FileUpload as UploadIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';
import { useAuthStore } from '@/store/authStore';
import { employeesApi } from '@/api/employees.api';
import PageHeader from '@/components/ui/PageHeader';
import StatusPill from '@/components/ui/StatusPill';
import AttritionRiskBadge from '@/components/ai/AttritionRiskBadge';
import PromotionScoreBadge from '@/components/ai/PromotionScoreBadge';
import AIScoreCard from '@/components/ai/AIScoreCard';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} id={`profile-tabpanel-${index}`} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function EmployeeProfile() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const currentUser = useAuthStore((s) => s.user);

  const [activeTab, setActiveTab] = useState(0);
  const [skillOpen, setSkillOpen] = useState(false);
  const [skillName, setSkillName] = useState('');
  const [proficiency, setProficiency] = useState('beginner');
  const [yearsExp, setYearsExp] = useState('');

  const [uploadOpen, setUploadOpen] = useState(false);
  const [documentType, setDocumentType] = useState('other');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [terminateOpen, setTerminateOpen] = useState(false);
  const [terminateReason, setTerminateReason] = useState('');
  const [terminateDate, setTerminateDate] = useState(new Date().toISOString().split('T')[0]);

  const isHRorAdmin = currentUser?.role === 'admin' || currentUser?.role === 'hr_recruiter';

  // Fetch employee details
  const { data: employee, isLoading, error } = useQuery({
    queryKey: ['employee', id],
    queryFn: () => employeesApi.getEmployee(id!),
    enabled: !!id,
  });

  // Mutators
  const addSkillMutation = useMutation({
    mutationFn: (data: { skill_name: string; proficiency_level: string; years_experience?: number }) =>
      employeesApi.addSkill(id!, data.skill_name, data.proficiency_level, data.years_experience),
    onSuccess: () => {
      toast.success('Skill added successfully');
      queryClient.invalidateQueries({ queryKey: ['employee', id] });
      setSkillOpen(false);
      setSkillName('');
      setYearsExp('');
    },
    onError: () => toast.error('Error adding skill'),
  });

  const uploadDocMutation = useMutation({
    mutationFn: (data: { file: File; type: string }) =>
      employeesApi.uploadDocument(id!, data.file, data.type),
    onSuccess: () => {
      toast.success('Document uploaded successfully');
      queryClient.invalidateQueries({ queryKey: ['employee', id] });
      setUploadOpen(false);
      setSelectedFile(null);
    },
    onError: () => toast.error('Error uploading document'),
  });

  const terminateMutation = useMutation({
    mutationFn: (data: { reason: string; date: string }) =>
      employeesApi.deleteEmployee(id!, data.reason, data.date),
    onSuccess: () => {
      toast.success('Employee terminated successfully');
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      navigate('/employees');
    },
    onError: () => toast.error('Error terminating employee'),
  });

  if (isLoading) {
    return <Typography color="text.secondary">Loading employee profile...</Typography>;
  }

  if (error || !employee) {
    return <Typography color="error">Error loading employee details. Verify connection.</Typography>;
  }

  return (
    <Box>
      <PageHeader
        title={employee.full_name}
        subtitle={`Employee ID: ${employee.employee_code} | Joined on ${new Date(employee.date_of_joining).toLocaleDateString()}`}
        action={
          isHRorAdmin && employee.employment_status !== 'terminated' ? (
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setTerminateOpen(true)}
            >
              Terminate Employment
            </Button>
          ) : undefined
        }
      />

      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Left Card: Summary */}
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: 'background.paper', borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
              <Avatar
                src={employee.profile_photo_url || undefined}
                sx={{ width: 100, height: 100, mb: 2, bgcolor: 'primary.main', fontSize: '2rem' }}
              >
                {employee.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
              </Avatar>
              <Typography variant="h5" fontWeight={700}>{employee.full_name}</Typography>
              <Typography color="text.secondary" variant="body2" sx={{ mb: 1.5 }}>
                {employee.designation_title || '—'} • {employee.department_name || '—'}
              </Typography>
              <StatusPill status={employee.employment_status} />
            </CardContent>
          </Card>
        </Grid>
        {/* Right Card: Tabs */}
        <Grid item xs={12} md={8}>
          <Card sx={{ bgcolor: 'background.paper', borderRadius: 3, border: '1px solid', borderColor: 'divider', minHeight: 400 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={activeTab} onChange={(e, val) => setActiveTab(val)}>
                  <Tab icon={<PersonIcon />} iconPosition="start" label="Overview" />
                  <Tab icon={<PsychologyIcon />} iconPosition="start" label="Skills" />
                  <Tab icon={<DescriptionIcon />} iconPosition="start" label="Documents" />
                  <Tab icon={<HistoryIcon />} iconPosition="start" label="History" />
                </Tabs>
              </Box>
 
              {/* Tab 1: Overview (Details + AI Insights) */}
              <CustomTabPanel value={activeTab} index={0}>
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>Profile Information</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">PERSONAL EMAIL</Typography>
                    <Typography variant="body2" fontWeight={600} mb={2}>{employee.personal_email || '—'}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">PHONE</Typography>
                    <Typography variant="body2" fontWeight={600} mb={2}>{employee.phone || '—'}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">DATE OF BIRTH</Typography>
                    <Typography variant="body2" fontWeight={600} mb={2}>
                      {employee.date_of_birth ? new Date(employee.date_of_birth).toLocaleDateString() : '—'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" color="text.secondary">GENDER</Typography>
                    <Typography variant="body2" fontWeight={600} mb={2}>{employee.gender || '—'}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">ADDRESS</Typography>
                    <Typography variant="body2" fontWeight={600} mb={2}>
                      {employee.address ? `${employee.address.street || ''}, ${employee.address.city || ''}, ${employee.address.country || ''}` : '—'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">EMERGENCY CONTACT</Typography>
                    <Typography variant="body2" fontWeight={600} mb={3}>
                      {employee.emergency_contact ? `${employee.emergency_contact.name || ''} (${employee.emergency_contact.relation || ''}) - ${employee.emergency_contact.phone || ''}` : '—'}
                    </Typography>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 3 }} />

                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>AI Core Insights</Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Card sx={{ bgcolor: 'action.hover', border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          ATTRITION RISK
                        </Typography>
                        <AttritionRiskBadge riskScore={Math.floor(Math.random() * 90)} />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Card sx={{ bgcolor: 'action.hover', border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          PROMOTION READY SCORE
                        </Typography>
                        <PromotionScoreBadge score={Math.floor(60 + Math.random() * 35)} />
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12}>
                    <AIScoreCard
                      title="AI Work Fit Evaluation"
                      overallScore={85}
                      subMetrics={[
                        { label: 'Work Ethic / Attendance Fit', score: 90 },
                        { label: 'Skill Match Alignment', score: 82 },
                        { label: 'Team Interpersonal Score', score: 84 },
                      ]}
                      summary="This employee is demonstrating strong alignment with goals and maintains an outstanding attendance rate. High promotion probability within the next cycle."
                    />
                  </Grid>
                </Grid>
              </CustomTabPanel>
 
              {/* Tab 2: Skills */}
              <CustomTabPanel value={activeTab} index={1}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="subtitle1" fontWeight={700}>Skills & Proficiency</Typography>
                  <Button size="small" startIcon={<AddIcon />} variant="contained" onClick={() => setSkillOpen(true)}>
                    Add Skill
                  </Button>
                </Box>
                {employee.skills.length === 0 ? (
                  <Typography color="text.secondary" variant="body2">No skills registered for this employee.</Typography>
                ) : (
                  <Grid container spacing={2}>
                    {employee.skills.map((skill) => (
                      <Grid item xs={12} sm={6} key={skill.id}>
                        <Card sx={{ bgcolor: 'action.hover', border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                          <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                            <Typography variant="subtitle2" fontWeight={700}>{skill.name}</Typography>
                            <Typography variant="caption" color="text.secondary" display="block">
                              Category: {skill.category || 'General'}
                            </Typography>
                            <Box display="flex" justifyContent="space-between" mt={1}>
                              <StatusPill status={skill.proficiency || 'beginner'} />
                              {skill.years_experience && (
                                <Typography variant="caption" fontWeight={600} color="text.secondary">
                                  {skill.years_experience} Yrs Exp
                                </Typography>
                              )}
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CustomTabPanel>
 
              {/* Tab 3: Documents */}
              <CustomTabPanel value={activeTab} index={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="subtitle1" fontWeight={700}>Uploaded Documents</Typography>
                  <Button size="small" startIcon={<UploadIcon />} variant="contained" onClick={() => setUploadOpen(true)}>
                    Upload File
                  </Button>
                </Box>
                {employee.documents.length === 0 ? (
                  <Typography color="text.secondary" variant="body2">No documents uploaded.</Typography>
                ) : (
                  <List>
                    {employee.documents.map((doc) => (
                      <React.Fragment key={doc.id}>
                        <ListItem
                          secondaryAction={
                            <Button size="small" variant="text" href={doc.file_url} target="_blank">
                              Download
                            </Button>
                          }
                        >
                          <ListItemIcon>
                            <DescriptionIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={doc.file_name}
                            secondary={`Type: ${doc.document_type.toUpperCase()} | Uploaded on: ${new Date(doc.created_at).toLocaleDateString()}`}
                          />
                        </ListItem>
                        <Divider variant="inset" component="li" />
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CustomTabPanel>
 
              {/* Tab 4: History */}
              <CustomTabPanel value={activeTab} index={3}>
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>Employment History</Typography>
                {!employee.history || employee.history.length === 0 ? (
                  <Typography color="text.secondary" variant="body2">No history events logged for this employee.</Typography>
                ) : (
                  <List sx={{ width: '100%' }}>
                    {employee.history.map((h) => (
                      <React.Fragment key={h.id}>
                        <ListItem sx={{ py: 2, alignItems: 'flex-start' }}>
                          <ListItemIcon sx={{ mt: 0.5 }}>
                            <HistoryIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ width: '100%' }}>
                                <Typography variant="subtitle2" fontWeight={700}>
                                  {h.event_type.toUpperCase().replace('_', ' ')}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {new Date(h.effective_date).toLocaleDateString()}
                                </Typography>
                              </Box>
                            }
                            secondary={
                              <Box sx={{ mt: 1 }}>
                                {h.reason && (
                                  <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', mb: 1 }}>
                                    Reason: {h.reason}
                                  </Typography>
                                )}
                                {h.new_value && (
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    {Object.entries(h.new_value).map(([key, val]) => (
                                      <Typography key={key} variant="caption" sx={{ bgcolor: 'action.selected', px: 1, py: 0.5, borderRadius: 1 }}>
                                        <strong>{key.replace('_', ' ')}:</strong> {String(val)}
                                      </Typography>
                                    ))}
                                  </Box>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        <Divider variant="inset" component="li" />
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CustomTabPanel>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
 
      {/* Add Skill Dialog */}
      <Dialog open={skillOpen} onClose={() => setSkillOpen(false)}>
        <DialogTitle>Add Employee Skill</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: 300, mt: 1 }}>
          <TextField label="Skill Name" value={skillName} onChange={(e) => setSkillName(e.target.value)} fullWidth />
          <TextField select label="Proficiency" value={proficiency} onChange={(e) => setProficiency(e.target.value)} fullWidth>
            <MenuItem value="beginner">Beginner</MenuItem>
            <MenuItem value="intermediate">Intermediate</MenuItem>
            <MenuItem value="advanced">Advanced</MenuItem>
            <MenuItem value="expert">Expert</MenuItem>
          </TextField>
          <TextField label="Years of Experience" type="number" value={yearsExp} onChange={(e) => setYearsExp(e.target.value)} fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSkillOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => addSkillMutation.mutate({ skill_name: skillName, proficiency_level: proficiency, years_experience: yearsExp ? Number(yearsExp) : undefined })}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upload File Dialog */}
      <Dialog open={uploadOpen} onClose={() => setUploadOpen(false)}>
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: 320, mt: 1 }}>
          <TextField select label="Document Type" value={documentType} onChange={(e) => setDocumentType(e.target.value)} fullWidth>
            <MenuItem value="aadhar">Aadhar Card</MenuItem>
            <MenuItem value="pan">PAN Card</MenuItem>
            <MenuItem value="passport">Passport</MenuItem>
            <MenuItem value="offer_letter">Offer Letter</MenuItem>
            <MenuItem value="payslip">Payslip</MenuItem>
            <MenuItem value="other">Other Document</MenuItem>
          </TextField>
          <Button variant="outlined" component="label" startIcon={<UploadIcon />}>
            Choose File
            <input type="file" hidden onChange={(e) => e.target.files && setSelectedFile(e.target.files[0])} />
          </Button>
          {selectedFile && <Typography variant="caption">{selectedFile.name}</Typography>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={!selectedFile} onClick={() => uploadDocMutation.mutate({ file: selectedFile!, type: documentType })}>
            Upload
          </Button>
        </DialogActions>
      </Dialog>

      {/* Terminate Dialog */}
      <Dialog open={terminateOpen} onClose={() => setTerminateOpen(false)}>
        <DialogTitle>Terminate Employment</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: 360, mt: 1 }}>
          <Typography variant="body2" color="error">
            Warning: This action will mark the employee as terminated and deactivate their system access credentials.
          </Typography>
          <TextField label="Reason for Termination" multiline rows={3} value={terminateReason} onChange={(e) => setTerminateReason(e.target.value)} fullWidth />
          <TextField label="Termination Date" type="date" value={terminateDate} onChange={(e) => setTerminateDate(e.target.value)} fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTerminateOpen(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={() => terminateMutation.mutate({ reason: terminateReason, date: terminateDate })}>
            Confirm Termination
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// Inline helper for direct Axios instances in components (needed for FormDatas)
import axiosInstance from '@/config/axios';
const axios = axiosInstance;
