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

# Debug logging
def log_debug(message):
    sys.stderr.write(f"DEBUG: {message}\n")
    sys.stderr.flush()

[... rest of the file unchanged until handle_stdio() ...]

def handle_stdio():
    """Handle stdio communication (JSON-RPC style)."""
    server = SeleniumServer()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            log_debug(f"Received: {line.strip()}")
            request = json.loads(line)
            method = request.get("method")
            if not method:
                method = request.get("type")
                # Convert type to method for backward compatibility
                request["method"] = method
                request.pop("type", None)

            log_debug(f"Parsed request: {json.dumps(request)}")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "name": "selenium",
                        "version": "0.2.0",
                        "tools": [
                            # ... tools list unchanged ...
                        ]
                    }
                }
                log_debug(f"Sending response: {json.dumps(response)}")
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

                log_debug(f"Tool: {tool_name}, Params: {json.dumps(params)}")

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
                    log_debug(f"Sending error response: {json.dumps(response)}")
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
                log_debug(f"Sending response: {json.dumps(response)}")
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
                log_debug(f"Sending error response: {json.dumps(response)}")
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
            log_debug(f"Sending error response: {json.dumps(response)}")
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

    server.cleanup()

if __name__ == "__main__":
    handle_stdio()