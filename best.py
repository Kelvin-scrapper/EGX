import pandas as pd
import pdfplumber
import re
from typing import List, Dict, Tuple, Optional
import numpy as np
import os
from datetime import datetime
import glob

# CSV structure - First column is period, followed by all EGX columns
HEADER_1 = [
    "",  # Period column
    "EGXEDW.EGYPTIANS.TOTAL.BUY.W",
    "EGXEDW.EGYPTIANS.BANKS.BUY.W", 
    "EGXEDW.EGYPTIANS.COMPANIES.BUY.W",
    "EGXEDW.EGYPTIANS.FUNDS.BUY.W",
    "EGXEDW.EGYPTIANS.OTHERS.BUY.W",
    "EGXEDW.EGYPTIANS.PORFTOLIO.BUY.W",
    "EGXEDW.EGYPTIANS.TOTAL.SELL.W",
    "EGXEDW.EGYPTIANS.BANKS.SELL.W",
    "EGXEDW.EGYPTIANS.COMPANIES.SELL.W",
    "EGXEDW.EGYPTIANS.FUNDS.SELL.W",
    "EGXEDW.EGYPTIANS.OTHERS.SELL.W",
    "EGXEDW.EGYPTIANS.PORFTOLIO.SELL.W",
    "EGXEDW.EGYPTIANS.TOTAL.NETBUY.W",
    "EGXEDW.EGYPTIANS.BANKS.NETBUY.W",
    "EGXEDW.EGYPTIANS.COMPANIES.NETBUY.W",
    "EGXEDW.EGYPTIANS.FUNDS.NETBUY.W",
    "EGXEDW.EGYPTIANS.OTHERS.NETBUY.W",
    "EGXEDW.EGYPTIANS.PORFTOLIO.NETBUY.W",
    "EGXEDW.ARABS.TOTAL.BUY.W",
    "EGXEDW.ARABS.BANKS.BUY.W",
    "EGXEDW.ARABS.COMPANIES.BUY.W",
    "EGXEDW.ARABS.FUNDS.BUY.W",
    "EGXEDW.ARABS.OTHERS.BUY.W",
    "EGXEDW.ARABS.PORFTOLIO.BUY.W",
    "EGXEDW.ARABS.TOTAL.SELL.W",
    "EGXEDW.ARABS.BANKS.SELL.W",
    "EGXEDW.ARABS.COMPANIES.SELL.W",
    "EGXEDW.ARABS.FUNDS.SELL.W",
    "EGXEDW.ARABS.OTHERS.SELL.W",
    "EGXEDW.ARABS.PORFTOLIO.SELL.W",
    "EGXEDW.ARABS.TOTAL.NETBUY.W",
    "EGXEDW.ARABS.BANKS.NETBUY.W",
    "EGXEDW.ARABS.COMPANIES.NETBUY.W",
    "EGXEDW.ARABS.FUNDS.NETBUY.W",
    "EGXEDW.ARABS.OTHERS.NETBUY.W",
    "EGXEDW.ARABS.PORFTOLIO.NETBUY.W",
    "EGXEDW.FOREIGNERS.TOTAL.BUY.W",
    "EGXEDW.FOREIGNERS.BANKS.BUY.W",
    "EGXEDW.FOREIGNERS.COMPANIES.BUY.W",
    "EGXEDW.FOREIGNERS.FUNDS.BUY.W",
    "EGXEDW.FOREIGNERS.OTHERS.BUY.W",
    "EGXEDW.FOREIGNERS.PORFTOLIO.BUY.W",
    "EGXEDW.FOREIGNERS.TOTAL.SELL.W",
    "EGXEDW.FOREIGNERS.BANKS.SELL.W",
    "EGXEDW.FOREIGNERS.COMPANIES.SELL.W",
    "EGXEDW.FOREIGNERS.FUNDS.SELL.W",
    "EGXEDW.FOREIGNERS.OTHERS.SELL.W",
    "EGXEDW.FOREIGNERS.PORFTOLIO.SELL.W",
    "EGXEDW.FOREIGNERS.TOTAL.NETBUY.W",
    "EGXEDW.FOREIGNERS.BANKS.NETBUY.W",
    "EGXEDW.FOREIGNERS.COMPANIES.NETBUY.W",
    "EGXEDW.FOREIGNERS.FUNDS.NETBUY.W",
    "EGXEDW.FOREIGNERS.OTHERS.NETBUY.W",
    "EGXEDW.FOREIGNERS.PORFTOLIO.NETBUY.W",
    "EGXEDW.RETAIL.EGYPTIANS.BUY.W",
    "EGXEDW.RETAIL.EGYPTIANS.SELL.W",
    "EGXEDW.RETAIL.EGYPTIANS.NETBUY.W",
    "EGXEDW.RETAIL.ARABS.BUY.W",
    "EGXEDW.RETAIL.ARABS.SELL.W",
    "EGXEDW.RETAIL.ARABS.NETBUY.W",
    "EGXEDW.RETAIL.FOREIGNERS.BUY.W",
    "EGXEDW.RETAIL.FOREIGNERS.SELL.W",
    "EGXEDW.RETAIL.FOREIGNERS.NETBUY.W",
    "EGXEDW.RETAIL.TOTAL.BUY.W",
    "EGXEDW.RETAIL.TOTAL.SELL.W",
    "EGXEDW.RETAIL.TOTAL.NETBUY.W",
    "EGXEDW.EGYPTIANS.NA.BUY.W",
    "EGXEDW.EGYPTIANS.NA.SELL.W",
    "EGXEDW.EGYPTIANS.NA.NETBUY.W",
    "EGXEDW.ARABS.NA.BUY.W",
    "EGXEDW.ARABS.NA.SELL.W",
    "EGXEDW.ARABS.NA.NETBUY.W",
    "EGXEDW.FOREIGNERS.NA.BUY.W",
    "EGXEDW.FOREIGNERS.NA.SELL.W",
    "EGXEDW.FOREIGNERS.NA.NETBUY.W"
]

