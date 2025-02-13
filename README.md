# MCP Selenium Server

A Model Context Protocol (MCP) server implementation for Selenium WebDriver, allowing AI agents to control web browsers.

## Installation

```bash
npm install -g @angiejones/mcp-selenium
```

## Usage

Start the server by running:

```bash
mcp-selenium
```

Or use with NPX in your MCP configuration:

```json
{
  "mcpServers": {
    "selenium": {
      "command": "npx",
      "args": [
        "-y",
        "@angiejones/mcp-selenium"
      ]
    }
  }
}
```

The server implements the Model Context Protocol and provides the following capabilities:

- Browser session management (Chrome and Firefox)
- Navigation
- Element interaction (find, click, type, hover)
- Advanced actions (drag and drop, keyboard input)
- Screenshots
- File uploads

## Supported Browsers

- Chrome
- Firefox

## Features

- Start browser sessions with customizable options
- Navigate to URLs
- Find elements using various locator strategies
- Click, type, and interact with elements
- Perform mouse actions (hover, drag and drop)
- Handle keyboard input
- Take screenshots
- Upload files
- Support for headless mode

## Development

To work on this project:

1. Clone the repository
2. Install dependencies: `npm install`
3. Run the server: `npm start`

## License

MIT