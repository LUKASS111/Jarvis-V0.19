#!/usr/bin/env python3
"""
Smart GUI Orchestration Components for Jarvis v1.0.0
Implements intelligent UI components with adaptive behavior and AI orchestration.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque

try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QTabWidget, QTextEdit, QProgressBar,
                                QFrame, QScrollArea, QGroupBox)
    from PyQt5.QtCore import QTimer, pyqtSignal, QThread, QObject
    from PyQt5.QtGui import QFont, QPalette, QColor
    PYQT_AVAILABLE = True
except ImportError:
    # Create dummy classes for when PyQt5 is not available
    class QWidget: pass
    class QTabWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QTextEdit: pass
    class QProgressBar: pass
    class QFrame: pass
    class QScrollArea: pass
    class QGroupBox: pass
    class QTimer: 
        def __init__(self): pass
        def timeout(self): pass
        def start(self, interval): pass
        def connect(self, func): pass
    
    PYQT_AVAILABLE = False

# Import Jarvis components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.design_standards import COLORS, TYPOGRAPHY, SPACING


class UserBehaviorTracker:
    """Tracks user behavior patterns for adaptive UI optimization"""
    
    def __init__(self, data_file: str = "memory/user_behavior.json"):
        self.data_file = data_file
        self.session_data = {
            'tab_usage': defaultdict(int),
            'feature_usage': defaultdict(int), 
            'session_duration': defaultdict(float),
            'error_patterns': defaultdict(int),
            'ai_provider_preferences': defaultdict(int),
            'workflow_patterns': deque(maxlen=100)
        }
        self.session_start = time.time()
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical user behavior data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    historical_data = json.load(f)
                    # Merge with session data
                    for key in self.session_data:
                        if key in historical_data:
                            if isinstance(self.session_data[key], defaultdict):
                                self.session_data[key].update(historical_data[key])
                            elif isinstance(self.session_data[key], deque):
                                self.session_data[key].extend(historical_data[key][-50:])  # Keep recent data
        except Exception as e:
            print(f"[UserBehaviorTracker] Error loading data: {e}")
    
    def save_behavior_data(self):
        """Save user behavior data to persistent storage"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Convert defaultdict to regular dict for JSON serialization
            save_data = {}
            for key, value in self.session_data.items():
                if isinstance(value, defaultdict):
                    save_data[key] = dict(value)
                elif isinstance(value, deque):
                    save_data[key] = list(value)
                else:
                    save_data[key] = value
            
            with open(self.data_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"[UserBehaviorTracker] Error saving data: {e}")
    
    def track_tab_usage(self, tab_name: str, duration: float = 0):
        """Track which tabs are used most frequently"""
        self.session_data['tab_usage'][tab_name] += 1
        if duration > 0:
            self.session_data['session_duration'][tab_name] += duration
    
    def track_feature_usage(self, feature_name: str):
        """Track feature usage patterns"""
        self.session_data['feature_usage'][feature_name] += 1
        self.session_data['workflow_patterns'].append({
            'timestamp': time.time(),
            'action': feature_name,
            'context': self.get_current_context()
        })
    
    def track_ai_provider_usage(self, provider: str, success: bool):
        """Track AI provider performance and preferences"""
        if success:
            self.session_data['ai_provider_preferences'][provider] += 1
        else:
            self.session_data['error_patterns'][f"{provider}_error"] += 1
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current usage context"""
        return {
            'session_time': time.time() - self.session_start,
            'recent_actions': list(self.session_data['workflow_patterns'])[-5:]
        }
    
    def get_tab_priority_order(self) -> List[str]:
        """Get recommended tab order based on usage patterns"""
        tab_scores = {}
        
        for tab, usage_count in self.session_data['tab_usage'].items():
            # Calculate score based on usage frequency and recency
            recent_weight = 1.0
            if tab in self.session_data['session_duration']:
                avg_duration = self.session_data['session_duration'][tab] / max(usage_count, 1)
                recent_weight = min(avg_duration / 60.0, 2.0)  # Cap at 2x weight for long sessions
            
            tab_scores[tab] = usage_count * recent_weight
        
        # Sort by score descending
        return sorted(tab_scores.keys(), key=lambda x: tab_scores[x], reverse=True)
    
    def get_recommended_ai_provider(self, task_type: str = "general") -> str:
        """Get recommended AI provider based on success patterns"""
        providers = dict(self.session_data['ai_provider_preferences'])
        if not providers:
            return "gpt-4"  # Default fallback
        
        # Find provider with highest success rate
        return max(providers.keys(), key=lambda x: providers[x])


class AdaptiveTabManager(QTabWidget if PYQT_AVAILABLE else object):
    """Intelligent tab manager that adapts to user behavior"""
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            return
            
        super().__init__(parent)
        self.behavior_tracker = UserBehaviorTracker()
        self.tab_usage_timer = QTimer()
        self.current_tab_start_time = time.time()
        self.setup_adaptive_features()
    
    def setup_adaptive_features(self):
        """Setup adaptive tab management features"""
        # Track tab changes
        self.currentChanged.connect(self.on_tab_changed)
        
        # Setup periodic optimization
        self.optimization_timer = QTimer()
        self.optimization_timer.timeout.connect(self.optimize_tab_order)
        self.optimization_timer.start(300000)  # Optimize every 5 minutes
        
        # Track usage time
        self.tab_usage_timer.timeout.connect(self.track_current_tab_time)
        self.tab_usage_timer.start(1000)  # Update every second
    
    def on_tab_changed(self, index: int):
        """Handle tab change events"""
        # Track previous tab usage time
        if hasattr(self, 'previous_tab_index'):
            duration = time.time() - self.current_tab_start_time
            previous_tab_name = self.tabText(self.previous_tab_index)
            self.behavior_tracker.track_tab_usage(previous_tab_name, duration)
        
        # Start tracking new tab
        self.current_tab_start_time = time.time()
        self.previous_tab_index = index
        
        if index >= 0:
            current_tab_name = self.tabText(index)
            self.behavior_tracker.track_tab_usage(current_tab_name)
    
    def track_current_tab_time(self):
        """Track time spent on current tab"""
        if self.currentIndex() >= 0:
            current_tab_name = self.tabText(self.currentIndex())
            # Update session duration tracking
    
    def optimize_tab_order(self):
        """Optimize tab order based on usage patterns"""
        try:
            priority_order = self.behavior_tracker.get_tab_priority_order()
            current_order = [self.tabText(i) for i in range(self.count())]
            
            # Only reorder if there's a significant difference
            if priority_order != current_order[:len(priority_order)]:
                self.reorder_tabs_by_priority(priority_order)
        except Exception as e:
            print(f"[AdaptiveTabManager] Error optimizing tabs: {e}")
    
    def reorder_tabs_by_priority(self, priority_order: List[str]):
        """Reorder tabs based on priority list"""
        # Create a mapping of current tabs
        current_tabs = {}
        for i in range(self.count()):
            tab_name = self.tabText(i)
            tab_widget = self.widget(i)
            current_tabs[tab_name] = tab_widget
        
        # Remove all tabs temporarily
        for i in range(self.count() - 1, -1, -1):
            self.removeTab(i)
        
        # Re-add tabs in priority order
        for tab_name in priority_order:
            if tab_name in current_tabs:
                self.addTab(current_tabs[tab_name], tab_name)
        
        # Add any remaining tabs
        for tab_name, widget in current_tabs.items():
            if tab_name not in priority_order:
                self.addTab(widget, tab_name)


class IntelligentStatusWidget(QWidget if PYQT_AVAILABLE else object):
    """Smart status widget with predictive capabilities"""
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            return
            
        super().__init__(parent)
        self.behavior_tracker = UserBehaviorTracker()
        self.ai_providers_status = {}
        self.setup_ui()
        self.setup_monitoring()
    
    def setup_ui(self):
        """Setup intelligent status display"""
        layout = QVBoxLayout(self)
        
        # System status section
        self.system_group = QGroupBox("🖥️ System Status")
        system_layout = QVBoxLayout(self.system_group)
        
        self.system_status_label = QLabel("System: Initializing...")
        self.cpu_usage_bar = QProgressBar()
        self.memory_usage_bar = QProgressBar()
        
        system_layout.addWidget(self.system_status_label)
        system_layout.addWidget(QLabel("CPU Usage:"))
        system_layout.addWidget(self.cpu_usage_bar)
        system_layout.addWidget(QLabel("Memory Usage:"))
        system_layout.addWidget(self.memory_usage_bar)
        
        # AI Provider status section
        self.ai_group = QGroupBox("🤖 AI Provider Status")
        self.ai_layout = QVBoxLayout(self.ai_group)
        
        self.recommended_provider_label = QLabel("Recommended: Analyzing...")
        self.ai_layout.addWidget(self.recommended_provider_label)
        
        # Predictive insights section
        self.insights_group = QGroupBox("🔮 Intelligent Insights")
        insights_layout = QVBoxLayout(self.insights_group)
        
        self.insights_text = QTextEdit()
        self.insights_text.setMaximumHeight(100)
        self.insights_text.setReadOnly(True)
        insights_layout.addWidget(self.insights_text)
        
        # Add all groups to main layout
        layout.addWidget(self.system_group)
        layout.addWidget(self.ai_group)
        layout.addWidget(self.insights_group)
        layout.addStretch()
    
    def setup_monitoring(self):
        """Setup intelligent monitoring and prediction"""
        # Update status every 5 seconds
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_intelligent_status)
        self.status_timer.start(5000)
        
        # Generate insights every 30 seconds
        self.insights_timer = QTimer()
        self.insights_timer.timeout.connect(self.generate_predictive_insights)
        self.insights_timer.start(30000)
    
    def update_intelligent_status(self):
        """Update status with intelligent predictions"""
        try:
            import psutil
            
            # Update system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            self.cpu_usage_bar.setValue(int(cpu_percent))
            self.memory_usage_bar.setValue(int(memory_percent))
            
            # Smart status message
            if cpu_percent > 80:
                status_msg = "System: ⚠️ High CPU usage detected"
            elif memory_percent > 85:
                status_msg = "System: ⚠️ High memory usage detected"
            else:
                status_msg = "System: ✅ Optimal performance"
                
            self.system_status_label.setText(status_msg)
            
            # Update AI provider recommendations
            recommended_provider = self.behavior_tracker.get_recommended_ai_provider()
            self.recommended_provider_label.setText(f"Recommended: {recommended_provider}")
            
        except Exception as e:
            self.system_status_label.setText(f"System: ❌ Monitoring error: {str(e)[:50]}")
    
    def generate_predictive_insights(self):
        """Generate intelligent insights based on usage patterns"""
        try:
            insights = []
            
            # Analyze tab usage patterns
            tab_priority = self.behavior_tracker.get_tab_priority_order()
            if tab_priority:
                most_used = tab_priority[0] if tab_priority else "Unknown"
                insights.append(f"💡 Most used feature: {most_used}")
            
            # Analyze workflow patterns
            workflows = list(self.behavior_tracker.session_data['workflow_patterns'])
            if len(workflows) > 5:
                recent_patterns = [w['action'] for w in workflows[-5:]]
                if len(set(recent_patterns)) == 1:
                    insights.append(f"🔄 Repetitive workflow detected: {recent_patterns[0]}")
            
            # Performance suggestions
            total_errors = sum(self.behavior_tracker.session_data['error_patterns'].values())
            if total_errors > 5:
                insights.append("⚠️ Multiple errors detected - consider checking system logs")
            
            # Session insights
            session_time = time.time() - self.behavior_tracker.session_start
            if session_time > 3600:  # 1 hour
                insights.append("⏰ Long session detected - consider taking a break")
            
            # Update insights display
            if insights:
                insights_text = "\n".join(insights[-3:])  # Show last 3 insights
                self.insights_text.setText(insights_text)
            else:
                self.insights_text.setText("📊 Collecting usage data for intelligent insights...")
                
        except Exception as e:
            self.insights_text.setText(f"Error generating insights: {str(e)[:100]}")


class AIOrchestrationEngine:
    """Intelligent AI provider orchestration and optimization"""
    
    def __init__(self):
        self.behavior_tracker = UserBehaviorTracker()
        self.provider_performance = defaultdict(lambda: {'response_time': [], 'success_rate': 0, 'total_requests': 0})
        self.load_provider_metrics()
    
    def load_provider_metrics(self):
        """Load AI provider performance metrics"""
        try:
            metrics_file = "memory/ai_provider_metrics.json"
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    self.provider_performance.update(json.load(f))
        except Exception as e:
            print(f"[AIOrchestrationEngine] Error loading metrics: {e}")
    
    def save_provider_metrics(self):
        """Save AI provider performance metrics"""
        try:
            os.makedirs("memory", exist_ok=True)
            metrics_file = "memory/ai_provider_metrics.json"
            
            # Convert defaultdict to regular dict for JSON
            save_data = {k: dict(v) for k, v in self.provider_performance.items()}
            
            with open(metrics_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"[AIOrchestrationEngine] Error saving metrics: {e}")
    
    def select_optimal_provider(self, task_type: str = "general", complexity: str = "medium") -> str:
        """Select optimal AI provider based on task requirements and performance"""
        
        # Get user preference
        preferred_provider = self.behavior_tracker.get_recommended_ai_provider(task_type)
        
        # Check provider performance
        if preferred_provider in self.provider_performance:
            metrics = self.provider_performance[preferred_provider]
            avg_response_time = sum(metrics['response_time'][-10:]) / max(len(metrics['response_time'][-10:]), 1)
            
            # If preferred provider is performing well, use it
            if metrics['success_rate'] > 0.8 and avg_response_time < 5.0:
                return preferred_provider
        
        # Fallback to best performing provider
        best_provider = "gpt-4"  # Default
        best_score = 0
        
        for provider, metrics in self.provider_performance.items():
            if metrics['total_requests'] > 0:
                score = metrics['success_rate'] * 0.7  # Weight success rate highly
                if metrics['response_time']:
                    avg_time = sum(metrics['response_time'][-10:]) / len(metrics['response_time'][-10:])
                    time_score = max(0, (10 - avg_time) / 10)  # Better score for faster response
                    score += time_score * 0.3
                
                if score > best_score:
                    best_score = score
                    best_provider = provider
        
        return best_provider
    
    def track_provider_performance(self, provider: str, response_time: float, success: bool):
        """Track AI provider performance metrics"""
        metrics = self.provider_performance[provider]
        
        # Update response time (keep last 50 entries)
        metrics['response_time'].append(response_time)
        if len(metrics['response_time']) > 50:
            metrics['response_time'] = metrics['response_time'][-50:]
        
        # Update success rate
        metrics['total_requests'] += 1
        if success:
            metrics['success_rate'] = (metrics['success_rate'] * (metrics['total_requests'] - 1) + 1) / metrics['total_requests']
        else:
            metrics['success_rate'] = (metrics['success_rate'] * (metrics['total_requests'] - 1)) / metrics['total_requests']
        
        # Track in behavior tracker too
        self.behavior_tracker.track_ai_provider_usage(provider, success)
        
        # Save metrics periodically
        if metrics['total_requests'] % 10 == 0:
            self.save_provider_metrics()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get AI provider performance summary"""
        summary = {}
        for provider, metrics in self.provider_performance.items():
            if metrics['total_requests'] > 0:
                avg_response_time = sum(metrics['response_time'][-10:]) / max(len(metrics['response_time'][-10:]), 1)
                summary[provider] = {
                    'success_rate': f"{metrics['success_rate']:.1%}",
                    'avg_response_time': f"{avg_response_time:.2f}s",
                    'total_requests': metrics['total_requests']
                }
        return summary


def create_smart_orchestration_widgets() -> Dict[str, QWidget]:
    """Factory function to create smart orchestration widgets"""
    if not PYQT_AVAILABLE:
        return {}
    
    widgets = {}
    
    try:
        # Create intelligent status widget
        widgets['intelligent_status'] = IntelligentStatusWidget()
        
        print("[SmartOrchestration] Created intelligent GUI components")
        
    except Exception as e:
        print(f"[SmartOrchestration] Error creating widgets: {e}")
    
    return widgets


# Global orchestration engine instance
ai_orchestration_engine = AIOrchestrationEngine()