HEADER_2 = [
    "",
    "Egyptians, Institutions Total, Buy",
    "Egyptians, Banks, Buy",
    "Egyptians, Companies, Buy",
    "Egyptians, Funds, Buy",
    "Egyptians, Others, Buy",
    "Egyptians, Portfolio, Buy",
    "Egyptians, Institutions Total, Sell",
    "Egyptians, Banks, Sell",
    "Egyptians, Companies, Sell",
    "Egyptians, Funds, Sell",
    "Egyptians, Others, Sell",
    "Egyptians, Portfolio, Sell",
    "Egyptians, Institutions Total, Net Buy",
    "Egyptians, Banks, Net Buy",
    "Egyptians, Companies, Net Buy",
    "Egyptians, Funds, Net Buy",
    "Egyptians, Others, Net Buy",
    "Egyptians, Portfolio, Net Buy",
    "Arabs, Institutions Total, Buy",
    "Arabs, Banks, Buy",
    "Arabs, Companies, Buy",
    "Arabs, Funds, Buy",
    "Arabs, Others, Buy",
    "Arabs, Portfolio, Buy",
    "Arabs, Institutions Total, Sell",
    "Arabs, Banks, Sell",
    "Arabs, Companies, Sell",
    "Arabs, Funds, Sell",
    "Arabs, Others, Sell",
    "Arabs, Portfolio, Sell",
    "Arabs, Institutions Total, Net Buy",
    "Arabs, Banks, Net Buy",
    "Arabs, Companies, Net Buy",
    "Arabs, Funds, Net Buy",
    "Arabs, Others, Net Buy",
    "Arabs, Portfolio, Net Buy",
    "Foreigners, Institutions Total, Buy",
    "Foreigners, Banks, Buy",
    "Foreigners, Companies, Buy",
    "Foreigners, Funds, Buy",
    "Foreigners, Others, Buy",
    "Foreigners, Portfolio, Buy",
    "Foreigners, Institutions Total, Sell",
    "Foreigners, Banks, Sell",
    "Foreigners, Companies, Sell",
    "Foreigners, Funds, Sell",
    "Foreigners, Others, Sell",
    "Foreigners, Portfolio, Sell",
    "Foreigners, Institutions Total, Net Buy",
    "Foreigners, Banks, Net Buy",
    "Foreigners, Companies, Net Buy",
    "Foreigners, Funds, Net Buy",
    "Foreigners, Others, Net Buy",
    "Foreigners, Portfolio, Net Buy",
    "Retail, Egyptians, Buy",
    "Retail, Egyptians, Sell",
    "Retail, Egyptians, Net Buy",
    "Retail, Arabs, Buy",
    "Retail, Arabs, Sell",
    "Retail, Arabs, Net Buy",
    "Retail, Foreigners, Buy",
    "Retail, Foreigners, Sell",
    "Retail, Foreigners, Net Buy",
    "Retail, Total Nationalities, Buy",
    "Retail, Total Nationalities, Sell",
    "Retail, Total Nationalities, Net Buy",
    "Egyptians, N\\A, Buy",
    "Egyptians, N\\A, Sell",
    "Egyptians, N\\A, Netbuy",
    "Arabs, N\\A, Buy",
    "Arabs, N\\A, Sell",
    "Arabs, N\\A, Netbuy",
    "Foreigners, N\\A, Buy",
    "Foreigners, N\\A, Sell",
    "Foreigners, N\\A, Netbuy"
]

