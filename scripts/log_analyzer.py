#!/usr/bin/env python3
"""
Log Analysis and Management Tools for Consolidated Logging System
Provides tools to analyze, search, and manage consolidated logs efficiently.
"""

import os
import sys
import json
import gzip
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.consolidated_log_manager import ConsolidatedLogManager

class LogAnalyzer:
    """
    Advanced log analysis tools for the consolidated logging system
    """
    
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.log_root = self.project_root / "tests" / "output" / "consolidated_logs"
        
    def list_sessions(self):
        """List all available log sessions"""
        sessions = set()
        
        for log_file in self.log_root.glob("*_????????_??????.*"):
            # Extract session ID from filename
            parts = log_file.stem.split('_')
            if len(parts) >= 3:
                session_id = '_'.join(parts[-2:])  # date_time
                sessions.add(session_id)
        
        return sorted(list(sessions))
    
    def get_session_info(self, session_id):
        """Get detailed information about a specific session"""
        summary_file = self.log_root / f"session_summary_{session_id}.json"
        
        if not summary_file.exists():
            return None
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Could not read session summary: {e}")
            return None
    
    def search_logs(self, query, session_id=None, category=None, limit=100):
        """
        Search through consolidated logs
        
        Args:
            query: Text to search for
            session_id: Specific session to search (None for all)
            category: Specific category to search (None for all)
            limit: Maximum number of results to return
        """
        results = []
        
        # Get session list
        sessions = [session_id] if session_id else self.list_sessions()
        
        for session in sessions:
            if len(results) >= limit:
                break
                
            # Search in session files
            pattern = f"*_{session}.*" if session else "*"
            
            for log_file in self.log_root.glob(pattern):
                if category:
                    # Check if file matches category
                    file_category = log_file.stem.split('_')[0]
                    if file_category != category:
                        continue
                
                try:
                    # Read file based on extension
                    if log_file.suffix == '.gz':
                        with gzip.open(log_file, 'rt', encoding='utf-8') as f:
                            self._search_in_file(f, query, log_file, results, limit)
                    else:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            self._search_in_file(f, query, log_file, results, limit)
                            
                    if len(results) >= limit:
                        break
                        
                except Exception as e:
                    print(f"[WARN] Could not search in {log_file}: {e}")
        
        return results[:limit]
    
    def _search_in_file(self, file_handle, query, file_path, results, limit):
        """Search for query in a single file"""
        line_number = 0
        
        for line in file_handle:
            line_number += 1
            if len(results) >= limit:
                break
                
            if query.lower() in line.lower():
                try:
                    log_entry = json.loads(line.strip())
                    results.append({
                        'file': str(file_path.name),
                        'line': line_number,
                        'timestamp': log_entry.get('timestamp', ''),
                        'category': log_entry.get('category', ''),
                        'context': log_entry.get('context', ''),
                        'data': log_entry.get('data', {}),
                        'match_line': line.strip()
                    })
                except json.JSONDecodeError:
                    # Handle non-JSON lines
                    results.append({
                        'file': str(file_path.name),
                        'line': line_number,
                        'timestamp': '',
                        'category': 'raw',
                        'context': '',
                        'data': {},
                        'match_line': line.strip()
                    })
    
    def generate_session_report(self, session_id):
        """Generate a comprehensive report for a session"""
        session_info = self.get_session_info(session_id)
        if not session_info:
            return f"Session {session_id} not found"
        
        report = []
        report.append(f"SESSION REPORT: {session_id}")
        report.append("=" * 60)
        report.append(f"Created: {session_info['created_at']}")
        report.append(f"Total Entries: {session_info['total_entries']}")
        report.append(f"Files Created: {len(session_info['files_created'])}")
        report.append("")
        
        # Category breakdown
        report.append("CATEGORY BREAKDOWN:")
        report.append("-" * 30)
        
        for category, details in session_info['categories'].items():
            entries = details['entries']
            size_mb = details['file_size'] / (1024 * 1024)
            buffered = details.get('buffered_entries', 0)
            
            report.append(f"{category:<20} {entries:>8} entries  {size_mb:>6.2f} MB")
            if buffered > 0:
                report.append(f"{'':<20} {buffered:>8} buffered")
        
        report.append("")
        
        # Files created
        report.append("FILES CREATED:")
        report.append("-" * 30)
        for file_path in session_info['files_created']:
            report.append(f"  {file_path}")
        
        return "\n".join(report)
    
    def cleanup_old_logs(self, days_to_keep=7, dry_run=True):
        """Clean up old log files"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = cutoff_date.strftime("%Y%m%d")
        
        files_to_remove = []
        
        for log_file in self.log_root.iterdir():
            if log_file.is_file():
                # Extract timestamp from filename
                parts = log_file.stem.split('_')
                if len(parts) >= 2:
                    try:
                        file_timestamp = parts[-2]  # YYYYMMDD
                        if len(file_timestamp) == 8 and file_timestamp < cutoff_timestamp:
                            files_to_remove.append(log_file)
                    except (ValueError, IndexError):
                        continue
        
        if dry_run:
            return files_to_remove
        else:
            for file_path in files_to_remove:
                file_path.unlink()
            return files_to_remove
    
    def get_statistics(self):
        """Get overall statistics about the logging system"""
        sessions = self.list_sessions()
        total_files = len(list(self.log_root.glob("*")))
        total_size = sum(f.stat().st_size for f in self.log_root.glob("*") if f.is_file())
        
        # Category distribution
        category_stats = Counter()
        
        for log_file in self.log_root.glob("*.jsonl"):
            category = log_file.stem.split('_')[0]
            category_stats[category] += 1
        
        return {
            'total_sessions': len(sessions),
            'total_files': total_files,
            'total_size_mb': total_size / (1024 * 1024),
            'category_distribution': dict(category_stats),
            'latest_session': sessions[-1] if sessions else None,
            'oldest_session': sessions[0] if sessions else None
        }


def main():
    """Command-line interface for log analysis"""
    parser = argparse.ArgumentParser(description="Consolidated Log Analysis Tools")
    parser.add_argument('--list-sessions', action='store_true', help='List all available sessions')
    parser.add_argument('--session-info', help='Get info about specific session')
    parser.add_argument('--session-report', help='Generate report for specific session')
    parser.add_argument('--search', help='Search for text in logs')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--limit', type=int, default=100, help='Limit search results')
    parser.add_argument('--cleanup', type=int, help='Clean up logs older than X days')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be cleaned up without deleting')
    parser.add_argument('--stats', action='store_true', help='Show overall statistics')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer()
    
    if args.list_sessions:
        sessions = analyzer.list_sessions()
        print("Available sessions:")
        for session in sessions:
            print(f"  {session}")
    
    elif args.session_info:
        info = analyzer.get_session_info(args.session_info)
        if info:
            print(json.dumps(info, indent=2))
        else:
            print(f"Session {args.session_info} not found")
    
    elif args.session_report:
        report = analyzer.generate_session_report(args.session_report)
        print(report)
    
    elif args.search:
        results = analyzer.search_logs(
            args.search, 
            category=args.category,
            limit=args.limit
        )
        
        print(f"Found {len(results)} results:")
        for result in results:
            print(f"\n[{result['file']}:{result['line']}] {result['timestamp']}")
            print(f"Category: {result['category']}, Context: {result['context']}")
            print(f"Match: {result['match_line'][:200]}")
    
    elif args.cleanup is not None:
        files_to_remove = analyzer.cleanup_old_logs(
            days_to_keep=args.cleanup,
            dry_run=args.dry_run
        )
        
        if args.dry_run:
            print(f"Would remove {len(files_to_remove)} files:")
            for file_path in files_to_remove:
                print(f"  {file_path}")
        else:
            print(f"Removed {len(files_to_remove)} old log files")
    
    elif args.stats:
        stats = analyzer.get_statistics()
        print("Consolidated Logging Statistics:")
        print(f"  Total Sessions: {stats['total_sessions']}")
        print(f"  Total Files: {stats['total_files']}")
        print(f"  Total Size: {stats['total_size_mb']:.2f} MB")
        print(f"  Latest Session: {stats['latest_session']}")
        print(f"  Oldest Session: {stats['oldest_session']}")
        print(f"  Category Distribution:")
        for category, count in stats['category_distribution'].items():
            print(f"    {category}: {count} files")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()