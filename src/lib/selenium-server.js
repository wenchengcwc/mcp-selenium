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

    // ... [rest of the SeleniumServer class implementation] ...
}