def get_local_downloads_folder() -> str:
    """Get Downloads folder in same directory as script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    downloads_path = os.path.join(script_dir, "Downloads")
    return downloads_path

def find_pdf_files_in_downloads() -> List[str]:
    """Find all PDF files in Downloads folder"""
    downloads_path = get_local_downloads_folder()
    
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
        print(f"Created Downloads folder: {downloads_path}")
    
    pdf_files = glob.glob(os.path.join(downloads_path, "*.pdf"))
    return sorted(pdf_files)

def create_csv_with_headers(csv_path: str) -> bool:
    """Create CSV with correct two-header structure"""
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            # Write header 1
            f.write(','.join(HEADER_1) + '\n')
            
            # Write header 2 (quoted for items with commas)
            header_2_quoted = []
            for item in HEADER_2:
                if item == "":
                    header_2_quoted.append("")
                else:
                    header_2_quoted.append(f'"{item}"')
            f.write(','.join(header_2_quoted) + '\n')
        
        print(f"[OK] Created CSV: {csv_path}")
        return True
        
    except Exception as e:
        print(f"Error creating CSV: {e}")
        return False

def extract_period_from_text(page_text: str) -> Optional[str]:
    """Extract period and convert to YYYY-W format"""
    patterns = [
        r'Period:\s*(\d{2}/\d{2}/\d{4})-(\d{2}/\d{2}/\d{4})',
        r'(\d{2}/\d{2}/\d{4})-(\d{2}/\d{2}/\d{4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, page_text)
        if match:
            start_date_str = match.group(1)
            try:
                start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
                year, week, _ = start_date.isocalendar()
                return f"{year}-{week}"
            except ValueError:
                continue
    return None

def clean_number(value_str):
    """Clean and convert extracted number strings to float."""
    if not value_str or str(value_str).strip() == "":
        return 0.0
    
    # Remove commas and spaces
    cleaned = re.sub(r'[,\s]', '', str(value_str).strip())
    
    # Handle parentheses (negative numbers)
    if cleaned.startswith('(') and cleaned.endswith(')'):
        cleaned = '-' + cleaned[1:-1]
    
    # Handle "NA" values
    if cleaned.upper() == 'NA':
        return 0.0
    
    # Convert to float
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def extract_retail_data_from_text(page_text: str) -> Dict[str, float]:
    """Extract retail trading data from the Trading by Categories section."""
    
    print("[RETAIL] Extracting retail data...")
    
    # Find the "Trading by Categories of Investors" section
    section_pattern = r'Trading by Categories of Investors in EGP Million.*?(?=(?:Bonds|OTC|Listed Stocks incl\.|$))'
    section_match = re.search(section_pattern, page_text, re.DOTALL | re.IGNORECASE)
    
    if not section_match:
        print("[ERROR] Trading by Categories section not found")
        return {}
    
    section_text = section_match.group(0)
    
    # Find "Listed Stocks including Deals" table within the section
    listed_stocks_pattern = r'Listed Stocks including Deals.*?(?=(?:Bonds|OTC|Listed Stocks incl\.|$))'
    listed_stocks_match = re.search(listed_stocks_pattern, section_text, re.DOTALL | re.IGNORECASE)
    
    if not listed_stocks_match:
        print("[ERROR] Listed Stocks including Deals section not found")
        return {}
    
    table_text = listed_stocks_match.group(0)
    print(f"[TABLE] Table text preview: {table_text[:300]}...")
    
    retail_data = {}
    
    # Look for the header pattern first to understand structure
    header_pattern = r'Nationalities\s+Buy\s+Sell\s+Buy \+ Sell\s+Net Buy\s+Buy\s+Sell\s+Buy \+ Sell\s+Net Buy'
    header_match = re.search(header_pattern, table_text, re.IGNORECASE)
    
    if header_match:
        print("[OK] Found correct table header with Institutions and Retail columns")
    else:
        print("[WARNING] Table header not found, trying alternative extraction")
    
    # Split the text into lines and process line by line for better accuracy
    lines = table_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check each nationality
        for nationality in ['EGYPTIANS', 'ARABS', 'FOREIGNERS', 'TOTAL']:
            nationality_lower = nationality.lower()
            line_lower = line.lower()
            
            # Look for lines that start with the nationality name
            if line_lower.startswith(nationality_lower) or (nationality == 'EGYPTIANS' and line_lower.startswith('egyptians')):
                print(f"[SEARCH] Processing line for {nationality}: {line}")
                
                # Extract all numbers from this line
                # Pattern to match numbers including negatives in parentheses
                number_pattern = r'([\d,.-]+(?:\.\d+)?|\([\d,.-]+(?:\.\d+)?\))'
                numbers = re.findall(number_pattern, line)
                
                if len(numbers) >= 8:
                    print(f"[DATA] Found {len(numbers)} numbers: {numbers}")
                    
                    # Convert to clean numbers
                    clean_numbers = [clean_number(num) for num in numbers]
                    
                    # Extract retail values (positions 4, 5, 7 = buy, sell, netbuy)
                    # Based on the table structure: [inst_buy, inst_sell, inst_buy+sell, inst_netbuy, retail_buy, retail_sell, retail_buy+sell, retail_netbuy]
                    if len(clean_numbers) >= 8:
                        retail_buy = clean_numbers[4]      # 5th position (0-indexed)
                        retail_sell = clean_numbers[5]     # 6th position 
                        retail_netbuy = clean_numbers[7]   # 8th position (Net Buy)
                        
                        retail_data[f"EGXEDW.RETAIL.{nationality}.BUY.W"] = retail_buy
                        retail_data[f"EGXEDW.RETAIL.{nationality}.SELL.W"] = retail_sell
                        retail_data[f"EGXEDW.RETAIL.{nationality}.NETBUY.W"] = retail_netbuy
                        
                        print(f"[OK] {nationality}: Buy={retail_buy}, Sell={retail_sell}, NetBuy={retail_netbuy}")
                    else:
                        print(f"[ERROR] Insufficient numbers found for {nationality}: {len(clean_numbers)}")
                else:
                    print(f"[ERROR] Not enough numbers in line for {nationality}: found {len(numbers)}")
    
    # Fill missing data with 0.0
    for nationality in ['EGYPTIANS', 'ARABS', 'FOREIGNERS', 'TOTAL']:
        for action in ['BUY', 'SELL', 'NETBUY']:
            key = f"EGXEDW.RETAIL.{nationality}.{action}.W"
            if key not in retail_data:
                retail_data[key] = 0.0
    
    return retail_data

def extract_retail_data_from_table(tables: List[List]) -> Dict[str, float]:
    """Extract retail data from table structure as fallback."""
    
    print("[RETAIL] Extracting retail data from tables...")
    retail_data = {}
    
    for table_idx, table in enumerate(tables):
        if not table or len(table) < 3:
            continue
        
        print(f"[TABLE] Analyzing table {table_idx + 1} with {len(table)} rows")
        
        # Look for the "Trading by Categories" table by checking headers
        header_found = False
        header_row_idx = -1
        
        for row_idx, row in enumerate(table[:5]):  # Check first 5 rows for headers
            if not row:
                continue
            
            row_text = ' '.join([str(cell) for cell in row if cell])
            if any(keyword in row_text.lower() for keyword in ['categories', 'nationalities', 'retail', 'institutions']):
                header_found = True
                header_row_idx = row_idx
                print(f"[OK] Found potential header at row {row_idx}: {row_text}")
                break
        
        if not header_found:
            continue
        
        print(f"[DATA] Processing table with header at row {header_row_idx}")
        
        # Look for nationality data rows
        for row_idx, row in enumerate(table):
            if not row or len(row) < 8:  # Need at least 8 columns
                continue
            
            first_cell = str(row[0]).strip().lower() if row[0] else ''
            
            nationality = None
            # FIX: Using exact match (==) to prevent misidentifying a "Total" row as an "Egyptians" row.
            if first_cell == 'egyptians':
                nationality = 'EGYPTIANS'
            elif first_cell == 'arabs':
                nationality = 'ARABS'
            elif first_cell == 'foreigners':
                nationality = 'FOREIGNERS'
            elif first_cell == 'total':
                nationality = 'TOTAL'
            
            if nationality:
                print(f"[SEARCH] Processing table row for {nationality}: {first_cell}")
                
                # Extract numbers from the row
                numbers = []
                for cell_idx, cell in enumerate(row[1:], 1):  # Skip first cell (nationality name)
                    if cell is None or str(cell).strip() == "":
                        numbers.append(None)  # Mark empty cells as None
                        continue

                    cell_str = str(cell).strip()

                    # Handle negative values in parentheses
                    if cell_str.startswith('(') and cell_str.endswith(')'):
                        cell_str = '-' + cell_str[1:-1]

                    try:
                        value = float(re.sub(r'[,\s]', '', cell_str))
                        numbers.append(value)
                    except:
                        numbers.append(None)  # Mark unparseable cells as None
                
                print(f"[DATA] Extracted {len(numbers)} values: {numbers[:8]}")
                
                # The table structure should be:
                # [inst_buy, inst_sell, inst_buy+sell, inst_netbuy, retail_buy, retail_sell, retail_buy+sell, retail_netbuy]
                if len(numbers) >= 8:
                    retail_buy = numbers[4]      # 5th column (0-indexed)
                    retail_sell = numbers[5]     # 6th column
                    retail_netbuy = numbers[7]   # 8th column (Net Buy)
                    
                    # Validate that these look like reasonable retail values
                    if retail_buy > 0 or retail_sell > 0 or retail_netbuy != 0:
                        retail_data[f"EGXEDW.RETAIL.{nationality}.BUY.W"] = retail_buy
                        retail_data[f"EGXEDW.RETAIL.{nationality}.SELL.W"] = retail_sell
                        retail_data[f"EGXEDW.RETAIL.{nationality}.NETBUY.W"] = retail_netbuy
                        
                        print(f"[OK] Table: {nationality}: Buy={retail_buy}, Sell={retail_sell}, NetBuy={retail_netbuy}")
                    else:
                        print(f"[WARNING] Suspicious values for {nationality}, might be wrong columns")
                else:
                    print(f"[ERROR] Insufficient columns for {nationality}: found {len(numbers)}")
        
        # If we found retail data in this table, we're done
        if retail_data:
            break
    
    # Fill missing data
    for nationality in ['EGYPTIANS', 'ARABS', 'FOREIGNERS', 'TOTAL']:
        for action in ['BUY', 'SELL', 'NETBUY']:
            key = f"EGXEDW.RETAIL.{nationality}.{action}.W"
            if key not in retail_data:
                retail_data[key] = 0.0
    
    extracted_count = sum(1 for v in retail_data.values() if v != 0.0)
    print(f"[DATA] Table extraction: {extracted_count}/12 retail data points")
    
    return retail_data

def extract_institutional_data_complete(pdf_path: str) -> Optional[Tuple[str, Dict[str, float]]]:
    """Extract complete institutional AND retail data from PDF"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            period_info = None
            institutional_data = {}
            retail_data = {}
            
            # Search all pages
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                page_text = page.extract_text()
                
                # Extract period
                if not period_info:
                    period_info = extract_period_from_text(page_text)
                    if period_info:
                        print(f"Found period: {period_info}")
                
                # Look for institutional trading table
                if "Institutional Trades in Listed Stocks" in page_text:
                    print(f"Found institutional data on page {page_num + 1}")
                    
                    # Extract the complete institutional table
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            data = parse_complete_institutional_table(table)
                            if data:
                                institutional_data = data
                                break
                    
                    # If table extraction failed, try text parsing
                    if not institutional_data:
                        institutional_data = parse_institutional_from_text(page_text)
                
                # Look for retail trading data
                if "Trading by Categories of Investors" in page_text:
                    print(f"Found retail data section on page {page_num + 1}")
                    
                    # FIX: Prioritize the more robust table extraction method.
                    tables = page.extract_tables()
                    if tables:
                        retail_data = extract_retail_data_from_table(tables)

                    # Use text extraction only as a fallback if table extraction fails completely.
                    if not retail_data or all(v == 0.0 for v in retail_data.values()):
                        print("[WARNING] Table extraction failed, using text-based fallback for retail data.")
                        retail_data = extract_retail_data_from_text(page_text)
                
                if period_info and institutional_data and retail_data:
                    break
            
            if not period_info:
                print("ERROR: No period found")
                return None
            
            if not institutional_data:
                institutional_data = {} # Initialize to avoid error
            
            # Merge institutional and retail data
            combined_data = institutional_data.copy()
            combined_data.update(retail_data)
            
            # Count extracted retail values
            retail_count = sum(1 for k, v in retail_data.items() if k.startswith('EGXEDW.RETAIL.') and v != 0.0)
            print(f"[DATA] Extracted {retail_count} retail data points")
            
            return period_info, combined_data
            
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

