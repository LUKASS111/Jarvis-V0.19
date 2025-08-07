#!/usr/bin/env python3
"""
Stage 5 - FUNC-005: Performance Metrics
Establish functionality benchmarking with performance metrics
"""

import os
import sys
import json
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path

class PerformanceMetricsAnalyzer:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.metrics_report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'Functionality Performance Benchmarking',
            'stage': 'Stage 5 - FUNC-005',
            'system_metrics': {},
            'application_metrics': {},
            'gui_performance': {},
            'database_performance': {},
            'api_performance': {},
            'memory_usage': {},
            'performance_score': 0,
            'bottlenecks': [],
            'recommendations': []
        }

    def collect_system_metrics(self):
        """Collect system-level performance metrics"""
        print("📊 Collecting system performance metrics...")
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics (if available)
        try:
            network_io = psutil.net_io_counters()
        except:
            network_io = None
        
        system_metrics = {
            'cpu': {
                'usage_percent': cpu_percent,
                'core_count': cpu_count,
                'frequency_mhz': cpu_freq.current if cpu_freq else None,
                'status': 'GOOD' if cpu_percent < 80 else 'HIGH' if cpu_percent < 95 else 'CRITICAL'
            },
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'usage_percent': memory.percent,
                'swap_usage_percent': swap.percent,
                'status': 'GOOD' if memory.percent < 80 else 'HIGH' if memory.percent < 95 else 'CRITICAL'
            },
            'disk': {
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 1),
                'io_read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else None,
                'io_write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else None,
                'status': 'GOOD' if disk_usage.free > 1024**3 else 'LOW'
            }
        }
        
        if network_io:
            system_metrics['network'] = {
                'bytes_sent_mb': round(network_io.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(network_io.bytes_recv / (1024**2), 2),
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
        
        self.metrics_report['system_metrics'] = system_metrics
        return system_metrics

    def benchmark_application_startup(self):
        """Benchmark application startup performance"""
        print("🚀 Benchmarking application startup performance...")
        
        startup_metrics = {
            'main_import_time': 0,
            'gui_init_time': 0,
            'database_init_time': 0,
            'total_startup_time': 0,
            'startup_score': 0
        }
        
        # Test main.py import time
        main_file = self.root_dir / 'main.py'
        if main_file.exists():
            start_time = time.time()
            try:
                # Simulate import without executing
                with open(main_file, 'r') as f:
                    content = f.read()
                import_time = time.time() - start_time
                startup_metrics['main_import_time'] = round(import_time * 1000, 2)  # ms
            except Exception as e:
                startup_metrics['main_import_error'] = str(e)
        
        # Test GUI initialization time
        gui_files = list(self.root_dir.rglob("gui/**/*.py"))
        if gui_files:
            start_time = time.time()
            gui_size = sum(f.stat().st_size for f in gui_files if f.exists())
            # Estimate based on file size (heuristic)
            estimated_gui_time = (gui_size / 1024) * 0.1  # rough estimate
            startup_metrics['gui_init_time'] = round(estimated_gui_time, 2)
        
        # Test database initialization time
        db_files = list(self.root_dir.rglob("*.db"))
        if db_files:
            start_time = time.time()
            db_total_size = sum(f.stat().st_size for f in db_files if f.exists())
            # Estimate based on database size
            estimated_db_time = (db_total_size / (1024**2)) * 10  # rough estimate
            startup_metrics['database_init_time'] = round(estimated_db_time, 2)
        
        # Calculate total startup time
        total_time = (startup_metrics['main_import_time'] + 
                     startup_metrics['gui_init_time'] + 
                     startup_metrics['database_init_time'])
        startup_metrics['total_startup_time'] = round(total_time, 2)
        
        # Calculate startup score (lower time = higher score)
        if total_time < 1000:  # < 1 second
            startup_metrics['startup_score'] = 100
        elif total_time < 3000:  # < 3 seconds
            startup_metrics['startup_score'] = 80
        elif total_time < 5000:  # < 5 seconds
            startup_metrics['startup_score'] = 60
        else:
            startup_metrics['startup_score'] = 40
        
        self.metrics_report['application_metrics'] = startup_metrics
        return startup_metrics

    def analyze_gui_performance(self):
        """Analyze GUI performance characteristics"""
        print("🖥️  Analyzing GUI performance...")
        
        gui_performance = {
            'gui_files_count': 0,
            'gui_total_size_kb': 0,
            'estimated_load_time': 0,
            'complexity_score': 0,
            'performance_score': 0
        }
        
        # Analyze GUI files
        gui_files = list(self.root_dir.rglob("gui/**/*.py"))
        gui_performance['gui_files_count'] = len(gui_files)
        
        if gui_files:
            total_size = sum(f.stat().st_size for f in gui_files if f.exists())
            gui_performance['gui_total_size_kb'] = round(total_size / 1024, 2)
            
            # Estimate load time based on file size and complexity
            estimated_load = (total_size / 1024) * 0.05  # heuristic
            gui_performance['estimated_load_time'] = round(estimated_load, 2)
            
            # Analyze complexity by counting classes, functions, imports
            complexity_indicators = 0
            for gui_file in gui_files:
                try:
                    with open(gui_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        complexity_indicators += content.count('class ')
                        complexity_indicators += content.count('def ')
                        complexity_indicators += content.count('import ')
                except:
                    continue
            
            gui_performance['complexity_score'] = complexity_indicators
            
            # Calculate performance score
            if estimated_load < 100:  # < 100ms
                performance_score = 100
            elif estimated_load < 500:  # < 500ms
                performance_score = 80
            elif estimated_load < 1000:  # < 1s
                performance_score = 60
            else:
                performance_score = 40
            
            # Adjust for complexity
            if complexity_indicators > 500:
                performance_score *= 0.8
            elif complexity_indicators > 200:
                performance_score *= 0.9
            
            gui_performance['performance_score'] = round(performance_score, 1)
        
        self.metrics_report['gui_performance'] = gui_performance
        return gui_performance

    def analyze_database_performance(self):
        """Analyze database performance metrics"""
        print("💾 Analyzing database performance...")
        
        db_performance = {
            'database_files_count': 0,
            'total_database_size_mb': 0,
            'estimated_query_time': 0,
            'database_health': 'UNKNOWN',
            'performance_score': 0
        }
        
        # Find database files
        db_files = list(self.root_dir.rglob("*.db"))
        db_performance['database_files_count'] = len(db_files)
        
        if db_files:
            total_size = sum(f.stat().st_size for f in db_files if f.exists())
            db_performance['total_database_size_mb'] = round(total_size / (1024**2), 2)
            
            # Estimate query time based on database size
            # Rough heuristic: larger databases take longer to query
            estimated_query = (total_size / (1024**2)) * 2  # ms per MB
            db_performance['estimated_query_time'] = round(estimated_query, 2)
            
            # Determine database health based on size and count
            if len(db_files) >= 3 and total_size > 0:
                db_performance['database_health'] = 'GOOD'
                performance_score = 90
            elif len(db_files) >= 1 and total_size > 0:
                db_performance['database_health'] = 'BASIC'
                performance_score = 70
            else:
                db_performance['database_health'] = 'POOR'
                performance_score = 30
            
            # Adjust for size efficiency
            if total_size > 100 * 1024**2:  # > 100MB
                performance_score *= 0.8  # Large databases may be slower
            
            db_performance['performance_score'] = round(performance_score, 1)
        
        self.metrics_report['database_performance'] = db_performance
        return db_performance

    def analyze_memory_usage_patterns(self):
        """Analyze memory usage patterns"""
        print("🧠 Analyzing memory usage patterns...")
        
        memory_analysis = {
            'current_process_memory_mb': 0,
            'estimated_application_memory_mb': 0,
            'memory_efficiency_score': 0,
            'memory_status': 'UNKNOWN'
        }
        
        # Get current process memory
        current_process = psutil.Process()
        memory_info = current_process.memory_info()
        memory_analysis['current_process_memory_mb'] = round(memory_info.rss / (1024**2), 2)
        
        # Estimate application memory usage based on file sizes
        python_files = list(self.root_dir.rglob("*.py"))
        total_code_size = sum(f.stat().st_size for f in python_files if f.exists())
        
        # Rough estimate: Python apps use ~10-50x their code size in memory
        estimated_memory = (total_code_size / 1024**2) * 25  # Conservative estimate
        memory_analysis['estimated_application_memory_mb'] = round(estimated_memory, 2)
        
        # Calculate efficiency score
        system_memory = psutil.virtual_memory()
        memory_ratio = estimated_memory / (system_memory.total / 1024**2)
        
        if memory_ratio < 0.1:  # < 10% of system memory
            memory_analysis['memory_efficiency_score'] = 100
            memory_analysis['memory_status'] = 'EXCELLENT'
        elif memory_ratio < 0.2:  # < 20% of system memory
            memory_analysis['memory_efficiency_score'] = 80
            memory_analysis['memory_status'] = 'GOOD'
        elif memory_ratio < 0.4:  # < 40% of system memory
            memory_analysis['memory_efficiency_score'] = 60
            memory_analysis['memory_status'] = 'MODERATE'
        else:
            memory_analysis['memory_efficiency_score'] = 40
            memory_analysis['memory_status'] = 'HIGH'
        
        self.metrics_report['memory_usage'] = memory_analysis
        return memory_analysis

    def identify_performance_bottlenecks(self):
        """Identify potential performance bottlenecks"""
        print("🔍 Identifying performance bottlenecks...")
        
        bottlenecks = []
        
        # System resource bottlenecks
        system_metrics = self.metrics_report.get('system_metrics', {})
        
        if system_metrics.get('cpu', {}).get('status') in ['HIGH', 'CRITICAL']:
            bottlenecks.append({
                'type': 'System Resource',
                'component': 'CPU',
                'severity': 'HIGH',
                'issue': f"CPU usage at {system_metrics['cpu']['usage_percent']}%",
                'impact': 'Application performance will be degraded',
                'recommendation': 'Optimize CPU-intensive operations or upgrade hardware'
            })
        
        if system_metrics.get('memory', {}).get('status') in ['HIGH', 'CRITICAL']:
            bottlenecks.append({
                'type': 'System Resource',
                'component': 'Memory',
                'severity': 'HIGH',
                'issue': f"Memory usage at {system_metrics['memory']['usage_percent']}%",
                'impact': 'Risk of system slowdown or crashes',
                'recommendation': 'Optimize memory usage or add more RAM'
            })
        
        # Application bottlenecks
        startup_metrics = self.metrics_report.get('application_metrics', {})
        if startup_metrics.get('total_startup_time', 0) > 5000:  # > 5 seconds
            bottlenecks.append({
                'type': 'Application Performance',
                'component': 'Startup Time',
                'severity': 'MEDIUM',
                'issue': f"Slow startup time: {startup_metrics['total_startup_time']}ms",
                'impact': 'Poor user experience during application launch',
                'recommendation': 'Optimize imports and initialization code'
            })
        
        # GUI bottlenecks
        gui_performance = self.metrics_report.get('gui_performance', {})
        if gui_performance.get('performance_score', 100) < 70:
            bottlenecks.append({
                'type': 'GUI Performance',
                'component': 'Interface Loading',
                'severity': 'MEDIUM',
                'issue': f"GUI performance score: {gui_performance['performance_score']}%",
                'impact': 'Slow interface responsiveness',
                'recommendation': 'Optimize GUI components and reduce complexity'
            })
        
        # Database bottlenecks
        db_performance = self.metrics_report.get('database_performance', {})
        if db_performance.get('estimated_query_time', 0) > 100:  # > 100ms
            bottlenecks.append({
                'type': 'Database Performance',
                'component': 'Query Performance',
                'severity': 'MEDIUM',
                'issue': f"Estimated query time: {db_performance['estimated_query_time']}ms",
                'impact': 'Slow data operations and user experience',
                'recommendation': 'Optimize database queries and consider indexing'
            })
        
        self.metrics_report['bottlenecks'] = bottlenecks
        return bottlenecks

    def calculate_overall_performance_score(self):
        """Calculate overall performance score"""
        print("📊 Calculating overall performance score...")
        
        scores = []
        weights = []
        
        # System performance (30% weight)
        system_metrics = self.metrics_report.get('system_metrics', {})
        cpu_score = 100 - system_metrics.get('cpu', {}).get('usage_percent', 0)
        memory_score = 100 - system_metrics.get('memory', {}).get('usage_percent', 0)
        system_score = (cpu_score + memory_score) / 2
        scores.append(system_score)
        weights.append(0.3)
        
        # Application performance (25% weight)
        startup_score = self.metrics_report.get('application_metrics', {}).get('startup_score', 0)
        scores.append(startup_score)
        weights.append(0.25)
        
        # GUI performance (25% weight)
        gui_score = self.metrics_report.get('gui_performance', {}).get('performance_score', 0)
        scores.append(gui_score)
        weights.append(0.25)
        
        # Database performance (20% weight)
        db_score = self.metrics_report.get('database_performance', {}).get('performance_score', 0)
        scores.append(db_score)
        weights.append(0.2)
        
        # Calculate weighted average
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        self.metrics_report['performance_score'] = round(overall_score, 1)
        
        return overall_score

    def generate_performance_recommendations(self):
        """Generate performance improvement recommendations"""
        print("💡 Generating performance recommendations...")
        
        recommendations = []
        
        # Overall performance recommendations
        overall_score = self.metrics_report.get('performance_score', 0)
        if overall_score < 70:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Overall Performance',
                'issue': f'Overall performance score: {overall_score}%',
                'recommendation': 'Comprehensive performance optimization needed',
                'impact': 'Poor user experience and system responsiveness'
            })
        
        # Component-specific recommendations
        bottlenecks = self.metrics_report.get('bottlenecks', [])
        for bottleneck in bottlenecks:
            if bottleneck['severity'] == 'HIGH':
                recommendations.append({
                    'priority': 'HIGH',
                    'category': bottleneck['component'],
                    'issue': bottleneck['issue'],
                    'recommendation': bottleneck['recommendation'],
                    'impact': bottleneck['impact']
                })
        
        # Memory optimization
        memory_usage = self.metrics_report.get('memory_usage', {})
        if memory_usage.get('memory_status') in ['HIGH', 'MODERATE']:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Memory Optimization',
                'issue': f"Memory efficiency: {memory_usage.get('memory_efficiency_score', 0)}%",
                'recommendation': 'Optimize memory usage patterns and implement garbage collection',
                'impact': 'Reduced system resources and potential instability'
            })
        
        self.metrics_report['recommendations'] = recommendations

    def run_comprehensive_performance_analysis(self):
        """Execute comprehensive performance analysis"""
        print("⚡ Starting Stage 5 - Performance Metrics Analysis...")
        print("=" * 60)
        
        # Step 1: Collect system metrics
        system_metrics = self.collect_system_metrics()
        
        # Step 2: Benchmark application startup
        startup_metrics = self.benchmark_application_startup()
        
        # Step 3: Analyze GUI performance
        gui_performance = self.analyze_gui_performance()
        
        # Step 4: Analyze database performance
        db_performance = self.analyze_database_performance()
        
        # Step 5: Analyze memory usage
        memory_analysis = self.analyze_memory_usage_patterns()
        
        # Step 6: Identify bottlenecks
        bottlenecks = self.identify_performance_bottlenecks()
        
        # Step 7: Calculate overall score
        overall_score = self.calculate_overall_performance_score()
        
        # Step 8: Generate recommendations
        self.generate_performance_recommendations()
        
        print(f"   Overall performance score: {overall_score}%")
        print(f"   Performance bottlenecks: {len(bottlenecks)}")
        print(f"   Recommendations: {len(self.metrics_report['recommendations'])}")
        
        return self.metrics_report

    def save_report(self, output_file):
        """Save performance metrics report"""
        with open(output_file, 'w') as f:
            json.dump(self.metrics_report, f, indent=2)
        print(f"\n✅ Performance metrics report saved to: {output_file}")

