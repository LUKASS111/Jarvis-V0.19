#!/usr/bin/env python3
"""
Production GUI Interface for Jarvis v1.0
Enterprise-grade interface leveraging full backend capabilities
"""

import sys
import os
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Backend imports
from jarvis.backend import get_jarvis_backend, shutdown_jarvis_backend
from jarvis.core.error_handler import error_handler, ErrorLevel

# GUI Framework
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QGridLayout, QTabWidget, QTextEdit, QLineEdit, QPushButton,
        QLabel, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
        QProgressBar, QComboBox, QSpinBox, QSlider, QGroupBox, QSplitter,
        QListWidget, QListWidgetItem, QMenuBar, QMenu, QAction, QStatusBar,
        QToolBar, QFileDialog, QMessageBox, QInputDialog, QDialog,
        QFormLayout, QCheckBox, QFrame, QScrollArea, QSizePolicy
    )
    from PyQt5.QtCore import (
        Qt, QTimer, QThread, pyqtSignal, QObject, QSize
    )
    from PyQt5.QtGui import (
        QFont, QPixmap, QIcon, QPalette, QColor, QTextCursor
    )
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Don't exit immediately - create mock classes for testing
    print("[INFO] PyQt5 not available. Production GUI will fallback to CLI mode.")
    
    # Create minimal mock classes for import compatibility
    class QObject:
        def __init__(self, *args, **kwargs): 
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    class QMainWindow:
        def __init__(self, *args, **kwargs): pass
    class QWidget:
        def __init__(self, *args, **kwargs): pass
    def pyqtSignal(*args): 
        return lambda f: f

class SessionManager(QObject):
    """Manages backend session and communication"""
    
    # Define signals as class attributes (required for PyQt5)
    if PYQT_AVAILABLE:
        session_created = pyqtSignal(str)
        response_received = pyqtSignal(dict)
        error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.backend = get_jarvis_backend()
        self.session_id = None
        
        # Initialize mock signals if PyQt5 not available
        if not PYQT_AVAILABLE:
            try:
                from unittest.mock import Mock
                self.session_created = Mock()
                self.response_received = Mock()
                self.error_occurred = Mock()
            except ImportError:
                # Create simple callable mocks
                self.session_created = lambda x: None
                self.response_received = lambda x: None
                self.error_occurred = lambda x: None
        
        self.initialize_session()
    
    def initialize_session(self):
        """
        Initialize a new session with the backend.
        
        Creates a new session with the unified backend service, enabling
        persistent conversation history and state management.
        
        Raises:
            Exception: If session creation fails or backend is unavailable
            
        Emits:
            session_created: When session is successfully created
            error_occurred: When session creation fails
        """
        try:
            self.session_id = self.backend.create_session(
                session_type="production_gui",
                metadata={"interface": "production_gui", "version": "1.0.0"}
            )
            if self.session_id:
                self.session_created.emit(self.session_id)
                print(f"[GUI] Session created: {self.session_id[:8]}")
            else:
                self.error_occurred.emit("Failed to create backend session")
        except Exception as e:
            self.error_occurred.emit(f"Session initialization failed: {str(e)}")
    
    def send_request(self, request_type: str, data: Dict[str, Any]):
        """
        Send request to backend service.
        
        Args:
            request_type (str): Type of request ('chat', 'memory', 'file', etc.)
            data (Dict[str, Any]): Request data with parameters
            
        Raises:
            Exception: If request processing fails or session is invalid
            
        Emits:
            response_received: When response is successfully received
            error_occurred: When request fails or session is invalid
        """
        if not self.session_id:
            self.error_occurred.emit("No active session")
            return
        
        try:
            response = self.backend.process_request(self.session_id, request_type, data)
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(f"Request failed: {str(e)}")
    
    def get_session_info(self):
        """
        Get current session information.
        
        Returns:
            Dict[str, Any] or None: Session information including metadata,
                creation time, and status, or None if no active session
        """
        if self.session_id:
            return self.backend.get_session_info(self.session_id)
        return None
    
    def get_conversation_history(self, limit=50):
        """
        Get conversation history from current session.
        
        Args:
            limit (int): Maximum number of conversation entries to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of conversation entries with timestamps,
                user messages, and assistant responses, or empty list if no session
        """
        if self.session_id:
            return self.backend.get_conversation_history(self.session_id, limit)
        return []

