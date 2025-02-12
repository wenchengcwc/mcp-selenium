import sys
import json
import traceback
from typing import Dict, Any, Optional, List
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
import os

class SeleniumServer:
    def __init__(self):
        self.drivers: Dict[str, WebDriver] = {}
        self.current_session: Optional[str] = None

    def start_browser(self, browser: str, options: Dict[str, Any] = None) -> str:
        """Start a new browser session."""
        options = options or {}
        
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
            raise ValueError(f"Unsupported browser: {browser}")

        session_id = f"{browser}_{id(driver)}"
        self.drivers[session_id] = driver
        self.current_session = session_id
        return session_id

    def navigate(self, url: str) -> None:
        """Navigate to a URL in the current browser session."""
        if not self.current_session:
            raise RuntimeError("No active browser session")
        self.drivers[self.current_session].get(url)

    def find_element(self, by: str, value: str, timeout: int = 10) -> Dict[str, Any]:
        """Find an element on the page using the specified locator strategy."""
        element = self._get_element(by, value, timeout)
        return {
            "tag_name": element.tag_name,
            "text": element.text,
            "is_displayed": element.is_displayed(),
            "is_enabled": element.is_enabled(),
            "location": element.location,
            "size": element.size
        }

    def click_element(self, by: str, value: str, timeout: int = 10) -> None:
        """Click on an element."""
        element = self._get_element(by, value, timeout)
        element.click()

    def type_text(self, by: str, value: str, text: str, clear_first: bool = True, timeout: int = 10) -> None:
        """Type text into an input element."""
        element = self._get_element(by, value, timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def _get_element(self, by: str, value: str, timeout: int = 10):
        """Internal method to find and return a WebElement."""
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

    def hover(self, by: str, value: str, timeout: int = 10) -> None:
        """Mouse hover over an element."""
        element = self._get_element(by, value, timeout)
        ActionChains(self.drivers[self.current_session]).move_to_element(element).perform()

    def drag_and_drop(self, source_by: str, source_value: str, target_by: str, target_value: str, timeout: int = 10) -> None:
        """Drag and drop an element to a target location."""
        source = self._get_element(source_by, source_value, timeout)
        target = self._get_element(target_by, target_value, timeout)
        ActionChains(self.drivers[self.current_session]).drag_and_drop(source, target).perform()

    def double_click(self, by: str, value: str, timeout: int = 10) -> None:
        """Double click on an element."""
        element = self._get_element(by, value, timeout)
        ActionChains(self.drivers[self.current_session]).double_click(element).perform()

    def right_click(self, by: str, value: str, timeout: int = 10) -> None:
        """Right click on an element."""
        element = self._get_element(by, value, timeout)
        ActionChains(self.drivers[self.current_session]).context_click(element).perform()

    def press_key(self, key: str, by: str = None, value: str = None, timeout: int = 10) -> None:
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
        
        selenium_key = key_map.get(key)
        if not selenium_key:
            raise ValueError(f"Unsupported key: {key}")

        if by and value:
            element = self._get_element(by, value, timeout)
            element.send_keys(selenium_key)
        else:
            ActionChains(self.drivers[self.current_session]).send_keys(selenium_key).perform()

    def upload_file(self, by: str, value: str, file_path: str, timeout: int = 10) -> None:
        """Upload a file using a file input element."""
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        element = self._get_element(by, value, timeout)
        element.send_keys(os.path.abspath(file_path))

    def cleanup(self):
        """Clean up browser sessions when shutting down."""
        for driver in self.drivers.values():
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
        self.current_session = None

def handle_stdio():
    """Handle stdio communication."""
    server = SeleniumServer()
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
                
            try:
                request = json.loads(line)
                
                if request.get("type") == "initialize":
                    response = {
                        "id": request.get("id"),
                        "type": "success",
                        "result": {
                            "name": "selenium",
                            "version": "0.1.0",
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
                                            "enum": ["ENTER", "TAB", "ESCAPE", "BACKSPACE", "DELETE", 
                                                    "ARROW_DOWN", "ARROW_UP", "ARROW_LEFT", "ARROW_RIGHT"]
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
                                }
                            ]
                        }
                    }
                elif request.get("type") == "invoke":
                    tool_name = request["tool"]
                    params = request["parameters"]
                    tool_method = getattr(server, tool_name)
                    result = tool_method(**params)
                    response = {
                        "id": request.get("id"),
                        "type": "success",
                        "result": result
                    }
                else:
                    response = {
                        "id": request.get("id"),
                        "type": "error",
                        "error": f"Unknown request type: {request.get('type')}"
                    }
                    
            except Exception as e:
                traceback.print_exc(file=sys.stderr)
                response = {
                    "id": request.get("id"),
                    "type": "error",
                    "error": str(e)
                }
            
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        pass
    finally:
        server.cleanup()

if __name__ == "__main__":
    handle_stdio()