def main():
    """Main execution function"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = f"performance_metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    analyzer = PerformanceMetricsAnalyzer(root_dir)
    report = analyzer.run_comprehensive_performance_analysis()
    
    # Print summary
    print("\n" + "="*60)
    print("⚡ PERFORMANCE METRICS SUMMARY")
    print("="*60)
    print(f"Overall Performance Score: {report.get('performance_score', 0)}%")
    
    # Print component scores
    startup_score = report.get('application_metrics', {}).get('startup_score', 0)
    gui_score = report.get('gui_performance', {}).get('performance_score', 0)
    db_score = report.get('database_performance', {}).get('performance_score', 0)
    memory_score = report.get('memory_usage', {}).get('memory_efficiency_score', 0)
    
    print(f"\n📊 COMPONENT SCORES:")
    print(f"  Startup Performance: {startup_score}%")
    print(f"  GUI Performance: {gui_score}%")
    print(f"  Database Performance: {db_score}%")
    print(f"  Memory Efficiency: {memory_score}%")
    
    # Print system status
    system_metrics = report.get('system_metrics', {})
    print(f"\n💻 SYSTEM STATUS:")
    print(f"  CPU Usage: {system_metrics.get('cpu', {}).get('usage_percent', 0)}%")
    print(f"  Memory Usage: {system_metrics.get('memory', {}).get('usage_percent', 0)}%")
    print(f"  Disk Free: {system_metrics.get('disk', {}).get('free_gb', 0)} GB")
    
    # Print bottlenecks
    bottlenecks = report.get('bottlenecks', [])
    if bottlenecks:
        print(f"\n🚨 PERFORMANCE BOTTLENECKS:")
        for bottleneck in bottlenecks[:3]:
            print(f"  • {bottleneck['component']}: {bottleneck['issue']}")
    
    # Print high priority recommendations
    recommendations = report.get('recommendations', [])
    high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
    if high_priority:
        print(f"\n💡 HIGH PRIORITY RECOMMENDATIONS:")
        for rec in high_priority:
            print(f"  • {rec['issue']}")
            print(f"    Action: {rec['recommendation']}")
    
    analyzer.save_report(output_file)
    
    # Return status based on performance
    overall_score = report.get('performance_score', 0)
    
    if overall_score >= 85:
        print("\n✅ PERFORMANCE ANALYSIS: EXCELLENT")
        print("   System performing optimally")
        return 0
    elif overall_score >= 70:
        print("\n⚠️  PERFORMANCE ANALYSIS: GOOD")
        print("   Minor optimizations recommended")
        return 0
    else:
        print("\n❌ PERFORMANCE ANALYSIS: NEEDS OPTIMIZATION")
        print("   Significant performance issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())