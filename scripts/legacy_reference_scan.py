#!/usr/bin/env python3
"""
Stage 5 - GUI-011: Legacy Code Removal Verification
Confirm zero legacy references remain in the codebase
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

class LegacyReferenceScanner:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.scan_report = {
            'timestamp': datetime.now().isoformat(),
            'scan_type': 'Legacy Code Removal Verification',
            'stage': 'Stage 5 - GUI-011',
            'total_files_scanned': 0,
            'legacy_references_found': 0,
            'legacy_files_found': 0,
            'legacy_imports_found': 0,
            'legacy_functions_found': 0,
            'legacy_patterns': [],
            'clean_verification': False,
            'detailed_findings': [],
            'recommendations': []
        }
        
        # Define legacy patterns to search for
        self.legacy_patterns = {
            'legacy_keywords': [
                r'\blegacy\b', r'\bold\b', r'\bdeprecated\b', r'\bobsolete\b',
                r'\bunused\b', r'\bremove\b', r'\btodo.*remove\b', r'\bfixme.*legacy\b'
            ],
            'legacy_imports': [
                r'import.*legacy', r'from.*legacy', r'import.*old', r'from.*old',
                r'import.*deprecated', r'from.*deprecated'
            ],
            'legacy_functions': [
                r'def.*legacy', r'def.*old_', r'def.*deprecated',
                r'class.*Legacy', r'class.*Old', r'class.*Deprecated'
            ],
            'legacy_comments': [
                r'#.*legacy', r'#.*old version', r'#.*deprecated',
                r'#.*remove', r'#.*obsolete', r'""".*legacy.*"""'
            ],
            'legacy_variables': [
                r'\blegacy_\w+', r'\bold_\w+', r'\bdeprecated_\w+',
                r'\bobsolete_\w+'
            ],
            'legacy_directories': [
                r'legacy/', r'old/', r'deprecated/', r'obsolete/',
                r'backup/', r'archive/', r'temp/'
            ]
        }

    def scan_file_content(self, file_path):
        """Scan individual file for legacy references"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            for pattern_category, patterns in self.legacy_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                        
                        finding = {
                            'file': str(file_path.relative_to(self.root_dir)),
                            'line': line_num,
                            'pattern': pattern,
                            'category': pattern_category,
                            'match': match.group(),
                            'context': line_content,
                            'severity': self._determine_severity(pattern_category, match.group())
                        }
                        findings.append(finding)
            
            return findings
            
        except Exception as e:
            return [{
                'file': str(file_path.relative_to(self.root_dir)),
                'error': f"Could not scan file: {str(e)}",
                'severity': 'ERROR'
            }]

    def _determine_severity(self, category, match_text):
        """Determine severity of legacy reference"""
        high_severity_indicators = ['import', 'class', 'def', 'function']
        medium_severity_indicators = ['variable', 'comment']
        
        if category in ['legacy_imports', 'legacy_functions']:
            return 'HIGH'
        elif category in ['legacy_keywords'] and any(indicator in match_text.lower() for indicator in high_severity_indicators):
            return 'HIGH'
        elif category in ['legacy_comments', 'legacy_variables']:
            return 'MEDIUM'
        else:
            return 'LOW'

    def scan_directory_structure(self):
        """Check for legacy directories"""
        legacy_dirs = []
        
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            relative_path = root_path.relative_to(self.root_dir)
            
            # Check directory names
            for dir_name in dirs:
                if any(legacy_term in dir_name.lower() for legacy_term in ['legacy', 'old', 'deprecated', 'obsolete', 'backup', 'archive', 'temp']):
                    legacy_dirs.append({
                        'type': 'directory',
                        'path': str(relative_path / dir_name),
                        'severity': 'HIGH',
                        'recommendation': 'Remove legacy directory'
                    })
            
            # Check file names
            for file_name in files:
                if any(legacy_term in file_name.lower() for legacy_term in ['legacy', 'old', 'deprecated', 'obsolete']):
                    legacy_dirs.append({
                        'type': 'file',
                        'path': str(relative_path / file_name),
                        'severity': 'MEDIUM',
                        'recommendation': 'Review and remove legacy file'
                    })
        
        return legacy_dirs

    def scan_configuration_files(self):
        """Scan configuration files for legacy references"""
        config_files = [
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',
            'package.json', 'yarn.lock', 'composer.json',
            '.gitignore', '.dockerignore', 'Dockerfile',
            'config.json', 'settings.py', 'config.py'
        ]
        
        config_findings = []
        
        for config_file in config_files:
            config_path = self.root_dir / config_file
            if config_path.exists():
                findings = self.scan_file_content(config_path)
                config_findings.extend(findings)
        
        return config_findings

    def verify_imports_clean(self):
        """Verify all import statements are clean of legacy references"""
        import_findings = []
        python_files = list(self.root_dir.rglob("*.py"))
        
        for py_file in python_files:
            # Skip test files and cache
            if any(skip in str(py_file) for skip in ['test_', '__pycache__', '.pyc', '/tmp/']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line_clean = line.strip()
                    if line_clean.startswith(('import ', 'from ')):
                        # Check for legacy imports
                        if any(legacy in line_clean.lower() for legacy in ['legacy', 'old', 'deprecated']):
                            import_findings.append({
                                'file': str(py_file.relative_to(self.root_dir)),
                                'line': line_num,
                                'import': line_clean,
                                'severity': 'HIGH',
                                'issue': 'Legacy import statement found'
                            })
            
            except Exception as e:
                continue
        
        return import_findings

    def run_comprehensive_scan(self):
        """Execute comprehensive legacy reference scan"""
        print("🧹 Starting Stage 5 - Legacy Code Removal Verification...")
        print("=" * 60)
        
        all_findings = []
        
        # Step 1: Scan all source files
        print("📁 Scanning source files for legacy references...")
        source_extensions = ['.py', '.js', '.ts', '.json', '.md', '.txt', '.yaml', '.yml']
        file_count = 0
        
        for ext in source_extensions:
            for file_path in self.root_dir.rglob(f"*{ext}"):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                    continue
                
                file_count += 1
                findings = self.scan_file_content(file_path)
                all_findings.extend(findings)
        
        self.scan_report['total_files_scanned'] = file_count
        print(f"   Scanned {file_count} files")
        
        # Step 2: Scan directory structure
        print("📂 Checking directory structure for legacy components...")
        directory_findings = self.scan_directory_structure()
        all_findings.extend(directory_findings)
        print(f"   Found {len(directory_findings)} legacy directory/file references")
        
        # Step 3: Scan configuration files
        print("⚙️  Scanning configuration files...")
        config_findings = self.scan_configuration_files()
        all_findings.extend(config_findings)
        print(f"   Found {len(config_findings)} legacy references in config files")
        
        # Step 4: Verify import statements
        print("📦 Verifying import statements are clean...")
        import_findings = self.verify_imports_clean()
        all_findings.extend(import_findings)
        print(f"   Found {len(import_findings)} legacy import statements")
        
        # Process findings
        self.process_findings(all_findings)
        
        return self.scan_report

    def process_findings(self, findings):
        """Process and categorize all findings"""
        # Count findings by type
        legacy_references = len([f for f in findings if 'legacy' in f.get('match', '').lower()])
        legacy_files = len(set(f.get('file', f.get('path', 'unknown')) for f in findings if f.get('type') == 'file'))
        legacy_imports = len([f for f in findings if f.get('category') == 'legacy_imports'])
        legacy_functions = len([f for f in findings if f.get('category') == 'legacy_functions'])
        
        self.scan_report['legacy_references_found'] = len(findings)
        self.scan_report['legacy_files_found'] = legacy_files
        self.scan_report['legacy_imports_found'] = legacy_imports
        self.scan_report['legacy_functions_found'] = legacy_functions
        
        # Categorize by severity
        high_severity = [f for f in findings if f.get('severity') == 'HIGH']
        medium_severity = [f for f in findings if f.get('severity') == 'MEDIUM']
        low_severity = [f for f in findings if f.get('severity') == 'LOW']
        
        self.scan_report['severity_breakdown'] = {
            'high': len(high_severity),
            'medium': len(medium_severity),
            'low': len(low_severity)
        }
        
        # Store detailed findings
        self.scan_report['detailed_findings'] = findings
        
        # Determine if codebase is clean
        critical_findings = high_severity + medium_severity
        self.scan_report['clean_verification'] = len(critical_findings) == 0
        
        # Generate recommendations
        self.generate_recommendations(high_severity, medium_severity)

    def generate_recommendations(self, high_severity, medium_severity):
        """Generate recommendations for legacy code cleanup"""
        recommendations = []
        
        if high_severity:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'High Severity Legacy Code',
                'issue': f'{len(high_severity)} high-severity legacy references found',
                'recommendation': 'Immediately remove all legacy imports, functions, and critical references',
                'impact': 'Legacy code may cause system instability or security issues',
                'files_affected': list(set(f.get('file', 'unknown') for f in high_severity))
            })
        
        if medium_severity:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Medium Severity Legacy Code',
                'issue': f'{len(medium_severity)} medium-severity legacy references found',
                'recommendation': 'Clean up legacy comments, variables, and documentation',
                'impact': 'Technical debt and confusion for developers',
                'files_affected': list(set(f.get('file', 'unknown') for f in medium_severity))
            })
        
        # File-specific recommendations
        affected_files = set(f.get('file', 'unknown') for f in high_severity + medium_severity)
        if affected_files:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'File Cleanup',
                'issue': f'{len(affected_files)} files contain legacy references',
                'recommendation': 'Review and clean each affected file individually',
                'impact': 'Reduced code quality and maintainability',
                'files_affected': list(affected_files)
            })
        
        self.scan_report['recommendations'] = recommendations

    def save_report(self, output_file):
        """Save legacy scan report"""
        with open(output_file, 'w') as f:
            json.dump(self.scan_report, f, indent=2)
        print(f"\n✅ Legacy reference scan report saved to: {output_file}")

