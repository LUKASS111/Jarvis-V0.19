#!/usr/bin/env python3
"""
Jarvis V0.19 - Stage 3: QUAL-006 - Engineering Metrics Dashboard
Engineering Rigor Implementation with comprehensive quality metrics and GUI performance KPIs

This script establishes engineering metrics dashboard with GUI performance KPIs.
"""

import sys
import json
import time
import os
import psutil
from datetime import datetime
from pathlib import Path


class EngineeringMetrics:
    """Engineering metrics dashboard with comprehensive quality metrics"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "Stage 3 - QUAL-006",
            "title": "Engineering Metrics Dashboard",
            "code_metrics": {},
            "quality_metrics": {},
            "performance_metrics": {},
            "gui_metrics": {},
            "system_metrics": {},
            "overall_engineering_score": 0,
            "dashboard_status": "UNKNOWN"
        }
        
    def collect_code_metrics(self):
        """Collect comprehensive code metrics"""
        python_files = list(Path(self.repo_root).rglob("*.py"))
        python_files = [f for f in python_files if not any(exclude in str(f) for exclude in ['.git', '__pycache__', 'archive', 'data'])]
        
        code_stats = {
            "total_files": len(python_files),
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "total_imports": 0,
            "total_comments": 0,
            "total_docstrings": 0,
            "average_file_size": 0,
            "largest_file": {"file": "", "lines": 0},
            "complexity_distribution": {"simple": 0, "moderate": 0, "complex": 0},
            "file_types": {"gui": 0, "core": 0, "scripts": 0, "tests": 0}
        }
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                file_lines = len(lines)
                code_stats["total_lines"] += file_lines
                
                # Track largest file
                if file_lines > code_stats["largest_file"]["lines"]:
                    code_stats["largest_file"] = {
                        "file": str(py_file.relative_to(self.repo_root)),
                        "lines": file_lines
                    }
                
                # Categorize file type
                file_path_str = str(py_file)
                if "gui" in file_path_str:
                    code_stats["file_types"]["gui"] += 1
                elif "script" in file_path_str:
                    code_stats["file_types"]["scripts"] += 1
                elif "test" in file_path_str:
                    code_stats["file_types"]["tests"] += 1
                else:
                    code_stats["file_types"]["core"] += 1
                
                # Analyze content
                function_count = 0
                class_count = 0
                import_count = 0
                comment_count = 0
                docstring_count = 0
                
                in_docstring = False
                docstring_delimiter = None
                
                for line in lines:
                    stripped = line.strip()
                    
                    # Count functions and classes
                    if stripped.startswith('def '):
                        function_count += 1
                    elif stripped.startswith('class '):
                        class_count += 1
                    elif stripped.startswith('import ') or stripped.startswith('from '):
                        import_count += 1
                    elif stripped.startswith('#'):
                        comment_count += 1
                    
                    # Count docstrings
                    if not in_docstring:
                        if stripped.startswith('"""') or stripped.startswith("'''"):
                            docstring_count += 1
                            docstring_delimiter = stripped[:3]
                            if not (stripped.endswith('"""') and len(stripped) > 6) and not (stripped.endswith("'''") and len(stripped) > 6):
                                in_docstring = True
                    else:
                        if docstring_delimiter in stripped:
                            in_docstring = False
                
                # Update totals
                code_stats["total_functions"] += function_count
                code_stats["total_classes"] += class_count
                code_stats["total_imports"] += import_count
                code_stats["total_comments"] += comment_count
                code_stats["total_docstrings"] += docstring_count
                
                # Determine complexity
                if file_lines < 100:
                    code_stats["complexity_distribution"]["simple"] += 1
                elif file_lines < 300:
                    code_stats["complexity_distribution"]["moderate"] += 1
                else:
                    code_stats["complexity_distribution"]["complex"] += 1
                    
            except Exception:
                continue
        
        # Calculate averages
        if code_stats["total_files"] > 0:
            code_stats["average_file_size"] = round(code_stats["total_lines"] / code_stats["total_files"], 1)
            code_stats["functions_per_file"] = round(code_stats["total_functions"] / code_stats["total_files"], 1)
            code_stats["classes_per_file"] = round(code_stats["total_classes"] / code_stats["total_files"], 1)
            code_stats["comment_ratio"] = round((code_stats["total_comments"] / code_stats["total_lines"]) * 100, 1)
            code_stats["docstring_coverage"] = round((code_stats["total_docstrings"] / max(code_stats["total_functions"], 1)) * 100, 1)
        
        self.results["code_metrics"] = code_stats
        return True
    
    def collect_quality_metrics(self):
        """Collect code quality metrics"""
        # Run previous quality checks to get metrics
        quality_stats = {
            "code_quality_score": 0,
            "test_coverage": 0,
            "linting_issues": 0,
            "security_score": 0,
            "performance_score": 0,
            "maintainability_index": 0
        }
        
        try:
            # Check if quality reports exist
            reports_dir = self.repo_root
            
            # Look for recent quality reports
            quality_files = list(reports_dir.glob("*quality*report*.json"))
            security_files = list(reports_dir.glob("*security*report*.json"))
            performance_files = list(reports_dir.glob("*performance*report*.json"))
            
            # Extract metrics from latest reports
            if quality_files:
                latest_quality = max(quality_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(latest_quality, 'r') as f:
                        quality_data = json.load(f)
                        quality_stats["code_quality_score"] = quality_data.get("overall_score", 0)
                except:
                    pass
            
            if security_files:
                latest_security = max(security_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(latest_security, 'r') as f:
                        security_data = json.load(f)
                        quality_stats["security_score"] = security_data.get("overall_security_score", 0)
                except:
                    pass
            
            if performance_files:
                latest_performance = max(performance_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(latest_performance, 'r') as f:
                        perf_data = json.load(f)
                        quality_stats["performance_score"] = perf_data.get("performance_summary", {}).get("performance_score", 0)
                except:
                    pass
            
            # Calculate maintainability index
            code_metrics = self.results.get("code_metrics", {})
            if code_metrics:
                # Simple maintainability calculation based on code metrics
                comment_ratio = code_metrics.get("comment_ratio", 0)
                docstring_coverage = code_metrics.get("docstring_coverage", 0)
                avg_file_size = code_metrics.get("average_file_size", 0)
                
                # Normalize metrics (higher is better, except file size)
                size_score = max(0, 100 - (avg_file_size / 10))  # Penalize large files
                maintainability = (comment_ratio + docstring_coverage + size_score) / 3
                quality_stats["maintainability_index"] = round(maintainability, 1)
            
        except Exception:
            pass
        
        self.results["quality_metrics"] = quality_stats
        return True
    
    def collect_performance_metrics(self):
        """Collect system and application performance metrics"""
        # System performance
        system_perf = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('.').percent,
            "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "cpu_count": psutil.cpu_count(),
            "load_average": getattr(psutil, 'getloadavg', lambda: [0, 0, 0])(),
        }
        
        # Application performance simulation
        app_perf = {
            "startup_time_estimate": 0,
            "import_time_estimate": 0,
            "response_time_estimate": 0
        }
        
        try:
            # Estimate startup time by importing main module
            start_time = time.time()
            try:
                import jarvis.main
                app_perf["startup_time_estimate"] = round((time.time() - start_time) * 1000, 2)
            except:
                app_perf["startup_time_estimate"] = "N/A"
            
            # Estimate import time for critical modules
            critical_modules = ['jarvis.database.manager', 'jarvis.api.api_manager', 'gui.enhanced.comprehensive_dashboard']
            import_times = []
            
            for module in critical_modules:
                try:
                    start_time = time.time()
                    __import__(module)
                    import_time = (time.time() - start_time) * 1000
                    import_times.append(import_time)
                except:
                    continue
            
            if import_times:
                app_perf["import_time_estimate"] = round(sum(import_times) / len(import_times), 2)
            
            # Estimate response time (simple file I/O test)
            start_time = time.time()
            test_file = self.repo_root / "temp_perf_test.txt"
            with open(test_file, 'w') as f:
                f.write("performance test")
            with open(test_file, 'r') as f:
                content = f.read()
            test_file.unlink()
            app_perf["response_time_estimate"] = round((time.time() - start_time) * 1000, 2)
            
        except Exception as e:
            app_perf["error"] = str(e)
        
        self.results["performance_metrics"] = {
            "system_performance": system_perf,
            "application_performance": app_perf
        }
        return True
    
    def collect_gui_metrics(self):
        """Collect GUI-specific metrics and KPIs"""
        gui_files = list(Path(self.repo_root / "gui").rglob("*.py"))
        
        gui_stats = {
            "total_gui_files": len(gui_files),
            "gui_lines_of_code": 0,
            "gui_components": 0,
            "gui_complexity": {"simple": 0, "moderate": 0, "complex": 0},
            "pyqt_usage": {"widgets": 0, "layouts": 0, "signals": 0, "slots": 0},
            "gui_best_practices": {
                "error_handling": 0,
                "responsive_design": 0,
                "accessibility": 0,
                "performance_optimization": 0
            },
            "user_interface_coverage": 0
        }
        
        pyqt_patterns = [
            (r'Q\w+Widget', 'widgets'),
            (r'Q\w+Layout', 'layouts'),
            (r'\.connect\(', 'signals'),
            (r'@pyqtSlot', 'slots')
        ]
        
        best_practice_patterns = [
            (r'try:', 'error_handling'),
            (r'setMinimum\w+', 'responsive_design'),
            (r'setAccessible\w+', 'accessibility'),
            (r'cache|lazy|optimize', 'performance_optimization')
        ]
        
        for gui_file in gui_files:
            try:
                with open(gui_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                gui_stats["gui_lines_of_code"] += len(lines)
                
                # Count GUI components (classes)
                class_count = content.count('class ')
                gui_stats["gui_components"] += class_count
                
                # Determine complexity
                if len(lines) < 100:
                    gui_stats["gui_complexity"]["simple"] += 1
                elif len(lines) < 300:
                    gui_stats["gui_complexity"]["moderate"] += 1
                else:
                    gui_stats["gui_complexity"]["complex"] += 1
                
                # Check PyQt usage patterns
                import re
                for pattern, category in pyqt_patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    gui_stats["pyqt_usage"][category] += matches
                
                # Check best practices
                for pattern, category in best_practice_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        gui_stats["gui_best_practices"][category] += 1
                        
            except Exception:
                continue
        
        # Calculate GUI metrics
        if gui_stats["total_gui_files"] > 0:
            gui_stats["average_gui_file_size"] = round(gui_stats["gui_lines_of_code"] / gui_stats["total_gui_files"], 1)
            gui_stats["components_per_file"] = round(gui_stats["gui_components"] / gui_stats["total_gui_files"], 1)
            
            # GUI best practices score
            total_best_practices = sum(gui_stats["gui_best_practices"].values())
            max_possible = gui_stats["total_gui_files"] * 4  # 4 categories
            gui_stats["best_practices_score"] = round((total_best_practices / max_possible) * 100, 1) if max_possible > 0 else 0
            
            # Estimate user interface coverage (simplified)
            total_widgets = gui_stats["pyqt_usage"]["widgets"]
            estimated_functions = self.results.get("code_metrics", {}).get("total_functions", 1)
            gui_stats["user_interface_coverage"] = round(min(100, (total_widgets / estimated_functions) * 100), 1)
        
        self.results["gui_metrics"] = gui_stats
        return True
    
    def collect_system_metrics(self):
        """Collect system-wide metrics"""
        # Repository metrics
        repo_stats = {
            "repository_size_mb": 0,
            "file_count": 0,
            "directory_count": 0,
            "git_metrics": {"commits": 0, "branches": 0, "contributors": 0}
        }
        
        try:
            # Calculate repository size
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for item in self.repo_root.rglob("*"):
                if item.is_file() and '.git' not in str(item):
                    total_size += item.stat().st_size
                    file_count += 1
                elif item.is_dir() and '.git' not in str(item):
                    dir_count += 1
            
            repo_stats["repository_size_mb"] = round(total_size / (1024 * 1024), 2)
            repo_stats["file_count"] = file_count
            repo_stats["directory_count"] = dir_count
            
            # Git metrics (if available)
            try:
                import subprocess
                
                # Count commits
                result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                      capture_output=True, text=True, cwd=self.repo_root)
                if result.returncode == 0:
                    repo_stats["git_metrics"]["commits"] = int(result.stdout.strip())
                
                # Count branches
                result = subprocess.run(['git', 'branch', '-a'], 
                                      capture_output=True, text=True, cwd=self.repo_root)
                if result.returncode == 0:
                    branches = [line.strip() for line in result.stdout.split('\n') if line.strip() and not line.startswith('*')]
                    repo_stats["git_metrics"]["branches"] = len(branches)
                
            except:
                pass
            
        except Exception as e:
            repo_stats["error"] = str(e)
        
        # Development metrics
        dev_stats = {
            "test_files": len(list(self.repo_root.rglob("*test*.py"))),
            "config_files": len(list(self.repo_root.rglob("*.json")) + list(self.repo_root.rglob("*.yaml")) + list(self.repo_root.rglob("*.yml"))),
            "documentation_files": len(list(self.repo_root.rglob("*.md")) + list(self.repo_root.rglob("*.rst")) + list(self.repo_root.rglob("*.txt"))),
            "script_files": len(list(self.repo_root.rglob("script*.py")) + list(self.repo_root.rglob("**/scripts/*.py")))
        }
        
        self.results["system_metrics"] = {
            "repository": repo_stats,
            "development": dev_stats
        }
        return True
    
    def calculate_engineering_score(self):
        """Calculate overall engineering excellence score"""
        metrics = self.results
        
        # Individual metric scores
        scores = {
            "code_quality": 0,
            "performance": 0,
            "security": 0,
            "gui_quality": 0,
            "maintainability": 0,
            "test_coverage": 0
        }
        
        # Code quality score
        code_metrics = metrics.get("code_metrics", {})
        if code_metrics:
            # Based on comment ratio, docstring coverage, and complexity distribution
            comment_ratio = code_metrics.get("comment_ratio", 0)
            docstring_coverage = code_metrics.get("docstring_coverage", 0)
            complexity = code_metrics.get("complexity_distribution", {})
            simple_ratio = complexity.get("simple", 0) / max(sum(complexity.values()), 1) * 100
            
            scores["code_quality"] = (comment_ratio + docstring_coverage + simple_ratio) / 3
        
        # Performance score
        quality_metrics = metrics.get("quality_metrics", {})
        scores["performance"] = quality_metrics.get("performance_score", 0)
        scores["security"] = quality_metrics.get("security_score", 0)
        scores["maintainability"] = quality_metrics.get("maintainability_index", 0)
        
        # GUI quality score
        gui_metrics = metrics.get("gui_metrics", {})
        if gui_metrics:
            best_practices_score = gui_metrics.get("best_practices_score", 0)
            ui_coverage = gui_metrics.get("user_interface_coverage", 0)
            scores["gui_quality"] = (best_practices_score + ui_coverage) / 2
        
        # Test coverage (estimated)
        system_metrics = metrics.get("system_metrics", {})
        if system_metrics:
            test_files = system_metrics.get("development", {}).get("test_files", 0)
            total_files = code_metrics.get("total_files", 1)
            scores["test_coverage"] = min(100, (test_files / total_files) * 100)
        
        # Calculate weighted overall score
        weights = {
            "code_quality": 0.20,
            "performance": 0.15,
            "security": 0.20,
            "gui_quality": 0.20,
            "maintainability": 0.15,
            "test_coverage": 0.10
        }
        
        overall_score = sum(scores[metric] * weights[metric] for metric in scores)
        
        self.results["overall_engineering_score"] = round(overall_score, 1)
        self.results["individual_scores"] = {k: round(v, 1) for k, v in scores.items()}
        
        # Determine dashboard status
        if overall_score >= 90:
            self.results["dashboard_status"] = "EXCELLENT"
        elif overall_score >= 75:
            self.results["dashboard_status"] = "GOOD"
        elif overall_score >= 60:
            self.results["dashboard_status"] = "ACCEPTABLE"
        else:
            self.results["dashboard_status"] = "NEEDS_IMPROVEMENT"
        
        return overall_score >= 60
    
    def generate_metrics_dashboard(self):
        """Generate comprehensive engineering metrics dashboard"""
        dashboard_file = self.repo_root / "ENGINEERING_METRICS.md"
        
        dashboard_content = f"""# Engineering Metrics Dashboard
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 Overall Engineering Excellence Score: {self.results['overall_engineering_score']}%
**Status: {self.results['dashboard_status']}**

---

## 🔢 Code Metrics

| Metric | Value |
|--------|-------|
| Total Files | {self.results['code_metrics'].get('total_files', 0)} |
| Total Lines of Code | {self.results['code_metrics'].get('total_lines', 0):,} |
| Total Functions | {self.results['code_metrics'].get('total_functions', 0)} |
| Total Classes | {self.results['code_metrics'].get('total_classes', 0)} |
| Average File Size | {self.results['code_metrics'].get('average_file_size', 0)} lines |
| Comment Ratio | {self.results['code_metrics'].get('comment_ratio', 0)}% |
| Docstring Coverage | {self.results['code_metrics'].get('docstring_coverage', 0)}% |

### File Type Distribution
- **GUI Files**: {self.results['code_metrics'].get('file_types', {}).get('gui', 0)}
- **Core Files**: {self.results['code_metrics'].get('file_types', {}).get('core', 0)}
- **Script Files**: {self.results['code_metrics'].get('file_types', {}).get('scripts', 0)}
- **Test Files**: {self.results['code_metrics'].get('file_types', {}).get('tests', 0)}

### Complexity Distribution
- **Simple (<100 lines)**: {self.results['code_metrics'].get('complexity_distribution', {}).get('simple', 0)} files
- **Moderate (100-300 lines)**: {self.results['code_metrics'].get('complexity_distribution', {}).get('moderate', 0)} files
- **Complex (>300 lines)**: {self.results['code_metrics'].get('complexity_distribution', {}).get('complex', 0)} files

---

## 🎯 Quality Metrics

| Category | Score |
|----------|-------|
| Code Quality | {self.results.get('individual_scores', {}).get('code_quality', 0)}% |
| Performance | {self.results.get('individual_scores', {}).get('performance', 0)}% |
| Security | {self.results.get('individual_scores', {}).get('security', 0)}% |
| GUI Quality | {self.results.get('individual_scores', {}).get('gui_quality', 0)}% |
| Maintainability | {self.results.get('individual_scores', {}).get('maintainability', 0)}% |
| Test Coverage | {self.results.get('individual_scores', {}).get('test_coverage', 0)}% |

---

## 🖥️ GUI Metrics & KPIs

| Metric | Value |
|--------|-------|
| GUI Files | {self.results['gui_metrics'].get('total_gui_files', 0)} |
| GUI Lines of Code | {self.results['gui_metrics'].get('gui_lines_of_code', 0):,} |
| GUI Components | {self.results['gui_metrics'].get('gui_components', 0)} |
| Average GUI File Size | {self.results['gui_metrics'].get('average_gui_file_size', 0)} lines |
| Best Practices Score | {self.results['gui_metrics'].get('best_practices_score', 0)}% |
| UI Coverage Estimate | {self.results['gui_metrics'].get('user_interface_coverage', 0)}% |

### PyQt Usage Statistics
- **Widgets**: {self.results['gui_metrics'].get('pyqt_usage', {}).get('widgets', 0)}
- **Layouts**: {self.results['gui_metrics'].get('pyqt_usage', {}).get('layouts', 0)}
- **Signals**: {self.results['gui_metrics'].get('pyqt_usage', {}).get('signals', 0)}
- **Slots**: {self.results['gui_metrics'].get('pyqt_usage', {}).get('slots', 0)}

### GUI Best Practices
- **Error Handling**: {self.results['gui_metrics'].get('gui_best_practices', {}).get('error_handling', 0)} files
- **Responsive Design**: {self.results['gui_metrics'].get('gui_best_practices', {}).get('responsive_design', 0)} files
- **Accessibility**: {self.results['gui_metrics'].get('gui_best_practices', {}).get('accessibility', 0)} files
- **Performance Optimization**: {self.results['gui_metrics'].get('gui_best_practices', {}).get('performance_optimization', 0)} files

---

## ⚡ Performance Metrics

### System Performance
- **CPU Usage**: {self.results['performance_metrics'].get('system_performance', {}).get('cpu_usage', 0)}%
- **Memory Usage**: {self.results['performance_metrics'].get('system_performance', {}).get('memory_usage', 0)}%
- **Available Memory**: {self.results['performance_metrics'].get('system_performance', {}).get('available_memory_gb', 0)} GB
- **CPU Cores**: {self.results['performance_metrics'].get('system_performance', {}).get('cpu_count', 0)}

### Application Performance
- **Startup Time**: {self.results['performance_metrics'].get('application_performance', {}).get('startup_time_estimate', 'N/A')} ms
- **Import Time**: {self.results['performance_metrics'].get('application_performance', {}).get('import_time_estimate', 'N/A')} ms
- **Response Time**: {self.results['performance_metrics'].get('application_performance', {}).get('response_time_estimate', 'N/A')} ms

---

## 🗂️ System Metrics

### Repository Statistics
- **Repository Size**: {self.results['system_metrics'].get('repository', {}).get('repository_size_mb', 0)} MB
- **Total Files**: {self.results['system_metrics'].get('repository', {}).get('file_count', 0):,}
- **Directories**: {self.results['system_metrics'].get('repository', {}).get('directory_count', 0)}

### Development Assets
- **Test Files**: {self.results['system_metrics'].get('development', {}).get('test_files', 0)}
- **Configuration Files**: {self.results['system_metrics'].get('development', {}).get('config_files', 0)}
- **Documentation Files**: {self.results['system_metrics'].get('development', {}).get('documentation_files', 0)}
- **Script Files**: {self.results['system_metrics'].get('development', {}).get('script_files', 0)}

---

## 📈 Trends & Recommendations

### Current Strengths
"""

        # Add strengths based on scores
        individual_scores = self.results.get('individual_scores', {})
        for metric, score in individual_scores.items():
            if score >= 80:
                dashboard_content += f"- ✅ **{metric.replace('_', ' ').title()}**: Excellent ({score}%)\n"

        dashboard_content += "\n### Areas for Improvement\n"
        
        # Add improvement areas
        for metric, score in individual_scores.items():
            if score < 60:
                dashboard_content += f"- ⚠️ **{metric.replace('_', ' ').title()}**: Needs attention ({score}%)\n"

        dashboard_content += f"""

### Recommendations
1. **Code Quality**: Maintain high comment ratio and docstring coverage
2. **GUI Excellence**: Continue implementing modern design patterns
3. **Performance**: Monitor startup and response times regularly
4. **Security**: Regular vulnerability scans and dependency updates
5. **Testing**: Increase test coverage for better reliability

---

## 🎯 Quality Gates Status

| Gate | Status | Score |
|------|--------|-------|
| Code Quality | {'✅ PASS' if individual_scores.get('code_quality', 0) >= 70 else '❌ FAIL'} | {individual_scores.get('code_quality', 0)}% |
| Performance | {'✅ PASS' if individual_scores.get('performance', 0) >= 70 else '❌ FAIL'} | {individual_scores.get('performance', 0)}% |
| Security | {'✅ PASS' if individual_scores.get('security', 0) >= 70 else '❌ FAIL'} | {individual_scores.get('security', 0)}% |
| GUI Quality | {'✅ PASS' if individual_scores.get('gui_quality', 0) >= 70 else '❌ FAIL'} | {individual_scores.get('gui_quality', 0)}% |

---

*Engineering Metrics Dashboard - Stage 3 Complete*  
*Next Update: After Stage 4 completion*
"""

        try:
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)
            return True
        except Exception as e:
            self.results["dashboard_error"] = str(e)
            return False
    
    def run_all_metrics_collection(self):
        """Run all metrics collection and generate dashboard"""
        print("📊 Collecting Engineering Metrics & Generating Dashboard (QUAL-006)...")
        print("=" * 70)
        
        collections = [
            ("Code Metrics", self.collect_code_metrics),
            ("Quality Metrics", self.collect_quality_metrics),
            ("Performance Metrics", self.collect_performance_metrics),
            ("GUI Metrics", self.collect_gui_metrics),
            ("System Metrics", self.collect_system_metrics),
            ("Engineering Score Calculation", self.calculate_engineering_score),
            ("Dashboard Generation", self.generate_metrics_dashboard)
        ]
        
        all_successful = True
        for collection_name, collection_func in collections:
            print(f"Collecting {collection_name}...")
            try:
                result = collection_func()
                status = "✅ COLLECTED" if result else "⚠️  PARTIAL"
                print(f"  {status}")
                if not result:
                    all_successful = False
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                all_successful = False
        
        print("\n" + "=" * 70)
        
        print(f"📊 Overall Engineering Score: {self.results['overall_engineering_score']}%")
        print(f"🎯 Dashboard Status: {self.results['dashboard_status']}")
        
        # Show key metrics
        if "individual_scores" in self.results:
            print("\n📈 Key Metrics:")
            for metric, score in self.results["individual_scores"].items():
                status_icon = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
                print(f"  {status_icon} {metric.replace('_', ' ').title()}: {score}%")
        
        # Generate detailed report
        report_file = self.repo_root / f"engineering_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📋 Detailed metrics report saved: {report_file}")
        print(f"📊 Engineering dashboard saved: ENGINEERING_METRICS.md")
        
        return all_successful and self.results["overall_engineering_score"] >= 60


def main():
    """Main execution function"""
    metrics = EngineeringMetrics()
    success = metrics.run_all_metrics_collection()
    
    if success:
        print("\n✅ QUAL-006 COMPLETED: Engineering metrics dashboard created!")
        sys.exit(0)
    else:
        print("\n❌ QUAL-006 NEEDS ATTENTION: Metrics collection issues detected")
        sys.exit(1)


if __name__ == "__main__":
    main()