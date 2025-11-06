#!/usr/bin/env python3
"""
Simple EGX File Downloader
Downloads PDF files from https://www.egx.com.eg/en/Services_Reports.aspx
Target: Specific year and month - NO PROCESSING, JUST DOWNLOAD
Added: File counting before and after downloads
"""

import time
import os
import random
import re
import requests
from urllib.parse import urljoin, urlparse

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("❌ Selenium not installed. Please install: pip install selenium")
    SELENIUM_AVAILABLE = False

# ================================
# CONFIGURATION - MODIFY THESE VALUES
# ================================
AUTO_DETECT = True            # Auto-detect most recent year/month from page
TARGET_YEAR = None            # Set to specific year (e.g., "2025") or None for auto-detect
TARGET_MONTH = None           # Set to specific month (e.g., "July") or None for auto-detect
DOWNLOAD_PATH = "downloads"
HEADLESS_MODE = True          # Set to False to see browser
MAX_RETRY_ATTEMPTS = 3
ELEMENT_WAIT_TIMEOUT = 20
DOWNLOAD_DELAY_MIN = 2
DOWNLOAD_DELAY_MAX = 4
BROWSER_CLOSE_WAIT = 45       # Wait 45 seconds before closing browser

# User agents for anti-detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Month ordering for comparison (supports partial names)
MONTH_ORDER = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}