class ConversationWidget(QWidget):
    """
    Advanced conversation interface with history management.
    
    Provides a full-featured chat interface with conversation history,
    model selection, and export capabilities. Integrates with the
    unified backend service for persistent session management.
    
    Attributes:
        session_manager (SessionManager): Backend session manager
        conversation_display (QTextEdit): Main conversation view
        message_input (QLineEdit): User message input field
        model_selector (QComboBox): LLM model selection dropdown
    """
    
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Conversation display
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setMinimumHeight(400)
        
        # Input section
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter your message to Jarvis...")
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumSize(80, 35)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear Conversation")
        self.export_button = QPushButton("Export History")
        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama3:8b", "codellama:13b", "llama3:70b", "auto"])
        
        controls_layout.addWidget(QLabel("Model:"))
        controls_layout.addWidget(self.model_selector)
        controls_layout.addStretch()
        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.export_button)
        
        layout.addWidget(self.conversation_display)
        layout.addLayout(controls_layout)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
    
    def connect_signals(self):
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        self.clear_button.clicked.connect(self.clear_conversation)
        self.export_button.clicked.connect(self.export_conversation)
        self.session_manager.response_received.connect(self.handle_response)
    
    def send_message(self):
        """
        Send user message to the backend LLM service.
        
        Retrieves message from input field, clears the field, displays
        the message in conversation view, and sends to backend with
        current model selection and parameters.
        
        Does nothing if message field is empty.
        """
        message = self.message_input.text().strip()
        if not message:
            return
        
        self.message_input.clear()
        self.add_message("User", message)
        
        # Send to backend
        self.session_manager.send_request("chat", {
            "message": message,
            "model": self.model_selector.currentText(),
            "temperature": 0.7,
            "max_tokens": 2000
        })
    
    def handle_response(self, response):
        """
        Handle response from backend service.
        
        Args:
            response (Dict[str, Any]): Backend response containing success
                status, data payload, and error information if applicable
                
        Displays successful chat responses in conversation view or
        shows error messages for failed requests.
        """
        if response.get("success") and "data" in response:
            chat_data = response["data"].get("chat_response", {})
            assistant_message = chat_data.get("response", "No response received")
            self.add_message("Jarvis", assistant_message)
        else:
            self.add_message("System", f"Error: {response.get('error', 'Unknown error')}")
    
    def add_message(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"<div style='margin: 10px; padding: 10px; border-left: 3px solid {'#48bb78' if sender == 'User' else '#667eea' if sender == 'Jarvis' else '#ed8936'};'>"
        formatted_message += f"<strong>[{timestamp}] {sender}:</strong><br>"
        formatted_message += f"<span style='margin-left: 10px;'>{message}</span></div>"
        
        self.conversation_display.insertHtml(formatted_message)
        
        # Scroll to bottom
        cursor = self.conversation_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.conversation_display.setTextCursor(cursor)
    
    def clear_conversation(self):
        self.conversation_display.clear()
    
    def export_conversation(self):
        history = self.session_manager.get_conversation_history()
        if not history:
            QMessageBox.information(self, "Export", "No conversation history to export")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Conversation", 
            f"jarvis_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Export", f"Conversation exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

class MemoryManagementWidget(QWidget):
    """Advanced memory management interface"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Left side - Memory operations
        left_panel = QVBoxLayout()
        
        # Store memory section
        store_group = QGroupBox("Store Information")
        store_layout = QFormLayout()
        
        self.store_content = QTextEdit()
        self.store_content.setPlaceholderText("Enter information to store in memory...")
        self.store_content.setMaximumHeight(100)
        
        self.store_category = QLineEdit()
        self.store_category.setPlaceholderText("Category (optional)")
        
        self.store_tags = QLineEdit()
        self.store_tags.setPlaceholderText("Tags (comma-separated)")
        
        self.store_button = QPushButton("Store in Memory")
        
        store_layout.addRow("Content:", self.store_content)
        store_layout.addRow("Category:", self.store_category)
        store_layout.addRow("Tags:", self.store_tags)
        store_layout.addRow(self.store_button)
        store_group.setLayout(store_layout)
        
        # Search memory section
        search_group = QGroupBox("Search Memory")
        search_layout = QFormLayout()
        
        self.search_query = QLineEdit()
        self.search_query.setPlaceholderText("Enter search query...")
        
        self.search_category = QComboBox()
        self.search_category.addItems(["All Categories", "personal", "work", "projects", "notes"])
        self.search_category.setEditable(True)
        
        self.search_button = QPushButton("Search")
        self.recall_button = QPushButton("Recall All")
        
        search_layout.addRow("Query:", self.search_query)
        search_layout.addRow("Category:", self.search_category)
        
        search_buttons = QHBoxLayout()
        search_buttons.addWidget(self.search_button)
        search_buttons.addWidget(self.recall_button)
        search_layout.addRow(search_buttons)
        
        search_group.setLayout(search_layout)
        
        left_panel.addWidget(store_group)
        left_panel.addWidget(search_group)
        left_panel.addStretch()
        
        # Right side - Memory results
        right_panel = QVBoxLayout()
        
        results_group = QGroupBox("Memory Results")
        results_layout = QVBoxLayout()
        
        self.memory_results = QTextEdit()
        self.memory_results.setReadOnly(True)
        self.memory_results.setPlaceholderText("Memory search results will appear here...")
        
        # Memory statistics
        stats_layout = QHBoxLayout()
        self.memory_stats = QLabel("Memory stats will appear here")
        stats_layout.addWidget(self.memory_stats)
        
        results_layout.addWidget(self.memory_results)
        results_layout.addLayout(stats_layout)
        results_group.setLayout(results_layout)
        
        right_panel.addWidget(results_group)
        
        # Add panels to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def connect_signals(self):
        self.store_button.clicked.connect(self.store_memory)
        self.search_button.clicked.connect(self.search_memory)
        self.recall_button.clicked.connect(self.recall_all)
        self.search_query.returnPressed.connect(self.search_memory)
        self.session_manager.response_received.connect(self.handle_memory_response)
    
    def store_memory(self):
        content = self.store_content.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Invalid Input", "Please enter content to store")
            return
        
        data = {
            "content": content,
            "category": self.store_category.text().strip() or "general",
            "tags": [tag.strip() for tag in self.store_tags.text().split(",") if tag.strip()]
        }
        
        self.session_manager.send_request("memory_store", data)
        self.store_content.clear()
        self.store_category.clear()
        self.store_tags.clear()
    
    def search_memory(self):
        query = self.search_query.text().strip()
        if not query:
            QMessageBox.warning(self, "Invalid Input", "Please enter a search query")
            return
        
        category = self.search_category.currentText()
        if category == "All Categories":
            category = None
        
        data = {
            "query": query,
            "category": category,
            "limit": 20
        }
        
        self.session_manager.send_request("memory_search", data)
    
    def recall_all(self):
        self.session_manager.send_request("memory_recall", {"limit": 50})
    
    def handle_memory_response(self, response):
        if not response.get("success"):
            self.memory_results.append(f"Error: {response.get('error', 'Unknown error')}")
            return
        
        data = response.get("data", {})
        
        if "memory_store" in str(response):
            self.memory_results.append(f"✓ Stored: {data.get('message', 'Information stored successfully')}")
        elif "search_results" in data:
            results = data["search_results"]
            self.display_search_results(results)
        elif "recall_results" in data:
            results = data["recall_results"]
            self.display_recall_results(results)
    
    def display_search_results(self, results):
        self.memory_results.clear()
        if not results:
            self.memory_results.append("No search results found.")
            return
        
        self.memory_results.append(f"Found {len(results)} search results:\n")
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "No content")
            category = result.get("category", "No category")
            timestamp = result.get("timestamp", "No timestamp")
            
            self.memory_results.append(f"{i}. [{category}] {content}")
            self.memory_results.append(f"   Time: {timestamp}\n")
    
    def display_recall_results(self, results):
        self.memory_results.clear()
        if not results:
            self.memory_results.append("No memories found.")
            return
        
        self.memory_results.append(f"Recalled {len(results)} memories:\n")
        
        for i, memory in enumerate(results, 1):
            content = memory.get("content", "No content")
            category = memory.get("category", "No category")
            
            self.memory_results.append(f"{i}. [{category}] {content}\n")

class FileProcessingWidget(QWidget):
    """File processing interface"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox("File Processing")
        file_layout = QFormLayout()
        
        file_select_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Select a file to process...")
        self.browse_button = QPushButton("Browse")
        file_select_layout.addWidget(self.file_path)
        file_select_layout.addWidget(self.browse_button)
        
        self.process_button = QPushButton("Process File")
        self.process_button.setEnabled(False)
        
        file_layout.addRow("File:", file_select_layout)
        file_layout.addRow(self.process_button)
        file_group.setLayout(file_layout)
        
        # Processing results
        results_group = QGroupBox("Processing Results")
        results_layout = QVBoxLayout()
        
        self.processing_results = QTextEdit()
        self.processing_results.setReadOnly(True)
        self.processing_results.setPlaceholderText("File processing results will appear here...")
        
        results_layout.addWidget(self.processing_results)
        results_group.setLayout(results_layout)
        
        layout.addWidget(file_group)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
    
    def connect_signals(self):
        self.browse_button.clicked.connect(self.browse_file)
        self.process_button.clicked.connect(self.process_file)
        self.file_path.textChanged.connect(self.on_file_path_changed)
        self.session_manager.response_received.connect(self.handle_file_response)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Process",
            "", "All Files (*.*)"
        )
        
        if file_path:
            self.file_path.setText(file_path)
    
    def on_file_path_changed(self, text):
        self.process_button.setEnabled(bool(text.strip()))
    
    def process_file(self):
        file_path = self.file_path.text().strip()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Invalid File", "Please select a valid file")
            return
        
        self.processing_results.append(f"Processing file: {file_path}")
        
        data = {
            "file_path": file_path,
            "extract_text": True,
            "analyze_content": True
        }
        
        self.session_manager.send_request("file_process", data)
    
    def handle_file_response(self, response):
        if "file_process" not in str(response):
            return
        
        if not response.get("success"):
            self.processing_results.append(f"Error: {response.get('error', 'Unknown error')}")
            return
        
        data = response.get("data", {})
        file_data = data.get("file_response", {})
        
        self.processing_results.append("✓ File processed successfully!")
        self.processing_results.append(f"File type: {file_data.get('file_type', 'Unknown')}")
        self.processing_results.append(f"Size: {file_data.get('size', 'Unknown')} bytes")
        
        if "content" in file_data:
            content = file_data["content"]
            self.processing_results.append(f"\nExtracted content (first 500 chars):")
            self.processing_results.append(content[:500] + ("..." if len(content) > 500 else ""))

