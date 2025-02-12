# MCP Selenium

> [!CAUTION]
> ## Still testing, not ready to use



A Model Context Protocol (MCP) server implementation for Selenium WebDriver, enabling browser automation through standardized MCP clients.

```json
{
  "mcpServers": {
    "selenium": {
      "command": "npx",
      "args": ["-y", "@angiejones/mcp-selenium"]
    }
  }
}
```

## Installation

```bash
npm install -g @angiejones/mcp-selenium
```

## Features

### Browser Management
- Start Chrome or Firefox browser sessions
- Navigate to URLs
- Support for headless mode and browser arguments

### Element Location
- Find elements using various locator strategies:
  - ID
  - CSS Selector
  - XPath
  - Name
  - Tag Name
  - Class Name

### Basic Interactions
- Click elements
- Type text
- Submit forms
- Get element text and attributes

### Advanced Interactions
- Hover over elements
- Drag and drop
- Double click
- Right click (context menu)
- Press keyboard keys
- Upload files

## Tools

### Browser Tools
- `start_browser`: Start a new browser session with optional configuration
- `navigate`: Navigate to a URL

### Element Tools
- `find_element`: Find and get information about an element
- `click_element`: Click on an element
- `type_text`: Type text into an input element with optional clearing

### Advanced Tools
- `hover`: Move mouse over an element
- `drag_and_drop`: Drag and drop elements
- `double_click`: Double click on elements
- `right_click`: Open context menu on elements
- `press_key`: Simulate keyboard key presses
- `upload_file`: Upload files through file input elements

## Requirements

- Node.js 14+
- Python 3.7+
- Chrome or Firefox browser

## License

MIT
