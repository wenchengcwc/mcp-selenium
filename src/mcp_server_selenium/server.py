#!/usr/bin/env python3

import sys
import json
import traceback
import os
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import base64

# We'll adopt the same idea of an array "content" with typed data,
# and an "isError" boolean, to be consistent with the Playwright approach.

class SeleniumServer:
    def __init__(self):
        self.drivers: Dict[str, WebDriver] = {}
        self.current_session: Optional[str] = None

    # [Previous methods remain unchanged...]
    # Keeping all the existing methods exactly as they are
    
    def start_browser(self, browser: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a new browser session (returns dict with session_id)."""
        options = options or {}

        try:
            if browser == "chrome":
                chrome_options = webdriver.ChromeOptions()
                if options.get("headless"):
                    chrome_options.add_argument("--headless")
                for arg in options.get("arguments", []):
                    chrome_options.add_argument(arg)
                driver = webdriver.Chrome(
                    service=webdriver.ChromeService(ChromeDriverManager().install()),
                    options=chrome_options
                )
            elif browser == "firefox":
                firefox_options = webdriver.FirefoxOptions()
                if options.get("headless"):
                    firefox_options.add_argument("--headless")
                for arg in options.get("arguments", []):
                    firefox_options.add_argument(arg)
                driver = webdriver.Firefox(
                    service=webdriver.FirefoxService(GeckoDriverManager().install()),
                    options=firefox_options
                )
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unsupported browser: {browser}"
                        }
                    ],
                    "isError": True
                }

            session_id = f"{browser}_{id(driver)}"
            self.drivers[session_id] = driver
            self.current_session = session_id
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Browser started with session_id: {session_id}"
                    }
                ],
                "session_id": session_id,
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error starting browser: {str(e)}"
                    }
                ],
                "isError": True
            }

    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL in the current browser session."""
        if not self.current_session:
            return {
                "content": [
                    {"type": "text", "text": "No active browser session"}
                ],
                "isError": True
            }
        try:
            self.drivers[self.current_session].get(url)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Navigated to: {url}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error navigating: {str(e)}"
                    }
                ],
                "isError": True
            }

    def find_element(self, by: str, value: str, timeout: int = 10) -> Dict[str, Any]:
        """Find an element on the page."""
        try:
            element = self._get_element(by, value, timeout)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Element found.",
                    },
                    {
                        "type": "text",
                        "text": f"tag_name: {element.tag_name}, text: {element.text}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error finding element: {str(e)}"
                    }
                ],
                "isError": True
            }

    def click_element(self, by: str, value: str, timeout: int = 10) -> Dict[str, Any]:
        """Click on an element."""
        try:
            element = self._get_element(by, value, timeout)
            element.click()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Clicked element located by {by}={value}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error clicking element: {str(e)}"
                    }
                ],
                "isError": True
            }

    def type_text(self, by: str, value: str, text: str, clear_first: bool = True, timeout: int = 10) -> Dict[str, Any]:
        """Type text into an input element."""
        try:
            element = self._get_element(by, value, timeout)
            if clear_first:
                element.clear()
            element.send_keys(text)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Typed text into element located by {by}={value}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {"type": "text", "text": f"Error typing text: {str(e)}"}
                ],
                "isError": True
            }

    def hover(self, by: str, value: str, timeout: int = 10) -> Dict[str, Any]:
        """Hover on an element."""
        try:
            element = self._get_element(by, value, timeout)
            ActionChains(self.drivers[self.current_session]).move_to_element(element).perform()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Hovered over element located by {by}={value}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error hovering over element: {str(e)}"
                    }
                ],
                "isError": True
            }

    def drag_and_drop(self,
                      source_by: str,
                      source_value: str,
                      target_by: str,
                      target_value: str,
                      timeout: int = 10) -> Dict[str, Any]:
        """Drag an element to a target location."""
        try:
            source = self._get_element(source_by, source_value, timeout)
            target = self._get_element(target_by, target_value, timeout)
            ActionChains(self.drivers[self.current_session]).drag_and_drop(source, target).perform()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Dragged from {source_value} to {target_value}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error dragging and dropping: {str(e)}"
                    }
                ],
                "isError": True
            }

    def double_click(self, by: str, value: str, timeout: int = 10) -> Dict[str, Any]:
        """Double click an element."""
        try:
            element = self._get_element(by, value, timeout)
            ActionChains(self.drivers[self.current_session]).double_click(element).perform()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Double-clicked element located by {by}={value}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {"type": "text", "text": f"Error double-clicking: {str(e)}"}
                ],
                "isError": True
            }

    def right_click(self, by: str, value: str, timeout: int = 10) -> Dict[str, Any]:
        """Right click an element."""
        try:
            element = self._get_element(by, value, timeout)
            ActionChains(self.drivers[self.current_session]).context_click(element).perform()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Right-clicked element located by {by}={value}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {"type": "text", "text": f"Error right-clicking element: {str(e)}"}
                ],
                "isError": True
            }

    def press_key(self, key: str, by: str = None, value: str = None, timeout: int = 10) -> Dict[str, Any]:
        """Press a keyboard key, optionally on a specific element."""
        key_map = {
            "ENTER": Keys.ENTER,
            "TAB": Keys.TAB,
            "ESCAPE": Keys.ESCAPE,
            "BACKSPACE": Keys.BACK_SPACE,
            "DELETE": Keys.DELETE,
            "ARROW_DOWN": Keys.ARROW_DOWN,
            "ARROW_UP": Keys.ARROW_UP,
            "ARROW_LEFT": Keys.ARROW_LEFT,
            "ARROW_RIGHT": Keys.ARROW_RIGHT
        }
        if key not in key_map:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Unsupported key: {key}"
                    }
                ],
                "isError": True
            }
        try:
            if by and value:
                element = self._get_element(by, value, timeout)
                element.send_keys(key_map[key])
            else:
                # if no element specified, just do an ActionChains send_keys
                driver = self.drivers[self.current_session]
                ActionChains(driver).send_keys(key_map[key]).perform()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Pressed {key}."
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {"type": "text", "text": f"Error pressing key: {str(e)}"}
                ],
                "isError": True
            }

    def upload_file(self, by: str, value: str, file_path: str, timeout: int = 10) -> Dict[str, Any]:
        """Upload a file using a file input element."""
        if not os.path.exists(file_path):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"File does not exist: {file_path}"
                    }
                ],
                "isError": True
            }
        try:
            element = self._get_element(by, value, timeout)
            element.send_keys(os.path.abspath(file_path))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Uploaded file {file_path} to element located by {by}={value}"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error uploading file: {str(e)}"
                    }
                ],
                "isError": True
            }

    def take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot of the current page, returning base64 data."""
        if not self.current_session:
            return {
                "content": [
                    {
                        "type": "text", "text": "No active browser session"
                    }
                ],
                "isError": True
            }
        try:
            driver = self.drivers[self.current_session]
            screenshot_png = driver.get_screenshot_as_png()
            b64_data = base64.b64encode(screenshot_png).decode("utf-8")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Screenshot captured"
                    },
                    {
                        "type": "image",
                        "data": b64_data,
                        "mimeType": "image/png"
                    }
                ],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error taking screenshot: {str(e)}"
                    }
                ],
                "isError": True
            }

    def cleanup(self):
        """Clean up browser sessions when shutting down."""
        for driver in self.drivers.values():
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
        self.current_session = None

    def _get_element(self, by: str, value: str, timeout: int = 10):
        if not self.current_session:
            raise RuntimeError("No active browser session")
        driver = self.drivers[self.current_session]
        by_map = {
            "id": By.ID,
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME
        }
        selenium_by = by_map.get(by)
        if not selenium_by:
            raise ValueError(f"Invalid locator strategy: {by}")
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((selenium_by, value))
        )


def handle_stdio():
    """Handle stdio communication (JSON-RPC style)."""
    server = SeleniumServer()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request = json.loads(line)
            method = request.get("method") or request.get("type")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "name": "selenium",
                        "version": "0.2.0",
                        "tools": [
                            {
                                "name": "start_browser",
                                "description": "Start a new browser session",
                                "parameters": {
                                    "browser": {
                                        "type": "string",
                                        "enum": ["chrome", "firefox"]
                                    },
                                    "options": {
                                        "type": "object",
                                        "properties": {
                                            "headless": {"type": "boolean"},
                                            "arguments": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            }
                                        }
                                    }
                                },
                                "required": ["browser"]
                            },
                            {
                                "name": "navigate",
                                "description": "Navigate to a URL",
                                "parameters": {
                                    "url": {
                                        "type": "string",
                                        "format": "uri"
                                    }
                                },
                                "required": ["url"]
                            },
                            {
                                "name": "find_element",
                                "description": "Find an element on the page",
                                "parameters": {
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "value": {"type": "string"},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["by", "value"]
                            },
                            {
                                "name": "click_element",
                                "description": "Click on an element",
                                "parameters": {
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "value": {"type": "string"},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["by", "value"]
                            },
                            {
                                "name": "type_text",
                                "description": "Type text into an input element",
                                "parameters": {
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "value": {"type": "string"},
                                    "text": {"type": "string"},
                                    "clear_first": {"type": "boolean", "default": True},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["by", "value", "text"]
                            },
                            {
                                "name": "hover",
                                "description": "Mouse hover over an element",
                                "parameters": {
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "value": {"type": "string"},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["by", "value"]
                            },
                            {
                                "name": "drag_and_drop",
                                "description": "Drag and drop an element to a target location",
                                "parameters": {
                                    "source_by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "source_value": {"type": "string"},
                                    "target_by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "target_value": {"type": "string"},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["source_by", "source_value", "target_by", "target_value"]
                            },
                            {
                                "name": "double_click",
                                "description": "Double click on an element",
                                "parameters": {
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "value": {"type": "string"},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["by", "value"]
                            },
                            {
                                "name": "right_click",
                                "description": "Right click on an element",
                                "parameters": {
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "value": {"type": "string"},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["by", "value"]
                            },
                            {
                                "name": "press_key",
                                "description": "Press a keyboard key",
                                "parameters": {
                                    "key": {
                                        "type": "string",
                                        "enum": ["ENTER", "TAB", "ESCAPE", "BACKSPACE", "DELETE", "ARROW_DOWN", "ARROW_UP", "ARROW_LEFT", "ARROW_RIGHT"]
                                    },
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"],
                                        "description": "Optional: target element"
                                    },
                                    "value": {
                                        "type": "string",
                                        "description": "Optional: target element"
                                    },
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["key"]
                            },
                            {
                                "name": "upload_file",
                                "description": "Upload a file using a file input element",
                                "parameters": {
                                    "by": {
                                        "type": "string",
                                        "enum": ["id", "css", "xpath", "name", "tag", "class"]
                                    },
                                    "value": {"type": "string"},
                                    "file_path": {"type": "string"},
                                    "timeout": {"type": "integer", "default": 10}
                                },
                                "required": ["by", "value", "file_path"]
                            },
                            {
                                "name": "take_screenshot",
                                "description": "Take a screenshot of the current page.",
                                "parameters": {},
                                "required": []
                            }
                        ]
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            elif method == "invoke":
                # Handle both old and new parameter formats
                if "tool" in request:
                    tool_name = request["tool"]
                    params = request.get("parameters", {})
                else:
                    params_obj = request.get("params", {})
                    tool_name = params_obj.get("tool")
                    params = params_obj.get("parameters", {})

                # dispatch to the corresponding method
                if tool_name == "start_browser":
                    result = server.start_browser(params.get("browser"), params.get("options"))
                elif tool_name == "navigate":
                    url = params["url"]
                    result = server.navigate(url)
                elif tool_name == "find_element":
                    result = server.find_element(
                        by=params["by"],
                        value=params["value"],
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "click_element":
                    result = server.click_element(
                        by=params["by"],
                        value=params["value"],
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "type_text":
                    result = server.type_text(
                        by=params["by"],
                        value=params["value"],
                        text=params["text"],
                        clear_first=params.get("clear_first", True),
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "hover":
                    result = server.hover(
                        by=params["by"],
                        value=params["value"],
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "drag_and_drop":
                    result = server.drag_and_drop(
                        source_by=params["source_by"],
                        source_value=params["source_value"],
                        target_by=params["target_by"],
                        target_value=params["target_value"],
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "double_click":
                    result = server.double_click(
                        by=params["by"],
                        value=params["value"],
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "right_click":
                    result = server.right_click(
                        by=params["by"],
                        value=params["value"],
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "press_key":
                    result = server.press_key(
                        key=params["key"],
                        by=params.get("by"),
                        value=params.get("value"),
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "upload_file":
                    result = server.upload_file(
                        by=params["by"],
                        value=params["value"],
                        file_path=params["file_path"],
                        timeout=params.get("timeout", 10)
                    )
                elif tool_name == "take_screenshot":
                    result = server.take_screenshot()
                else:
                    # unknown tool
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    continue

                if result.get("isError"):
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32000,
                            "message": result["content"][0]["text"] if result["content"] else "Unknown error"
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": result
                    }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            else:
                # unknown request type
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

    server.cleanup()

if __name__ == "__main__":
    handle_stdio()