class SystemMonitoringWidget(QWidget):
    """System monitoring and analytics"""
    
    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self.setup_ui()
        self.setup_timer()
        self.update_system_status()
    
    def setup_ui(self):
        layout = QGridLayout()
        
        # System status overview
        status_group = QGroupBox("System Status")
        status_layout = QFormLayout()
        
        self.service_status = QLabel("Checking...")
        self.uptime_label = QLabel("Checking...")
        self.session_count = QLabel("Checking...")
        self.request_count = QLabel("Checking...")
        self.success_rate = QLabel("Checking...")
        
        status_layout.addRow("Service Status:", self.service_status)
        status_layout.addRow("Uptime:", self.uptime_label)
        status_layout.addRow("Active Sessions:", self.session_count)
        status_layout.addRow("Total Requests:", self.request_count)
        status_layout.addRow("Success Rate:", self.success_rate)
        
        status_group.setLayout(status_layout)
        
        # Subsystem health
        subsystem_group = QGroupBox("Subsystem Health")
        subsystem_layout = QFormLayout()
        
        self.memory_health = QLabel("Checking...")
        self.llm_health = QLabel("Checking...")
        self.api_health = QLabel("Checking...")
        
        subsystem_layout.addRow("Memory System:", self.memory_health)
        subsystem_layout.addRow("LLM System:", self.llm_health)
        subsystem_layout.addRow("API System:", self.api_health)
        
        subsystem_group.setLayout(subsystem_layout)
        
        # Performance metrics
        performance_group = QGroupBox("Performance Metrics")
        performance_layout = QVBoxLayout()
        
        self.system_metrics = QTextEdit()
        self.system_metrics.setReadOnly(True)
        self.system_metrics.setMaximumHeight(200)
        
        performance_layout.addWidget(self.system_metrics)
        performance_group.setLayout(performance_layout)
        
        # Controls
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh Now")
        self.auto_refresh = QCheckBox("Auto-refresh (30s)")
        self.auto_refresh.setChecked(True)
        
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.auto_refresh)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        
        # Layout grid
        layout.addWidget(status_group, 0, 0)
        layout.addWidget(subsystem_group, 0, 1)
        layout.addWidget(performance_group, 1, 0, 1, 2)
        layout.addWidget(controls_group, 2, 0, 1, 2)
        
        self.setLayout(layout)
        
        # Connect signals
        self.refresh_button.clicked.connect(self.update_system_status)
    
    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_update)
        self.update_timer.start(30000)  # 30 seconds
    
    def auto_update(self):
        if self.auto_refresh.isChecked():
            self.update_system_status()
    
    def update_system_status(self):
        try:
            status = self.session_manager.backend.get_system_status()
            
            # Service status
            service_info = status.get("service", {})
            self.service_status.setText(f"🟢 {service_info.get('status', 'unknown').title()}")
            
            uptime = service_info.get("uptime", 0)
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            self.uptime_label.setText(f"{hours}h {minutes}m")
            
            # Session info
            sessions = status.get("sessions", {})
            self.session_count.setText(str(sessions.get("active", 0)))
            
            # Request info
            requests = status.get("requests", {})
            self.request_count.setText(str(requests.get("total", 0)))
            
            success_rate = requests.get("success_rate", 0) * 100
            self.success_rate.setText(f"{success_rate:.1f}%")
            
            # Subsystem health
            subsystems = status.get("subsystems", {})
            health = subsystems.get("health", {})
            
            self.memory_health.setText(self._format_health(health.get("memory", {})))
            self.llm_health.setText(self._format_health(health.get("llm", {})))
            self.api_health.setText(self._format_health(health.get("api", {})))
            
            # System metrics
            metrics = status.get("system_metrics", {})
            self.system_metrics.clear()
            
            metrics_text = "System Performance Metrics:\n\n"
            metrics_text += f"Health Score: {metrics.get('health_score', 'N/A')}/100\n"
            
            if "memory" in metrics:
                mem = metrics["memory"]
                metrics_text += f"Memory Usage: {mem.get('percent', 'N/A')}%\n"
                metrics_text += f"Available: {mem.get('available_gb', 'N/A')} GB\n"
            
            if "cpu" in metrics:
                cpu = metrics["cpu"]
                metrics_text += f"CPU Usage: {cpu.get('percent', 'N/A')}%\n"
            
            self.system_metrics.setText(metrics_text)
            
        except Exception as e:
            error_handler.log_error(e, "System Status Update", ErrorLevel.WARNING)
            self.service_status.setText("🔴 Error")
    
    def _format_health(self, health_data):
        if not health_data:
            return "❓ Unknown"
        
        status = health_data.get("status", "unknown")
        score = health_data.get("score", 0)
        
        if status == "operational" and score >= 90:
            return f"🟢 Excellent ({score}%)"
        elif status == "operational" and score >= 75:
            return f"🟡 Good ({score}%)"
        elif status == "operational":
            return f"🟠 Fair ({score}%)"
        else:
            return f"🔴 {status.title()}"

