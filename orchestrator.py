#!/usr/bin/env python3
"""
EGX Data Pipeline Orchestrator

This orchestrator coordinates the EGX data extraction pipeline:
1. Download PDF files from EGX website (scrape1.py)
2. Process PDFs to extract trading data into CSV (best.py)
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import argparse

class EGXPipelineOrchestrator:
    def __init__(self):
        """Initialize the orchestrator"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.scraper_script = os.path.join(self.script_dir, "scrape1.py")
        self.processor_script = os.path.join(self.script_dir, "best.py")
        self.downloads_dir = os.path.join(self.script_dir, "downloads")
        self.output_dir = os.path.join(self.script_dir, "output")

        print("EGX Data Pipeline Orchestrator")
        print(f"Working directory: {self.script_dir}")
        print(f"Downloads directory: {self.downloads_dir}")
        print(f"Output directory: {self.output_dir}")
    
    def check_dependencies(self):
        """Check if required scripts exist"""
        missing_scripts = []
        
        if not os.path.exists(self.scraper_script):
            missing_scripts.append("scrape1.py")
        
        if not os.path.exists(self.processor_script):
            missing_scripts.append("best.py")
        
        if missing_scripts:
            print(f"Missing required scripts: {', '.join(missing_scripts)}")
            return False
        
        print("All required scripts found")
        return True
    
    def run_script(self, script_path, description):
        """Run a Python script and return success status"""
        print(f"\n{'='*60}")
        print(f"Starting: {description}")
        print(f"Script: {os.path.basename(script_path)}")
        print(f"{'='*60}")
        
        try:
            # Run the script
            result = subprocess.run([sys.executable, script_path], 
                                  cwd=self.script_dir,
                                  capture_output=False,
                                  text=True)
            
            if result.returncode == 0:
                print(f"{description} completed successfully")
                return True
            else:
                print(f"{description} failed with return code: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"Error running {description}: {e}")
            return False
    
    def check_downloads(self):
        """Check if PDF files were downloaded"""
        if not os.path.exists(self.downloads_dir):
            print("Downloads directory not found")
            return False
        
        pdf_files = [f for f in os.listdir(self.downloads_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("No PDF files found in Downloads directory")
            return False
        
        print(f"Found {len(pdf_files)} PDF files for processing")
        return True
    
    def run_pipeline(self, skip_download=False, skip_processing=False):
        """Run the complete EGX data pipeline"""
        print(f"\nStarting EGX Data Pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        success = True
        
        # Step 1: Download PDFs (if not skipped)
        if not skip_download:
            print("\nSTEP 1: Download PDF files from EGX website")
            if not self.run_script(self.scraper_script, "PDF Download"):
                print("Download step failed")
                success = False
            else:
                # Wait a moment for files to be written
                time.sleep(2)
        else:
            print("\nSTEP 1: Skipping PDF download (as requested)")
        
        # Check if we have files to process
        if success or skip_download:
            if not self.check_downloads():
                if not skip_download:
                    print("No files downloaded, cannot proceed to processing")
                    success = False
                else:
                    print("No existing files found for processing")
                    success = False
        
        # Step 2: Process PDFs (if not skipped and we have files)
        if (success or skip_download) and not skip_processing:
            print("\nSTEP 2: Process PDF files and extract data")
            if not self.run_script(self.processor_script, "PDF Processing"):
                print("Processing step failed")
                success = False
        elif skip_processing:
            print("\nSTEP 2: Skipping PDF processing (as requested)")
        
        # Final summary
        print(f"\n{'='*60}")
        if success:
            print("EGX Data Pipeline completed successfully!")
            
            # Check for output CSV
            csv_file = os.path.join(self.output_dir, "EGX_Weekly_Data.csv")
            if os.path.exists(csv_file):
                print(f"Output CSV: {csv_file}")
                try:
                    # Get file size and modification time
                    file_size = os.path.getsize(csv_file)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(csv_file))
                    print(f"File size: {file_size:,} bytes")
                    print(f"Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    pass
        else:
            print("EGX Data Pipeline completed with errors")
        
        print(f"Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        return success
    
    def show_status(self):
        """Show current pipeline status"""
        print(f"\nEGX Pipeline Status")
        print(f"{'='*40}")
        
        # Check scripts
        print("Scripts:")
        print(f"   scrape1.py: {'Found' if os.path.exists(self.scraper_script) else 'Missing'}")
        print(f"   best.py: {'Found' if os.path.exists(self.processor_script) else 'Missing'}")
        
        # Check downloads folder
        print("\nDownloads:")
        if os.path.exists(self.downloads_dir):
            pdf_files = [f for f in os.listdir(self.downloads_dir) if f.endswith('.pdf')]
            print(f"   PDF files: {len(pdf_files)} found")
            if pdf_files:
                print(f"   Latest: {max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(self.downloads_dir, f)))}")
        else:
            print("   Output directory: Not found")
        
        # Check output
        print("\nOutput:")
        csv_file = os.path.join(self.output_dir, "EGX_Weekly_Data.csv")
        if os.path.exists(csv_file):
            try:
                file_size = os.path.getsize(csv_file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(csv_file))
                print(f"   EGX_Weekly_Data.csv: Found ({file_size:,} bytes)")
                print(f"   Last updated: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print("   EGX_Weekly_Data.csv: Found (size unknown)")
        else:
            print("   EGX_Weekly_Data.csv: Not found")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='EGX Data Pipeline Orchestrator')
    parser.add_argument('--skip-download', action='store_true', 
                       help='Skip PDF download step (use existing files)')
    parser.add_argument('--skip-processing', action='store_true',
                       help='Skip PDF processing step (download only)')
    parser.add_argument('--status', action='store_true',
                       help='Show pipeline status and exit')
    
    args = parser.parse_args()
    
    orchestrator = EGXPipelineOrchestrator()
    
    if args.status:
        orchestrator.show_status()
        return
    
    success = orchestrator.run_pipeline(
        skip_download=args.skip_download,
        skip_processing=args.skip_processing
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()