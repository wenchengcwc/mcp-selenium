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
DEBUG = True

def log_debug(message):
    if DEBUG:
        sys.stderr.write(f"DEBUG: {message}\n")
        sys.stderr.flush()

def log_error(message):
    sys.stderr.write(f"ERROR: {message}\n")
    sys.stderr.flush()

def send_response(response):
    log_debug(f"Sending response: {json.dumps(response)}")
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()

[... rest of the file unchanged until handle_stdio() ...]

def handle_stdio():
    """Handle stdio communication (JSON-RPC style)."""
    server = SeleniumServer()

    while True:
        try:
            log_debug("Waiting for input...")
            line = sys.stdin.readline()
            if not line:
                log_debug("End of input stream")
                break

            log_debug(f"Received raw input: {line.strip()}")
            
            try:
                request = json.loads(line)
                log_debug(f"Parsed request: {json.dumps(request)}")
            except json.JSONDecodeError as e:
                log_error(f"Failed to parse JSON: {e}")
                send_response({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                })
                continue

            # Get method from either method or type field
            method = request.get("method")
            if not method:
                method = request.get("type")
                log_debug(f"Using type field for method: {method}")

            request_id = request.get("id")
            log_debug(f"Request ID: {request_id}")

            if not method:
                log_error("No method or type field found in request")
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request - no method specified"
                    }
                })
                continue

            if method == "initialize":
                log_debug("Handling initialize request")
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "name": "selenium",
                        "version": "0.2.0",
                        "tools": [
                            # ... tools list unchanged ...
                        ]
                    }
                }
                send_response(response)

            elif method == "invoke":
                log_debug("Handling invoke request")
                
                # Get tool and params
                if "tool" in request:
                    tool_name = request["tool"]
                    params = request.get("parameters", {})
                    log_debug("Using direct tool/parameters fields")
                else:
                    params_obj = request.get("params", {})
                    tool_name = params_obj.get("tool")
                    params = params_obj.get("parameters", {})
                    log_debug("Using params.tool/params.parameters fields")

                log_debug(f"Tool: {tool_name}")
                log_debug(f"Parameters: {json.dumps(params)}")

                if not tool_name:
                    log_error("No tool specified in invoke request")
                    send_response({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params - no tool specified"
                        }
                    })
                    continue

                # dispatch to the corresponding method
                try:
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
                        send_response({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Unknown tool: {tool_name}"
                            }
                        })
                        continue

                    log_debug(f"Tool result: {json.dumps(result)}")

                    if result.get("isError"):
                        send_response({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32000,
                                "message": result["content"][0]["text"] if result["content"] else "Unknown error"
                            }
                        })
                    else:
                        send_response({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": result
                        })

                except KeyError as e:
                    log_error(f"Missing required parameter: {e}")
                    send_response({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": f"Missing required parameter: {e}"
                        }
                    })
                except Exception as e:
                    log_error(f"Error executing tool: {e}")
                    send_response({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32000,
                            "message": str(e)
                        }
                    })

            else:
                log_error(f"Unknown method: {method}")
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                })

        except KeyboardInterrupt:
            log_debug("Received keyboard interrupt")
            break
        except Exception as e:
            log_error(f"Unexpected error: {e}")
            traceback.print_exc(file=sys.stderr)
            try:
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id if 'request_id' in locals() else None,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                })
            except:
                log_error("Failed to send error response")

    log_debug("Cleaning up server")
    server.cleanup()

if __name__ == "__main__":
    handle_stdio()