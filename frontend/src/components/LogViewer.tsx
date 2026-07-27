import React, { useState, useMemo } from 'react';
import { Box, Select, MenuItem, TextField, Typography, IconButton, Chip } from '@mui/material';
import { Download, ContentCopy } from '@mui/icons-material';

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

interface Props {
  logs: LogEntry[];
}

export const LogViewer: React.FC<Props> = ({ logs }) => {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const filtered = useMemo(
    () =>
      logs.filter((l) => {
        return (
          (filter === 'ALL' || l.level === filter) &&
          (!search || l.message.toLowerCase().includes(search.toLowerCase()))
        );
      }),
    [logs, filter, search]
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Select value={filter} onChange={(e) => setFilter(e.target.value)} size="small">
          <MenuItem value="ALL">All</MenuItem>
          <MenuItem value="INFO">INFO</MenuItem>
          <MenuItem value="DEBUG">DEBUG</MenuItem>
          <MenuItem value="WARNING">WARNING</MenuItem>
          <MenuItem value="ERROR">ERROR</MenuItem>
        </Select>
        <TextField
          size="small"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ flex: 1 }}
        />
        <IconButton aria-label="Download">
          <Download />
        </IconButton>
        <IconButton
          aria-label="Copy"
          onClick={() => navigator.clipboard.writeText(JSON.stringify(logs, null, 2))}
        >
          <ContentCopy />
        </IconButton>
      </Box>
      <Box
        sx={{
          bgcolor: 'grey.900',
          color: 'grey.100',
          borderRadius: 1,
          p: 2,
          fontFamily: 'monospace',
          fontSize: '0.8rem',
          maxHeight: 400,
          overflow: 'auto',
        }}
      >
        {filtered.map((log, i) => (
          <Box key={i} sx={{ display: 'flex', gap: 2, py: 0.5 }}>
            <Typography variant="caption" sx={{ color: 'grey.400', minWidth: 180 }}>
              {log.timestamp}
            </Typography>
            <Chip label={log.level} size="small" sx={{ minWidth: 70, height: 20, fontSize: '0.65rem' }} />
            <Typography variant="body2">{log.message}</Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};
