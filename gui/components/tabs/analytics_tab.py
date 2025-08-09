#!/usr/bin/env python3
"""
Analytics Tab Component - System Analytics and Metrics
Professional component for viewing system analytics and performance metrics
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                                QPushButton, QFrame, QProgressBar, QTableWidget, 
                                QTableWidgetItem, QTabWidget)
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

class AnalyticsTab(BaseTab):
    """Professional analytics and metrics tab"""
    
    def __init__(self):
        super().__init__("Analytics", "📊")
        self.setup_content()
    
    def setup_content(self):
        """Setup the analytics interface"""
        if not PYQT_AVAILABLE:
            return
            
        # Main layout
        main_layout = QVBoxLayout()
        
        # Create tabbed interface for different analytics categories
        analytics_tabs = QTabWidget()
        
        # System Performance Tab
        self.create_performance_tab(analytics_tabs)
        
        # Usage Statistics Tab  
        self.create_usage_tab(analytics_tabs)
        
        # Trends Tab
        self.create_trends_tab(analytics_tabs)
        
        main_layout.addWidget(analytics_tabs)
        self.setLayout(main_layout)
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
        
        # Initial load
        self.refresh_analytics()
    
    def create_performance_tab(self, parent):
        """Create system performance analytics tab"""
        perf_widget = QFrame()
        layout = QVBoxLayout(perf_widget)
        
        # Header
        header = QLabel("System Performance Metrics")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        
        # CPU Usage
        cpu_frame = self.create_metric_frame("CPU Usage", "75%", "#3498db")
        metrics_layout.addWidget(cpu_frame, 0, 0)
        
        # Memory Usage
        memory_frame = self.create_metric_frame("Memory Usage", "60%", "#e74c3c")
        metrics_layout.addWidget(memory_frame, 0, 1)
        
        # Disk I/O
        disk_frame = self.create_metric_frame("Disk I/O", "45%", "#f39c12")
        metrics_layout.addWidget(disk_frame, 1, 0)
        
        # Network
        network_frame = self.create_metric_frame("Network", "30%", "#27ae60")
        metrics_layout.addWidget(network_frame, 1, 1)
        
        layout.addLayout(metrics_layout)
        
        # Performance progress bars
        self.create_progress_section(layout)
        
        parent.addTab(perf_widget, "Performance")
    
    def create_usage_tab(self, parent):
        """Create usage statistics tab"""
        usage_widget = QFrame()
        layout = QVBoxLayout(usage_widget)
        
        # Header
        header = QLabel("Usage Statistics")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Statistics table
        self.usage_table = QTableWidget(10, 3)
        self.usage_table.setHorizontalHeaderLabels(["Function", "Usage Count", "Last Used"])
        self.usage_table.setStyleSheet("""
            QTableWidget {
                background-color: #ecf0f1;
                gridline-color: #bdc3c7;
                border: 1px solid #95a5a6;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
        """)
        
        # Populate with sample data
        self.populate_usage_table()
        
        layout.addWidget(self.usage_table)
        
        parent.addTab(usage_widget, "Usage Stats")
    
    def create_trends_tab(self, parent):
        """Create trends analysis tab"""
        trends_widget = QFrame()
        layout = QVBoxLayout(trends_widget)
        
        # Header
        header = QLabel("Performance Trends")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Trend indicators
        trends_layout = QGridLayout()
        
        # Response Time Trend
        response_trend = self.create_trend_indicator("Response Time", "↓ 15%", "#27ae60", "Improving")
        trends_layout.addWidget(response_trend, 0, 0)
        
        # Memory Usage Trend
        memory_trend = self.create_trend_indicator("Memory Usage", "↑ 8%", "#e74c3c", "Increasing")
        trends_layout.addWidget(memory_trend, 0, 1)
        
        # Error Rate Trend
        error_trend = self.create_trend_indicator("Error Rate", "↓ 25%", "#27ae60", "Decreasing")
        trends_layout.addWidget(error_trend, 1, 0)
        
        # Throughput Trend
        throughput_trend = self.create_trend_indicator("Throughput", "↑ 12%", "#27ae60", "Improving")
        trends_layout.addWidget(throughput_trend, 1, 1)
        
        layout.addLayout(trends_layout)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Trends")
        refresh_btn.clicked.connect(self.refresh_trends)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        
        parent.addTab(trends_widget, "Trends")
    
    def create_metric_frame(self, title, value, color):
        """Create a metric display frame"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet(f"color: {color}; margin: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setStyleSheet("color: #2c3e50; margin: 5px;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        return frame
    
    def create_progress_section(self, parent_layout):
        """Create progress bars section"""
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.StyledPanel)
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin: 10px 0;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(progress_frame)
        
        # Performance metrics with progress bars
        self.cpu_progress = self.create_progress_bar("CPU Performance", 75)
        layout.addWidget(self.cpu_progress)
        
        self.memory_progress = self.create_progress_bar("Memory Efficiency", 60)
        layout.addWidget(self.memory_progress)
        
        self.response_progress = self.create_progress_bar("Response Time", 85)
        layout.addWidget(self.response_progress)
        
        parent_layout.addWidget(progress_frame)
    
    def create_progress_bar(self, label, value):
        """Create a labeled progress bar"""
        container = QFrame()
        layout = QHBoxLayout(container)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(150)
        layout.addWidget(label_widget)
        
        # Progress bar
        progress = QProgressBar()
        progress.setValue(value)
        progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(progress)
        
        # Value label
        value_label = QLabel(f"{value}%")
        value_label.setMinimumWidth(50)
        layout.addWidget(value_label)
        
        return container
    
    def create_trend_indicator(self, title, change, color, status):
        """Create a trend indicator widget"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 4px;
                margin: 5px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Change value
        change_label = QLabel(change)
        change_label.setFont(QFont("Arial", 16, QFont.Bold))
        change_label.setStyleSheet(f"color: {color};")
        layout.addWidget(change_label)
        
        # Status
        status_label = QLabel(status)
        status_label.setFont(QFont("Arial", 8))
        status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(status_label)
        
        return frame
    
    def populate_usage_table(self):
        """Populate the usage statistics table with sample data"""
        functions = [
            ("AI Processing", 145, "2 hours ago"),
            ("Memory Management", 89, "1 hour ago"),
            ("System Monitoring", 234, "30 minutes ago"),
            ("Vector Database", 67, "45 minutes ago"),
            ("Configuration", 23, "3 hours ago"),
            ("Analytics", 156, "15 minutes ago"),
            ("Log Viewing", 78, "1 hour ago"),
            ("Help System", 34, "2 hours ago"),
            ("Development Tools", 45, "90 minutes ago"),
            ("Agent Workflows", 67, "25 minutes ago")
        ]
        
        for row, (func, count, last_used) in enumerate(functions):
            self.usage_table.setItem(row, 0, QTableWidgetItem(func))
            self.usage_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.usage_table.setItem(row, 2, QTableWidgetItem(last_used))
        
        self.usage_table.resizeColumnsToContents()
    
    def refresh_analytics(self):
        """Refresh all analytics data"""
        # Update progress bars with simulated values
        if hasattr(self, 'cpu_progress'):
            new_cpu = random.randint(50, 90)
            self.update_progress_bar(self.cpu_progress, new_cpu)
        
        if hasattr(self, 'memory_progress'):
            new_memory = random.randint(40, 80)
            self.update_progress_bar(self.memory_progress, new_memory)
        
        if hasattr(self, 'response_progress'):
            new_response = random.randint(70, 95)
            self.update_progress_bar(self.response_progress, new_response)
    
    def update_progress_bar(self, container, value):
        """Update a progress bar with new value"""
        layout = container.layout()
        if layout and layout.count() >= 2:
            progress_bar = layout.itemAt(1).widget()
            value_label = layout.itemAt(2).widget()
            if isinstance(progress_bar, QProgressBar):
                progress_bar.setValue(value)
                value_label.setText(f"{value}%")
    
    def refresh_trends(self):
        """Refresh trend indicators"""
        print("[Analytics] Refreshing trend data...")

def create_analytics_tab():
    """Factory function to create analytics tab"""
    return AnalyticsTab()

if __name__ == "__main__":
    # Test the component
    if PYQT_AVAILABLE:
        from PyQt5.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        tab = AnalyticsTab()
        tab.show()
        sys.exit(app.exec_())
    else:
        print("PyQt5 not available for testing")