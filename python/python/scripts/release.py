#!/usr/bin/env python3
"""
Release management script for BPlusTree3.

This script automates version bumping, changelog updates, and release preparation.
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class ReleaseManager:
    """Manages releases for the BPlusTree3 project."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.python_dir = project_root / "python"
        self.version_file = self.python_dir / "__init__.py"
        self.changelog_file = self.python_dir / "CHANGELOG.md"
        
    def get_current_version(self) -> str:
        """Get the current version from __init__.py."""
        if not self.version_file.exists():
            raise FileNotFoundError(f"Version file not found: {self.version_file}")
        
        content = self.version_file.read_text()
        match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
        if not match:
            raise ValueError("Could not find version in __init__.py")
        
        return match.group(1)
    
    def set_version(self, new_version: str) -> None:
        """Set a new version in __init__.py."""
        content = self.version_file.read_text()
        new_content = re.sub(
            r'__version__ = ["\'][^"\']+["\']',
            f'__version__ = "{new_version}"',
            content
        )
        self.version_file.write_text(new_content)
        print(f"Updated version to {new_version} in {self.version_file}")
    
    def parse_version(self, version: str) -> Tuple[int, int, int, Optional[str]]:
        """Parse a version string into components."""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$', version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")
        
        major, minor, patch, prerelease = match.groups()
        return int(major), int(minor), int(patch), prerelease
    
    def format_version(self, major: int, minor: int, patch: int, prerelease: Optional[str] = None) -> str:
        """Format version components into a version string."""
        version = f"{major}.{minor}.{patch}"
        if prerelease:
            version += f"-{prerelease}"
        return version
    
    def bump_version(self, bump_type: str) -> str:
        """Bump the version according to the specified type."""
        current = self.get_current_version()
        major, minor, patch, prerelease = self.parse_version(current)
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
            prerelease = None
        elif bump_type == "minor":
            minor += 1
            patch = 0
            prerelease = None
        elif bump_type == "patch":
            patch += 1
            prerelease = None
        elif bump_type == "prerelease":
            if prerelease:
                # Increment prerelease number
                match = re.match(r'^(.+?)(\d+)$', prerelease)
                if match:
                    prefix, number = match.groups()
                    prerelease = f"{prefix}{int(number) + 1}"
                else:
                    prerelease = f"{prerelease}.1"
            else:
                # First prerelease
                prerelease = "rc.1"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        new_version = self.format_version(major, minor, patch, prerelease)
        return new_version
    
    def update_changelog(self, version: str, changes: List[str]) -> None:
        """Update the changelog with a new version entry."""
        if not self.changelog_file.exists():
            # Create new changelog
            content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        else:
            content = self.changelog_file.read_text()
        
        # Create new entry
        date = datetime.now().strftime("%Y-%m-%d")
        entry = f"## [{version}] - {date}\n\n"
        
        if changes:
            entry += "### Changed\n\n"
            for change in changes:
                entry += f"- {change}\n"
            entry += "\n"
        else:
            entry += "### Added\n\n### Changed\n\n### Fixed\n\n"
        
        # Insert after the header
        lines = content.split('\n')
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith('#') and 'changelog' in line.lower():
                header_end = i + 1
                break
        
        # Skip empty lines after header
        while header_end < len(lines) and not lines[header_end].strip():
            header_end += 1
        
        # Insert new entry
        new_lines = lines[:header_end] + [''] + entry.split('\n') + lines[header_end:]
        new_content = '\n'.join(new_lines)
        
        self.changelog_file.write_text(new_content)
        print(f"Updated changelog with version {version}")
    
    def run_tests(self) -> bool:
        """Run the test suite."""
        print("Running tests...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
                cwd=self.python_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print("❌ Tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def run_linting(self) -> bool:
        """Run code linting."""
        print("Running linting...")
        try:
            # Run black
            result = subprocess.run(
                [sys.executable, "-m", "black", "--check", "."],
                cwd=self.python_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("❌ Black formatting issues found")
                print("Run 'black .' to fix formatting")
                return False
            
            # Run ruff
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "."],
                cwd=self.python_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("❌ Ruff linting issues found:")
                print(result.stdout)
                return False
            
            print("✅ Linting passed")
            return True
        except Exception as e:
            print(f"❌ Error running linting: {e}")
            return False
    
    def check_git_status(self) -> bool:
        """Check if git working directory is clean."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print("❌ Git working directory is not clean:")
                print(result.stdout)
                print("Please commit or stash your changes before releasing")
                return False
            return True
        except Exception as e:
            print(f"❌ Error checking git status: {e}")
            return False
    
    def create_git_tag(self, version: str) -> bool:
        """Create a git tag for the release."""
        try:
            tag_name = f"v{version}"
            
            # Create annotated tag
            result = subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Failed to create tag: {result.stderr}")
                return False
            
            print(f"✅ Created git tag {tag_name}")
            return True
        except Exception as e:
            print(f"❌ Error creating git tag: {e}")
            return False
    
    def build_package(self) -> bool:
        """Build the package."""
        print("Building package...")
        try:
            # Clean previous builds
            build_dir = self.python_dir / "build"
            dist_dir = self.python_dir / "dist"
            
            if build_dir.exists():
                subprocess.run(["rm", "-rf", str(build_dir)])
            if dist_dir.exists():
                subprocess.run(["rm", "-rf", str(dist_dir)])
            
            # Build package
            result = subprocess.run(
                [sys.executable, "-m", "build"],
                cwd=self.python_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Package build failed:")
                print(result.stdout)
                print(result.stderr)
                return False
            
            print("✅ Package built successfully")
            return True
        except Exception as e:
            print(f"❌ Error building package: {e}")
            return False
    
    def prepare_release(self, version: str, changes: List[str], skip_tests: bool = False) -> bool:
        """Prepare a release with the given version."""
        print(f"Preparing release {version}...")
        
        # Check git status
        if not self.check_git_status():
            return False
        
        # Run tests and linting
        if not skip_tests:
            if not self.run_tests():
                return False
            if not self.run_linting():
                return False
        
        # Update version and changelog
        self.set_version(version)
        self.update_changelog(version, changes)
        
        # Build package to verify
        if not self.build_package():
            return False
        
        print(f"✅ Release {version} prepared successfully!")
        print(f"Next steps:")
        print(f"1. Review the changes in {self.version_file} and {self.changelog_file}")
        print(f"2. Commit the changes: git add -A && git commit -m 'chore: release v{version}'")
        print(f"3. Create and push tag: git tag v{version} && git push origin v{version}")
        print(f"4. The GitHub Actions will handle building and publishing")
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="BPlusTree3 release management")
    parser.add_argument("--version", help="Specific version to release (e.g., 1.0.0)")
    parser.add_argument("--bump", choices=["major", "minor", "patch", "prerelease"],
                      help="Bump version type")
    parser.add_argument("--changes", nargs="*", help="List of changes for changelog")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--current", action="store_true", help="Show current version")
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    manager = ReleaseManager(project_root)
    
    if args.current:
        current = manager.get_current_version()
        print(f"Current version: {current}")
        return
    
    if args.version:
        new_version = args.version
    elif args.bump:
        new_version = manager.bump_version(args.bump)
    else:
        current = manager.get_current_version()
        print(f"Current version: {current}")
        print("Please specify --version or --bump to create a release")
        return
    
    changes = args.changes or []
    
    success = manager.prepare_release(new_version, changes, args.skip_tests)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()