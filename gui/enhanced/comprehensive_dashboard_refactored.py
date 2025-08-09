#!/usr/bin/env python3
"""
Refactored Comprehensive Dashboard for Jarvis 1.0.0
Clean, modular architecture using component-based design.
Replaces the monolithic 1705-line comprehensive_dashboard.py with focused modules.
"""

import sys
import os
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
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

class JarvisComprehensiveDashboard(QMainWindow if PYQT_AVAILABLE else object):
    """
    Refactored comprehensive dashboard with modular tab architecture.
    Replaces the 1705-line monolithic implementation.
    """
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            print("GUI not available - PyQt5 required")
            return
            
        super().__init__()
        self.tab_widget = None
        self.init_ui()
        self.apply_modern_styling()
    
    def init_ui(self):
        """Initialize the user interface with modular tabs"""
        self.setWindowTitle("Jarvis 1.0.0 - Comprehensive Professional Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup menu and status bar
        self.setup_menu_bar()
        self.setup_status_bar()
        
        # Load all tabs using factory pattern
        self.load_tabs()
        
        # Setup responsive layout
        self.setup_responsive_layout()
    
    def setup_menu_bar(self):
        """Setup application menu bar"""
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
            if hasattr(tab_widget, 'layout') and tab_widget.layout():
                layout = tab_widget.layout()
                layout.setSpacing(SPACING["md"])
                layout.setContentsMargins(
                    SPACING["lg"], SPACING["lg"], 
                    SPACING["lg"], SPACING["lg"]
                )
    
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
        QMessageBox.about(self, "About Jarvis", 
                         "Jarvis 1.0.0\nComprehensive AI Assistant Dashboard\n\n"
                         "Built with modular architecture for enhanced maintainability.")
    
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