class SimpleEGXDownloader:
    def __init__(self):
        """Initialize simple EGX downloader"""
        self.url = "https://www.egx.com.eg/en/Services_Reports.aspx"
        self.driver = None
        self.wait = None
        self.actions = None
        self.session = requests.Session()
        self.downloaded_count = 0
        self.failed_count = 0
        
        # File counting variables
        self.initial_file_count = 0
        self.initial_files = []
        self.final_file_count = 0
        self.final_files = []
        
        # Create download directory
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        
        print("🎯 Simple EGX File Downloader")
        if AUTO_DETECT and (TARGET_YEAR is None or TARGET_MONTH is None):
            print(f"📅 Mode: Auto-detect most recent year/month")
        else:
            print(f"📅 Target: {TARGET_MONTH} {TARGET_YEAR}")
        print(f"📁 Download folder: {DOWNLOAD_PATH}")
        print(f"⏰ Browser close wait: {BROWSER_CLOSE_WAIT} seconds")
    
    def count_pdf_files(self):
        """Count PDF files in download folder and return count + file list"""
        try:
            files = [f for f in os.listdir(DOWNLOAD_PATH) if f.lower().endswith('.pdf')]
            files.sort()  # Sort for consistent ordering
            return len(files), files
        except Exception as e:
            print(f"⚠️ Error counting files: {e}")
            return 0, []
    
    def show_initial_file_count(self):
        """Show initial file count before starting downloads"""
        print("\n" + "="*50)
        print("📊 INITIAL FILE COUNT")
        print("="*50)
        
        self.initial_file_count, self.initial_files = self.count_pdf_files()
        print(f"📄 PDF files in folder before download: {self.initial_file_count}")
        
        if self.initial_files:
            print("📋 Existing files:")
            for i, filename in enumerate(self.initial_files, 1):
                try:
                    file_path = os.path.join(DOWNLOAD_PATH, filename)
                    file_size = os.path.getsize(file_path)
                    size_mb = file_size / (1024 * 1024)
                    print(f"   {i:2d}. {filename} ({size_mb:.1f} MB)")
                except:
                    print(f"   {i:2d}. {filename}")
        else:
            print("📋 No existing PDF files found")
        
        print("="*50)
    
    def show_final_file_count(self):
        """Show final file count after downloads complete"""
        print("\n" + "="*50)
        print("📊 FINAL FILE COUNT & COMPARISON")
        print("="*50)
        
        self.final_file_count, self.final_files = self.count_pdf_files()
        
        print(f"📄 PDF files before download: {self.initial_file_count}")
        print(f"📄 PDF files after download:  {self.final_file_count}")
        
        new_files_count = self.final_file_count - self.initial_file_count
        if new_files_count > 0:
            print(f"✅ NEW FILES DOWNLOADED: {new_files_count}")
            
            # Find which files are new
            new_files = [f for f in self.final_files if f not in self.initial_files]
            if new_files:
                print("\n📥 Newly downloaded files:")
                for i, filename in enumerate(new_files, 1):
                    try:
                        file_path = os.path.join(DOWNLOAD_PATH, filename)
                        file_size = os.path.getsize(file_path)
                        size_mb = file_size / (1024 * 1024)
                        print(f"   {i:2d}. {filename} ({size_mb:.1f} MB)")
                    except:
                        print(f"   {i:2d}. {filename}")
        elif new_files_count == 0:
            print("⚠️  NO NEW FILES: Same number of files as before")
            print("💡 Files may have been re-downloaded with same names")
        else:
            print("❓ FEWER FILES: Some files may have been removed")
        
        print("\n📋 All current files:")
        for i, filename in enumerate(self.final_files, 1):
            try:
                file_path = os.path.join(DOWNLOAD_PATH, filename)
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)
                print(f"   {i:2d}. {filename} ({size_mb:.1f} MB)")
            except:
                print(f"   {i:2d}. {filename}")
        
        print("="*50)
        
        # Summary
        if new_files_count > 0:
            print(f"🎉 SUCCESS: {new_files_count} new files downloaded!")
        else:
            print("⚠️  Check: No new files detected (but downloads may have succeeded)")
    
    def get_random_user_agent(self):
        """Get random user agent"""
        return random.choice(USER_AGENTS)
    
    def human_delay(self, min_sec=1, max_sec=3):
        """Human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def get_month_number(self, month_text):
        """Extract month number from text (supports partial matches)"""
        if not month_text:
            return 0

        # Convert to lowercase and strip
        month_lower = month_text.lower().strip()

        # Try exact match first
        if month_lower in MONTH_ORDER:
            return MONTH_ORDER[month_lower]

        # Try to find month name within the text
        for month_name, month_num in MONTH_ORDER.items():
            if month_name in month_lower:
                return month_num

        return 0

    def detect_most_recent_year(self):
        """Detect the most recent year available in Weekly Reports section"""
        print("🔍 Auto-detecting most recent year...")

        try:
            # Look for year elements within Weekly Reports section
            # Pattern: onclick="HideShowYears('years_YYYY_9')"
            year_elements = self.driver.find_elements(
                By.XPATH,
                "//div[@id='div_9']//div[contains(@onclick, 'HideShowYears')]"
            )

            if not year_elements:
                print("❌ No year elements found")
                return None

            # Extract year values
            years = []
            for element in year_elements:
                try:
                    year_text = element.text.strip()
                    # Try to extract 4-digit year
                    year_match = re.search(r'\b(20\d{2})\b', year_text)
                    if year_match:
                        year = year_match.group(1)
                        years.append(year)
                        print(f"   📅 Found year: {year}")
                except:
                    continue

            if not years:
                print("❌ No valid years extracted")
                return None

            # Sort and get most recent (highest)
            years.sort(reverse=True)
            most_recent_year = years[0]

            print(f"✅ Most recent year detected: {most_recent_year}")
            return most_recent_year

        except Exception as e:
            print(f"❌ Error detecting year: {e}")
            return None

    def find_available_months(self, year):
        """Find all available months for a given year"""
        print(f"🔍 Scanning available months for year {year}...")

        try:
            # Make sure year is expanded
            years_div_id = f"years_{year}_9"
            if not self.is_expanded(years_div_id):
                print(f"⚠️ Year {year} not expanded, expanding now...")
                if not self.find_and_expand_year(year):
                    return []

            self.human_delay(2, 3)

            # Find month elements within the year's div
            month_elements = self.driver.find_elements(
                By.XPATH,
                f"//div[@id='years_{year}_9']//div[contains(@onclick, 'showHidePDF')]"
            )

            if not month_elements:
                print(f"⚠️ No month elements found for year {year}")
                return []

            # Extract month names and numbers
            months = []
            for element in month_elements:
                try:
                    if element.is_displayed():
                        month_text = element.text.strip()
                        month_num = self.get_month_number(month_text)

                        if month_num > 0:
                            months.append((month_text, month_num, element))
                            print(f"   📊 Found month: {month_text} (order: {month_num})")
                except:
                    continue

            # Sort by month number (descending - most recent first)
            months.sort(key=lambda x: x[1], reverse=True)

            print(f"✅ Found {len(months)} months for year {year}")
            return months

        except Exception as e:
            print(f"❌ Error finding months: {e}")
            return []

    def detect_most_recent_month(self, year):
        """Detect most recent month with PDFs for a given year"""
        print(f"🔍 Auto-detecting most recent month for year {year}...")

        months = self.find_available_months(year)

        if not months:
            print(f"❌ No months found for year {year}")
            return None, None

        # Try each month starting from most recent
        for month_text, month_num, month_element in months:
            print(f"🔄 Checking month: {month_text}...")

            try:
                # Extract PDF div ID from onclick
                onclick = month_element.get_attribute('onclick') or ''
                match = re.search(r"showHidePDF\('([^']+)'\)", onclick)

                if not match:
                    print(f"   ⚠️ Could not extract PDF div ID")
                    continue

                pdf_div_id = match.group(1)

                # Expand the month if not already expanded
                if not self.is_month_expanded(pdf_div_id):
                    print(f"   🔄 Expanding month {month_text}...")
                    if not self.enhanced_click(month_element, f"month {month_text}"):
                        print(f"   ❌ Failed to expand month {month_text}")
                        continue

                    # Wait for expansion
                    self.human_delay(2, 3)

                # Check if month has PDF files
                if self.is_month_expanded(pdf_div_id):
                    pdf_div = self.driver.find_element(By.ID, pdf_div_id)
                    pdf_links = pdf_div.find_elements(
                        By.XPATH,
                        ".//a[contains(@href, 'get_pdf.aspx') or contains(@href, '.pdf')]"
                    )

                    if len(pdf_links) > 0:
                        print(f"✅ Month {month_text} has {len(pdf_links)} PDF files")
                        print(f"✅ Most recent month detected: {month_text}")
                        return month_text, pdf_div_id
                    else:
                        print(f"   ⚠️ Month {month_text} has no PDF files, trying previous month...")
                else:
                    print(f"   ⚠️ Month {month_text} did not expand properly")

            except Exception as e:
                print(f"   ❌ Error checking month {month_text}: {e}")
                continue

        print(f"❌ No months with PDF files found for year {year}")
        return None, None

    def setup_driver(self):
        """Setup Chrome driver for downloads"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available")
            return False
        
        chrome_options = Options()
        
        # Anti-detection
        user_agent = self.get_random_user_agent()
        chrome_options.add_argument(f"--user-agent={user_agent}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performance
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Download settings - NO POPUPS
        prefs = {
            "download.default_directory": os.path.abspath(DOWNLOAD_PATH),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        if HEADLESS_MODE:
            chrome_options.add_argument("--headless=new")
            print("🔇 Running in headless mode")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Stealth script
            stealth_script = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """
            self.driver.execute_script(stealth_script)
            
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT)
            self.actions = ActionChains(self.driver)
            
            # Setup requests session
            self.setup_session()
            
            print("✅ Chrome driver initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup driver: {e}")
            return False
    
    def setup_session(self):
        """Setup requests session with browser cookies"""
        try:
            # Will sync cookies after page loads
            self.session.headers.update({
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'application/pdf,application/octet-stream,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            print("✅ Requests session configured")
        except Exception as e:
            print(f"⚠️ Session setup warning: {e}")
    
    def sync_cookies(self):
        """Sync cookies between Selenium and requests"""
        try:
            selenium_cookies = self.driver.get_cookies()
            for cookie in selenium_cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            self.session.headers.update({
                'Referer': self.driver.current_url
            })
        except Exception as e:
            print(f"⚠️ Cookie sync warning: {e}")
    
    def enhanced_click(self, element, description="element"):
        """Enhanced clicking with multiple strategies"""
        print(f"🎯 Clicking {description}...")
        
        # Scroll to element first
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self.human_delay(1, 2)
        except:
            pass
        
        # Try multiple click strategies
        strategies = [
            ("JavaScript Click", lambda: self.driver.execute_script("arguments[0].click();", element)),
            ("Direct Click", lambda: element.click()),
            ("ActionChains Click", lambda: self.actions.move_to_element(element).click().perform()),
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                print(f"   🔄 Trying {strategy_name}")
                strategy_func()
                print(f"   ✅ {strategy_name} successful!")
                self.human_delay(1, 2)
                return True
            except Exception as e:
                print(f"   ❌ {strategy_name} failed: {str(e)[:50]}")
                continue
        
        print(f"❌ All click strategies failed for {description}")
        return False
    
    def open_website(self):
        """Open EGX website"""
        print(f"🌐 Opening {self.url}...")
        
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                print(f"   🔄 Attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}")
                self.driver.get(self.url)
                
                # Wait for page to load
                self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                
                # Sync cookies and delay
                self.sync_cookies()
                self.human_delay(3, 5)
                
                # Check if page loaded properly
                if len(self.driver.page_source) > 5000:
                    print("✅ Website loaded successfully")
                    return True
                    
            except Exception as e:
                print(f"   ❌ Attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    self.human_delay(5, 8)
        
        print("❌ Failed to open website")
        return False
    
    def find_weekly_reports_section(self):
        """Find and locate Weekly Reports section"""
        print("🔍 Looking for Weekly Reports section...")
        
        # Multiple strategies to find Weekly Reports
        strategies = [
            ("Direct ID (div_9)", lambda: self.driver.find_elements(By.ID, "div_9")),
            ("Text search (Weekly Reports)", lambda: self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Weekly Reports')]")),
            ("Text search (Weekly)", lambda: self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Weekly')]")),
            ("Onclick elements", lambda: self.driver.find_elements(By.XPATH, "//*[@onclick and contains(@onclick, 'HideShow')]")),
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                print(f"   🔄 Trying {strategy_name}")
                elements = strategy_func()
                
                if elements:
                    print(f"   ✅ Found {len(elements)} elements")
                    for element in elements[:3]:
                        try:
                            if element.is_displayed():
                                print("   ✅ Weekly Reports section found")
                                return True
                        except:
                            continue
            except Exception as e:
                print(f"   ❌ {strategy_name} failed: {e}")
        
        print("❌ Could not find Weekly Reports section")
        return False
    
    def find_and_expand_year(self, target_year):
        """Find and expand target year"""
        print(f"📅 Looking for year {target_year}...")
        
        # Multiple selectors for year
        year_selectors = [
            f"//div[@id='div_9']//div[@onclick=\"HideShowYears('years_{target_year}_9')\"]",
            f"//div[@id='div_9']//div[text()='{target_year}' and @onclick]",
            f"//*[@onclick and contains(@onclick, 'HideShowYears') and text()='{target_year}']",
        ]
        
        year_element = None
        for selector in year_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.text.strip() == target_year:
                        year_element = element
                        break
                if year_element:
                    break
            except:
                continue
        
        if not year_element:
            print(f"❌ Year {target_year} not found")
            return False
        
        # Check if already expanded
        years_div_id = f"years_{target_year}_9"
        if self.is_expanded(years_div_id):
            print(f"✅ Year {target_year} already expanded")
            return True
        
        # Click to expand
        print(f"🔄 Expanding year {target_year}...")
        if self.enhanced_click(year_element, f"year {target_year}"):
            # Wait for expansion
            for i in range(10):
                time.sleep(1)
                if self.is_expanded(years_div_id):
                    print(f"✅ Year {target_year} expanded successfully")
                    return True
            
            print(f"⚠️ Year {target_year} clicked but may not be expanded")
            return True  # Assume success
        
        return False
    
    def find_and_expand_month(self, target_month):
        """Find and expand target month"""
        print(f"📊 Looking for month {target_month}...")
        
        self.human_delay(2, 4)
        
        # Multiple selectors for month
        month_selectors = [
            f"//div[contains(@onclick, 'showHidePDF') and contains(text(), '{target_month}')]",
            f"//*[contains(@onclick, 'showHidePDF') and contains(text(), '{target_month}')]",
        ]
        
        month_element = None
        pdf_div_id = None
        
        for selector in month_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and target_month.lower() in element.text.lower():
                        onclick = element.get_attribute('onclick') or ''
                        if 'showHidePDF' in onclick:
                            month_element = element
                            # Extract PDF div ID
                            match = re.search(r"showHidePDF\('([^']+)'\)", onclick)
                            if match:
                                pdf_div_id = match.group(1)
                                break
                if month_element:
                    break
            except:
                continue
        
        if not month_element or not pdf_div_id:
            print(f"❌ Month {target_month} not found")
            return False, None
        
        # Check if already expanded
        if self.is_month_expanded(pdf_div_id):
            print(f"✅ Month {target_month} already expanded")
            return True, pdf_div_id
        
        # Click to expand
        print(f"🔄 Expanding month {target_month}...")
        if self.enhanced_click(month_element, f"month {target_month}"):
            # Wait for expansion
            for i in range(8):
                time.sleep(1.5)
                if self.is_month_expanded(pdf_div_id):
                    print(f"✅ Month {target_month} expanded successfully")
                    return True, pdf_div_id
            
            print(f"⚠️ Month {target_month} clicked but may not be expanded")
            return True, pdf_div_id  # Assume success
        
        return False, None
    
    def is_expanded(self, div_id):
        """Check if div is expanded"""
        try:
            elements = self.driver.find_elements(By.ID, div_id)
            if elements:
                div = elements[0]
                style = div.get_attribute('style') or ''
                return div.is_displayed() and 'display:none' not in style
            return False
        except:
            return False
    
    def is_month_expanded(self, pdf_div_id):
        """Check if month is expanded and has PDF links"""
        try:
            pdf_divs = self.driver.find_elements(By.ID, pdf_div_id)
            if not pdf_divs:
                return False
            
            pdf_div = pdf_divs[0]
            if not pdf_div.is_displayed():
                return False
            
            # Check for PDF links
            pdf_links = pdf_div.find_elements(By.XPATH, ".//a[contains(@href, 'get_pdf.aspx') or contains(@href, '.pdf')]")
            return len(pdf_links) > 0
        except:
            return False
    
    def download_files_from_month(self, pdf_div_id):
        """Download all PDF files from the expanded month"""
        print(f"📥 Looking for PDF files to download...")
        
        try:
            pdf_div = self.driver.find_element(By.ID, pdf_div_id)
        except:
            print("❌ Could not find PDF container")
            return 0
        
        # Find all PDF links
        pdf_links = pdf_div.find_elements(By.XPATH, ".//a[contains(@href, 'get_pdf.aspx') or contains(@href, '.pdf')]")
        
        if not pdf_links:
            print("❌ No PDF links found")
            return 0
        
        print(f"✅ Found {len(pdf_links)} PDF files to download")
        
        # Download each PDF
        downloaded = 0
        for i, pdf_link in enumerate(pdf_links, 1):
            try:
                link_text = pdf_link.text.strip()
                href = pdf_link.get_attribute('href')
                
                print(f"\n📄 [{i}/{len(pdf_links)}] Downloading: {link_text[:50]}...")
                
                if self.download_single_file(pdf_link, href, i):
                    downloaded += 1
                    self.downloaded_count += 1
                    print(f"   ✅ Downloaded successfully!")
                else:
                    print(f"   ❌ Download failed")
                    self.failed_count += 1
                
                # Delay between downloads
                if i < len(pdf_links):
                    delay = random.uniform(DOWNLOAD_DELAY_MIN, DOWNLOAD_DELAY_MAX)
                    print(f"   ⏳ Waiting {delay:.1f}s...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.failed_count += 1
                continue
        
        print(f"\n📊 Downloaded {downloaded}/{len(pdf_links)} files")
        return downloaded
    
    def download_single_file(self, pdf_link, href, file_num):
        """Download a single PDF file - prioritize browser downloads for original names"""
        if not href:
            return False
        
        # Construct absolute URL
        if href.startswith('../'):
            base_url = self.driver.current_url
            parsed_base = urlparse(base_url)
            parent_path = '/'.join(parsed_base.path.split('/')[:-1])
            clean_relative = href.replace('../', '')
            absolute_url = f"{parsed_base.scheme}://{parsed_base.netloc}{parent_path}/{clean_relative}"
        else:
            absolute_url = urljoin(self.driver.current_url, href)
        
        print(f"     🔗 URL: {absolute_url}")
        
        # Prioritize new tab method to preserve original filenames
        if self.download_with_new_tab(pdf_link, absolute_url, file_num):
            return True
        
        # Fallback: try direct download
        return self.download_direct(absolute_url, file_num)
    
    def download_direct(self, url, file_num):
        """Try direct download with requests - preserve original filename"""
        try:
            # Update session cookies
            self.sync_cookies()
            
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                return False  # It's a redirect page
            
            # Try to get original filename from Content-Disposition header
            filename = None
            if 'content-disposition' in response.headers:
                import re
                cd = response.headers['content-disposition']
                # Try different patterns for filename extraction
                patterns = [
                    r'filename\*=UTF-8\'\'(.+)',
                    r'filename="(.+)"',
                    r'filename=(.+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, cd, re.IGNORECASE)
                    if match:
                        filename = match.group(1).strip('"\'')
                        break
            
            # If no filename from headers, try to extract from URL path
            if not filename:
                from urllib.parse import unquote, urlparse
                parsed_url = urlparse(url)
                path_parts = parsed_url.path.split('/')
                
                # Look for a meaningful filename in the URL path
                for part in reversed(path_parts):
                    if part and ('.' in part or len(part) > 5):
                        filename = unquote(part)
                        break
            
            # If still no filename, check query parameters for filename hints
            if not filename:
                from urllib.parse import parse_qs
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                
                # Look for filename in common parameter names
                filename_params = ['filename', 'file', 'name', 'document', 'doc']
                for param in filename_params:
                    if param in query_params and query_params[param]:
                        filename = query_params[param][0]
                        break
            
            # Last resort - but still try to make it meaningful
            if not filename:
                # Use timestamp to make it unique without losing info
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"egx_document_{timestamp}.pdf"
                print(f"     ⚠️ Could not determine original filename, using: {filename}")
            else:
                print(f"     ✅ Using original filename: {filename}")
            
            filepath = os.path.join(DOWNLOAD_PATH, filename)
            
            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Check file size
            file_size = os.path.getsize(filepath)
            if file_size > 1000:  # At least 1KB
                print(f"     ✅ Direct download: {filename} ({file_size:,} bytes)")
                return True
            else:
                os.remove(filepath)
                return False
                
        except Exception as e:
            print(f"     ⚠️ Direct download failed: {e}")
            return False
    
    def download_with_new_tab(self, pdf_link, url, file_num):
        """Download using new tab method"""
        try:
            print(f"     🔄 Trying new tab method...")
            
            original_window = self.driver.current_window_handle
            initial_windows = set(self.driver.window_handles)
            
            # Open new tab
            script = f"window.open('{url}', '_blank');"
            self.driver.execute_script(script)
            
            # Wait for new tab
            new_tab_opened = False
            for i in range(5):
                time.sleep(1)
                current_windows = set(self.driver.window_handles)
                new_windows = current_windows - initial_windows
                if new_windows:
                    new_tab_opened = True
                    break
            
            if new_tab_opened:
                new_window = list(new_windows)[0]
                self.driver.switch_to.window(new_window)
                
                # Wait longer for download to initiate
                print(f"     ⏳ Waiting for download to start...")
                time.sleep(5)  # Increased wait time
                
                # Close new tab and return to original
                self.driver.close()
                self.driver.switch_to.window(original_window)
                
                print(f"     ✅ New tab method completed")
                return True
            else:
                print(f"     ❌ No new tab opened")
                return False
                
        except Exception as e:
            print(f"     ❌ New tab method failed: {e}")
            # Ensure we're back on original window
            try:
                self.driver.switch_to.window(original_window)
            except:
                pass
            return False
    
    def run(self):
        """Main execution function"""
        print("🚀 Starting EGX file download...")
        
        # Show initial file count BEFORE starting
        self.show_initial_file_count()
        
        try:
            # Setup
            if not self.setup_driver():
                return False
            
            # Open website
            if not self.open_website():
                return False
            
            # Find weekly reports
            if not self.find_weekly_reports_section():
                return False

            # Determine year and month to download
            target_year = None
            target_month = None
            pdf_div_id = None

            # Auto-detect or use manual configuration
            if AUTO_DETECT and TARGET_YEAR is None:
                # Auto-detect year
                target_year = self.detect_most_recent_year()
                if not target_year:
                    print("❌ Failed to auto-detect year")
                    return False
            else:
                # Use manual configuration
                target_year = TARGET_YEAR
                print(f"📅 Using manual year: {target_year}")

            # Expand target year
            if not self.find_and_expand_year(target_year):
                return False

            # Determine month
            if AUTO_DETECT and TARGET_MONTH is None:
                # Auto-detect month (with fallback to previous months)
                target_month, pdf_div_id = self.detect_most_recent_month(target_year)

                if not target_month or not pdf_div_id:
                    print("❌ Failed to auto-detect month with PDFs")
                    return False
            else:
                # Use manual configuration
                target_month = TARGET_MONTH
                print(f"📅 Using manual month: {target_month}")

                # Expand target month
                success, pdf_div_id = self.find_and_expand_month(target_month)
                if not success:
                    return False

            # Print final target
            print(f"\n🎯 Final target: {target_month} {target_year}")
            print(f"📦 PDF container ID: {pdf_div_id}")
            
            # Download files
            downloaded = self.download_files_from_month(pdf_div_id)
            
            # Wait for downloads to complete - Extended to 60 seconds
            pdf_div = self.driver.find_element(By.ID, pdf_div_id)
            pdf_links = pdf_div.find_elements(By.XPATH, ".//a[contains(@href, 'get_pdf.aspx') or contains(@href, '.pdf')]")
            
            if len(pdf_links) > 0:
                print(f"\n⏰ Found {len(pdf_links)} PDF links - Waiting {BROWSER_CLOSE_WAIT} seconds for downloads to complete...")
                print("🔄 Keeping browser open to allow downloads to finish...")
                
                for i in range(BROWSER_CLOSE_WAIT, 0, -1):
                    minutes = i // 60
                    seconds = i % 60
                    if minutes > 0:
                        time_str = f"{minutes:02d}:{seconds:02d}"
                    else:
                        time_str = f"{seconds} seconds"
                    print(f"⏳ Waiting {time_str} for downloads to complete...", end='\r')
                    time.sleep(1)
                print(f"\n✅ {BROWSER_CLOSE_WAIT}-second wait completed!")
            else:
                print("⚠️ No PDF links found, no wait needed")
            
            # After browser closes, check for new files and mark them as downloaded
            print("\n🔍 Scanning folder for downloaded files...")
            current_file_count, current_files = self.count_pdf_files()
            
            # Any files that exist now but weren't there initially are new downloads
            new_downloaded_files = [f for f in current_files if f not in self.initial_files]
            
            if new_downloaded_files:
                print(f"✅ Detected {len(new_downloaded_files)} newly downloaded files:")
                for i, filename in enumerate(new_downloaded_files, 1):
                    try:
                        file_path = os.path.join(DOWNLOAD_PATH, filename)
                        file_size = os.path.getsize(file_path)
                        size_mb = file_size / (1024 * 1024)
                        print(f"   {i}. {filename} ({size_mb:.1f} MB)")
                        self.downloaded_count += 1  # Count as successful download
                    except:
                        print(f"   {i}. {filename}")
                        self.downloaded_count += 1
                
                print(f"🎉 Total successful downloads: {len(new_downloaded_files)}")
            else:
                print("⚠️ No new files detected in download folder")
            
            # Show final file count after downloads
            self.show_final_file_count()
            
            print(f"\n📈 Download Summary:")
            print(f"   ✅ Successfully downloaded: {self.downloaded_count}")
            print(f"   ❌ Failed downloads: {self.failed_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            return False
        
        finally:
            # Clean up browser
            if self.driver:
                try:
                    print("🧹 Closing browser...")
                    self.driver.quit()
                    print("✅ Browser closed successfully")
                except Exception as e:
                    print(f"⚠️ Error closing browser: {e}")


def main():
    """Main function to run the downloader"""
    downloader = SimpleEGXDownloader()
    
    try:
        success = downloader.run()
        
        if success:
            print("\n🎉 EGX Download completed successfully!")
        else:
            print("\n⚠️ EGX Download completed with errors")
            
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("👋 Goodbye!")


if __name__ == "__main__":
    main()