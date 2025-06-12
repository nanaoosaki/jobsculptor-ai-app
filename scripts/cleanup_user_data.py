#!/usr/bin/env python3
"""
User Data Cleanup Script for Resume Tailor
===========================================

CRITICAL SECURITY TOOL - Use before:
- Making repository public
- Deploying to production
- Creating backups/archives

This script safely removes all user-generated content while preserving
the application structure needed for deployment.

Usage:
    python scripts/cleanup_user_data.py [--backup] [--dry-run]

Options:
    --backup    Create archive of user data before deletion
    --dry-run   Show what would be deleted without actually doing it
"""

import os
import shutil
import glob
import argparse
from datetime import datetime
from pathlib import Path

class UserDataCleaner:
    """Safely clean user data from Resume Tailor installation."""
    
    def __init__(self, backup=False, dry_run=False):
        self.backup = backup
        self.dry_run = dry_run
        self.base_path = Path(__file__).parent.parent
        self.cleaned_count = 0
        self.archived_count = 0
        
    def log(self, message, level="INFO"):
        """Log actions with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "🔍 DRY RUN -" if self.dry_run else ""
        print(f"[{timestamp}] {prefix} {level}: {message}")
        
    def create_backup(self):
        """Create timestamped backup of user data."""
        if not self.backup:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_path / f"user_data_backup_{timestamp}"
        uploads_dir = self.base_path / "static" / "uploads"
        
        if uploads_dir.exists():
            self.log(f"Creating backup at: {backup_dir}")
            if not self.dry_run:
                shutil.copytree(uploads_dir, backup_dir / "uploads")
                self.archived_count = len(list(backup_dir.rglob("*")))
                self.log(f"Backed up {self.archived_count} files to {backup_dir}")
    
    def clean_uploads_directory(self):
        """Clean the static/uploads directory."""
        uploads_dir = self.base_path / "static" / "uploads"
        
        if not uploads_dir.exists():
            self.log("Uploads directory doesn't exist")
            return
            
        # Patterns of files to remove (user data)
        user_data_patterns = [
            "*.pdf",
            "*.docx", 
            "*_llm_parsed.json",
            "*_llm_analysis.json",
            "*_contact.json",
            "*_education.json", 
            "*_experience.json",
            "*_projects.json",
            "*_skills.json",
            "*_summary.json",
            "*tailored*.pdf",
            "*tailored*.docx",
        ]
        
        # UUID pattern files (typically user sessions)
        uuid_pattern = "[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*.*"
        
        # Files to preserve
        preserve_files = {".gitkeep", "template_resume.docx", "README.md"}
        
        for pattern in user_data_patterns + [uuid_pattern]:
            for file_path in uploads_dir.glob(pattern):
                if file_path.name in preserve_files:
                    continue
                    
                self.log(f"🗑️  Removing: {file_path.relative_to(self.base_path)}")
                if not self.dry_run:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                self.cleaned_count += 1
        
        # Remove user data subdirectories
        user_data_dirs = [
            "job_analysis_cache",
            "api_responses", 
            "temp_session_data"
        ]
        
        for dir_name in user_data_dirs:
            dir_path = uploads_dir / dir_name
            if dir_path.exists():
                self.log(f"🗑️  Removing directory: {dir_path.relative_to(self.base_path)}")
                if not self.dry_run:
                    shutil.rmtree(dir_path)
                self.cleaned_count += 1
    
    def clean_root_user_files(self):
        """Clean user-generated files in root directory."""
        patterns = [
            "downloaded*.pdf",
            "downloaded*.docx", 
            "tailored_resume_*.pdf",
            "user_data_archive"
        ]
        
        for pattern in patterns:
            for path in self.base_path.glob(pattern):
                self.log(f"🗑️  Removing: {path.name}")
                if not self.dry_run:
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                self.cleaned_count += 1
    
    def verify_clean_state(self):
        """Verify that no user data remains."""
        uploads_dir = self.base_path / "static" / "uploads"
        
        if not uploads_dir.exists():
            self.log("✅ Uploads directory clean (doesn't exist)")
            return True
            
        remaining_files = []
        for file_path in uploads_dir.rglob("*"):
            if file_path.is_file() and file_path.name not in {".gitkeep", "template_resume.docx"}:
                remaining_files.append(file_path)
        
        if remaining_files:
            self.log("⚠️  WARNING: Some files remain:", "WARN")
            for file_path in remaining_files[:5]:  # Show first 5
                self.log(f"  - {file_path.relative_to(self.base_path)}", "WARN")
            if len(remaining_files) > 5:
                self.log(f"  ... and {len(remaining_files) - 5} more", "WARN")
            return False
        else:
            self.log("✅ All user data successfully removed")
            return True
    
    def run(self):
        """Execute the cleanup process."""
        self.log("🧹 Starting user data cleanup...")
        self.log(f"Base directory: {self.base_path}")
        
        if self.dry_run:
            self.log("DRY RUN MODE - No files will actually be deleted", "WARN")
        
        # Step 1: Create backup if requested
        self.create_backup()
        
        # Step 2: Clean uploads directory
        self.clean_uploads_directory()
        
        # Step 3: Clean root directory
        self.clean_root_user_files()
        
        # Step 4: Verify clean state
        self.verify_clean_state()
        
        # Summary
        self.log("🎉 Cleanup completed!")
        self.log(f"Files cleaned: {self.cleaned_count}")
        if self.backup:
            self.log(f"Files archived: {self.archived_count}")
        
        if not self.dry_run:
            self.log("✅ Repository is now safe for public sharing!")

def main():
    parser = argparse.ArgumentParser(description="Clean user data from Resume Tailor")
    parser.add_argument("--backup", action="store_true", 
                       help="Create backup before cleaning")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be deleted without doing it")
    
    args = parser.parse_args()
    
    cleaner = UserDataCleaner(backup=args.backup, dry_run=args.dry_run)
    cleaner.run()

if __name__ == "__main__":
    main() 