def parse_complete_institutional_table(table: List[List]) -> Optional[Dict[str, float]]:
    """Parse institutional table and return complete data mapping"""
    if not table or len(table) < 3:
        return None
    
    print(f"Parsing institutional table with {len(table)} rows")

    # Initialize empty data dictionary (no pre-filling with zeros)
    data = {}
    
    # Parse each row of the institutional table
    for row_idx, row in enumerate(table):
        if not row or not any(row):
            continue
        
        first_cell = str(row[0]).strip().lower() if row[0] else ''
        
        # Identify institution type
        institution = None
        if 'banks' in first_cell:
            institution = 'BANKS'
        elif 'companies' in first_cell:
            institution = 'COMPANIES'
        elif first_cell == 'funds':
            institution = 'FUNDS'
        elif first_cell.startswith('n/a'):
            institution = 'NA'
        elif 'others' in first_cell:
            institution = 'OTHERS'
        elif 'portfolio' in first_cell:
            institution = 'PORFTOLIO'
        elif 'total' in first_cell:
            institution = 'TOTAL'
        
        if not institution:
            continue
        
        print(f"Processing {institution}: {first_cell}")
        
        # Extract numbers from the row
        numbers = []
        for cell in row[1:]:
            if cell is None or str(cell).strip() == "":
                numbers.append(None)  # Mark empty cells as None
                continue

            cell_str = str(cell).strip()

            # Handle negative values in parentheses
            if cell_str.startswith('(') and cell_str.endswith(')'):
                cell_str = '-' + cell_str[1:-1]

            try:
                value = float(re.sub(r'[,\s]', '', cell_str))
                numbers.append(value)
            except:
                numbers.append(None)  # Mark unparseable cells as None
        
        print(f"  Extracted {len(numbers)} values: {numbers[:9]}")  # Show first 9
        
        # Map numbers to the correct columns
        # Expected order: EGY_BUY, EGY_SELL, EGY_NET, ARA_BUY, ARA_SELL, ARA_NET, FOR_BUY, FOR_SELL, FOR_NET
        if len(numbers) >= 9:
            nationalities = ['EGYPTIANS', 'ARABS', 'FOREIGNERS']
            actions = ['BUY', 'SELL', 'NETBUY']
            
            idx = 0
            for nat in nationalities:
                for action in actions:
                    if idx < len(numbers):
                        col_name = f"EGXEDW.{nat}.{institution}.{action}.W"
                        # Only add to dictionary if value is not None (empty cell)
                        if numbers[idx] is not None:
                            data[col_name] = numbers[idx]
                            if numbers[idx] != 0:
                                print(f"    {col_name} = {numbers[idx]}")
                        idx += 1
    
    # Count non-zero values
    non_zero = sum(1 for v in data.values() if v != 0)
    print(f"Mapped {non_zero} non-zero institutional values")
    
    return data if non_zero > 0 else None

