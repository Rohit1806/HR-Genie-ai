import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Box,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  Button,
  Grid,
  TextField,
  MenuItem,
  Typography,
  Divider,
} from '@mui/material';
import { toast } from 'react-hot-toast';
import { employeesApi } from '@/api/employees.api';
import PageHeader from '@/components/ui/PageHeader';

// 1. Define Zod validation schemas for step validation
const onboardingSchema = z.object({
  // Step 1: Personal Details
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  personal_email: z.string().email('Invalid email address'),
  phone: z.string().min(10, 'Phone must be at least 10 digits'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum(['male', 'female', 'other']),

  // Step 2: Contact & Address
  street: z.string().min(1, 'Street is required'),
  city: z.string().min(1, 'City is required'),
  country: z.string().min(1, 'Country is required'),
  emergency_name: z.string().min(1, 'Emergency contact name is required'),
  emergency_relation: z.string().min(1, 'Emergency relation is required'),
  emergency_phone: z.string().min(10, 'Emergency phone must be at least 10 digits'),

  // Step 3: Employment Info
  date_of_joining: z.string().min(1, 'Joining date is required'),
  employment_type: z.enum(['full_time', 'part_time', 'contract', 'intern']),
  department_id: z.string().uuid('Department selection is required'),
  designation_id: z.string().uuid('Designation selection is required'),
  reporting_manager_id: z.string().optional().or(z.literal('')),
  work_location: z.string().min(1, 'Work location is required'),
});

type OnboardingFormValues = z.infer<typeof onboardingSchema>;

const stepFields: (keyof OnboardingFormValues)[][] = [
  ['first_name', 'last_name', 'personal_email', 'phone', 'date_of_birth', 'gender'],
  ['street', 'city', 'country', 'emergency_name', 'emergency_relation', 'emergency_phone'],
  ['date_of_joining', 'employment_type', 'department_id', 'designation_id', 'reporting_manager_id', 'work_location'],
];

export default function OnboardingWizard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeStep, setActiveStep] = useState(0);

  // Pre-seeded dropdown selections corresponding directly to DB seeds
  const mockDepts = [
    { id: '20ae9523-14d6-4363-b1ef-d7bc49655052', name: 'Engineering' },
    { id: '4c84b2f5-9bf2-41ac-ba26-457d87057fcb', name: 'Human Resources' },
    { id: '77d83ff6-ee93-46ad-87a4-ba0df4400064', name: 'Sales' },
    { id: '14ca5f0c-52fd-4cce-94c9-3d91f2a4ce03', name: 'Finance' },
  ];

  const mockDesgs = [
    { id: '6666829e-cb67-4e16-bc4d-247cc5a551bd', name: 'Chief Technical Officer' },
    { id: 'c8512f18-38c5-480b-ba86-05f595a21370', name: 'Software Engineer' },
    { id: '2cc4a5da-933e-49a7-a62a-90281de58480', name: 'HR Director' },
    { id: '78d723a6-329d-4133-93a2-988c7c3b0095', name: 'Talent Recruiter' },
    { id: '9d4961a8-9315-4d89-9737-169c3a8b63bd', name: 'Sales Executive' },
    { id: '7a11b198-d260-4d6e-8ca1-8bc67536bcbf', name: 'Finance Head' },
  ];

  const steps = ['Personal Details', 'Contact & Address', 'Employment Info', 'Review & Onboard'];

  const {
    control,
    handleSubmit,
    trigger,
    getValues,
    formState: { errors },
  } = useForm<OnboardingFormValues>({
    resolver: zodResolver(onboardingSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      personal_email: '',
      phone: '',
      date_of_birth: '',
      gender: 'male',
      street: '',
      city: '',
      country: 'India',
      emergency_name: '',
      emergency_relation: '',
      emergency_phone: '',
      date_of_joining: new Date().toISOString().split('T')[0],
      employment_type: 'full_time',
      department_id: '',
      designation_id: '',
      reporting_manager_id: '',
      work_location: 'Office',
    },
    mode: 'onTouched',
  });

  const onboardMutation = useMutation({
    mutationFn: (values: OnboardingFormValues) => {
      return employeesApi.createEmployee({
        first_name: values.first_name,
        last_name: values.last_name,
        personal_email: values.personal_email,
        phone: values.phone,
        date_of_birth: values.date_of_birth,
        gender: values.gender,
        date_of_joining: values.date_of_joining,
        employment_type: values.employment_type,
        department_id: values.department_id,
        designation_id: values.designation_id,
        reporting_manager_id: values.reporting_manager_id || undefined,
        work_location: values.work_location,
        address: { street: values.street, city: values.city, country: values.country },
        emergency_contact: {
          name: values.emergency_name,
          relation: values.emergency_relation,
          phone: values.emergency_phone,
        },
      });
    },
    onSuccess: (res) => {
      toast.success(
        `Employee onboarded successfully. Default password: ${(res as any).default_password || 'Welcome@123'}`
      );
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      navigate('/employees');
    },
    onError: () => {
      toast.error('Failed to onboard employee. Verify unique email & inputs.');
    },
  });

  const onSubmit = (values: OnboardingFormValues) => {
    onboardMutation.mutate(values);
  };

  const handleNext = async () => {
    if (activeStep < steps.length - 1) {
      const fieldsToValidate = stepFields[activeStep];
      const isStepValid = await trigger(fieldsToValidate);
      if (!isStepValid) {
        toast.error('Please correct the validation errors before proceeding.');
        return;
      }
      setActiveStep((prev) => prev + 1);
    } else {
      handleSubmit(onSubmit)();
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const formValues = getValues();

  return (
    <Box>
      <PageHeader
        title="Onboard New Employee"
        subtitle="Follow the 4-step wizard to register a new employee and create their user account profile."
      />

      <Card sx={{ bgcolor: 'background.paper', borderRadius: 3, border: '1px solid', borderColor: 'divider', mt: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 5 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Step 1: Personal Details */}
          {activeStep === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="first_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="First Name *"
                      fullWidth
                      error={!!errors.first_name}
                      helperText={errors.first_name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="last_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Last Name *"
                      fullWidth
                      error={!!errors.last_name}
                      helperText={errors.last_name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="personal_email"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Personal Email *"
                      type="email"
                      fullWidth
                      error={!!errors.personal_email}
                      helperText={errors.personal_email?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="phone"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Phone Number *"
                      fullWidth
                      error={!!errors.phone}
                      helperText={errors.phone?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="date_of_birth"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Date of Birth *"
                      type="date"
                      InputLabelProps={{ shrink: true }}
                      fullWidth
                      error={!!errors.date_of_birth}
                      helperText={errors.date_of_birth?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="gender"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Gender"
                      fullWidth
                      error={!!errors.gender}
                      helperText={errors.gender?.message}
                    >
                      <MenuItem value="male">Male</MenuItem>
                      <MenuItem value="female">Female</MenuItem>
                      <MenuItem value="other">Other</MenuItem>
                    </TextField>
                  )}
                />
              </Grid>
            </Grid>
          )}

          {/* Step 2: Contact & Address */}
          {activeStep === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="street"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Street Address *"
                      fullWidth
                      error={!!errors.street}
                      helperText={errors.street?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="city"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="City *"
                      fullWidth
                      error={!!errors.city}
                      helperText={errors.city?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="country"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Country *"
                      fullWidth
                      error={!!errors.country}
                      helperText={errors.country?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2" fontWeight={700} sx={{ mt: 2, mb: 1 }}>
                  Emergency Contact Details
                </Typography>
                <Divider sx={{ mb: 2 }} />
              </Grid>

              <Grid item xs={12} sm={4}>
                <Controller
                  name="emergency_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Contact Name *"
                      fullWidth
                      error={!!errors.emergency_name}
                      helperText={errors.emergency_name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="emergency_relation"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Relationship *"
                      fullWidth
                      error={!!errors.emergency_relation}
                      helperText={errors.emergency_relation?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="emergency_phone"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Phone Number *"
                      fullWidth
                      error={!!errors.emergency_phone}
                      helperText={errors.emergency_phone?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          )}

          {/* Step 3: Employment Details */}
          {activeStep === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="date_of_joining"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Joining Date *"
                      type="date"
                      InputLabelProps={{ shrink: true }}
                      fullWidth
                      error={!!errors.date_of_joining}
                      helperText={errors.date_of_joining?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="employment_type"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Employment Type"
                      fullWidth
                      error={!!errors.employment_type}
                      helperText={errors.employment_type?.message}
                    >
                      <MenuItem value="full_time">Full Time</MenuItem>
                      <MenuItem value="part_time">Part Time</MenuItem>
                      <MenuItem value="contract">Contract</MenuItem>
                      <MenuItem value="intern">Intern</MenuItem>
                    </TextField>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="department_id"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Department *"
                      fullWidth
                      error={!!errors.department_id}
                      helperText={errors.department_id?.message}
                    >
                      {mockDepts.map((d) => (
                        <MenuItem key={d.id} value={d.id}>
                          {d.name}
                        </MenuItem>
                      ))}
                    </TextField>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="designation_id"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Designation *"
                      fullWidth
                      error={!!errors.designation_id}
                      helperText={errors.designation_id?.message}
                    >
                      {mockDesgs.map((d) => (
                        <MenuItem key={d.id} value={d.id}>
                          {d.name}
                        </MenuItem>
                      ))}
                    </TextField>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="reporting_manager_id"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Reporting Manager ID (optional)"
                      fullWidth
                      error={!!errors.reporting_manager_id}
                      helperText={errors.reporting_manager_id?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="work_location"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Work Location *"
                      fullWidth
                      error={!!errors.work_location}
                      helperText={errors.work_location?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>
          )}

          {/* Step 4: Review */}
          {activeStep === 3 && (
            <Box>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Review Details
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                Review all profile configuration details below before confirming submission.
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    FULL NAME
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.first_name} {formValues.last_name}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    PERSONAL EMAIL
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.personal_email}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    PHONE
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.phone}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    GENDER
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.gender.toUpperCase()}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    ADDRESS
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.street}, {formValues.city}, {formValues.country}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    EMERGENCY CONTACT
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.emergency_name} ({formValues.emergency_relation}) - {formValues.emergency_phone}
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    JOINING DATE
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.date_of_joining}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    EMPLOYMENT TYPE
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {formValues.employment_type.replace('_', ' ').toUpperCase()}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    DEPARTMENT
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {mockDepts.find((d) => d.id === formValues.department_id)?.name || '—'}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="text.secondary">
                    DESIGNATION
                  </Typography>
                  <Typography variant="body1" fontWeight={600} mb={1}>
                    {mockDesgs.find((d) => d.id === formValues.designation_id)?.name || '—'}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Wizard actions */}
          <Box display="flex" justifyContent="flex-end" gap={2} sx={{ mt: 5 }}>
            {activeStep > 0 && (
              <Button onClick={handleBack} disabled={onboardMutation.isPending}>
                Back
              </Button>
            )}
            <Button variant="contained" onClick={handleNext} disabled={onboardMutation.isPending}>
              {activeStep === steps.length - 1 ? (onboardMutation.isPending ? 'Onboarding...' : 'Confirm & Onboard') : 'Next'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
