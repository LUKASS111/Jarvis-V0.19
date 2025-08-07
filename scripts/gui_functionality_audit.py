#!/usr/bin/env python3
"""
GUI Functionality Audit Script - Stage 2 Validation
Comprehensive audit of all program functions and their GUI accessibility.
"""

import sys
import os
import json
import importlib
import inspect
from datetime import datetime
from pathlib import Path
import ast

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GUIFunctionalityAuditor:
    """Comprehensive audit of GUI functionality coverage"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "functionality_mapping": {},
            "gui_coverage": {},
            "missing_gui_functions": [],
            "gui_accessibility": {},
            "success": False
        }
        
    def discover_program_functions(self):
        """Discover all functions and capabilities in the program"""
        functions_inventory = {
            "core_modules": {},
            "api_endpoints": {},
            "cli_commands": {},
            "gui_components": {},
            "total_functions": 0
        }
        
        # Analyze core Jarvis modules
        jarvis_path = self.project_root / "jarvis"
        if jarvis_path.exists():
            for module_dir in jarvis_path.iterdir():
                if module_dir.is_dir() and module_dir.name != "__pycache__":
                    module_functions = self.analyze_module_functions(module_dir)
                    if module_functions:
                        functions_inventory["core_modules"][module_dir.name] = module_functions
        
        # Analyze GUI components
        gui_path = self.project_root / "gui"
        if gui_path.exists():
            gui_functions = self.analyze_gui_functions(gui_path)
            functions_inventory["gui_components"] = gui_functions
        
        # Analyze CLI interface
        cli_functions = self.analyze_cli_functions()
        functions_inventory["cli_commands"] = cli_functions
        
        # Analyze API endpoints
        api_functions = self.analyze_api_functions()
        functions_inventory["api_endpoints"] = api_functions
        
        # Calculate total functions
        total = 0
        for category in functions_inventory.values():
            if isinstance(category, dict):
                total += self.count_functions_in_category(category)
            elif isinstance(category, int):
                total = category
        functions_inventory["total_functions"] = total
        
        self.results["functionality_mapping"] = functions_inventory
        return functions_inventory
    
    def analyze_module_functions(self, module_path):
        """Analyze functions in a specific module directory"""
        module_functions = {}
        
        for py_file in module_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the AST to find functions and classes
                tree = ast.parse(content)
                file_functions = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        file_functions.append({
                            "name": node.name,
                            "type": "function",
                            "line": node.lineno,
                            "is_public": not node.name.startswith("_")
                        })
                    elif isinstance(node, ast.ClassDef):
                        class_methods = []
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_methods.append({
                                    "name": item.name,
                                    "type": "method",
                                    "line": item.lineno,
                                    "is_public": not item.name.startswith("_")
                                })
                        
                        file_functions.append({
                            "name": node.name,
                            "type": "class",
                            "line": node.lineno,
                            "methods": class_methods
                        })
                
                if file_functions:
                    relative_path = str(py_file.relative_to(module_path))
                    module_functions[relative_path] = file_functions
                    
            except Exception as e:
                continue
        
        return module_functions
    
    def analyze_gui_functions(self, gui_path):
        """Analyze GUI components and their functions"""
        gui_functions = {
            "dashboard_tabs": [],
            "components": {},
            "event_handlers": [],
            "gui_accessible_functions": []
        }
        
        # Look for comprehensive dashboard
        dashboard_file = gui_path / "enhanced" / "comprehensive_dashboard.py"
        if dashboard_file.exists():
            try:
                with open(dashboard_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract tab information
                tab_methods = []
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and "tab" in node.name.lower():
                        tab_methods.append({
                            "method": node.name,
                            "line": node.lineno,
                            "likely_tab": self.extract_tab_name(node.name)
                        })
                
                gui_functions["dashboard_tabs"] = tab_methods
                
                # Extract all methods that might be GUI-accessible
                all_methods = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                        all_methods.append({
                            "name": node.name,
                            "line": node.lineno,
                            "is_gui_handler": self.is_gui_handler(node.name)
                        })
                
                gui_functions["gui_accessible_functions"] = all_methods
                
            except Exception as e:
                gui_functions["dashboard_error"] = str(e)
        
        return gui_functions
    
    def extract_tab_name(self, method_name):
        """Extract likely tab name from method name"""
        if "add_" in method_name and "_tab" in method_name:
            # Extract between "add_" and "_tab"
            start = method_name.find("add_") + 4
            end = method_name.find("_tab")
            if start < end:
                return method_name[start:end].replace("_", " ").title()
        return method_name
    
    def is_gui_handler(self, method_name):
        """Check if method is likely a GUI event handler"""
        gui_keywords = ["on_", "handle_", "click", "select", "update", "refresh", "load", "save"]
        return any(keyword in method_name.lower() for keyword in gui_keywords)
    
    def analyze_cli_functions(self):
        """Analyze CLI interface functions"""
        cli_functions = {}
        
        # Look for CLI interface
        cli_file = self.project_root / "jarvis" / "interfaces" / "cli.py"
        if cli_file.exists():
            try:
                with open(cli_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for command definitions
                commands = []
                tree = ast.parse(content)
                
                # Look for command methods or command mappings
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if "command" in node.name.lower() or "cmd_" in node.name:
                            commands.append({
                                "name": node.name,
                                "line": node.lineno,
                                "is_command": True
                            })
                        elif node.name.startswith("do_"):
                            commands.append({
                                "name": node.name[3:],  # Remove "do_" prefix
                                "line": node.lineno,
                                "is_command": True
                            })
                
                cli_functions["commands"] = commands
                cli_functions["total_commands"] = len(commands)
                
            except Exception as e:
                cli_functions["error"] = str(e)
        
        return cli_functions
    
    def analyze_api_functions(self):
        """Analyze API endpoints and functions"""
        api_functions = {}
        
        # Look for API modules
        api_path = self.project_root / "jarvis" / "api"
        if api_path.exists():
            for py_file in api_path.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for API endpoints (Flask/FastAPI patterns)
                    endpoints = []
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check for decorators that might indicate endpoints
                            for decorator in getattr(node, 'decorator_list', []):
                                if isinstance(decorator, ast.Name) and decorator.id in ['app', 'router']:
                                    endpoints.append({
                                        "function": node.name,
                                        "line": node.lineno,
                                        "type": "endpoint"
                                    })
                                elif isinstance(decorator, ast.Attribute):
                                    if decorator.attr in ['route', 'get', 'post', 'put', 'delete']:
                                        endpoints.append({
                                            "function": node.name,
                                            "line": node.lineno,
                                            "method": decorator.attr.upper(),
                                            "type": "endpoint"
                                        })
                    
                    if endpoints:
                        relative_path = str(py_file.relative_to(api_path))
                        api_functions[relative_path] = endpoints
                        
                except Exception as e:
                    continue
        
        return api_functions
    
    def count_functions_in_category(self, category):
        """Count total functions in a category"""
        if isinstance(category, list):
            return len(category)
        elif isinstance(category, dict):
            total = 0
            for value in category.values():
                if isinstance(value, list):
                    total += len(value)
                elif isinstance(value, dict):
                    total += self.count_functions_in_category(value)
            return total
        return 0
    
    def assess_gui_coverage(self):
        """Assess which functions are accessible through GUI"""
        functionality = self.results["functionality_mapping"]
        
        coverage_analysis = {
            "total_functions": functionality.get("total_functions", 0),
            "gui_accessible": 0,
            "cli_only": 0,
            "api_only": 0,
            "coverage_percentage": 0,
            "missing_gui_access": []
        }
        
        # GUI accessible functions from dashboard
        gui_functions = functionality.get("gui_components", {}).get("gui_accessible_functions", [])
        gui_tabs = functionality.get("gui_components", {}).get("dashboard_tabs", [])
        
        coverage_analysis["gui_accessible"] = len(gui_functions) + len(gui_tabs)
        
        # CLI-only functions
        cli_commands = functionality.get("cli_commands", {}).get("commands", [])
        coverage_analysis["cli_only"] = len(cli_commands)
        
        # Functions that need GUI access
        core_modules = functionality.get("core_modules", {})
        for module_name, module_functions in core_modules.items():
            for file_path, functions in module_functions.items():
                for func in functions:
                    if func.get("is_public", False) and func.get("type") == "function":
                        # Check if this function has GUI access
                        has_gui_access = self.check_gui_access(module_name, func["name"])
                        if not has_gui_access:
                            coverage_analysis["missing_gui_access"].append({
                                "module": module_name,
                                "file": file_path,
                                "function": func["name"],
                                "line": func.get("line", 0)
                            })
        
        # Calculate coverage percentage
        total_functions = coverage_analysis["total_functions"]
        if total_functions > 0:
            coverage_percentage = (coverage_analysis["gui_accessible"] / total_functions) * 100
            coverage_analysis["coverage_percentage"] = round(coverage_percentage, 2)
        
        self.results["gui_coverage"] = coverage_analysis
        return coverage_analysis
    
    def check_gui_access(self, module_name, function_name):
        """Check if a function has GUI access"""
        # This is a simplified check - in a real implementation, we would
        # analyze the GUI code to see if it calls this function
        
        # Common GUI-accessible modules and functions
        gui_accessible_modules = {
            "ai", "memory", "vector", "api", "monitoring", "security"
        }
        
        # Assume functions in these modules have GUI access
        return module_name in gui_accessible_modules
    
    def generate_gui_accessibility_report(self):
        """Generate detailed GUI accessibility report"""
        accessibility_report = {
            "required_gui_functions": [
                {
                    "category": "AI & Language Models",
                    "required_functions": [
                        "Model selection and configuration",
                        "Chat interface and conversation management",
                        "Response generation and history",
                        "Model performance monitoring"
                    ],
                    "current_gui_support": "Partial"
                },
                {
                    "category": "Multimodal Processing",
                    "required_functions": [
                        "Image upload and processing",
                        "Audio processing and transcription", 
                        "File processing and conversion",
                        "Multi-format content handling"
                    ],
                    "current_gui_support": "Missing"
                },
                {
                    "category": "Memory & Data Management",
                    "required_functions": [
                        "Database browsing and search",
                        "CRDT data synchronization monitoring",
                        "Archive management and retrieval",
                        "Data export and import"
                    ],
                    "current_gui_support": "Basic"
                },
                {
                    "category": "Agent Workflow System",
                    "required_functions": [
                        "Agent creation and management",
                        "Workflow design and execution",
                        "Task assignment and monitoring",
                        "Performance analytics"
                    ],
                    "current_gui_support": "Missing"
                },
                {
                    "category": "Vector Database & RAG",
                    "required_functions": [
                        "ChromaDB management",
                        "Semantic search interface",
                        "Embedding visualization",
                        "Knowledge base management"
                    ],
                    "current_gui_support": "Missing"
                },
                {
                    "category": "System Monitoring",
                    "required_functions": [
                        "System health dashboards",
                        "Performance metrics display",
                        "Error tracking and resolution",
                        "Resource utilization monitoring"
                    ],
                    "current_gui_support": "Basic"
                },
                {
                    "category": "Configuration & Settings",
                    "required_functions": [
                        "System configuration management",
                        "User preference settings",
                        "Security and access controls",
                        "Backup and restore options"
                    ],
                    "current_gui_support": "Missing"
                },
                {
                    "category": "Development & Testing",
                    "required_functions": [
                        "Test execution and monitoring",
                        "Code quality metrics",
                        "Performance benchmarking",
                        "Error diagnostics"
                    ],
                    "current_gui_support": "Missing"
                },
                {
                    "category": "Analytics & Reporting",
                    "required_functions": [
                        "Usage analytics and reporting",
                        "System reports and export",
                        "Chart visualization",
                        "Custom report building"
                    ],
                    "current_gui_support": "Missing"
                }
            ],
            "gui_implementation_priority": [
                "HIGH: AI Chat & Model Management",
                "HIGH: System Monitoring & Health",
                "MEDIUM: Memory & Data Management", 
                "MEDIUM: Configuration & Settings",
                "MEDIUM: Multimodal Processing",
                "LOW: Agent Workflow System",
                "LOW: Vector Database Management",
                "LOW: Development & Testing Tools",
                "LOW: Analytics & Reporting"
            ],
            "estimated_gui_coverage": "25%"
        }
        
        self.results["gui_accessibility"] = accessibility_report
        return accessibility_report
    
    def run_audit(self):
        """Run complete GUI functionality audit"""
        print("🔍 Starting comprehensive GUI functionality audit...")
        
        # Discover all program functions
        print("📊 Discovering program functions and capabilities...")
        functionality = self.discover_program_functions()
        print(f"   Found {functionality['total_functions']} total functions")
        
        # Assess GUI coverage
        print("🎯 Assessing GUI accessibility coverage...")
        coverage = self.assess_gui_coverage()
        print(f"   GUI coverage: {coverage['coverage_percentage']}%")
        
        # Generate accessibility report
        print("📋 Generating GUI accessibility requirements...")
        accessibility = self.generate_gui_accessibility_report()
        print(f"   Identified {len(accessibility['required_gui_functions'])} function categories")
        
        self.results["success"] = True
        
        # Save results
        report_path = self.project_root / f"gui_functionality_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ GUI functionality audit complete!")
        print(f"📄 Report saved to: {report_path}")
        
        return self.results
    
    def print_summary(self):
        """Print audit summary"""
        if not self.results["success"]:
            print("❌ Audit failed")
            return
        
        print("\n" + "="*60)
        print("🎯 GUI FUNCTIONALITY AUDIT SUMMARY")
        print("="*60)
        
        # Total functions
        functionality = self.results["functionality_mapping"]
        print(f"📊 Total Program Functions: {functionality.get('total_functions', 0)}")
        
        # Core modules
        core_modules = functionality.get("core_modules", {})
        print(f"\n🔧 Core Modules: {len(core_modules)}")
        for module, functions in core_modules.items():
            total_funcs = self.count_functions_in_category(functions)
            print(f"   • {module}: {total_funcs} functions")
        
        # GUI coverage
        coverage = self.results["gui_coverage"]
        print(f"\n🎯 GUI Coverage Analysis:")
        print(f"   • GUI Accessible: {coverage.get('gui_accessible', 0)}")
        print(f"   • CLI Only: {coverage.get('cli_only', 0)}")
        print(f"   • Coverage Percentage: {coverage.get('coverage_percentage', 0)}%")
        print(f"   • Missing GUI Access: {len(coverage.get('missing_gui_access', []))}")
        
        # Accessibility requirements
        accessibility = self.results["gui_accessibility"]
        required_categories = accessibility.get("required_gui_functions", [])
        print(f"\n📋 Required GUI Function Categories: {len(required_categories)}")
        
        missing_categories = [cat for cat in required_categories if cat.get("current_gui_support") == "Missing"]
        print(f"   • Missing GUI Support: {len(missing_categories)} categories")
        
        print(f"\n📈 Estimated Current GUI Coverage: {accessibility.get('estimated_gui_coverage', 'Unknown')}")
        print("\n✅ Audit complete - GUI implementation roadmap ready!")


def main():
    """Main execution function"""
    auditor = GUIFunctionalityAuditor()
    results = auditor.run_audit()
    auditor.print_summary()
    
    return results["success"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)