def parse_institutional_from_text(page_text: str) -> Optional[Dict[str, float]]:
    """Parse institutional data from text as fallback"""
    lines = page_text.split('\n')
    data = {col: 0.0 for col in HEADER_1 if col.startswith('EGXEDW.') and not col.startswith('EGXEDW.RETAIL.')}
    
    in_section = False
    for line in lines:
        if "Institutional Trades in Listed Stocks" in line:
            in_section = True
            continue
        
        if not in_section:
            continue
        
        if "Listed Stocks Excluding Deals" in line:
            break
        
        line_lower = line.lower().strip()
        institution = None
        
        if re.match(r'^banks?\s+', line_lower):
            institution = 'BANKS'
        elif re.match(r'^companies\s+', line_lower):
            institution = 'COMPANIES'
        elif re.match(r'^funds\s+', line_lower):
            institution = 'FUNDS'
        elif re.match(r'^n/a\s+', line_lower):
            institution = 'NA'
        elif re.match(r'^others\s+', line_lower):
            institution = 'OTHERS'
        elif re.match(r'^portfolio\s+', line_lower):
            institution = 'PORFTOLIO'
        elif re.match(r'^total\s+', line_lower):
            institution = 'TOTAL'
        
        if institution:
            numbers = extract_numbers_from_line(line)
            if len(numbers) >= 9:
                nationalities = ['EGYPTIANS', 'ARABS', 'FOREIGNERS']
                actions = ['BUY', 'SELL', 'NETBUY']
                
                idx = 0
                for nat in nationalities:
                    for action in actions:
                        if idx < len(numbers):
                            col_name = f"EGXEDW.{nat}.{institution}.{action}.W"
                            if col_name in data:
                                data[col_name] = numbers[idx]
                            idx += 1
    
    return data if any(v != 0 for v in data.values()) else None