def main():
    """Main execution function"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = f"legacy_reference_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    scanner = LegacyReferenceScanner(root_dir)
    report = scanner.run_comprehensive_scan()
    
    # Print summary
    print("\n" + "="*60)
    print("🧹 LEGACY CODE REMOVAL VERIFICATION SUMMARY")
    print("="*60)
    print(f"Files Scanned: {report['total_files_scanned']}")
    print(f"Legacy References: {report['legacy_references_found']}")
    print(f"Legacy Files: {report['legacy_files_found']}")
    print(f"Legacy Imports: {report['legacy_imports_found']}")
    print(f"Legacy Functions: {report['legacy_functions_found']}")
    
    # Print severity breakdown
    severity = report.get('severity_breakdown', {})
    print(f"\n📊 SEVERITY BREAKDOWN:")
    print(f"  High: {severity.get('high', 0)}")
    print(f"  Medium: {severity.get('medium', 0)}")
    print(f"  Low: {severity.get('low', 0)}")
    
    # Print verification status
    is_clean = report.get('clean_verification', False)
    if is_clean:
        print("\n✅ VERIFICATION: CLEAN")
        print("   Zero legacy code references found")
    else:
        print("\n❌ VERIFICATION: LEGACY CODE DETECTED")
        print("   Legacy references require cleanup")
    
    # Print critical findings
    high_severity = [f for f in report.get('detailed_findings', []) if f.get('severity') == 'HIGH']
    if high_severity:
        print("\n🚨 CRITICAL LEGACY REFERENCES:")
        for finding in high_severity[:5]:  # Show first 5
            print(f"  • {finding.get('file', 'unknown')} line {finding.get('line', '?')}: {finding.get('match', 'N/A')}")
        if len(high_severity) > 5:
            print(f"  ... and {len(high_severity) - 5} more")
    
    # Print recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        print("\n💡 CLEANUP RECOMMENDATIONS:")
        for rec in recommendations[:3]:  # Show top 3
            print(f"  {rec['priority']}: {rec['issue']}")
            print(f"    Action: {rec['recommendation']}")
    
    scanner.save_report(output_file)
    
    # Return status based on verification
    if is_clean:
        print("\n✅ LEGACY VERIFICATION: PASSED")
        print("   Codebase completely free of legacy references")
        return 0
    else:
        critical_count = severity.get('high', 0) + severity.get('medium', 0)
        if critical_count <= 5:
            print("\n⚠️  LEGACY VERIFICATION: MINOR ISSUES")
            print("   Few legacy references found, cleanup recommended")
            return 0
        else:
            print("\n❌ LEGACY VERIFICATION: FAILED")
            print("   Significant legacy code cleanup required")
            return 1

if __name__ == "__main__":
    sys.exit(main())