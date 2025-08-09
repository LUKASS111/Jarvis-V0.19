#!/usr/bin/env python3
"""
Refactored Comprehensive Dashboard for Jarvis 1.0.0
Clean, modular architecture using component-based design.
Replaces the monolithic 1705-line comprehensive_dashboard.py with focused modules.
"""

import sys
import os
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout,
                                QWidget, QMenuBar, QStatusBar, QAction, QLabel)
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QIcon
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt5 not available, GUI will use fallback mode")

from gui.design_standards import (
    COLORS, TYPOGRAPHY, SPACING, DIMENSIONS, RADIUS, SHADOWS,
    COMPONENT_STYLES, create_professional_stylesheet, apply_style_to_widget
)

# Import smart orchestration components
try:
    from gui.components.smart_orchestration import (
        AdaptiveTabManager, IntelligentStatusWidget, AIOrchestrationEngine,
        UserBehaviorTracker, create_smart_orchestration_widgets
    )
    SMART_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"Smart orchestration features not available: {e}")
    SMART_FEATURES_AVAILABLE = False

class JarvisComprehensiveDashboard(QMainWindow if PYQT_AVAILABLE else object):
    """
    Smart comprehensive dashboard with adaptive behavior and AI orchestration.
    Features intelligent tab management and user behavior learning.
    """
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            print("GUI not available - PyQt5 required")
            return
            
        super().__init__()
        self.tab_widget = None
        self.behavior_tracker = None
        self.ai_orchestration = None
        self.intelligent_status = None
        
        self.init_smart_components()
        self.init_ui()
        self.apply_modern_styling()
    
    def init_smart_components(self):
        """Initialize smart orchestration components"""
        global SMART_FEATURES_AVAILABLE
        if SMART_FEATURES_AVAILABLE:
            try:
                self.behavior_tracker = UserBehaviorTracker()
                self.ai_orchestration = AIOrchestrationEngine()
                print("[Dashboard] Smart orchestration components initialized")
            except Exception as e:
                print(f"[Dashboard] Error initializing smart components: {e}")
                SMART_FEATURES_AVAILABLE = False
    
    def init_ui(self):
        """Initialize the user interface with smart adaptive tabs"""
        self.setWindowTitle("Jarvis 1.0.0 - Smart AI Orchestration Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create smart tab widget (adaptive if available)
        global SMART_FEATURES_AVAILABLE
        if SMART_FEATURES_AVAILABLE:
            self.tab_widget = AdaptiveTabManager()
            print("[Dashboard] Using adaptive tab manager")
        else:
            self.tab_widget = QTabWidget()
            print("[Dashboard] Using standard tab widget")
        
        # Create side panel for intelligent status
        if SMART_FEATURES_AVAILABLE:
            self.intelligent_status = IntelligentStatusWidget()
            self.intelligent_status.setMaximumWidth(300)
            self.intelligent_status.setMinimumWidth(250)
            main_layout.addWidget(self.intelligent_status, 0)
        
        # Add main tab widget
        main_layout.addWidget(self.tab_widget, 1)
        
        # Setup menu and status bar
        self.setup_menu_bar()
        self.setup_status_bar()
        
        # Load all tabs using factory pattern
        self.load_tabs()
        
        # Setup responsive layout
        self.setup_responsive_layout()
        
        # Setup smart features
        self.setup_smart_features()
    
    def setup_menu_bar(self):
        """Setup application menu bar with smart features"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Export Settings', self.export_settings)
        file_menu.addAction('Import Settings', self.import_settings)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # View menu
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Refresh All Tabs', self.refresh_all_tabs)
        view_menu.addAction('Reset Layout', self.reset_layout)
        
        # Smart features menu (if available)
        global SMART_FEATURES_AVAILABLE
        if SMART_FEATURES_AVAILABLE:
            smart_menu = menubar.addMenu('🤖 Smart Features')
            smart_menu.addAction('Optimize Tab Order', self.optimize_tabs)
            smart_menu.addAction('View Usage Analytics', self.show_usage_analytics)
            smart_menu.addAction('AI Provider Performance', self.show_ai_performance)
            smart_menu.addAction('Reset User Data', self.reset_user_data)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
        help_menu.addAction('Documentation', self.show_documentation)
    
    def setup_status_bar(self):
        """Setup status bar with system information"""
        status_bar = self.statusBar()
        status_bar.showMessage("Jarvis 1.0.0 - All systems operational")
        
        # Add permanent widgets
        system_status = QLabel("System: 🟢")
        status_bar.addPermanentWidget(system_status)
    
    def load_tabs(self):
        """Load all dashboard tabs using the factory pattern"""
        from gui.components.tabs.tab_factory import TabFactory
        
        # Get all available tab creators
        tab_creators = TabFactory.get_all_tab_creators()
        
        # Create and add each tab
        for tab_name, creator_func in tab_creators:
            try:
                tab_widget = creator_func()
                if tab_widget:
                    # Extract title from tab if available
                    tab_title = getattr(tab_widget, 'title', tab_name.replace('_', ' ').title())
                    tab_icon = getattr(tab_widget, 'icon', '')
                    
                    # Format tab title with icon
                    display_title = f"{tab_icon} {tab_title}" if tab_icon else tab_title
                    
                    self.tab_widget.addTab(tab_widget, display_title)
                    print(f"[Dashboard] Added tab: {tab_title}")
                else:
                    print(f"[Dashboard] Failed to create tab: {tab_name}")
            except Exception as e:
                print(f"[Dashboard] Error loading tab {tab_name}: {e}")
        
        print(f"[Dashboard] Loaded {self.tab_widget.count()} tabs successfully")
    
    def setup_responsive_layout(self):
        """Setup responsive layout following design standards"""
        if hasattr(self, 'tab_widget') and self.tab_widget:
            self.tab_widget.setMinimumSize(
                DIMENSIONS["panel_min_width"], 
                DIMENSIONS["panel_min_height"]
            )
        
        # Apply consistent spacing to all tabs
        for i in range(self.tab_widget.count() if self.tab_widget else 0):
            tab_widget = self.tab_widget.widget(i)
            if tab_widget and hasattr(tab_widget, 'layout'):
                try:
                    layout = tab_widget.layout()
                    if layout:
                        layout.setSpacing(SPACING["md"])
                        layout.setContentsMargins(
                            SPACING["lg"], SPACING["lg"], 
                            SPACING["lg"], SPACING["lg"]
                        )
                except Exception:
                    # Skip layout configuration if there are issues
                    continue
    
    def apply_modern_styling(self):
        """Apply modern professional styling"""
        try:
            stylesheet = create_professional_stylesheet()
            self.setStyleSheet(stylesheet)
            
            # Apply specific tab styling
            if self.tab_widget:
                apply_style_to_widget(self.tab_widget, COMPONENT_STYLES["tab_widget"])
                
        except Exception as e:
            print(f"[Dashboard] Error applying styling: {e}")
    
    def setup_smart_features(self):
        """Setup smart orchestration features"""
        global SMART_FEATURES_AVAILABLE
        if not SMART_FEATURES_AVAILABLE:
            return
            
        try:
            # Start behavior tracking if using adaptive tab manager
            if hasattr(self.tab_widget, 'behavior_tracker'):
                print("[Dashboard] Smart behavior tracking enabled")
            
            # Initialize AI orchestration monitoring
            if self.ai_orchestration:
                print("[Dashboard] AI orchestration engine ready")
                
        except Exception as e:
            print(f"[Dashboard] Error setting up smart features: {e}")
    
    # Smart feature menu handlers
    def optimize_tabs(self):
        """Manually trigger tab optimization"""
        global SMART_FEATURES_AVAILABLE
        if SMART_FEATURES_AVAILABLE and hasattr(self.tab_widget, 'optimize_tab_order'):
            self.tab_widget.optimize_tab_order()
            print("[Dashboard] Tab order optimized based on usage patterns")
        else:
            print("[Dashboard] Tab optimization not available")
    
    def show_usage_analytics(self):
        """Show user behavior analytics"""
        global SMART_FEATURES_AVAILABLE
        if SMART_FEATURES_AVAILABLE and self.behavior_tracker:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Usage Analytics")
            dialog.setGeometry(200, 200, 600, 400)
            
            layout = QVBoxLayout(dialog)
            
            analytics_text = QTextEdit()
            analytics_text.setReadOnly(True)
            
            # Generate analytics report
            report = self.generate_analytics_report()
            analytics_text.setText(report)
            
            layout.addWidget(analytics_text)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec_()
        else:
            print("[Dashboard] Usage analytics not available")
    
    def show_ai_performance(self):
        """Show AI provider performance metrics"""
        global SMART_FEATURES_AVAILABLE
        if SMART_FEATURES_AVAILABLE and self.ai_orchestration:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("AI Provider Performance")
            dialog.setGeometry(200, 200, 600, 400)
            
            layout = QVBoxLayout(dialog)
            
            performance_text = QTextEdit()
            performance_text.setReadOnly(True)
            
            # Get performance summary
            summary = self.ai_orchestration.get_performance_summary()
            report = "AI Provider Performance Summary\n" + "="*40 + "\n\n"
            
            for provider, metrics in summary.items():
                report += f"Provider: {provider}\n"
                report += f"  Success Rate: {metrics['success_rate']}\n"
                report += f"  Avg Response Time: {metrics['avg_response_time']}\n"
                report += f"  Total Requests: {metrics['total_requests']}\n\n"
            
            if not summary:
                report += "No AI provider metrics available yet.\nStart using AI features to see performance data."
            
            performance_text.setText(report)
            layout.addWidget(performance_text)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec_()
        else:
            print("[Dashboard] AI performance metrics not available")
    
    def reset_user_data(self):
        """Reset user behavior data"""
        global SMART_FEATURES_AVAILABLE
        if SMART_FEATURES_AVAILABLE and self.behavior_tracker:
            from PyQt5.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(self, "Reset User Data",
                                       "Are you sure you want to reset all user behavior data?\n"
                                       "This will clear usage patterns and preferences.",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Reset behavior data
                self.behavior_tracker.session_data = {
                    'tab_usage': defaultdict(int),
                    'feature_usage': defaultdict(int), 
                    'session_duration': defaultdict(float),
                    'error_patterns': defaultdict(int),
                    'ai_provider_preferences': defaultdict(int),
                    'workflow_patterns': deque(maxlen=100)
                }
                self.behavior_tracker.save_behavior_data()
                
                QMessageBox.information(self, "Reset Complete",
                                      "User behavior data has been reset.")
                print("[Dashboard] User behavior data reset")
        else:
            print("[Dashboard] User data reset not available")
    
    def generate_analytics_report(self) -> str:
        """Generate detailed analytics report"""
        global SMART_FEATURES_AVAILABLE
        if not (SMART_FEATURES_AVAILABLE and self.behavior_tracker):
            return "Analytics not available"
        
        data = self.behavior_tracker.session_data
        report = "User Behavior Analytics Report\n" + "="*35 + "\n\n"
        
        # Tab usage statistics
        report += "Tab Usage Statistics:\n" + "-"*25 + "\n"
        for tab, count in sorted(data['tab_usage'].items(), key=lambda x: x[1], reverse=True):
            duration = data['session_duration'].get(tab, 0)
            avg_time = duration / max(count, 1)
            report += f"  {tab}: {count} visits, {avg_time:.1f}s avg duration\n"
        
        # Feature usage
        report += f"\nFeature Usage Statistics:\n" + "-"*28 + "\n"
        for feature, count in sorted(data['feature_usage'].items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  {feature}: {count} uses\n"
        
        # AI provider preferences
        report += f"\nAI Provider Preferences:\n" + "-"*26 + "\n"
        for provider, count in sorted(data['ai_provider_preferences'].items(), key=lambda x: x[1], reverse=True):
            report += f"  {provider}: {count} successful requests\n"
        
        # Error patterns
        if data['error_patterns']:
            report += f"\nError Patterns:\n" + "-"*15 + "\n"
            for error, count in sorted(data['error_patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"  {error}: {count} occurrences\n"
        
        # Session info
        session_time = time.time() - self.behavior_tracker.session_start
        report += f"\nCurrent Session:\n" + "-"*16 + "\n"
        report += f"  Duration: {session_time/60:.1f} minutes\n"
        report += f"  Workflow Actions: {len(data['workflow_patterns'])}\n"
        
        return report
    
    # Menu action handlers
    def export_settings(self):
        """Export dashboard settings"""
        print("[Dashboard] Export settings requested")
    
    def import_settings(self):
        """Import dashboard settings"""
        print("[Dashboard] Import settings requested")
    
    def refresh_all_tabs(self):
        """Refresh all dashboard tabs"""
        print("[Dashboard] Refreshing all tabs")
        for i in range(self.tab_widget.count() if self.tab_widget else 0):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'refresh'):
                tab.refresh()
    
    def reset_layout(self):
        """Reset dashboard layout to defaults"""
        print("[Dashboard] Reset layout requested")
    
    def show_about(self):
        """Show about dialog"""
        from PyQt5.QtWidgets import QMessageBox
        global SMART_FEATURES_AVAILABLE
        about_text = ("Jarvis 1.0.0 - Smart AI Orchestration Dashboard\n\n"
                     "Features:\n"
                     "• Adaptive tab management\n"
                     "• Intelligent user behavior tracking\n"
                     "• AI provider performance optimization\n"
                     "• Professional modular architecture\n\n"
                     f"Smart Features: {'Enabled' if SMART_FEATURES_AVAILABLE else 'Disabled'}")
        
        QMessageBox.about(self, "About Jarvis", about_text)
    
    def show_documentation(self):
        """Show documentation"""
        print("[Dashboard] Documentation requested")

def launch_comprehensive_dashboard():
    """
    Launch the comprehensive dashboard application.
    Maintains compatibility with the original interface.
    """
    if not PYQT_AVAILABLE:
        print("[ERROR] PyQt5 required for comprehensive dashboard")
        print("[INFO] Install with: pip install PyQt5")
        return False
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Jarvis Comprehensive Dashboard")
        app.setApplicationVersion("1.0.0")
        
        dashboard = JarvisComprehensiveDashboard()
        dashboard.show()
        
        print("[GUI] Comprehensive dashboard launched successfully")
        return app.exec_()
    except Exception as e:
        print(f"[ERROR] Failed to launch comprehensive dashboard: {e}")
        return False

if __name__ == "__main__":
    sys.exit(launch_comprehensive_dashboard())