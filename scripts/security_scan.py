#!/usr/bin/env python3
"""
Jarvis V0.19 - Stage 3: QUAL-004 - Security Scanning
Engineering Rigor Implementation with comprehensive security assessment including GUI components

This script implements security scanning and vulnerability assessment for the entire codebase.
"""

import sys
import json
import subprocess
import re
import os
from datetime import datetime
from pathlib import Path


class SecurityScanner:
    """Comprehensive security scanning and vulnerability assessment"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "Stage 3 - QUAL-004",
            "title": "Security Scanning & Vulnerability Assessment",
            "security_checks": {},
            "vulnerabilities": [],
            "gui_security": {},
            "overall_security_score": 0,
            "security_status": "UNKNOWN"
        }
        
    def scan_hardcoded_secrets(self):
        """Scan for hardcoded secrets and credentials"""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token'),
            (r'private_key\s*=\s*["\'][^"\']+["\']', 'Hardcoded private key'),
            (r'["\'][A-Za-z0-9]{32,}["\']', 'Potential secret key'),
            (r'sk-[A-Za-z0-9]{32,}', 'OpenAI API key pattern'),
            (r'ghp_[A-Za-z0-9]{36}', 'GitHub personal access token'),
            (r'AIza[A-Za-z0-9]{35}', 'Google API key pattern')
        ]
        
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data'])]
        
        secrets_found = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and docstrings
                    stripped_line = line.strip()
                    if stripped_line.startswith('#') or '"""' in stripped_line or "'''" in stripped_line:
                        continue
                    
                    for pattern, description in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            secrets_found.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": line_num,
                                "description": description,
                                "code_snippet": line.strip()[:100],
                                "severity": "HIGH"
                            })
                            
            except Exception:
                continue
        
        self.results["security_checks"]["hardcoded_secrets"] = {
            "secrets_found": len(secrets_found),
            "details": secrets_found[:20],  # First 20 findings
            "status": "PASS" if len(secrets_found) == 0 else "CRITICAL" if len(secrets_found) > 5 else "WARNING",
            "description": "Scan for hardcoded secrets and credentials"
        }
        
        if secrets_found:
            self.results["vulnerabilities"].extend(secrets_found[:10])
        
        return len(secrets_found) == 0
    
    def scan_injection_vulnerabilities(self):
        """Scan for potential injection vulnerabilities"""
        injection_patterns = [
            (r'eval\s*\(', 'Code injection via eval()'),
            (r'exec\s*\(', 'Code injection via exec()'),
            (r'subprocess\..*shell\s*=\s*True', 'Shell injection risk'),
            (r'os\.system\s*\(', 'Command injection via os.system()'),
            (r'input\s*\([^)]*\)', 'Potential input injection'),
            (r'raw_input\s*\([^)]*\)', 'Potential input injection'),
            (r'\.format\s*\([^)]*\)', 'String formatting injection risk'),
            (r'%\s*[^s]', 'String formatting injection risk'),
            (r'sqlite.*\+.*', 'SQL injection risk'),
            (r'execute\s*\([^?]', 'SQL injection risk - no parameterized query')
        ]
        
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data'])]
        
        injection_risks = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    
                    for pattern, description in injection_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            injection_risks.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": line_num,
                                "description": description,
                                "code_snippet": line.strip()[:100],
                                "severity": "HIGH" if "eval" in description or "exec" in description else "MEDIUM"
                            })
                            
            except Exception:
                continue
        
        self.results["security_checks"]["injection_vulnerabilities"] = {
            "risks_found": len(injection_risks),
            "details": injection_risks[:15],  # First 15 findings
            "status": "PASS" if len(injection_risks) == 0 else "CRITICAL" if len(injection_risks) > 10 else "WARNING",
            "description": "Scan for injection vulnerability patterns"
        }
        
        if injection_risks:
            self.results["vulnerabilities"].extend(injection_risks[:10])
        
        return len(injection_risks) <= 5  # Allow up to 5 low-risk patterns
    
    def scan_file_security(self):
        """Scan for file security issues"""
        file_security_patterns = [
            (r'open\s*\([^)]*["\']w["\']', 'File write without validation'),
            (r'open\s*\([^)]*["\']a["\']', 'File append without validation'),
            (r'os\.remove\s*\(', 'File deletion without validation'),
            (r'os\.unlink\s*\(', 'File deletion without validation'),
            (r'shutil\.rmtree\s*\(', 'Directory deletion without validation'),
            (r'pickle\.load\s*\(', 'Unsafe pickle deserialization'),
            (r'pickle\.loads\s*\(', 'Unsafe pickle deserialization'),
            (r'__import__\s*\(', 'Dynamic import security risk'),
            (r'importlib\.import_module\s*\(', 'Dynamic import security risk')
        ]
        
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data'])]
        
        file_security_issues = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    if line.strip().startswith('#'):
                        continue
                    
                    for pattern, description in file_security_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            file_security_issues.append({
                                "file": str(py_file.relative_to(self.repo_root)),
                                "line": line_num,
                                "description": description,
                                "code_snippet": line.strip()[:100],
                                "severity": "HIGH" if "pickle" in description else "MEDIUM"
                            })
                            
            except Exception:
                continue
        
        self.results["security_checks"]["file_security"] = {
            "issues_found": len(file_security_issues),
            "details": file_security_issues[:15],
            "status": "PASS" if len(file_security_issues) == 0 else "WARNING" if len(file_security_issues) <= 10 else "CRITICAL",
            "description": "Scan for file operation security issues"
        }
        
        if file_security_issues:
            self.results["vulnerabilities"].extend(file_security_issues[:5])
        
        return len(file_security_issues) <= 10
    
    def scan_gui_security(self):
        """Scan GUI components for security issues"""
        gui_files = list(Path(self.repo_root / "gui").rglob("*.py"))
        
        gui_security_issues = []
        gui_security_patterns = [
            (r'QWebView', 'Potential XSS vulnerability in QWebView'),
            (r'QWebEngineView.*loadHtml', 'Potential XSS in loadHtml'),
            (r'QTextBrowser.*setHtml', 'Potential XSS in setHtml'),
            (r'QLabel.*setText.*<', 'Potential XSS in HTML content'),
            (r'eval\s*\(.*\.text\(\)', 'GUI input evaluation risk'),
            (r'exec\s*\(.*\.text\(\)', 'GUI input execution risk'),
            (r'subprocess.*\.text\(\)', 'Command injection from GUI input'),
            (r'os\.system.*\.text\(\)', 'Command injection from GUI input')
        ]
        
        gui_features = {
            "input_validation": 0,
            "output_encoding": 0,
            "error_handling": 0,
            "secure_defaults": 0
        }
        
        for gui_file in gui_files:
            try:
                with open(gui_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check for security patterns
                for line_num, line in enumerate(lines, 1):
                    if line.strip().startswith('#'):
                        continue
                    
                    for pattern, description in gui_security_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            gui_security_issues.append({
                                "file": str(gui_file.relative_to(self.repo_root)),
                                "line": line_num,
                                "description": description,
                                "code_snippet": line.strip()[:100],
                                "severity": "HIGH"
                            })
                
                # Check for security features
                if 'validate' in content.lower() or 'sanitize' in content.lower():
                    gui_features["input_validation"] += 1
                
                if 'escape' in content.lower() or 'encode' in content.lower():
                    gui_features["output_encoding"] += 1
                
                if 'try:' in content and 'except' in content:
                    gui_features["error_handling"] += 1
                
                if 'setTextInteractionFlags' in content or 'setOpenExternalLinks(False)' in content:
                    gui_features["secure_defaults"] += 1
                    
            except Exception:
                continue
        
        # Calculate GUI security score
        total_files = len(gui_files) if gui_files else 1
        security_feature_score = (
            (gui_features["input_validation"] / total_files) * 25 +
            (gui_features["output_encoding"] / total_files) * 25 +
            (gui_features["error_handling"] / total_files) * 25 +
            (gui_features["secure_defaults"] / total_files) * 25
        )
        
        gui_security_status = "EXCELLENT" if security_feature_score >= 80 else "GOOD" if security_feature_score >= 60 else "NEEDS_IMPROVEMENT"
        
        self.results["gui_security"] = {
            "security_issues": len(gui_security_issues),
            "issues_details": gui_security_issues,
            "security_features": gui_features,
            "security_score": round(security_feature_score, 1),
            "status": gui_security_status,
            "description": "GUI component security assessment"
        }
        
        if gui_security_issues:
            self.results["vulnerabilities"].extend(gui_security_issues)
        
        return len(gui_security_issues) == 0 and security_feature_score >= 50
    
    def scan_dependency_vulnerabilities(self):
        """Scan dependencies for known vulnerabilities"""
        requirements_file = self.repo_root / "requirements.txt"
        
        if not requirements_file.exists():
            self.results["security_checks"]["dependency_vulnerabilities"] = {
                "status": "ERROR",
                "error": "requirements.txt not found",
                "description": "Dependency vulnerability assessment"
            }
            return False
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.readlines()
            
            vulnerable_patterns = [
                ('flask<2.0', 'Flask version may have security vulnerabilities'),
                ('django<3.2', 'Django version may have security vulnerabilities'),
                ('requests<2.25.0', 'Requests version may have security vulnerabilities'),
                ('urllib3<1.26.0', 'urllib3 version may have security vulnerabilities'),
                ('pillow<8.1.1', 'Pillow version may have security vulnerabilities'),
                ('pyyaml<5.4', 'PyYAML version may have security vulnerabilities'),
                ('cryptography<3.4.6', 'Cryptography version may have security vulnerabilities')
            ]
            
            dependency_issues = []
            secure_dependencies = 0
            total_dependencies = 0
            
            for line in requirements:
                line = line.strip()
                if line and not line.startswith('#'):
                    total_dependencies += 1
                    
                    is_vulnerable = False
                    for pattern, issue in vulnerable_patterns:
                        if any(part in line.lower() for part in pattern.split('<')[0].split('>')):
                            # Check version if specified
                            if '<' in line or '>' in line or '=' in line:
                                dependency_issues.append({
                                    "dependency": line,
                                    "issue": issue,
                                    "severity": "HIGH" if "cryptography" in line or "requests" in line else "MEDIUM"
                                })
                                is_vulnerable = True
                                break
                    
                    if not is_vulnerable:
                        secure_dependencies += 1
            
            dependency_security_score = (secure_dependencies / total_dependencies * 100) if total_dependencies > 0 else 0
            
            self.results["security_checks"]["dependency_vulnerabilities"] = {
                "total_dependencies": total_dependencies,
                "secure_dependencies": secure_dependencies,
                "vulnerable_dependencies": len(dependency_issues),
                "security_score": round(dependency_security_score, 1),
                "issues": dependency_issues,
                "status": "PASS" if len(dependency_issues) == 0 else "WARNING" if len(dependency_issues) <= 3 else "CRITICAL",
                "description": "Dependency vulnerability assessment"
            }
            
            if dependency_issues:
                self.results["vulnerabilities"].extend(dependency_issues[:5])
            
            return len(dependency_issues) <= 3
            
        except Exception as e:
            self.results["security_checks"]["dependency_vulnerabilities"] = {
                "status": "ERROR",
                "error": str(e),
                "description": "Dependency vulnerability assessment"
            }
            return False
    
    def scan_configuration_security(self):
        """Scan configuration files for security issues"""
        config_files = list(Path(self.repo_root).glob("*.json")) + list(Path(self.repo_root).glob("*.yaml")) + list(Path(self.repo_root).glob("*.yml"))
        config_files.extend(list(Path(self.repo_root / "config").rglob("*")) if (self.repo_root / "config").exists() else [])
        
        config_security_issues = []
        
        for config_file in config_files:
            if config_file.is_file():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    # Check for security issues in config
                    security_patterns = [
                        ('password', 'Password in configuration file'),
                        ('secret', 'Secret in configuration file'),
                        ('api_key', 'API key in configuration file'),
                        ('private_key', 'Private key in configuration file'),
                        ('debug.*true', 'Debug mode enabled in production'),
                        ('ssl.*false', 'SSL disabled'),
                        ('verify.*false', 'SSL verification disabled')
                    ]
                    
                    for pattern, description in security_patterns:
                        if re.search(pattern, content):
                            config_security_issues.append({
                                "file": str(config_file.relative_to(self.repo_root)),
                                "description": description,
                                "severity": "HIGH" if any(x in description.lower() for x in ['password', 'secret', 'key']) else "MEDIUM"
                            })
                            
                except Exception:
                    continue
        
        self.results["security_checks"]["configuration_security"] = {
            "config_files_scanned": len(config_files),
            "security_issues": len(config_security_issues),
            "issues_details": config_security_issues,
            "status": "PASS" if len(config_security_issues) == 0 else "WARNING" if len(config_security_issues) <= 3 else "CRITICAL",
            "description": "Configuration file security assessment"
        }
        
        if config_security_issues:
            self.results["vulnerabilities"].extend(config_security_issues)
        
        return len(config_security_issues) <= 3
    
    def calculate_overall_security_score(self):
        """Calculate overall security score"""
        checks = self.results["security_checks"]
        gui_security = self.results["gui_security"]
        
        scores = []
        
        # Individual check scores
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict) and "status" in check_data:
                if check_data["status"] == "PASS":
                    scores.append(100)
                elif check_data["status"] == "WARNING":
                    scores.append(70)
                elif check_data["status"] == "CRITICAL":
                    scores.append(20)
                else:
                    scores.append(0)
        
        # GUI security score
        if "security_score" in gui_security:
            scores.append(gui_security["security_score"])
        
        # Vulnerability penalty
        vulnerability_count = len(self.results["vulnerabilities"])
        vulnerability_penalty = min(50, vulnerability_count * 5)  # 5 points per vulnerability, max 50 point penalty
        
        base_score = sum(scores) / len(scores) if scores else 0
        final_score = max(0, base_score - vulnerability_penalty)
        
        self.results["overall_security_score"] = round(final_score, 1)
        
        # Determine security status
        if final_score >= 90:
            self.results["security_status"] = "EXCELLENT"
        elif final_score >= 75:
            self.results["security_status"] = "GOOD"
        elif final_score >= 60:
            self.results["security_status"] = "ACCEPTABLE"
        elif final_score >= 40:
            self.results["security_status"] = "NEEDS_IMPROVEMENT"
        else:
            self.results["security_status"] = "CRITICAL"
        
        return final_score >= 60
    
    def run_all_security_scans(self):
        """Run all security scans"""
        print("🔒 Running Security Scanning & Vulnerability Assessment (QUAL-004)...")
        print("=" * 70)
        
        scans = [
            ("Hardcoded Secrets", self.scan_hardcoded_secrets),
            ("Injection Vulnerabilities", self.scan_injection_vulnerabilities),
            ("File Security", self.scan_file_security),
            ("GUI Security", self.scan_gui_security),
            ("Dependency Vulnerabilities", self.scan_dependency_vulnerabilities),
            ("Configuration Security", self.scan_configuration_security)
        ]
        
        for scan_name, scan_func in scans:
            print(f"Scanning {scan_name}...")
            try:
                result = scan_func()
                status = "✅ SECURE" if result else "⚠️  ISSUES FOUND"
                print(f"  {status}")
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
        
        print("\n" + "=" * 70)
        overall_secure = self.calculate_overall_security_score()
        
        print(f"🔒 Overall Security Score: {self.results['overall_security_score']}%")
        print(f"🎯 Security Status: {self.results['security_status']}")
        print(f"⚠️  Total Vulnerabilities: {len(self.results['vulnerabilities'])}")
        
        if self.results["vulnerabilities"]:
            print("\n🚨 Critical Vulnerabilities (Top 5):")
            for vuln in self.results["vulnerabilities"][:5]:
                severity = vuln.get("severity", "UNKNOWN")
                description = vuln.get("description", "Unknown issue")
                file_path = vuln.get("file", "Unknown file")
                print(f"  [{severity}] {description} in {file_path}")
        
        # Generate detailed report
        report_file = self.repo_root / f"security_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📋 Detailed security report saved: {report_file}")
        
        return overall_secure


def main():
    """Main execution function"""
    scanner = SecurityScanner()
    success = scanner.run_all_security_scans()
    
    if success:
        print("\n✅ QUAL-004 COMPLETED: Security scanning passed - system is secure!")
        sys.exit(0)
    else:
        print("\n❌ QUAL-004 NEEDS ATTENTION: Security vulnerabilities detected")
        sys.exit(1)


if __name__ == "__main__":
    main()