def extract_numbers_from_line(line: str) -> List[float]:
    """Extract numbers from text line"""
    pattern = r'-?\(?\d+(?:,\d{3})*(?:\.\d+)?\)?'
    matches = re.findall(pattern, line)
    
    numbers = []
    for match in matches:
        try:
            if match.startswith('(') and match.endswith(')'):
                number_str = '-' + match[1:-1]
            else:
                number_str = match
            
            number = float(re.sub(r'[,\s]', '', number_str))
            numbers.append(number)
        except:
            continue
    
    return numbers

def append_data_to_csv(csv_path: str, period: str, data: Dict[str, float]) -> bool:
    """Append new data row to CSV"""
    try:
        # Create the complete row
        row_data = [period]  # Start with period

        # Add all EGX columns in order
        for col in HEADER_1[1:]:  # Skip empty first column
            if col in data:
                # Column was extracted from PDF - write the value (even if 0.0)
                row_data.append(str(data[col]))
            else:
                # Column was not extracted - mark as NA
                row_data.append("NA")

        # Append to CSV file
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            f.write(','.join(row_data) + '\n')

        return True

    except Exception as e:
        print(f"Error appending to CSV: {e}")
        return False

def process_pdf_file(csv_path: str, pdf_path: str) -> bool:
    """Process single PDF file"""
    try:
        print(f"Processing: {os.path.basename(pdf_path)}")
        
        result = extract_institutional_data_complete(pdf_path)
        if not result:
            print("[ERROR] Failed to extract data")
            return False
        
        period, data = result
        
        # Check if period already exists
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if period in content:
                    print(f"[WARNING] Period {period} already exists. Skipping.")
                    return True
        
        # Append to CSV
        if append_data_to_csv(csv_path, period, data):
            non_zero_count = sum(1 for v in data.values() if v != 0)
            retail_count = sum(1 for k, v in data.items() if k.startswith('EGXEDW.RETAIL.') and v != 0)
            print(f"[OK] Added period {period} with {non_zero_count} total values ({retail_count} retail)")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False

