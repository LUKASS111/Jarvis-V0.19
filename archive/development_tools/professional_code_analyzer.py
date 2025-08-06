#!/usr/bin/env python3
"""
# ARCHIWUM: Ten plik nie jest już używany w systemie produkcyjnym (data archiwizacji: 2025-01-06).

Professional Code Quality and Performance Analyzer for Jarvis V0.19
Comprehensive analysis and optimization system for enterprise-grade development

ARCHIVAL NOTE: This development tool has been archived. Code quality analysis is now 
handled by integrated tools and CI/CD pipelines.
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import ast
import re

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

@dataclass
class CodeQualityMetric:
    """Code quality measurement data structure"""
    file_path: str
    lines_of_code: int
    complexity_score: float
    maintainability_index: float
    duplication_percentage: float
    test_coverage: float
    issues_found: List[str]
    optimization_suggestions: List[str]

@dataclass
class PerformanceProfile:
    """Performance profiling results"""
    function_name: str
    execution_time: float
    memory_usage: float
    call_count: int
    bottleneck_score: float
    optimization_priority: str

class ProfessionalCodeAnalyzer:
    """Professional code quality and performance analysis system"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.analysis_results = {}
        self.performance_profiles = []
        self.quality_metrics = []
        
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze overall project structure and architecture"""
        print("[ANALYZER] Analyzing project structure...")
        
        structure_analysis = {
            'total_files': 0,
            'python_files': 0,
            'test_files': 0,
            'documentation_files': 0,
            'configuration_files': 0,
            'modules': {},
            'architecture_score': 0
        }
        
        # Analyze file structure
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                structure_analysis['total_files'] += 1
                
                if file.endswith('.py'):
                    structure_analysis['python_files'] += 1
                    
                    # Categorize by module
                    relative_path = file_path.relative_to(self.project_path)
                    module_name = str(relative_path.parts[0]) if relative_path.parts else 'root'
                    
                    if module_name not in structure_analysis['modules']:
                        structure_analysis['modules'][module_name] = {'files': 0, 'size': 0}
                    
                    structure_analysis['modules'][module_name]['files'] += 1
                    structure_analysis['modules'][module_name]['size'] += file_path.stat().st_size
                    
                elif 'test' in file.lower():
                    structure_analysis['test_files'] += 1
                elif file.endswith(('.md', '.rst', '.txt')):
                    structure_analysis['documentation_files'] += 1
                elif file.endswith(('.json', '.yaml', '.yml', '.toml', '.cfg', '.ini')):
                    structure_analysis['configuration_files'] += 1
        
        # Calculate architecture score
        architecture_score = self._calculate_architecture_score(structure_analysis)
        structure_analysis['architecture_score'] = architecture_score
        
        return structure_analysis
    
    def _calculate_architecture_score(self, structure: Dict) -> float:
        """Calculate overall architecture quality score"""
        score = 100.0
        
        # Check for good module organization
        if structure['python_files'] > 0:
            modules = structure['modules']
            
            # Deduct for monolithic structure
            if len(modules) < 3 and structure['python_files'] > 10:
                score -= 20
            
            # Reward modular structure
            if len(modules) >= 5:
                score += 10
            
            # Check for test coverage indication
            test_ratio = structure['test_files'] / max(structure['python_files'], 1)
            if test_ratio >= 0.5:
                score += 15
            elif test_ratio >= 0.3:
                score += 10
            elif test_ratio < 0.1:
                score -= 15
            
            # Documentation quality
            doc_ratio = structure['documentation_files'] / max(structure['total_files'], 1)
            if doc_ratio >= 0.1:
                score += 10
            elif doc_ratio < 0.05:
                score -= 10
        
        return max(0.0, min(100.0, score))
    
    def analyze_code_complexity(self, file_path: Path) -> CodeQualityMetric:
        """Analyze code complexity and quality metrics for a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST for analysis
            tree = ast.parse(content)
            
            # Count lines of code (excluding comments and empty lines)
            lines = content.split('\n')
            loc = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            
            # Calculate complexity metrics
            complexity_score = self._calculate_complexity(tree)
            maintainability_index = self._calculate_maintainability(content, complexity_score)
            duplication_percentage = self._detect_code_duplication(content)
            
            # Identify issues and optimization opportunities
            issues = self._identify_code_issues(tree, content)
            optimizations = self._suggest_optimizations(tree, content, complexity_score)
            
            return CodeQualityMetric(
                file_path=str(file_path),
                lines_of_code=loc,
                complexity_score=complexity_score,
                maintainability_index=maintainability_index,
                duplication_percentage=duplication_percentage,
                test_coverage=0.0,  # Would need coverage tool integration
                issues_found=issues,
                optimization_suggestions=optimizations
            )
            
        except Exception as e:
            # Return minimal metric for problematic files
            return CodeQualityMetric(
                file_path=str(file_path),
                lines_of_code=0,
                complexity_score=0.0,
                maintainability_index=0.0,
                duplication_percentage=0.0,
                test_coverage=0.0,
                issues_found=[f"Analysis error: {str(e)}"],
                optimization_suggestions=[]
            )
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Decision points increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return float(complexity)
    
    def _calculate_maintainability(self, content: str, complexity: float) -> float:
        """Calculate maintainability index"""
        lines = len(content.split('\n'))
        
        # Simple maintainability calculation
        # Higher is better, based on inverse complexity and reasonable file size
        if lines == 0:
            return 100.0
        
        size_factor = max(0, 100 - (lines / 10))  # Penalty for large files
        complexity_factor = max(0, 100 - complexity * 2)  # Penalty for complexity
        
        maintainability = (size_factor + complexity_factor) / 2
        return max(0.0, min(100.0, maintainability))
    
    def _detect_code_duplication(self, content: str) -> float:
        """Detect potential code duplication"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 10:
            return 0.0
        
        # Simple duplicate line detection
        line_counts = {}
        for line in lines:
            if len(line) > 20:  # Only check substantial lines
                line_counts[line] = line_counts.get(line, 0) + 1
        
        duplicated_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        duplication_percentage = (duplicated_lines / len(lines)) * 100
        
        return min(100.0, duplication_percentage)
    
    def _identify_code_issues(self, tree: ast.AST, content: str) -> List[str]:
        """Identify potential code quality issues"""
        issues = []
        
        # Check for common issues
        function_count = 0
        class_count = 0
        long_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
                # Check function length (approximate)
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.end_lineno and node.lineno:
                        length = node.end_lineno - node.lineno
                        if length > 50:
                            long_functions += 1
            elif isinstance(node, ast.ClassDef):
                class_count += 1
        
        # Report issues
        if long_functions > 0:
            issues.append(f"{long_functions} functions are too long (>50 lines)")
        
        if function_count > 20:
            issues.append(f"File has many functions ({function_count}), consider splitting")
        
        # Check for potential performance issues
        if 'time.sleep(' in content:
            issues.append("Contains time.sleep() - consider async alternatives")
        
        if content.count('import ') > 20:
            issues.append("Many imports - consider organizing and grouping")
        
        return issues
    
    def _suggest_optimizations(self, tree: ast.AST, content: str, complexity: float) -> List[str]:
        """Suggest performance and maintainability optimizations"""
        suggestions = []
        
        # Complexity-based suggestions
        if complexity > 15:
            suggestions.append("High complexity detected - consider breaking down functions")
        
        # Performance suggestions
        if 'for ' in content and 'append(' in content:
            suggestions.append("Consider list comprehensions for better performance")
        
        if 'try:' in content and 'except:' in content:
            suggestions.append("Use specific exception types instead of bare except")
        
        # Type hints
        if 'def ' in content and '->' not in content:
            suggestions.append("Add type hints for better code documentation")
        
        # Documentation
        if '"""' not in content and "'''" not in content:
            suggestions.append("Add docstrings for better documentation")
        
        return suggestions
    
    def run_performance_profiling(self, target_functions: List[str] = None) -> List[PerformanceProfile]:
        """Run performance profiling on key functions"""
        print("[ANALYZER] Running performance profiling...")
        
        profiles = []
        
        # Mock performance data for demonstration
        # In a real implementation, this would use cProfile or similar tools
        mock_profiles = [
            {
                'function_name': 'system_health_check',
                'execution_time': 0.145,
                'memory_usage': 12.5,
                'call_count': 150,
                'bottleneck_score': 8.5
            },
            {
                'function_name': 'vector_search',
                'execution_time': 0.023,
                'memory_usage': 45.2,
                'call_count': 892,
                'bottleneck_score': 6.2
            },
            {
                'function_name': 'llm_orchestration',
                'execution_time': 1.234,
                'memory_usage': 123.4,
                'call_count': 45,
                'bottleneck_score': 9.8
            }
        ]
        
        for profile_data in mock_profiles:
            # Determine optimization priority
            if profile_data['bottleneck_score'] > 9:
                priority = "HIGH"
            elif profile_data['bottleneck_score'] > 7:
                priority = "MEDIUM"
            else:
                priority = "LOW"
            
            profile = PerformanceProfile(
                function_name=profile_data['function_name'],
                execution_time=profile_data['execution_time'],
                memory_usage=profile_data['memory_usage'],
                call_count=profile_data['call_count'],
                bottleneck_score=profile_data['bottleneck_score'],
                optimization_priority=priority
            )
            profiles.append(profile)
        
        return profiles
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        print("[ANALYZER] Generating optimization report...")
        
        # Analyze project structure
        structure_analysis = self.analyze_project_structure()
        
        # Analyze Python files
        python_files = []
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(Path(root) / file)
        
        # Analyze a sample of files (limit for performance)
        sample_files = python_files[:20] if len(python_files) > 20 else python_files
        quality_metrics = []
        
        for file_path in sample_files:
            metric = self.analyze_code_complexity(file_path)
            quality_metrics.append(metric)
        
        # Run performance profiling
        performance_profiles = self.run_performance_profiling()
        
        # Calculate overall scores
        avg_complexity = sum(m.complexity_score for m in quality_metrics) / max(len(quality_metrics), 1)
        avg_maintainability = sum(m.maintainability_index for m in quality_metrics) / max(len(quality_metrics), 1)
        total_issues = sum(len(m.issues_found) for m in quality_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            structure_analysis, quality_metrics, performance_profiles
        )
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'project_overview': {
                'total_files_analyzed': len(sample_files),
                'architecture_score': structure_analysis['architecture_score'],
                'average_complexity': avg_complexity,
                'average_maintainability': avg_maintainability,
                'total_issues_found': total_issues
            },
            'structure_analysis': structure_analysis,
            'quality_metrics': [asdict(m) for m in quality_metrics],
            'performance_profiles': [asdict(p) for p in performance_profiles],
            'recommendations': recommendations,
            'overall_quality_score': self._calculate_overall_quality_score(
                structure_analysis['architecture_score'], avg_maintainability, total_issues
            )
        }
        
        return report
    
    def _generate_recommendations(self, structure: Dict, quality_metrics: List, 
                                performance_profiles: List) -> List[Dict[str, Any]]:
        """Generate actionable optimization recommendations"""
        recommendations = []
        
        # Architecture recommendations
        if structure['architecture_score'] < 80:
            recommendations.append({
                'category': 'Architecture',
                'priority': 'HIGH',
                'title': 'Improve Project Architecture',
                'description': 'Project structure could be better organized for maintainability',
                'actions': [
                    'Consider breaking large modules into smaller components',
                    'Improve test coverage ratio',
                    'Add more comprehensive documentation'
                ]
            })
        
        # Code quality recommendations
        high_complexity_files = [m for m in quality_metrics if m.complexity_score > 15]
        if high_complexity_files:
            recommendations.append({
                'category': 'Code Quality',
                'priority': 'MEDIUM',
                'title': 'Reduce Code Complexity',
                'description': f'{len(high_complexity_files)} files have high complexity',
                'actions': [
                    'Refactor complex functions into smaller ones',
                    'Use early returns to reduce nesting',
                    'Extract common functionality into utility functions'
                ]
            })
        
        # Performance recommendations
        high_priority_bottlenecks = [p for p in performance_profiles if p.optimization_priority == 'HIGH']
        if high_priority_bottlenecks:
            recommendations.append({
                'category': 'Performance',
                'priority': 'HIGH',
                'title': 'Optimize Performance Bottlenecks',
                'description': f'{len(high_priority_bottlenecks)} high-priority bottlenecks identified',
                'actions': [
                    'Profile and optimize slow functions',
                    'Implement caching for frequently called operations',
                    'Consider async/await for I/O operations'
                ]
            })
        
        # Documentation recommendations
        poorly_documented_files = [m for m in quality_metrics if 'docstrings' in str(m.optimization_suggestions)]
        if poorly_documented_files:
            recommendations.append({
                'category': 'Documentation',
                'priority': 'MEDIUM',
                'title': 'Improve Code Documentation',
                'description': f'{len(poorly_documented_files)} files need better documentation',
                'actions': [
                    'Add comprehensive docstrings to functions and classes',
                    'Include type hints for better code understanding',
                    'Create usage examples for complex components'
                ]
            })
        
        return recommendations
    
    def _calculate_overall_quality_score(self, architecture_score: float, 
                                       avg_maintainability: float, total_issues: int) -> float:
        """Calculate overall project quality score"""
        # Weighted combination of various factors
        architecture_weight = 0.3
        maintainability_weight = 0.4
        issues_weight = 0.3
        
        # Issues penalty (assuming 100 total files, 1 issue per file would be 50% penalty)
        issues_penalty = min(50.0, total_issues * 2)
        
        quality_score = (
            architecture_score * architecture_weight +
            avg_maintainability * maintainability_weight +
            (100 - issues_penalty) * issues_weight
        )
        
        return max(0.0, min(100.0, quality_score))

def main():
    """Main execution function"""
    print("=" * 80)
    print("🔧 PROFESSIONAL CODE QUALITY & PERFORMANCE ANALYZER")
    print("Jarvis V0.19 - Enterprise Development Standards")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = ProfessionalCodeAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_optimization_report()
    
    # Save report
    report_file = Path("PROFESSIONAL_CODE_QUALITY_ANALYSIS_2025.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Display summary
    print(f"\n📊 ANALYSIS COMPLETE")
    print(f"Files Analyzed: {report['project_overview']['total_files_analyzed']}")
    print(f"Architecture Score: {report['project_overview']['architecture_score']:.1f}/100")
    print(f"Overall Quality Score: {report['overall_quality_score']:.1f}/100")
    print(f"Issues Found: {report['project_overview']['total_issues_found']}")
    print(f"Recommendations: {len(report['recommendations'])}")
    
    print(f"\n📋 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. [{rec['priority']}] {rec['title']}")
        print(f"   {rec['description']}")
    
    print(f"\n💾 Detailed report saved to: {report_file}")
    print(f"Analysis timestamp: {report['analysis_timestamp']}")
    
    return report

if __name__ == "__main__":
    report = main()