class ProductionGUI(QMainWindow):
    """Main production GUI application"""
    
    def __init__(self):
        super().__init__()
        self.session_manager = SessionManager()
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.connect_signals()
        
        # Set window properties
        self.setWindowTitle("Jarvis AI Assistant - Production Interface v1.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.conversation_tab = ConversationWidget(self.session_manager)
        self.memory_tab = MemoryManagementWidget(self.session_manager)
        self.file_tab = FileProcessingWidget(self.session_manager)
        self.system_tab = SystemMonitoringWidget(self.session_manager)
        
        self.tab_widget.addTab(self.conversation_tab, "💬 Conversation")
        self.tab_widget.addTab(self.memory_tab, "🧠 Memory")
        self.tab_widget.addTab(self.file_tab, "📁 Files")
        self.tab_widget.addTab(self.system_tab, "📊 System")
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_session_action = QAction("New Session", self)
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        system_status_action = QAction("System Status", self)
        system_status_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        tools_menu.addAction(system_status_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        self.status_bar = self.statusBar()
        self.session_label = QLabel("Initializing...")
        self.status_bar.addPermanentWidget(self.session_label)
    
    def connect_signals(self):
        self.session_manager.session_created.connect(self.on_session_created)
        self.session_manager.error_occurred.connect(self.on_error)
    
    def on_session_created(self, session_id):
        self.session_label.setText(f"Session: {session_id[:8]}")
        self.status_bar.showMessage("Production backend connected successfully", 3000)
    
    def on_error(self, error_message):
        self.status_bar.showMessage(f"Error: {error_message}", 5000)
        QMessageBox.critical(self, "Error", error_message)
    
    def new_session(self):
        reply = QMessageBox.question(
            self, "New Session",
            "Create a new session? Current conversation will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.session_manager.initialize_session()
            self.conversation_tab.clear_conversation()
    
    def show_about(self):
        QMessageBox.about(
            self, "About Jarvis AI Assistant",
            "Jarvis AI Assistant - Production Interface v1.0\n\n"
            "Enterprise-grade AI assistant with advanced memory,\n"
            "file processing, and conversation capabilities.\n\n"
            "Built with production backend infrastructure."
        )
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clean shutdown
            try:
                if self.session_manager.session_id:
                    self.session_manager.backend.end_session(self.session_manager.session_id)
            except:
                pass
            event.accept()
        else:
            event.ignore()

def main():
    """Main entry point for production GUI"""
    if not PYQT_AVAILABLE:
        print("[FALLBACK] PyQt5 not available. Switching to production CLI mode.")
        print("To use the GUI, install PyQt5: pip install PyQt5")
        
        # Fallback to production CLI
        try:
            from .production_cli import ProductionCLI
            print("[CLI] Starting Production CLI as GUI fallback...")
            cli = ProductionCLI()
            return cli.run()
        except Exception as e:
            print(f"[ERROR] Fallback CLI failed: {e}")
            return 1
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Jarvis AI Assistant")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Jarvis AI")
    
    # Apply dark theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2a2d3a;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #4a5568;
            background-color: #353846;
        }
        QTabBar::tab {
            background-color: #4a5568;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #667eea;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #4a5568;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #353846;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #48bb78;
        }
        QPushButton {
            background-color: #4a5568;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            color: white;
        }
        QPushButton:hover {
            background-color: #667eea;
        }
        QPushButton:pressed {
            background-color: #553c9a;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #4a5568;
            border: 1px solid #667eea;
            border-radius: 4px;
            padding: 4px;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
    """)
    
    try:
        # Create and show main window
        main_window = ProductionGUI()
        main_window.show()
        
        # Run application
        return app.exec_()
        
    except Exception as e:
        error_handler.log_error(e, "GUI Startup", ErrorLevel.CRITICAL)
        if PYQT_AVAILABLE:
            QMessageBox.critical(None, "Startup Error", f"Failed to start GUI: {str(e)}")
        else:
            print(f"Failed to start GUI: {str(e)}")
        return 1
    
    finally:
        # Ensure clean shutdown
        try:
            shutdown_jarvis_backend()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())