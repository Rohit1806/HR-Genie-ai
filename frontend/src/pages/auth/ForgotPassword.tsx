import { Link as RouterLink } from 'react-router-dom';
import { Box, Card, CardContent, Typography, TextField, Button, Link, CircularProgress } from '@mui/material';
import { AutoAwesome } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useForgotPassword } from '@/hooks/useAuth';

const schema = z.object({
  email: z.string().email('Please enter a valid email'),
});

type ForgotForm = z.infer<typeof schema>;

export default function ForgotPassword() {
  const { mutate: forgotPassword, isPending, isSuccess } = useForgotPassword();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotForm>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: ForgotForm) => {
    forgotPassword(data.email);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 440 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 3,
              background: 'linear-gradient(135deg, #8B5CF6, #6366F1)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
            }}
          >
            <AutoAwesome sx={{ color: '#fff', fontSize: 30 }} />
          </Box>
          <Typography variant="h4" fontWeight={800} gutterBottom>
            Reset Password
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Enter your email and we'll send a reset link
          </Typography>
        </Box>

        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 4 }}>
            {isSuccess ? (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="body1" color="success.main" fontWeight={600} gutterBottom>
                  Check your email!
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  If an account with that email exists, we've sent password reset instructions.
                </Typography>
              </Box>
            ) : (
              <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
                <TextField
                  {...register('email')}
                  label="Email Address"
                  type="email"
                  fullWidth
                  margin="normal"
                  error={!!errors.email}
                  helperText={errors.email?.message}
                  autoComplete="email"
                  autoFocus
                />
                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  size="large"
                  disabled={isPending}
                  sx={{
                    mt: 3,
                    py: 1.5,
                    background: 'linear-gradient(135deg, #8B5CF6, #6366F1)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #7C3AED, #4F46E5)',
                    },
                  }}
                >
                  {isPending ? <CircularProgress size={24} sx={{ color: '#fff' }} /> : 'Send Reset Link'}
                </Button>
              </Box>
            )}
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Link component={RouterLink} to="/login" variant="body2" sx={{ color: 'primary.main' }}>
                ← Back to Login
              </Link>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
