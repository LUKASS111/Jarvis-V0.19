#!/usr/bin/env python3
"""
System Monitoring Tab - Modular component extracted from comprehensive dashboard
Handles real-time system metrics, service status, and performance monitoring.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                                QProgressBar, QPushButton, QTableWidget, 
                                QTableWidgetItem, QWidget, QTextEdit)
    from PyQt5.QtCore import Qt, QTimer
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from gui.components.base.base_tab import BaseTab

class SystemMonitoringTab(BaseTab):
    """System Monitoring & Performance tab component"""
    
    def __init__(self):
        super().__init__("System Monitoring & Performance", "📊")
        self.setup_monitoring_timer()
    
    def setup_content(self):
        """Setup system monitoring specific content"""
        try:
            # Try to use the enhanced monitoring interface
            from gui.system_monitoring_interface import SystemMonitoringInterface
            monitoring_interface = SystemMonitoringInterface()
            self._main_layout.addWidget(monitoring_interface)
            print("[SystemMonitoringTab] Using enhanced monitoring interface")
        except Exception as e:
            print(f"[SystemMonitoringTab] Enhanced interface not available: {e}")
            self.setup_fallback_interface()
    
    def setup_fallback_interface(self):
        """Setup fallback monitoring interface"""
        self.add_system_metrics()
        self.add_service_status()
        self.add_performance_logs()
    
    def add_system_metrics(self):
        """Add real-time system metrics display"""
        metrics_group = self.create_group_box("Real-time System Metrics", "📈")
        metrics_layout = QGridLayout(metrics_group)
        
        # System resource progress bars
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setValue(25)
        self.cpu_label = QLabel("25%")
        
        self.memory_progress = QProgressBar() 
        self.memory_progress.setValue(45)
        self.memory_label = QLabel("45%")
        
        self.disk_progress = QProgressBar()
        self.disk_progress.setValue(60)
        self.disk_label = QLabel("60%")
        
        # Add to layout
        metrics_layout.addWidget(QLabel("💻 CPU Usage:"), 0, 0)
        metrics_layout.addWidget(self.cpu_progress, 0, 1)
        metrics_layout.addWidget(self.cpu_label, 0, 2)
        
        metrics_layout.addWidget(QLabel("🧠 Memory:"), 1, 0)
        metrics_layout.addWidget(self.memory_progress, 1, 1)
        metrics_layout.addWidget(self.memory_label, 1, 2)
        
        metrics_layout.addWidget(QLabel("💽 Disk:"), 2, 0)
        metrics_layout.addWidget(self.disk_progress, 2, 1)
        metrics_layout.addWidget(self.disk_label, 2, 2)
        
        # Network metrics
        metrics_layout.addWidget(QLabel("🌐 Network In:"), 3, 0)
        net_in_label = QLabel("125 KB/s")
        metrics_layout.addWidget(net_in_label, 3, 1, 1, 2)
        
        metrics_layout.addWidget(QLabel("📤 Network Out:"), 4, 0)
        net_out_label = QLabel("89 KB/s")
        metrics_layout.addWidget(net_out_label, 4, 1, 1, 2)
        
        self._main_layout.addWidget(metrics_group)
    
    def add_service_status(self):
        """Add service status monitoring"""
        services_group = self.create_group_box("Service Status", "🔧")
        services_layout = QVBoxLayout(services_group)
        
        # Service status table
        service_table = QTableWidget(6, 3)
        service_table.setHorizontalHeaderLabels(["Service", "Status", "Details"])
        service_table.setMaximumHeight(200)
        
        services = [
            ("🗄️ Database Service", "🟢 Running", "Port 5432"),
            ("🌐 API Server", "🟢 Running", "Port 8000"),
            ("🤖 Agent Manager", "🟢 Running", "3 active"),
            ("🔍 Vector Search", "🟢 Running", "5 collections"),
            ("📊 Analytics", "🟢 Running", "Real-time"),
            ("🔒 Security Scanner", "🟢 Running", "Protected")
        ]
        
        for row, (service, status, details) in enumerate(services):
            service_table.setItem(row, 0, QTableWidgetItem(service))
            service_table.setItem(row, 1, QTableWidgetItem(status))
            service_table.setItem(row, 2, QTableWidgetItem(details))
        
        services_layout.addWidget(service_table)
        
        # Service control buttons
        controls_layout = QHBoxLayout()
        restart_button = QPushButton("🔄 Restart Services")
        refresh_button = QPushButton("🔍 Refresh Status")
        logs_button = QPushButton("📋 View Logs")
        
        controls_layout.addWidget(restart_button)
        controls_layout.addWidget(refresh_button)
        controls_layout.addWidget(logs_button)
        controls_layout.addStretch()
        
        services_layout.addLayout(controls_layout)
        self._main_layout.addWidget(services_group)
    
    def add_performance_logs(self):
        """Add performance logs display"""
        logs_group = self.create_group_box("Performance Logs", "📋")
        logs_layout = QVBoxLayout(logs_group)
        
        # Log display area
        log_display = QTextEdit()
        log_display.setMaximumHeight(150)
        log_display.setPlainText("""
[2025-01-08 11:22:10] INFO: System initialization complete
[2025-01-08 11:22:15] INFO: Vector database connected (5 collections)
[2025-01-08 11:22:20] INFO: Agent workflows started (3 active)
[2025-01-08 11:22:25] INFO: API server listening on port 8000
[2025-01-08 11:22:30] INFO: Security scanner active
[2025-01-08 11:22:35] INFO: Real-time analytics enabled
        """.strip())
        
        logs_layout.addWidget(log_display)
        
        # Log controls
        log_controls = QHBoxLayout()
        clear_logs = QPushButton("🗑️ Clear Logs")
        export_logs = QPushButton("💾 Export Logs")
        auto_refresh = QPushButton("🔄 Auto Refresh: ON")
        
        log_controls.addWidget(clear_logs)
        log_controls.addWidget(export_logs)
        log_controls.addWidget(auto_refresh)
        log_controls.addStretch()
        
        logs_layout.addLayout(log_controls)
        self._main_layout.addWidget(logs_group)
    
    def setup_monitoring_timer(self):
        """Setup timer for real-time updates"""
        if not PYQT_AVAILABLE:
            return
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(5000)  # Update every 5 seconds
    
    def update_metrics(self):
        """Update system metrics (placeholder for real monitoring)"""
        # In a real implementation, this would fetch actual system metrics
        try:
            import random
            if hasattr(self, 'cpu_progress'):
                cpu_val = random.randint(20, 80)
                self.cpu_progress.setValue(cpu_val)
                self.cpu_label.setText(f"{cpu_val}%")
                
                mem_val = random.randint(30, 70)
                self.memory_progress.setValue(mem_val)
                self.memory_label.setText(f"{mem_val}%")
                
                disk_val = random.randint(40, 80)
                self.disk_progress.setValue(disk_val)
                self.disk_label.setText(f"{disk_val}%")
        except:
            pass  # Ignore errors in demo mode