import { Builder, By, Key, until } from 'selenium-webdriver';
import { Options as ChromeOptions } from 'selenium-webdriver/chrome.js';
import { Options as FirefoxOptions } from 'selenium-webdriver/firefox.js';
import chrome from 'selenium-webdriver/chrome.js';
import firefox from 'selenium-webdriver/firefox.js';
import { promisify } from 'util';
import { exec } from 'child_process';
import { resolve } from 'path';

const execAsync = promisify(exec);

export class SeleniumServer {
    constructor() {
        this.drivers = new Map();
        this.currentSession = null;
    }

    async _getDriverPath(browser) {
        try {
            // Use webdriver-manager to get the path to the latest driver
            const { stdout } = await execAsync('webdriver-manager update --versions.standalone latest');
            const driverPath = stdout.match(/driver.*?path: (.*?)$/m)?.[1];
            return driverPath;
        } catch (error) {
            console.error('Error getting driver path:', error);
            throw new Error('Failed to get WebDriver path');
        }
    }

    async startBrowser(browser, options = {}) {
        try {
            let builder = new Builder();
            let driver;

            // Get the driver path from webdriver-manager
            const driverPath = await this._getDriverPath(browser);

            if (browser === 'chrome') {
                const chromeOptions = new ChromeOptions();
                if (options.headless) {
                    chromeOptions.addArguments('--headless=new');
                }
                if (options.arguments) {
                    options.arguments.forEach(arg => chromeOptions.addArguments(arg));
                }
                
                const service = new chrome.ServiceBuilder(driverPath);
                driver = await builder
                    .forBrowser('chrome')
                    .setChromeOptions(chromeOptions)
                    .setChromeService(service)
                    .build();
            } else if (browser === 'firefox') {
                const firefoxOptions = new FirefoxOptions();
                if (options.headless) {
                    firefoxOptions.addArguments('--headless');
                }
                if (options.arguments) {
                    options.arguments.forEach(arg => firefoxOptions.addArguments(arg));
                }
                
                const service = new firefox.ServiceBuilder(driverPath);
                driver = await builder
                    .forBrowser('firefox')
                    .setFirefoxOptions(firefoxOptions)
                    .setFirefoxService(service)
                    .build();
            } else {
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Unsupported browser: ${browser}`
                        }
                    ],
                    isError: true
                };
            }

            const sessionId = `${browser}_${Date.now()}`;
            this.drivers.set(sessionId, driver);
            this.currentSession = sessionId;

            return {
                content: [
                    {
                        type: 'text',
                        text: `Browser started with session_id: ${sessionId}`
                    }
                ],
                session_id: sessionId,
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error starting browser: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async navigate(url) {
        if (!this.currentSession) {
            return {
                content: [
                    { type: 'text', text: 'No active browser session' }
                ],
                isError: true
            };
        }
        try {
            await this.drivers.get(this.currentSession).get(url);
            return {
                content: [
                    {
                        type: 'text',
                        text: `Navigated to: ${url}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error navigating: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async findElement(by, value, timeout = 10000) {
        try {
            const element = await this._getElement(by, value, timeout);
            const tagName = await element.getTagName();
            const text = await element.getText();
            
            return {
                content: [
                    {
                        type: 'text',
                        text: 'Element found.'
                    },
                    {
                        type: 'text',
                        text: `tag_name: ${tagName}, text: ${text}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error finding element: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async clickElement(by, value, timeout = 10000) {
        try {
            const element = await this._getElement(by, value, timeout);
            await element.click();
            return {
                content: [
                    {
                        type: 'text',
                        text: `Clicked element located by ${by}=${value}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error clicking element: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async typeText(by, value, text, clearFirst = true, timeout = 10000) {
        try {
            const element = await this._getElement(by, value, timeout);
            if (clearFirst) {
                await element.clear();
            }
            await element.sendKeys(text);
            return {
                content: [
                    {
                        type: 'text',
                        text: `Typed text into element located by ${by}=${value}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error typing text: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async hover(by, value, timeout = 10000) {
        try {
            const element = await this._getElement(by, value, timeout);
            const actions = this.drivers.get(this.currentSession).actions({ async: true });
            await actions.move({ origin: element }).perform();
            return {
                content: [
                    {
                        type: 'text',
                        text: `Hovered over element located by ${by}=${value}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error hovering over element: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async dragAndDrop(sourceBy, sourceValue, targetBy, targetValue, timeout = 10000) {
        try {
            const source = await this._getElement(sourceBy, sourceValue, timeout);
            const target = await this._getElement(targetBy, targetValue, timeout);
            const actions = this.drivers.get(this.currentSession).actions({ async: true });
            await actions.dragAndDrop(source, target).perform();
            return {
                content: [
                    {
                        type: 'text',
                        text: `Dragged from ${sourceValue} to ${targetValue}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error dragging and dropping: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async doubleClick(by, value, timeout = 10000) {
        try {
            const element = await this._getElement(by, value, timeout);
            const actions = this.drivers.get(this.currentSession).actions({ async: true });
            await actions.doubleClick(element).perform();
            return {
                content: [
                    {
                        type: 'text',
                        text: `Double-clicked element located by ${by}=${value}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error double-clicking: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async rightClick(by, value, timeout = 10000) {
        try {
            const element = await this._getElement(by, value, timeout);
            const actions = this.drivers.get(this.currentSession).actions({ async: true });
            await actions.contextClick(element).perform();
            return {
                content: [
                    {
                        type: 'text',
                        text: `Right-clicked element located by ${by}=${value}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error right-clicking element: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async pressKey(key, by = null, value = null, timeout = 10000) {
        const keyMap = {
            'ENTER': Key.RETURN,
            'TAB': Key.TAB,
            'ESCAPE': Key.ESCAPE,
            'BACKSPACE': Key.BACK_SPACE,
            'DELETE': Key.DELETE,
            'ARROW_DOWN': Key.ARROW_DOWN,
            'ARROW_UP': Key.ARROW_UP,
            'ARROW_LEFT': Key.ARROW_LEFT,
            'ARROW_RIGHT': Key.ARROW_RIGHT
        };

        if (!keyMap[key]) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Unsupported key: ${key}`
                    }
                ],
                isError: true
            };
        }

        try {
            if (by && value) {
                const element = await this._getElement(by, value, timeout);
                await element.sendKeys(keyMap[key]);
            } else {
                const actions = this.drivers.get(this.currentSession).actions({ async: true });
                await actions.sendKeys(keyMap[key]).perform();
            }
            return {
                content: [
                    {
                        type: 'text',
                        text: `Pressed ${key}.`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error pressing key: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async uploadFile(by, value, filePath, timeout = 10000) {
        try {
            const element = await this._getElement(by, value, timeout);
            const absolutePath = resolve(filePath);
            await element.sendKeys(absolutePath);
            return {
                content: [
                    {
                        type: 'text',
                        text: `Uploaded file ${filePath} to element located by ${by}=${value}`
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error uploading file: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async takeScreenshot() {
        if (!this.currentSession) {
            return {
                content: [
                    {
                        type: 'text',
                        text: 'No active browser session'
                    }
                ],
                isError: true
            };
        }
        try {
            const screenshot = await this.drivers.get(this.currentSession).takeScreenshot();
            return {
                content: [
                    {
                        type: 'text',
                        text: 'Screenshot captured'
                    },
                    {
                        type: 'image',
                        data: screenshot,
                        mimeType: 'image/png'
                    }
                ],
                isError: false
            };
        } catch (e) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Error taking screenshot: ${e.message}`
                    }
                ],
                isError: true
            };
        }
    }

    async cleanup() {
        for (const driver of this.drivers.values()) {
            try {
                await driver.quit();
            } catch (e) {
                console.error('Error during cleanup:', e);
            }
        }
        this.drivers.clear();
        this.currentSession = null;
    }

    async _getElement(by, value, timeout = 10000) {
        if (!this.currentSession) {
            throw new Error('No active browser session');
        }

        const driver = this.drivers.get(this.currentSession);
        const byMap = {
            'id': By.id,
            'css': By.css,
            'xpath': By.xpath,
            'name': By.name,
            'tag': By.tagName,
            'class': By.className
        };

        const locator = byMap[by];
        if (!locator) {
            throw new Error(`Invalid locator strategy: ${by}`);
        }

        return await driver.wait(until.elementLocated(locator(value)), timeout);
    }
}