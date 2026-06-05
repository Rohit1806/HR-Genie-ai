import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Drawer,
  IconButton,
  Typography,
  Divider,
  TextField,
  Button,
  Avatar,
  Paper,
  Chip,
  List,
  ListItem,
  CircularProgress,
} from '@mui/material';
import { Close as CloseIcon, Send as SendIcon, AutoAwesome as CopilotIcon } from '@mui/icons-material';
import axios from '@/config/axios';
import AIBadge from '@/components/ui/AIBadge';

interface AICopilotDrawerProps {
  open: boolean;
  onClose: () => void;
}

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export default function AICopilotDrawer({ open, onClose }: AICopilotDrawerProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: "Hello! I am HRGenie's AI assistant. I can help you draft emails, analyze employee flight risks, generate interview questions, and synthesize performance reviews. What would you like to do?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const quickPrompts = [
    'Analyze flight risk for engineering department',
    'Draft an offer letter for Lead Python Dev',
    'Generate interview questions for UI Designer',
    'Synthesize performance reviews',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim()) return;

    const userMessage: Message = {
      id: String(Date.now()),
      sender: 'user',
      text: textToSend,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('message', textToSend);
      
      const response = await axios.post('/api/v1/ai/copilot/chat', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const aiMessage: Message = {
        id: String(Date.now() + 1),
        sender: 'ai',
        text: response.data.reply || "Sorry, I couldn't process that request.",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Copilot error:', error);
      const errorMessage: Message = {
        id: String(Date.now() + 2),
        sender: 'ai',
        text: 'Error interacting with AI Copilot. Please check your Gemini connection or API configuration.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: { xs: '100%', sm: 400 },
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.paper',
          borderLeft: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      {/* Header */}
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box display="flex" alignItems="center" gap={1}>
          <Avatar sx={{ bgcolor: 'rgba(139, 92, 246, 0.1)', color: '#8B5CF6' }}>
            <CopilotIcon />
          </Avatar>
          <Box>
            <Box display="flex" alignItems="center" gap={0.5}>
              <Typography variant="h6" fontWeight={700}>HRGenie Copilot</Typography>
              <AIBadge label="AI" tooltip="Next-generation AI HR assistant" />
            </Box>
            <Typography variant="caption" color="text.secondary">Next-gen AI HR assistant</Typography>
          </Box>
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>
      <Divider />

      {/* Messages */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {messages.map((msg) => (
          <Box
            key={msg.id}
            sx={{
              display: 'flex',
              flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
              gap: 1.5,
            }}
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: msg.sender === 'user' ? 'primary.main' : '#8B5CF6',
                fontSize: '0.8rem',
              }}
            >
              {msg.sender === 'user' ? 'U' : 'AI'}
            </Avatar>
            <Paper
              sx={{
                p: 1.5,
                maxWidth: '75%',
                bgcolor: msg.sender === 'user' ? 'primary.main' : 'action.hover',
                borderRadius: msg.sender === 'user' ? '12px 4px 12px 12px' : '4px 12px 12px 12px',
                border: '1px solid',
                borderColor: msg.sender === 'user' ? 'primary.main' : 'divider',
              }}
            >
              <Typography variant="body2" sx={{ color: msg.sender === 'user' ? 'primary.contrastText' : 'text.primary', whiteSpace: 'pre-wrap' }}>
                {msg.text}
              </Typography>
            </Paper>
          </Box>
        ))}
        {loading && (
          <Box display="flex" gap={1.5}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: '#8B5CF6' }}>
              <CircularProgress size={16} color="inherit" />
            </Avatar>
            <Paper sx={{ p: 1.5, bgcolor: 'action.hover', borderRadius: '4px 12px 12px 12px', border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="body2" color="text.secondary">Thinking...</Typography>
            </Paper>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Quick suggestions */}
      {messages.length === 1 && (
        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Typography variant="caption" fontWeight={600} color="text.secondary">
            SUGGESTED PROMPTS
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {quickPrompts.map((prompt) => (
              <Chip
                key={prompt}
                label={prompt}
                onClick={() => handleSend(prompt)}
                sx={{
                  bgcolor: 'action.hover',
                  '&:hover': { bgcolor: 'action.selected' },
                  fontSize: '0.75rem',
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      <Divider />
      {/* Input */}
      <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Ask HRGenie Copilot..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
          disabled={loading}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={() => handleSend(input)}
          disabled={loading}
          sx={{ minWidth: 48, p: 0 }}
        >
          <SendIcon fontSize="small" />
        </Button>
      </Box>
    </Drawer>
  );
}
