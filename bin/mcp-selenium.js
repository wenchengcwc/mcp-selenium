#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get the absolute path to the Python script
const pythonScript = path.join(__dirname, '..', 'src', 'mcp_server_selenium', 'server.py');

// Make sure the Python script exists
if (!fs.existsSync(pythonScript)) {
    console.error(`Error: Could not find Python script at ${pythonScript}`);
    process.exit(1);
}

// Make the script executable
fs.chmodSync(pythonScript, '755');

// Run the Python script
const result = spawnSync('/usr/bin/python3', [pythonScript], {
    stdio: 'inherit',
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
});

if (result.error) {
    console.error('Failed to start Python script:', result.error);
    process.exit(1);
}

process.exit(result.status);
