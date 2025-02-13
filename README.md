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

## Tools

### start_browser
Start a new browser session.

**Parameters:**
- `browser` (required): Browser to use
  - Type: string
  - Enum: ["chrome", "firefox"]
- `options`: Browser configuration options
  - Type: object
  - Properties:
    - `headless`: Run in headless mode
      - Type: boolean
    - `arguments`: Additional browser arguments
      - Type: array of strings

**Example:**
```json
{
  "tool": "start_browser",
  "parameters": {
    "browser": "chrome",
    "options": {
      "headless": true,
      "arguments": ["--no-sandbox"]
    }
  }
}
```

### navigate
Navigate to a URL.

**Parameters:**
- `url` (required): The URL to navigate to
  - Type: string
  - Format: uri

**Example:**
```json
{
  "tool": "navigate",
  "parameters": {
    "url": "https://www.example.com"
  }
}
```

### find_element
Find an element on the page.

**Parameters:**
- `by` (required): Locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value` (required): Locator value
  - Type: string
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "find_element",
  "parameters": {
    "by": "id",
    "value": "search-input",
    "timeout": 5
  }
}
```

### click_element
Click on an element.

**Parameters:**
- `by` (required): Locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value` (required): Locator value
  - Type: string
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "click_element",
  "parameters": {
    "by": "css",
    "value": ".submit-button"
  }
}
```

### type_text
Type text into an input element.

**Parameters:**
- `by` (required): Locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value` (required): Locator value
  - Type: string
- `text` (required): Text to type
  - Type: string
- `clear_first`: Clear existing text before typing
  - Type: boolean
  - Default: true
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "type_text",
  "parameters": {
    "by": "name",
    "value": "username",
    "text": "testuser",
    "clear_first": true
  }
}
```

### hover
Mouse hover over an element.

**Parameters:**
- `by` (required): Locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value` (required): Locator value
  - Type: string
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "hover",
  "parameters": {
    "by": "css",
    "value": ".dropdown-menu"
  }
}
```

### drag_and_drop
Drag and drop an element to a target location.

**Parameters:**
- `source_by` (required): Source element locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `source_value` (required): Source element locator value
  - Type: string
- `target_by` (required): Target element locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `target_value` (required): Target element locator value
  - Type: string
- `timeout`: Maximum time to wait for elements
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "drag_and_drop",
  "parameters": {
    "source_by": "id",
    "source_value": "draggable",
    "target_by": "id",
    "target_value": "droppable"
  }
}
```

### double_click
Double click on an element.

**Parameters:**
- `by` (required): Locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value` (required): Locator value
  - Type: string
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "double_click",
  "parameters": {
    "by": "css",
    "value": ".editable-text"
  }
}
```

### right_click
Right click on an element.

**Parameters:**
- `by` (required): Locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value` (required): Locator value
  - Type: string
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "right_click",
  "parameters": {
    "by": "css",
    "value": ".context-menu-trigger"
  }
}
```

### press_key
Press a keyboard key.

**Parameters:**
- `key` (required): Key to press
  - Type: string
  - Enum: ["ENTER", "TAB", "ESCAPE", "BACKSPACE", "DELETE", "ARROW_DOWN", "ARROW_UP", "ARROW_LEFT", "ARROW_RIGHT"]
- `by`: Optional target element locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value`: Optional target element locator value
  - Type: string
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "press_key",
  "parameters": {
    "key": "ENTER",
    "by": "id",
    "value": "search-input"
  }
}
```

### upload_file
Upload a file using a file input element.

**Parameters:**
- `by` (required): Locator strategy
  - Type: string
  - Enum: ["id", "css", "xpath", "name", "tag", "class"]
- `value` (required): Locator value
  - Type: string
- `file_path` (required): Path to the file to upload
  - Type: string
- `timeout`: Maximum time to wait for element
  - Type: integer
  - Default: 10 (seconds)

**Example:**
```json
{
  "tool": "upload_file",
  "parameters": {
    "by": "id",
    "value": "file-input",
    "file_path": "/path/to/file.pdf"
  }
}
```

### take_screenshot
Take a screenshot of the current page.

**Parameters:** None

**Example:**
```json
{
  "tool": "take_screenshot",
  "parameters": {}
}
```

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