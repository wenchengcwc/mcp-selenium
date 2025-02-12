#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

const pythonScript = path.join(__dirname, '..', 'src', 'mcp_server_selenium', 'server.py');

const python = spawn('python3', [pythonScript], {
  stdio: 'inherit'
});

python.on('error', (err) => {
  console.error('Failed to start Python script:', err);
  process.exit(1);
});

python.on('close', (code) => {
  process.exit(code);
});
