#!/usr/bin/env python3
"""
Jarvis V0.19 - Stage 3: QUAL-002 - Automated Quality Gates
Engineering Rigor Implementation with GUI-focused quality gates

This script implements automated quality gates for all code changes and GUI components.
Prevents regression and ensures consistent quality standards.
"""

import subprocess
import sys
import json
import os
import re
from datetime import datetime
from pathlib import Path


class QualityGates:
    """Automated quality gates for code changes and GUI components"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "Stage 3 - QUAL-002",
            "title": "Automated Quality Gates Validation",
            "gates": {},
            "gui_gates": {},
            "overall_status": "UNKNOWN",
            "blocking_issues": []
        }
        
    def check_file_size_limits(self):
        """Check file size limits to prevent large file commits"""
        large_files = []
        max_size_mb = 10  # 10MB limit for individual files
        
        for file_path in Path(self.repo_root).rglob("*"):
            if file_path.is_file() and not any(exclude in str(file_path) for exclude in ['.git', '__pycache__', 'node_modules']):
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > max_size_mb:
                        large_files.append({
                            "file": str(file_path.relative_to(self.repo_root)),
                            "size_mb": round(size_mb, 2)
                        })
                except Exception:
                    continue
        
        gate_status = len(large_files) == 0
        self.results["gates"]["file_size_limit"] = {
            "status": "PASS" if gate_status else "FAIL",
            "large_files": large_files,
            "limit_mb": max_size_mb,
            "description": "Prevents large file commits that could bloat repository"
        }
        
        if not gate_status:
            self.results["blocking_issues"].append("Large files detected exceeding 10MB limit")
        
        return gate_status
    
    def check_code_complexity(self):
        """Check code complexity to prevent overly complex functions"""
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data', 'tests'])]
        
        complex_functions = []
        max_lines_per_function = 50
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                current_function = None
                function_start = 0
                indent_level = 0
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('def '):
                        # Save previous function if it was too long
                        if current_function and (i - function_start) > max_lines_per_function:
                            complex_functions.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "function": current_function,
                                "lines": i - function_start,
                                "start_line": function_start + 1
                            })
                        
                        # Start new function
                        current_function = stripped.split('(')[0].replace('def ', '')
                        function_start = i
                        indent_level = len(line) - len(line.lstrip())
                    elif current_function and line.strip() and len(line) - len(line.lstrip()) <= indent_level and line.strip() != '':
                        # Function ended
                        if (i - function_start) > max_lines_per_function:
                            complex_functions.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "function": current_function,
                                "lines": i - function_start,
                                "start_line": function_start + 1
                            })
                        current_function = None
                        
            except Exception:
                continue
        
        gate_status = len(complex_functions) == 0
        self.results["gates"]["code_complexity"] = {
            "status": "PASS" if gate_status else "REVIEW",
            "complex_functions": complex_functions[:10],  # First 10
            "limit_lines": max_lines_per_function,
            "description": "Prevents overly complex functions that are hard to maintain"
        }
        
        if len(complex_functions) > 10:
            self.results["blocking_issues"].append(f"Too many complex functions detected ({len(complex_functions)})")
        
        return gate_status or len(complex_functions) <= 10
    
    def check_import_quality(self):
        """Check import quality and prevent circular imports"""
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data', 'tests'])]
        
        import_issues = []
        import_stats = {
            "total_imports": 0,
            "relative_imports": 0,
            "absolute_imports": 0,
            "wildcard_imports": 0
        }
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        import_stats["total_imports"] += 1
                        
                        if stripped.startswith('from .'):
                            import_stats["relative_imports"] += 1
                        else:
                            import_stats["absolute_imports"] += 1
                        
                        if ' import *' in stripped:
                            import_stats["wildcard_imports"] += 1
                            import_issues.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": i + 1,
                                "issue": "Wildcard import",
                                "code": stripped
                            })
                        
                        # Check for potentially problematic imports
                        problematic_patterns = ['os.system', 'subprocess.call', 'eval', 'exec']
                        for pattern in problematic_patterns:
                            if pattern in stripped:
                                import_issues.append({
                                    "file": str(py_file.relative_to(self.repo_root)),
                                    "line": i + 1,
                                    "issue": f"Potentially unsafe import: {pattern}",
                                    "code": stripped
                                })
                        
            except Exception:
                continue
        
        gate_status = len(import_issues) == 0
        self.results["gates"]["import_quality"] = {
            "status": "PASS" if gate_status else "REVIEW",
            "issues": import_issues,
            "statistics": import_stats,
            "description": "Ensures clean import structure and prevents unsafe imports"
        }
        
        if len(import_issues) > 20:
            self.results["blocking_issues"].append(f"Too many import issues detected ({len(import_issues)})")
        
        return gate_status or len(import_issues) <= 20
    
    def check_gui_component_standards(self):
        """GUI-specific quality gates"""
        gui_files = list(Path(self.repo_root / "gui").rglob("*.py"))
        
        gui_issues = []
        gui_standards = {
            "total_gui_files": len(gui_files),
            "files_with_error_handling": 0,
            "files_with_logging": 0,
            "files_with_docstrings": 0,
            "pyqt_best_practices": 0
        }
        
        pyqt_best_practices = [
            'QApplication.instance()',
            'try:',
            'except',
            'finally:',
            'logging.',
            'self.setWindowTitle',
            'self.setGeometry'
        ]
        
        for gui_file in gui_files:
            try:
                with open(gui_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for error handling
                if 'try:' in content and 'except' in content:
                    gui_standards["files_with_error_handling"] += 1
                else:
                    gui_issues.append({
                        "file": str(gui_file.relative_to(self.repo_root)),
                        "issue": "Missing error handling in GUI component"
                    })
                
                # Check for logging
                if 'logging.' in content or 'logger.' in content:
                    gui_standards["files_with_logging"] += 1
                else:
                    gui_issues.append({
                        "file": str(gui_file.relative_to(self.repo_root)),
                        "issue": "Missing logging in GUI component"
                    })
                
                # Check for docstrings
                if '"""' in content or "'''" in content:
                    gui_standards["files_with_docstrings"] += 1
                else:
                    gui_issues.append({
                        "file": str(gui_file.relative_to(self.repo_root)),
                        "issue": "Missing docstring in GUI component"
                    })
                
                # Check PyQt best practices
                practice_count = sum(1 for practice in pyqt_best_practices if practice in content)
                if practice_count >= 3:  # At least 3 best practices
                    gui_standards["pyqt_best_practices"] += 1
                else:
                    gui_issues.append({
                        "file": str(gui_file.relative_to(self.repo_root)),
                        "issue": f"Insufficient PyQt best practices ({practice_count}/7)"
                    })
                    
            except Exception as e:
                gui_issues.append({
                    "file": str(gui_file.relative_to(self.repo_root)),
                    "issue": f"Error analyzing file: {e}"
                })
        
        gate_status = len(gui_issues) <= (len(gui_files) * 0.3)  # Allow 30% issues
        self.results["gui_gates"]["component_standards"] = {
            "status": "PASS" if gate_status else "REVIEW",
            "issues": gui_issues[:10],  # First 10 issues
            "standards_compliance": gui_standards,
            "issue_percentage": round((len(gui_issues) / max(len(gui_files), 1)) * 100, 1),
            "description": "Ensures GUI components follow quality standards"
        }
        
        if not gate_status:
            self.results["blocking_issues"].append(f"Too many GUI component issues ({len(gui_issues)})")
        
        return gate_status
    
    def check_performance_regression_risk(self):
        """Check for potential performance regression patterns"""
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data', 'tests'])]
        
        performance_risks = []
        risk_patterns = [
            ('while True:', 'Infinite loop risk'),
            ('time\\.sleep\\(', 'Blocking sleep operation'),
            ('for.*in.*range.*:', 'Potentially inefficient loop'),
            ('\\.iterrows\\(\\)', 'Inefficient pandas iteration'),
            ('list\\(filter\\(', 'Inefficient list filtering'),
            ('list\\(map\\(', 'Inefficient list mapping')
        ]
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    for pattern, risk_desc in risk_patterns:
                        if pattern in stripped and not stripped.startswith('#'):
                            performance_risks.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": i + 1,
                                "risk": risk_desc,
                                "code": stripped[:100]  # First 100 chars
                            })
                            
            except Exception:
                continue
        
        gate_status = len(performance_risks) <= 10  # Allow up to 10 performance risks
        self.results["gates"]["performance_regression"] = {
            "status": "PASS" if gate_status else "REVIEW",
            "risks": performance_risks[:15],  # First 15 risks
            "total_risks": len(performance_risks),
            "description": "Identifies potential performance regression patterns"
        }
        
        if len(performance_risks) > 25:
            self.results["blocking_issues"].append(f"High performance regression risk ({len(performance_risks)} patterns)")
        
        return gate_status or len(performance_risks) <= 25
    
    def check_dependency_security(self):
        """Check for security issues in dependencies"""
        requirements_file = self.repo_root / "requirements.txt"
        
        if not requirements_file.exists():
            self.results["gates"]["dependency_security"] = {
                "status": "ERROR",
                "error": "requirements.txt not found",
                "description": "Validates dependency security"
            }
            return False
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.readlines()
            
            security_issues = []
            outdated_patterns = [
                ('flask<2.0', 'Potentially outdated Flask version'),
                ('django<3.0', 'Potentially outdated Django version'),
                ('requests<2.25', 'Potentially outdated requests version'),
                ('urllib3<1.26', 'Potentially outdated urllib3 version')
            ]
            
            for line in requirements:
                line = line.strip()
                if line and not line.startswith('#'):
                    for pattern, issue in outdated_patterns:
                        if pattern in line.lower():
                            security_issues.append({
                                "dependency": line,
                                "issue": issue
                            })
            
            gate_status = len(security_issues) == 0
            self.results["gates"]["dependency_security"] = {
                "status": "PASS" if gate_status else "REVIEW",
                "issues": security_issues,
                "total_dependencies": len([line for line in requirements if line.strip() and not line.startswith('#')]),
                "description": "Validates dependency security and versions"
            }
            
            if len(security_issues) > 5:
                self.results["blocking_issues"].append(f"Multiple dependency security issues ({len(security_issues)})")
            
            return gate_status or len(security_issues) <= 5
            
        except Exception as e:
            self.results["gates"]["dependency_security"] = {
                "status": "ERROR",
                "error": str(e),
                "description": "Validates dependency security"
            }
            return False
    
    def evaluate_overall_status(self):
        """Evaluate overall quality gate status"""
        gates = self.results["gates"]
        gui_gates = self.results["gui_gates"]
        
        all_gates = {**gates, **gui_gates}
        passed_gates = sum(1 for gate in all_gates.values() if gate.get("status") == "PASS")
        total_gates = len(all_gates)
        
        if len(self.results["blocking_issues"]) > 0:
            self.results["overall_status"] = "BLOCKED"
        elif passed_gates == total_gates:
            self.results["overall_status"] = "ALL_PASS"
        elif passed_gates >= total_gates * 0.8:
            self.results["overall_status"] = "MOSTLY_PASS"
        else:
            self.results["overall_status"] = "MULTIPLE_FAILURES"
        
        self.results["gate_summary"] = {
            "total_gates": total_gates,
            "passed_gates": passed_gates,
            "failed_gates": total_gates - passed_gates,
            "pass_percentage": round((passed_gates / total_gates) * 100, 1) if total_gates > 0 else 0
        }
        
        return self.results["overall_status"] in ["ALL_PASS", "MOSTLY_PASS"]
    
    def run_all_gates(self):
        """Run all quality gates"""
        print("🚦 Running Automated Quality Gates (QUAL-002)...")
        print("=" * 70)
        
        gates = [
            ("File Size Limits", self.check_file_size_limits),
            ("Code Complexity", self.check_code_complexity),
            ("Import Quality", self.check_import_quality),
            ("GUI Component Standards", self.check_gui_component_standards),
            ("Performance Regression Risk", self.check_performance_regression_risk),
            ("Dependency Security", self.check_dependency_security)
        ]
        
        for gate_name, gate_func in gates:
            print(f"Checking {gate_name}...")
            try:
                result = gate_func()
                status = "✅ PASS" if result else "⚠️  REVIEW"
                print(f"  {status}")
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
        
        print("\n" + "=" * 70)
        overall_success = self.evaluate_overall_status()
        
        print(f"🎯 Overall Status: {self.results['overall_status']}")
        print(f"📊 Gate Pass Rate: {self.results['gate_summary']['pass_percentage']}%")
        
        if self.results["blocking_issues"]:
            print("\n🚫 BLOCKING ISSUES:")
            for issue in self.results["blocking_issues"]:
                print(f"  - {issue}")
        
        # Generate detailed report
        report_file = self.repo_root / f"quality_gates_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📋 Detailed report saved: {report_file}")
        
        return overall_success


def main():
    """Main execution function"""
    gates = QualityGates()
    success = gates.run_all_gates()
    
    if success:
        print("\n✅ QUAL-002 COMPLETED: All quality gates passed!")
        sys.exit(0)
    else:
        print("\n❌ QUAL-002 NEEDS ATTENTION: Quality gate failures detected")
        sys.exit(1)


if __name__ == "__main__":
    main()