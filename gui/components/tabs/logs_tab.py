#!/usr/bin/env python3
"""
Logs Tab Component - System Logs Management
Professional component for viewing and managing system logs
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, 
                                QPushButton, QLabel, QCheckBox, QFrame, QScrollArea)
    from PyQt5.QtCore import QTimer, Qt
    from PyQt5.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

if PYQT_AVAILABLE:
    from gui.components.base.base_tab import BaseTab
else:
    # Fallback for when PyQt5 is not available
    class BaseTab:
        def __init__(self, title, icon):
            self.title = title
            self.icon = icon

class LogsTab(BaseTab):
    """Professional logs management tab"""
    
    def __init__(self):
        super().__init__("Logs", "📋")
        self.log_content = ""
        self.auto_refresh = True
        self.setup_content()
    
    def setup_content(self):
        """Setup the logs interface"""
        if not PYQT_AVAILABLE:
            return
            
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        # Log level filter
        header_layout.addWidget(QLabel("Log Level:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["All", "Debug", "Info", "Warning", "Error", "Critical"])
        self.log_level_combo.currentTextChanged.connect(self.filter_logs)
        header_layout.addWidget(self.log_level_combo)
        
        # Auto-refresh checkbox
        self.auto_refresh_cb = QCheckBox("Auto Refresh")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        header_layout.addWidget(self.auto_refresh_cb)
        
        # Control buttons
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_logs)
        header_layout.addWidget(self.refresh_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_logs)
        header_layout.addWidget(self.export_btn)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        main_layout.addWidget(self.log_display)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        self.log_count_label = QLabel("Lines: 0")
        status_layout.addWidget(self.log_count_label)
        main_layout.addLayout(status_layout)
        
        self.setLayout(main_layout)
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_logs)
        if self.auto_refresh:
            self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        # Initial load
        self.refresh_logs()
    
    def refresh_logs(self):
        """Refresh log display"""
        try:
            # Get system logs (implementation would read from actual log files)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Simulate log entries - in real implementation, this would read from log files
            sample_logs = [
                f"[{current_time}] INFO: System startup completed successfully",
                f"[{current_time}] DEBUG: GUI components loaded",
                f"[{current_time}] INFO: All modules initialized",
                f"[{current_time}] DEBUG: Memory usage: 45%",
                f"[{current_time}] INFO: Ready for user interaction"
            ]
            
            # Filter logs based on selected level
            filtered_logs = self.filter_log_entries(sample_logs)
            
            # Update display
            self.log_display.clear()
            for log_entry in filtered_logs:
                self.add_log_entry(log_entry)
            
            # Update status
            self.log_count_label.setText(f"Lines: {len(filtered_logs)}")
            self.status_label.setText(f"Last updated: {current_time}")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
    
    def filter_logs(self):
        """Filter logs based on selected level"""
        self.refresh_logs()
    
    def filter_log_entries(self, logs):
        """Filter log entries based on current filter settings"""
        selected_level = self.log_level_combo.currentText().upper()
        if selected_level == "ALL":
            return logs
        
        filtered = []
        for log in logs:
            if selected_level in log.upper():
                filtered.append(log)
        return filtered
    
    def add_log_entry(self, entry):
        """Add a single log entry with appropriate formatting"""
        # Color code based on log level
        if "ERROR" in entry.upper():
            color = "#ff6b6b"
        elif "WARNING" in entry.upper():
            color = "#feca57"
        elif "INFO" in entry.upper():
            color = "#48dbfb"
        elif "DEBUG" in entry.upper():
            color = "#ff9ff3"
        else:
            color = "#ffffff"
        
        formatted_entry = f'<span style="color: {color};">{entry}</span>'
        self.log_display.append(formatted_entry)
    
    def toggle_auto_refresh(self, enabled):
        """Toggle auto-refresh functionality"""
        self.auto_refresh = enabled
        if enabled:
            self.refresh_timer.start(5000)
        else:
            self.refresh_timer.stop()
        
        self.status_label.setText(f"Auto-refresh: {'ON' if enabled else 'OFF'}")
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_display.clear()
        self.log_count_label.setText("Lines: 0")
        self.status_label.setText("Logs cleared")
    
    def export_logs(self):
        """Export logs to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", f"jarvis_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_display.toPlainText())
                self.status_label.setText(f"Logs exported to: {filename}")
            
        except Exception as e:
            self.status_label.setText(f"Export error: {str(e)}")

def create_logs_tab():
    """Factory function to create logs tab"""
    return LogsTab()

if __name__ == "__main__":
    # Test the component
    if PYQT_AVAILABLE:
        from PyQt5.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        tab = LogsTab()
        tab.show()
        sys.exit(app.exec_())
    else:
        print("PyQt5 not available for testing")