def process_all_pdfs() -> bool:
    """Process all PDF files in Downloads folder"""
    csv_file = "EGX_Weekly_Data.csv"
    
    # Find PDF files
    pdf_files = find_pdf_files_in_downloads()
    if not pdf_files:
        print("No PDF files found in Downloads folder")
        return False
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Create CSV if it doesn't exist
    if not os.path.exists(csv_file):
        create_csv_with_headers(csv_file)
    
    # Process each PDF
    success_count = 0
    total_retail_extracted = 0
    
    for i, pdf_path in enumerate(pdf_files):
        print(f"\n--- {i+1}/{len(pdf_files)} ---")
        if process_pdf_file(csv_file, pdf_path):
            success_count += 1
    
    print(f"\n[FINAL] Final: {success_count}/{len(pdf_files)} files processed successfully")
    
    if success_count > 0:
        # Show CSV summary with retail data analysis
        try:
            df = pd.read_csv(csv_file, skiprows=[1])  # Skip description row
            print(f"CSV now has {len(df)} data rows")
            
            if not df.empty and '' in df.columns:
                periods = df[''].tolist()
                print(f"Periods: {periods}")
                
                # Analyze retail data coverage
                retail_cols = [col for col in df.columns if 'RETAIL' in col]
                if retail_cols:
                    print(f"\n[DATA] RETAIL DATA ANALYSIS:")
                    print(f"Total retail columns: {len(retail_cols)}")
                    
                    for col in retail_cols[:6]:  # Show first 6 retail columns
                        non_na_count = df[col].notna().sum()
                        non_zero_count = (df[col] != 'NA').sum() if 'NA' in df[col].values else df[col].notna().sum()
                        print(f"  {col}: {non_zero_count}/{len(df)} weeks have data")
                    
                    if len(retail_cols) > 6:
                        print(f"  ... and {len(retail_cols) - 6} more retail columns")
                
        except Exception as e:
            print(f"Error analyzing CSV: {e}")
    
    return success_count > 0

# Main execution
if __name__ == "__main__":
    print("EGX INSTITUTIONAL + RETAIL DATA PROCESSOR")
    print("=" * 50)
    print(f"Downloads folder: {get_local_downloads_folder()}")
    print("[NEW] Now extracting retail data (12 additional columns)")
    print("=" * 50)
    
    success = process_all_pdfs()
    
    if success:
        print("\n[SUCCESS] SUCCESS: Data extracted and saved to EGX_Weekly_Data.csv")
        print("[OK] All 75 columns including retail data should now be captured!")
    else:
        print("\n[ERROR] FAILED: Could not process files")