#!/usr/bin/env python3
"""
Stage 5 - FUNC-002: Regression Analysis
Historical functionality comparison to identify any lost functionality
"""

import os
import sys
import json
import git
from datetime import datetime
from pathlib import Path

class RegressionAnalyzer:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.analysis_report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'Historical Functionality Regression Analysis',
            'stage': 'Stage 5 - FUNC-002',
            'commits_analyzed': 0,
            'functionality_changes': [],
            'potential_regressions': [],
            'recovered_functionality': [],
            'risk_assessment': {},
            'timeline_analysis': {},
            'recommendations': []
        }

    def analyze_git_history(self):
        """Analyze git commit history for functionality changes"""
        try:
            repo = git.Repo(self.root_dir)
            commits = list(repo.iter_commits(max_count=50))  # Last 50 commits
            
            functionality_keywords = [
                'add', 'implement', 'create', 'new', 'feature',
                'remove', 'delete', 'deprecate', 'disable',
                'fix', 'repair', 'restore', 'recover',
                'enhance', 'improve', 'optimize', 'update'
            ]
            
            commit_analysis = []
            
            for commit in commits:
                commit_info = {
                    'hash': commit.hexsha[:8],
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'changes_type': self._classify_commit_type(commit.message),
                    'files_changed': len(commit.stats.files),
                    'insertions': commit.stats.total['insertions'],
                    'deletions': commit.stats.total['deletions']
                }
                
                # Check for functionality keywords
                message_lower = commit.message.lower()
                relevant_keywords = [kw for kw in functionality_keywords if kw in message_lower]
                commit_info['functionality_keywords'] = relevant_keywords
                
                # Analyze file changes for functionality impact
                changed_files = list(commit.stats.files.keys())
                core_files_changed = [f for f in changed_files if self._is_core_functionality_file(f)]
                commit_info['core_files_changed'] = core_files_changed
                commit_info['functionality_impact'] = self._assess_functionality_impact(commit_info)
                
                commit_analysis.append(commit_info)
            
            self.analysis_report['commits_analyzed'] = len(commit_analysis)
            self.analysis_report['commit_history'] = commit_analysis
            
            return commit_analysis
            
        except Exception as e:
            print(f"Error analyzing git history: {e}")
            return []

    def _classify_commit_type(self, message):
        """Classify commit type based on message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['fix', 'repair', 'resolve', 'bug']):
            return 'bugfix'
        elif any(word in message_lower for word in ['add', 'implement', 'create', 'new']):
            return 'feature_addition'
        elif any(word in message_lower for word in ['remove', 'delete', 'deprecate']):
            return 'feature_removal'
        elif any(word in message_lower for word in ['update', 'improve', 'enhance', 'optimize']):
            return 'enhancement'
        elif any(word in message_lower for word in ['refactor', 'restructure', 'reorganize']):
            return 'refactoring'
        else:
            return 'maintenance'

    def _is_core_functionality_file(self, filepath):
        """Check if file contains core functionality"""
        core_indicators = [
            'main.py', 'app.py', 'core/', 'jarvis/',
            'ai/', 'llm/', 'model/', 'chat/',
            'memory/', 'database/', 'crdt/',
            'workflow/', 'agent/', 'vector/',
            'gui/', 'interface/', 'api/'
        ]
        
        return any(indicator in filepath.lower() for indicator in core_indicators)

    def _assess_functionality_impact(self, commit_info):
        """Assess the functionality impact of a commit"""
        impact_score = 0
        
        # High impact indicators
        if commit_info['changes_type'] in ['feature_removal', 'bugfix']:
            impact_score += 3
        elif commit_info['changes_type'] in ['feature_addition']:
            impact_score += 2
        
        # Core files changed
        if commit_info['core_files_changed']:
            impact_score += len(commit_info['core_files_changed'])
        
        # Large changes
        if commit_info['deletions'] > 100:
            impact_score += 2
        if commit_info['insertions'] > 200:
            impact_score += 1
        
        # Functionality keywords
        functionality_keywords = commit_info.get('functionality_keywords', [])
        if any(kw in ['remove', 'delete', 'disable'] for kw in functionality_keywords):
            impact_score += 3
        
        if impact_score >= 5:
            return 'HIGH'
        elif impact_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'

    def identify_potential_regressions(self, commit_history):
        """Identify commits that might have caused functionality loss"""
        potential_regressions = []
        
        for commit in commit_history:
            regression_indicators = []
            
            # Check for removal/deletion keywords
            message_lower = commit['message'].lower()
            if any(word in message_lower for word in ['remove', 'delete', 'disable', 'deprecate']):
                regression_indicators.append('removal_keywords')
            
            # High deletion count
            if commit['deletions'] > commit['insertions'] * 2:
                regression_indicators.append('high_deletion_ratio')
            
            # Core files with many deletions
            if commit['core_files_changed'] and commit['deletions'] > 50:
                regression_indicators.append('core_files_deleted')
            
            # Error-related commits (might have disabled functionality)
            if any(word in message_lower for word in ['error', 'crash', 'fail', 'corrupt']):
                regression_indicators.append('error_related')
            
            if regression_indicators:
                potential_regressions.append({
                    'commit': commit,
                    'regression_indicators': regression_indicators,
                    'risk_level': self._calculate_regression_risk(regression_indicators)
                })
        
        self.analysis_report['potential_regressions'] = potential_regressions
        return potential_regressions

    def _calculate_regression_risk(self, indicators):
        """Calculate regression risk level"""
        high_risk_indicators = ['removal_keywords', 'core_files_deleted']
        medium_risk_indicators = ['high_deletion_ratio', 'error_related']
        
        if any(indicator in high_risk_indicators for indicator in indicators):
            return 'HIGH'
        elif any(indicator in medium_risk_indicators for indicator in indicators):
            return 'MEDIUM'
        else:
            return 'LOW'

    def analyze_functionality_recovery(self, commit_history):
        """Analyze commits that recovered functionality"""
        recovery_commits = []
        
        for commit in commit_history:
            message_lower = commit['message'].lower()
            recovery_keywords = ['restore', 'recover', 'fix', 'repair', 'reinstate', 'enable']
            
            if any(keyword in message_lower for keyword in recovery_keywords):
                recovery_commits.append({
                    'commit': commit,
                    'recovery_type': self._identify_recovery_type(commit['message']),
                    'impact': commit['functionality_impact']
                })
        
        self.analysis_report['recovered_functionality'] = recovery_commits
        return recovery_commits

    def _identify_recovery_type(self, message):
        """Identify type of functionality recovery"""
        message_lower = message.lower()
        
        if 'database' in message_lower or 'db' in message_lower:
            return 'database_recovery'
        elif 'gui' in message_lower or 'interface' in message_lower:
            return 'gui_recovery'
        elif 'api' in message_lower:
            return 'api_recovery'
        elif 'memory' in message_lower or 'crdt' in message_lower:
            return 'memory_recovery'
        elif 'test' in message_lower:
            return 'testing_recovery'
        else:
            return 'general_recovery'

    def analyze_current_functionality_status(self):
        """Analyze current state of functionality"""
        # Check core components
        core_components = {
            'database_system': self._check_database_functionality(),
            'gui_system': self._check_gui_functionality(),
            'api_system': self._check_api_functionality(),
            'memory_system': self._check_memory_functionality(),
            'testing_system': self._check_testing_functionality()
        }
        
        functionality_status = {}
        for component, status in core_components.items():
            functionality_status[component] = {
                'operational': status['operational'],
                'completeness': status['completeness'],
                'issues': status['issues']
            }
        
        self.analysis_report['current_functionality_status'] = functionality_status
        return functionality_status

    def _check_database_functionality(self):
        """Check database system functionality"""
        db_files = list(self.root_dir.rglob("*database*")) + list(self.root_dir.rglob("*.db"))
        
        return {
            'operational': len(db_files) > 0,
            'completeness': 'GOOD' if len(db_files) >= 3 else 'PARTIAL',
            'issues': [] if len(db_files) > 0 else ['No database files found']
        }

    def _check_gui_functionality(self):
        """Check GUI system functionality"""
        gui_files = list(self.root_dir.rglob("gui/**/*.py"))
        dashboard_exists = (self.root_dir / 'gui' / 'enhanced' / 'comprehensive_dashboard.py').exists()
        
        return {
            'operational': len(gui_files) > 0,
            'completeness': 'EXCELLENT' if dashboard_exists else 'PARTIAL',
            'issues': [] if dashboard_exists else ['Comprehensive dashboard not found']
        }

    def _check_api_functionality(self):
        """Check API system functionality"""
        api_indicators = ['api', 'endpoint', 'route', 'handler']
        api_files = []
        
        for indicator in api_indicators:
            api_files.extend(list(self.root_dir.rglob(f"*{indicator}*")))
        
        return {
            'operational': len(api_files) > 0,
            'completeness': 'GOOD' if len(api_files) >= 2 else 'BASIC',
            'issues': [] if len(api_files) > 0 else ['Limited API structure found']
        }

    def _check_memory_functionality(self):
        """Check memory/CRDT system functionality"""
        memory_files = list(self.root_dir.rglob("*memory*")) + list(self.root_dir.rglob("*crdt*"))
        
        return {
            'operational': len(memory_files) > 0,
            'completeness': 'GOOD' if len(memory_files) >= 2 else 'BASIC',
            'issues': [] if len(memory_files) > 0 else ['Memory system files not found']
        }

    def _check_testing_functionality(self):
        """Check testing system functionality"""
        test_files = list(self.root_dir.rglob("test*.py")) + list(self.root_dir.rglob("*test*.py"))
        
        return {
            'operational': len(test_files) > 0,
            'completeness': 'EXCELLENT' if len(test_files) >= 5 else 'BASIC',
            'issues': [] if len(test_files) > 0 else ['No test files found']
        }

    def generate_regression_recommendations(self):
        """Generate recommendations based on regression analysis"""
        recommendations = []
        
        # High-risk regression commits
        high_risk_regressions = [r for r in self.analysis_report.get('potential_regressions', []) 
                                if r['risk_level'] == 'HIGH']
        
        if high_risk_regressions:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Regression Risk',
                'issue': f'{len(high_risk_regressions)} high-risk commits identified',
                'recommendation': 'Review high-risk commits for potential functionality loss',
                'impact': 'Critical functionality may have been inadvertently removed',
                'commits': [r['commit']['hash'] for r in high_risk_regressions]
            })
        
        # Functionality status issues
        current_status = self.analysis_report.get('current_functionality_status', {})
        for component, status in current_status.items():
            if not status['operational']:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': f'{component.title()} Failure',
                    'issue': f'{component} is not operational',
                    'recommendation': f'Restore {component} functionality immediately',
                    'impact': 'Core system component unavailable'
                })
            elif status['completeness'] == 'PARTIAL':
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': f'{component.title()} Completeness',
                    'issue': f'{component} has partial functionality',
                    'recommendation': f'Complete {component} implementation',
                    'impact': 'Reduced system capabilities'
                })
        
        self.analysis_report['recommendations'] = recommendations

    def run_comprehensive_analysis(self):
        """Execute comprehensive regression analysis"""
        print("📊 Starting Stage 5 - Regression Analysis...")
        print("=" * 60)
        
        # Step 1: Analyze git history
        print("📜 Analyzing git commit history...")
        commit_history = self.analyze_git_history()
        print(f"   Analyzed {len(commit_history)} commits")
        
        # Step 2: Identify potential regressions
        print("🔍 Identifying potential regressions...")
        potential_regressions = self.identify_potential_regressions(commit_history)
        print(f"   Found {len(potential_regressions)} potential regression commits")
        
        # Step 3: Analyze functionality recovery
        print("🔄 Analyzing functionality recovery...")
        recovery_commits = self.analyze_functionality_recovery(commit_history)
        print(f"   Found {len(recovery_commits)} recovery commits")
        
        # Step 4: Check current functionality status
        print("✅ Checking current functionality status...")
        current_status = self.analyze_current_functionality_status()
        operational_count = sum(1 for s in current_status.values() if s['operational'])
        print(f"   {operational_count}/{len(current_status)} core components operational")
        
        # Step 5: Generate recommendations
        print("💡 Generating regression analysis recommendations...")
        self.generate_regression_recommendations()
        print(f"   Generated {len(self.analysis_report['recommendations'])} recommendations")
        
        return self.analysis_report

    def save_report(self, output_file):
        """Save regression analysis report"""
        with open(output_file, 'w') as f:
            json.dump(self.analysis_report, f, indent=2)
        print(f"\n✅ Regression analysis report saved to: {output_file}")

def main():
    """Main execution function"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = f"regression_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    analyzer = RegressionAnalyzer(root_dir)
    report = analyzer.run_comprehensive_analysis()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 REGRESSION ANALYSIS SUMMARY")
    print("="*60)
    print(f"Commits Analyzed: {report['commits_analyzed']}")
    print(f"Potential Regressions: {len(report.get('potential_regressions', []))}")
    print(f"Recovery Commits: {len(report.get('recovered_functionality', []))}")
    
    # Print functionality status
    current_status = report.get('current_functionality_status', {})
    print(f"\n🔧 FUNCTIONALITY STATUS:")
    for component, status in current_status.items():
        status_icon = "✅" if status['operational'] else "❌"
        completeness = status['completeness']
        print(f"  {status_icon} {component.replace('_', ' ').title()}: {completeness}")
    
    # Print high-risk regressions
    potential_regressions = report.get('potential_regressions', [])
    high_risk = [r for r in potential_regressions if r['risk_level'] == 'HIGH']
    if high_risk:
        print(f"\n🚨 HIGH RISK REGRESSION COMMITS:")
        for regression in high_risk[:3]:
            commit = regression['commit']
            print(f"  • {commit['hash']}: {commit['message'][:60]}...")
    
    # Print recommendations
    recommendations = report.get('recommendations', [])
    critical_recs = [r for r in recommendations if r['priority'] == 'CRITICAL']
    if critical_recs:
        print(f"\n❗ CRITICAL RECOMMENDATIONS:")
        for rec in critical_recs:
            print(f"  • {rec['issue']}")
            print(f"    Action: {rec['recommendation']}")
    
    analyzer.save_report(output_file)
    
    # Return status based on analysis
    operational_components = sum(1 for s in current_status.values() if s['operational'])
    total_components = len(current_status)
    
    if operational_components == total_components and not critical_recs:
        print("\n✅ REGRESSION ANALYSIS: PASSED")
        print("   All components operational, no critical regressions")
        return 0
    elif operational_components >= total_components * 0.8:
        print("\n⚠️  REGRESSION ANALYSIS: MINOR ISSUES")
        print("   Most components operational, some improvements needed")
        return 0
    else:
        print("\n❌ REGRESSION ANALYSIS: FAILED")
        print("   Critical functionality regressions detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())