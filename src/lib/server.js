import { createReadStream } from 'fs';
import { SeleniumServer } from './selenium-server.js';

const TOOL_DEFINITIONS = {
    start_browser: {
        name: 'start_browser',
        description: 'Start a new browser session',
        parameters: {
            browser: {
                type: 'string',
                enum: ['chrome', 'firefox']
            },
            options: {
                type: 'object',
                properties: {
                    headless: { type: 'boolean' },
                    arguments: {
                        type: 'array',
                        items: { type: 'string' }
                    }
                }
            }
        },
        required: ['browser']
    },
    navigate: {
        name: 'navigate',
        description: 'Navigate to a URL',
        parameters: {
            url: {
                type: 'string',
                format: 'uri'
            }
        },
        required: ['url']
    },
    find_element: {
        name: 'find_element',
        description: 'Find an element on the page',
        parameters: {
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            value: { type: 'string' },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['by', 'value']
    },
    click_element: {
        name: 'click_element',
        description: 'Click on an element',
        parameters: {
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            value: { type: 'string' },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['by', 'value']
    },
    type_text: {
        name: 'type_text',
        description: 'Type text into an input element',
        parameters: {
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            value: { type: 'string' },
            text: { type: 'string' },
            clear_first: { type: 'boolean', default: true },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['by', 'value', 'text']
    },
    hover: {
        name: 'hover',
        description: 'Mouse hover over an element',
        parameters: {
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            value: { type: 'string' },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['by', 'value']
    },
    drag_and_drop: {
        name: 'drag_and_drop',
        description: 'Drag and drop an element to a target location',
        parameters: {
            source_by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            source_value: { type: 'string' },
            target_by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            target_value: { type: 'string' },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['source_by', 'source_value', 'target_by', 'target_value']
    },
    double_click: {
        name: 'double_click',
        description: 'Double click on an element',
        parameters: {
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            value: { type: 'string' },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['by', 'value']
    },
    right_click: {
        name: 'right_click',
        description: 'Right click on an element',
        parameters: {
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            value: { type: 'string' },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['by', 'value']
    },
    press_key: {
        name: 'press_key',
        description: 'Press a keyboard key',
        parameters: {
            key: {
                type: 'string',
                enum: ['ENTER', 'TAB', 'ESCAPE', 'BACKSPACE', 'DELETE', 'ARROW_DOWN', 'ARROW_UP', 'ARROW_LEFT', 'ARROW_RIGHT']
            },
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class'],
                description: 'Optional: target element'
            },
            value: {
                type: 'string',
                description: 'Optional: target element'
            },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['key']
    },
    upload_file: {
        name: 'upload_file',
        description: 'Upload a file using a file input element',
        parameters: {
            by: {
                type: 'string',
                enum: ['id', 'css', 'xpath', 'name', 'tag', 'class']
            },
            value: { type: 'string' },
            file_path: { type: 'string' },
            timeout: { type: 'integer', default: 10 }
        },
        required: ['by', 'value', 'file_path']
    },
    take_screenshot: {
        name: 'take_screenshot',
        description: 'Take a screenshot of the current page.',
        parameters: {},
        required: []
    }
};

async function handleStdio() {
    const server = new SeleniumServer();
    const rl = createReadStream(0);
    let buffer = '';

    rl.on('data', async (chunk) => {
        buffer += chunk;
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
            try {
                const request = JSON.parse(line);
                const method = request.method || request.type;

                if (method === 'initialize') {
                    const response = {
                        jsonrpc: '2.0',
                        id: request.id,
                        result: {
                            name: 'selenium',
                            version: '0.2.0',
                            tools: Object.values(TOOL_DEFINITIONS)
                        }
                    };
                    console.log(JSON.stringify(response));
                } else if (method === 'invoke') {
                    let toolName, params;
                    if ('tool' in request) {
                        toolName = request.tool;
                        params = request.parameters || {};
                    } else {
                        const paramsObj = request.params || {};
                        toolName = paramsObj.tool;
                        params = paramsObj.parameters || {};
                    }

                    let result;
                    switch (toolName) {
                        case 'start_browser':
                            result = await server.startBrowser(params.browser, params.options);
                            break;
                        case 'navigate':
                            result = await server.navigate(params.url);
                            break;
                        case 'find_element':
                            result = await server.findElement(
                                params.by,
                                params.value,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'click_element':
                            result = await server.clickElement(
                                params.by,
                                params.value,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'type_text':
                            result = await server.typeText(
                                params.by,
                                params.value,
                                params.text,
                                params.clear_first,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'hover':
                            result = await server.hover(
                                params.by,
                                params.value,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'drag_and_drop':
                            result = await server.dragAndDrop(
                                params.source_by,
                                params.source_value,
                                params.target_by,
                                params.target_value,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'double_click':
                            result = await server.doubleClick(
                                params.by,
                                params.value,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'right_click':
                            result = await server.rightClick(
                                params.by,
                                params.value,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'press_key':
                            result = await server.pressKey(
                                params.key,
                                params.by,
                                params.value,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'upload_file':
                            result = await server.uploadFile(
                                params.by,
                                params.value,
                                params.file_path,
                                (params.timeout || 10) * 1000
                            );
                            break;
                        case 'take_screenshot':
                            result = await server.takeScreenshot();
                            break;
                        default:
                            console.log(JSON.stringify({
                                jsonrpc: '2.0',
                                id: request.id,
                                error: {
                                    code: -32601,
                                    message: `Unknown tool: ${toolName}`
                                }
                            }));
                            continue;
                    }

                    if (result.isError) {
                        console.log(JSON.stringify({
                            jsonrpc: '2.0',
                            id: request.id,
                            error: {
                                code: -32000,
                                message: result.content[0].text || 'Unknown error'
                            }
                        }));
                    } else {
                        console.log(JSON.stringify({
                            jsonrpc: '2.0',
                            id: request.id,
                            result
                        }));
                    }
                } else {
                    console.log(JSON.stringify({
                        jsonrpc: '2.0',
                        id: request.id,
                        error: {
                            code: -32601,
                            message: `Unknown method: ${method}`
                        }
                    }));
                }
            } catch (e) {
                console.error(e);
                console.log(JSON.stringify({
                    jsonrpc: '2.0',
                    id: request.id,
                    error: {
                        code: -32000,
                        message: e.message
                    }
                }));
            }
        }
    });

    rl.on('end', async () => {
        await server.cleanup();
        process.exit(0);
    });

    // Handle process termination
    process.on('SIGTERM', async () => {
        await server.cleanup();
        process.exit(0);
    });

    process.on('SIGINT', async () => {
        await server.cleanup();
        process.exit(0);
    });
}

handleStdio().catch(console.error);