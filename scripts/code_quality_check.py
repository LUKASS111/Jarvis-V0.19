#!/usr/bin/env python3
"""
Jarvis V0.19 - Stage 3: QUAL-001 - Comprehensive Code Quality Standards Check
Engineering Rigor Implementation with GUI-focused quality validation

This script implements comprehensive code quality standards with special focus on GUI components.
Validates code formatting, linting, and GUI-specific quality metrics.
"""

import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path


class CodeQualityChecker:
    """Comprehensive code quality validation with GUI focus"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "Stage 3 - QUAL-001",
            "title": "Comprehensive Code Quality Standards Check",
            "checks": {},
            "gui_specific": {},
            "overall_score": 0,
            "status": "UNKNOWN"
        }
        
    def run_flake8_check(self):
        """Run flake8 linting on all Python files"""
        try:
            result = subprocess.run([
                'flake8', 
                str(self.repo_root),
                '--exclude=.git,__pycache__,archive,data,tests',
                '--max-line-length=88',
                '--count'
            ], capture_output=True, text=True, cwd=self.repo_root)
            
            violations = result.stdout.strip().split('\n') if result.stdout.strip() else []
            violation_count = len([v for v in violations if v.strip()])
            
            self.results["checks"]["flake8"] = {
                "violations": violation_count,
                "details": violations[:10] if violations else [],  # First 10 violations
                "status": "PASS" if violation_count == 0 else "REVIEW" if violation_count < 20 else "FAIL"
            }
            return violation_count == 0
            
        except Exception as e:
            self.results["checks"]["flake8"] = {
                "error": str(e),
                "status": "ERROR"
            }
            return False
    
    def run_black_format_check(self):
        """Check if code is properly formatted with black"""
        try:
            result = subprocess.run([
                'black', 
                '--check',
                '--diff',
                str(self.repo_root),
                '--exclude=archive|data|tests'
            ], capture_output=True, text=True, cwd=self.repo_root)
            
            format_issues = result.stdout.strip().split('\n') if result.stdout.strip() else []
            issue_count = len([i for i in format_issues if i.strip() and i.startswith('---')])
            
            self.results["checks"]["black_formatting"] = {
                "format_issues": issue_count,
                "status": "PASS" if issue_count == 0 else "FAIL",
                "details": format_issues[:5] if format_issues else []
            }
            return issue_count == 0
            
        except Exception as e:
            self.results["checks"]["black_formatting"] = {
                "error": str(e),
                "status": "ERROR"
            }
            return False
    
    def check_gui_code_quality(self):
        """GUI-specific code quality checks"""
        gui_files = list(Path(self.repo_root / "gui").rglob("*.py"))
        
        gui_analysis = {
            "total_files": len(gui_files),
            "files_analyzed": [],
            "quality_issues": [],
            "best_practices": {
                "error_handling": 0,
                "documentation": 0,
                "type_hints": 0,
                "class_structure": 0
            }
        }
        
        for gui_file in gui_files:
            try:
                with open(gui_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                file_analysis = {
                    "file": str(gui_file.relative_to(self.repo_root)),
                    "lines": len(content.split('\n')),
                    "has_docstring": '"""' in content or "'''" in content,
                    "has_type_hints": ' -> ' in content or ': ' in content,
                    "has_error_handling": 'try:' in content and 'except' in content,
                    "has_classes": 'class ' in content
                }
                
                gui_analysis["files_analyzed"].append(file_analysis)
                
                # Count best practices
                if file_analysis["has_error_handling"]:
                    gui_analysis["best_practices"]["error_handling"] += 1
                if file_analysis["has_docstring"]:
                    gui_analysis["best_practices"]["documentation"] += 1
                if file_analysis["has_type_hints"]:
                    gui_analysis["best_practices"]["type_hints"] += 1
                if file_analysis["has_classes"]:
                    gui_analysis["best_practices"]["class_structure"] += 1
                    
            except Exception as e:
                gui_analysis["quality_issues"].append(f"Error analyzing {gui_file}: {e}")
        
        # Calculate GUI quality score
        total_files = gui_analysis["total_files"]
        if total_files > 0:
            practices = gui_analysis["best_practices"]
            gui_score = (
                (practices["error_handling"] / total_files) * 25 +
                (practices["documentation"] / total_files) * 25 +
                (practices["type_hints"] / total_files) * 25 +
                (practices["class_structure"] / total_files) * 25
            )
        else:
            gui_score = 0
            
        gui_analysis["quality_score"] = round(gui_score, 1)
        gui_analysis["status"] = "EXCELLENT" if gui_score >= 90 else "GOOD" if gui_score >= 70 else "NEEDS_IMPROVEMENT"
        
        self.results["gui_specific"]["code_quality"] = gui_analysis
        return gui_score >= 70
    
    def check_documentation_coverage(self):
        """Check documentation coverage across codebase"""
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data'])]
        
        documented_files = 0
        total_functions = 0
        documented_functions = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check file docstring
                if content.strip().startswith('"""') or content.strip().startswith("'''"):
                    documented_files += 1
                
                # Count functions and their documentation
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('def '):
                        total_functions += 1
                        # Check if next few lines contain docstring
                        for j in range(i+1, min(i+5, len(lines))):
                            if '"""' in lines[j] or "'''" in lines[j]:
                                documented_functions += 1
                                break
                                
            except Exception as e:
                continue
        
        doc_coverage = {
            "total_files": len(python_files),
            "documented_files": documented_files,
            "file_coverage": round((documented_files / len(python_files)) * 100, 1) if python_files else 0,
            "total_functions": total_functions,
            "documented_functions": documented_functions,
            "function_coverage": round((documented_functions / total_functions) * 100, 1) if total_functions > 0 else 0
        }
        
        doc_coverage["status"] = "EXCELLENT" if doc_coverage["file_coverage"] >= 80 else "GOOD" if doc_coverage["file_coverage"] >= 60 else "NEEDS_IMPROVEMENT"
        
        self.results["checks"]["documentation_coverage"] = doc_coverage
        return doc_coverage["file_coverage"] >= 60
    
    def check_security_patterns(self):
        """Basic security pattern validation"""
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data'])]
        
        security_issues = []
        security_good_practices = 0
        
        patterns_to_avoid = [
            ('eval(', 'Use of eval() function'),
            ('exec(', 'Use of exec() function'),
            ('shell=True', 'Shell injection risk'),
            ('password', 'Potential hardcoded password'),
            ('secret', 'Potential hardcoded secret'),
            ('api_key', 'Potential hardcoded API key')
        ]
        
        patterns_good_practice = [
            ('os.environ.get', 'Environment variable usage'),
            ('cryptography', 'Cryptography library usage'),
            ('hashlib', 'Secure hashing'),
            ('getpass', 'Secure password input')
        ]
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                    for pattern, issue in patterns_to_avoid:
                        if pattern in content:
                            security_issues.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "issue": issue,
                                "pattern": pattern
                            })
                    
                    for pattern, practice in patterns_good_practice:
                        if pattern in content:
                            security_good_practices += 1
                            
            except Exception as e:
                continue
        
        security_analysis = {
            "security_issues": len(security_issues),
            "issues_details": security_issues[:10],  # First 10 issues
            "good_practices_count": security_good_practices,
            "status": "PASS" if len(security_issues) == 0 else "REVIEW" if len(security_issues) < 5 else "FAIL"
        }
        
        self.results["checks"]["security_patterns"] = security_analysis
        return len(security_issues) == 0
    
    def calculate_overall_score(self):
        """Calculate overall code quality score"""
        checks = self.results["checks"]
        scores = []
        
        # Flake8 score
        if "flake8" in checks and checks["flake8"]["status"] == "PASS":
            scores.append(100)
        elif "flake8" in checks and checks["flake8"]["status"] == "REVIEW":
            scores.append(70)
        else:
            scores.append(0)
        
        # Black formatting score
        if "black_formatting" in checks and checks["black_formatting"]["status"] == "PASS":
            scores.append(100)
        else:
            scores.append(0)
        
        # Documentation score
        if "documentation_coverage" in checks:
            scores.append(checks["documentation_coverage"]["file_coverage"])
        
        # Security score
        if "security_patterns" in checks and checks["security_patterns"]["status"] == "PASS":
            scores.append(100)
        elif "security_patterns" in checks and checks["security_patterns"]["status"] == "REVIEW":
            scores.append(70)
        else:
            scores.append(0)
        
        # GUI quality score
        if "code_quality" in self.results["gui_specific"]:
            scores.append(self.results["gui_specific"]["code_quality"]["quality_score"])
        
        overall_score = sum(scores) / len(scores) if scores else 0
        self.results["overall_score"] = round(overall_score, 1)
        
        if overall_score >= 90:
            self.results["status"] = "EXCELLENT"
        elif overall_score >= 70:
            self.results["status"] = "GOOD"
        elif overall_score >= 50:
            self.results["status"] = "NEEDS_IMPROVEMENT"
        else:
            self.results["status"] = "CRITICAL"
        
        return overall_score >= 70
    
    def run_all_checks(self):
        """Run all code quality checks"""
        print("🔍 Running Comprehensive Code Quality Standards Check (QUAL-001)...")
        print("=" * 70)
        
        checks = [
            ("Flake8 Linting", self.run_flake8_check),
            ("Black Formatting", self.run_black_format_check),
            ("GUI Code Quality", self.check_gui_code_quality),
            ("Documentation Coverage", self.check_documentation_coverage),
            ("Security Patterns", self.check_security_patterns)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"Running {check_name}...")
            try:
                result = check_func()
                status = "✅ PASS" if result else "⚠️  REVIEW"
                print(f"  {status}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                all_passed = False
        
        print("\n" + "=" * 70)
        self.calculate_overall_score()
        
        print(f"📊 Overall Code Quality Score: {self.results['overall_score']}%")
        print(f"🎯 Status: {self.results['status']}")
        
        # Generate detailed report
        report_file = self.repo_root / f"code_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📋 Detailed report saved: {report_file}")
        
        return all_passed and self.results["overall_score"] >= 70


def main():
    """Main execution function"""
    checker = CodeQualityChecker()
    success = checker.run_all_checks()
    
    if success:
        print("\n✅ QUAL-001 COMPLETED: Code quality standards check passed!")
        sys.exit(0)
    else:
        print("\n❌ QUAL-001 NEEDS ATTENTION: Code quality improvements required")
        sys.exit(1)


if __name__ == "__main__":
    main()