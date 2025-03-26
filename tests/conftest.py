import os
import pytest
import time
from datetime import datetime
from typing import List, Dict, Any

class SeleniumCustomReporter:
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """
        Capture detailed test information
        """
        outcome = yield
        report = outcome.get_result()
        
        # Only process test call phase
        if report.when == "call":
            # Capture start and end times
            start_time = getattr(item, 'start_time', datetime.now())
            end_time = datetime.now()

            # Determine browser type
            browser_type = self._get_browser_type(item)

            extra_info = {
                'test_name': item.name,
                'start_time': start_time,
                'end_time': end_time,
                'duration': report.duration,
                'result': report.outcome,
                'browser': browser_type
            }
            self.test_results.append(extra_info)

    def _get_browser_type(self, item):
        """
        Determine browser type based on test markers
        """
        # Check for headless marker first
        if item.get_closest_marker('headless'):
            return 'Headless'
        
        # Check for specific browser markers
        browser_markers = ['chrome', 'firefox', 'safari', 'edge']
        for marker in browser_markers:
            if item.get_closest_marker(marker):
                return marker.capitalize()
        
        # Default browser
        return 'Chrome'

    def generate_html_report(self, report_path='selenium_test_report.html'):
        """
        Create detailed HTML report with specific format
        """
        html_content = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>Selenium Test Report</title>',
            '<style>',
            'body { font-family: monospace; white-space: pre-wrap; line-height: 1.6; }',
            '.pass { color: green; }',
            '.fail { color: red; }',
            '.skip { color: orange; }',
            '</style>',
            '</head>',
            '<body>'
        ]

        for test in self.test_results:
            # Format duration to HH:MM:SS
            hours, rem = divmod(int(test['duration']), 3600)
            minutes, seconds = divmod(rem, 60)
            duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Create test report entry with exact specified format
            test_report = (
                f"TestMethod: {test['test_name']}\n"
                f"Duration: {duration_formatted} | "
                f"Started: {test['start_time'].strftime('%Y-%m-%d %H:%M:%S')} | "
                f"Ended: {test['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Browsers: {test['browser']}\n"
                f"Result: <span class='{test['result']}'>{test['result'].upper()}</span>\n\n"
            )
            html_content.append(test_report)

        html_content.extend([
            '</body>',
            '</html>'
        ])

        # Write HTML report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))

def pytest_configure(config):
    """
    Register custom report plugin
    """
    selenium_reporter = SeleniumCustomReporter()
    config.pluginmanager.register(selenium_reporter, "selenium-custom-reporter")
    config.selenium_reporter = selenium_reporter

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Generate HTML report after test run
    """
    if hasattr(config, 'selenium_reporter'):
        report_path = 'selenium_test_report.html'
        config.selenium_reporter.generate_html_report(report_path)
        print(f"\nHTML Report generated: {report_path}")

# Conftest for Selenium WebDriver setup
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def pytest_addoption(parser):
    """
    Add command-line options for browser and headless mode
    """
    parser.addoption(
        "--browser", 
        action="store", 
        default="chrome", 
        help="specify browser: chrome, firefox, safari"
    )
    parser.addoption(
        "--headless", 
        action="store_true", 
        default=False, 
        help="run tests in headless mode"
    )

@pytest.fixture(scope="function")
def selenium_driver(request):
    """
    Fixture to initialize WebDriver based on configuration
    """
    browser = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    if browser == 'chrome':
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
    elif browser == 'firefox':
        firefox_options = webdriver.FirefoxOptions()
        if headless:
            firefox_options.add_argument("-headless")
        driver = webdriver.Firefox(options=firefox_options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    # Set up implicit wait and maximize window
    driver.implicitly_wait(10)
    driver.maximize_window()

    yield driver

    # Teardown
    driver.quit()


