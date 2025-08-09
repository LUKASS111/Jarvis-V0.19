#!/usr/bin/env python3
"""
Help Tab Component - User Help and Documentation
Professional component for providing user assistance and documentation
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QTextEdit, QTreeWidget, 
                                QTreeWidgetItem, QPushButton, QLabel, QFrame, 
                                QSplitter, QScrollArea, QComboBox)
    from PyQt5.QtCore import Qt
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

class HelpTab(BaseTab):
    """Professional help and documentation tab"""
    
    def __init__(self):
        super().__init__("Help", "❓")
        self.help_content = {}
        self.setup_content()
        self.load_help_content()
    
    def setup_content(self):
        """Setup the help interface"""
        if not PYQT_AVAILABLE:
            return
            
        # Main layout with splitter
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("Jarvis Help & Documentation")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px; padding: 10px;")
        main_layout.addWidget(header)
        
        # Create splitter for navigation and content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Navigation tree
        nav_frame = QFrame()
        nav_frame.setFrameStyle(QFrame.StyledPanel)
        nav_frame.setMaximumWidth(300)
        nav_layout = QVBoxLayout(nav_frame)
        
        nav_label = QLabel("Topics")
        nav_label.setFont(QFont("Arial", 12, QFont.Bold))
        nav_layout.addWidget(nav_label)
        
        self.help_tree = QTreeWidget()
        self.help_tree.setHeaderLabel("Help Topics")
        self.help_tree.itemClicked.connect(self.on_topic_selected)
        self.help_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        nav_layout.addWidget(self.help_tree)
        
        # Search functionality
        search_label = QLabel("Quick Search:")
        nav_layout.addWidget(search_label)
        
        self.search_combo = QComboBox()
        self.search_combo.setEditable(True)
        self.search_combo.addItems([
            "How to start system",
            "Configure AI models",
            "Memory management",
            "System monitoring",
            "View logs",
            "Export settings",
            "Troubleshooting"
        ])
        self.search_combo.currentTextChanged.connect(self.search_help)
        nav_layout.addWidget(self.search_combo)
        
        splitter.addWidget(nav_frame)
        
        # Right panel - Content display
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.StyledPanel)
        content_layout = QVBoxLayout(content_frame)
        
        # Content area
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 15px;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        content_layout.addWidget(self.content_display)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.print_btn = QPushButton("Print")
        self.print_btn.clicked.connect(self.print_help)
        self.print_btn.setStyleSheet(self.get_button_style())
        button_layout.addWidget(self.print_btn)
        
        self.export_btn = QPushButton("Export PDF")
        self.export_btn.clicked.connect(self.export_help)
        self.export_btn.setStyleSheet(self.get_button_style())
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        self.feedback_btn = QPushButton("Send Feedback")
        self.feedback_btn.clicked.connect(self.send_feedback)
        self.feedback_btn.setStyleSheet(self.get_button_style("#28a745"))
        button_layout.addWidget(self.feedback_btn)
        
        content_layout.addLayout(button_layout)
        
        splitter.addWidget(content_frame)
        splitter.setSizes([300, 800])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Setup navigation tree
        self.setup_help_tree()
        
        # Show welcome content
        self.show_welcome_content()
    
    def setup_help_tree(self):
        """Setup the help navigation tree"""
        # Getting Started
        getting_started = QTreeWidgetItem(["Getting Started"])
        getting_started.addChild(QTreeWidgetItem(["System Overview"]))
        getting_started.addChild(QTreeWidgetItem(["First Time Setup"]))
        getting_started.addChild(QTreeWidgetItem(["Quick Start Guide"]))
        self.help_tree.addTopLevelItem(getting_started)
        
        # Core Functions
        core_functions = QTreeWidgetItem(["Core Functions"])
        core_functions.addChild(QTreeWidgetItem(["System Control"]))
        core_functions.addChild(QTreeWidgetItem(["AI Processing"]))
        core_functions.addChild(QTreeWidgetItem(["Memory Management"]))
        core_functions.addChild(QTreeWidgetItem(["Configuration"]))
        self.help_tree.addTopLevelItem(core_functions)
        
        # Monitoring & Analytics
        monitoring = QTreeWidgetItem(["Monitoring & Analytics"])
        monitoring.addChild(QTreeWidgetItem(["System Monitoring"]))
        monitoring.addChild(QTreeWidgetItem(["Performance Analytics"]))
        monitoring.addChild(QTreeWidgetItem(["Log Management"]))
        monitoring.addChild(QTreeWidgetItem(["Error Diagnostics"]))
        self.help_tree.addTopLevelItem(monitoring)
        
        # Advanced Features
        advanced = QTreeWidgetItem(["Advanced Features"])
        advanced.addChild(QTreeWidgetItem(["Vector Database"]))
        advanced.addChild(QTreeWidgetItem(["Agent Workflows"]))
        advanced.addChild(QTreeWidgetItem(["Development Tools"]))
        advanced.addChild(QTreeWidgetItem(["API Integration"]))
        self.help_tree.addTopLevelItem(advanced)
        
        # Troubleshooting
        troubleshooting = QTreeWidgetItem(["Troubleshooting"])
        troubleshooting.addChild(QTreeWidgetItem(["Common Issues"]))
        troubleshooting.addChild(QTreeWidgetItem(["Error Messages"]))
        troubleshooting.addChild(QTreeWidgetItem(["Performance Issues"]))
        troubleshooting.addChild(QTreeWidgetItem(["Recovery Procedures"]))
        self.help_tree.addTopLevelItem(troubleshooting)
        
        # Expand first level
        self.help_tree.expandAll()
    
    def load_help_content(self):
        """Load help content data"""
        self.help_content = {
            "System Overview": """
                <h2>Jarvis System Overview</h2>
                <p>Jarvis is a comprehensive AI assistant platform that provides:</p>
                <ul>
                    <li><strong>AI Processing:</strong> Advanced language model integration</li>
                    <li><strong>Memory Management:</strong> Intelligent data storage and retrieval</li>
                    <li><strong>System Monitoring:</strong> Real-time performance tracking</li>
                    <li><strong>Vector Database:</strong> Efficient similarity search capabilities</li>
                    <li><strong>Analytics:</strong> Performance metrics and usage statistics</li>
                </ul>
                <p>The system is designed for both novice and expert users, providing a professional
                interface for all AI assistant operations.</p>
            """,
            
            "First Time Setup": """
                <h2>First Time Setup</h2>
                <h3>1. System Configuration</h3>
                <p>Navigate to the Configuration tab to set up your system preferences:</p>
                <ul>
                    <li>Set API keys for AI models</li>
                    <li>Configure memory limits</li>
                    <li>Set performance parameters</li>
                </ul>
                
                <h3>2. Initial System Check</h3>
                <p>Go to Core System tab and run:</p>
                <ul>
                    <li>System Health Check</li>
                    <li>Diagnostics Test</li>
                    <li>Component Validation</li>
                </ul>
                
                <h3>3. Test Basic Functions</h3>
                <p>Verify everything works by testing:</p>
                <ul>
                    <li>AI Processing capabilities</li>
                    <li>Memory storage and retrieval</li>
                    <li>System monitoring displays</li>
                </ul>
            """,
            
            "System Control": """
                <h2>System Control Functions</h2>
                <p>The Core System tab provides essential system control functions:</p>
                
                <h3>Basic Operations</h3>
                <ul>
                    <li><strong>Start System:</strong> Initialize all system components</li>
                    <li><strong>Stop System:</strong> Safely shut down all operations</li>
                    <li><strong>Restart System:</strong> Perform a clean restart</li>
                </ul>
                
                <h3>Health & Diagnostics</h3>
                <ul>
                    <li><strong>Health Check:</strong> Verify all components are functioning</li>
                    <li><strong>Run Diagnostics:</strong> Comprehensive system analysis</li>
                    <li><strong>System Information:</strong> View detailed system status</li>
                </ul>
                
                <h3>Maintenance</h3>
                <ul>
                    <li><strong>Update System:</strong> Install latest updates</li>
                    <li><strong>Backup System:</strong> Create system backup</li>
                    <li><strong>Restore System:</strong> Restore from backup</li>
                </ul>
            """,
            
            "AI Processing": """
                <h2>AI Processing Features</h2>
                <p>The Processing tab provides comprehensive AI functionality:</p>
                
                <h3>Core AI Functions</h3>
                <ul>
                    <li>Natural language processing</li>
                    <li>Response generation</li>
                    <li>Context management</li>
                    <li>Model switching</li>
                </ul>
                
                <h3>Processing Queue</h3>
                <p>Monitor and manage AI processing tasks:</p>
                <ul>
                    <li>View current queue status</li>
                    <li>Prioritize tasks</li>
                    <li>Cancel pending operations</li>
                </ul>
                
                <h3>Model Management</h3>
                <p>Configure and optimize AI models:</p>
                <ul>
                    <li>Select active models</li>
                    <li>Adjust parameters</li>
                    <li>Monitor performance</li>
                </ul>
            """,
            
            "Common Issues": """
                <h2>Common Issues & Solutions</h2>
                
                <h3>System Won't Start</h3>
                <p><strong>Symptoms:</strong> Error messages during startup</p>
                <p><strong>Solutions:</strong></p>
                <ul>
                    <li>Check system requirements</li>
                    <li>Verify configuration files</li>
                    <li>Run system diagnostics</li>
                    <li>Check log files for errors</li>
                </ul>
                
                <h3>Slow Performance</h3>
                <p><strong>Symptoms:</strong> Delayed responses, high CPU usage</p>
                <p><strong>Solutions:</strong></p>
                <ul>
                    <li>Check available memory</li>
                    <li>Review active processes</li>
                    <li>Optimize model parameters</li>
                    <li>Clear temporary files</li>
                </ul>
                
                <h3>Memory Issues</h3>
                <p><strong>Symptoms:</strong> Out of memory errors</p>
                <p><strong>Solutions:</strong></p>
                <ul>
                    <li>Increase memory limits</li>
                    <li>Clear memory cache</li>
                    <li>Optimize data structures</li>
                    <li>Restart system</li>
                </ul>
            """
        }
    
    def get_button_style(self, color="#007bff"):
        """Get consistent button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
        """
    
    def on_topic_selected(self, item, column):
        """Handle help topic selection"""
        topic = item.text(0)
        self.show_help_content(topic)
    
    def show_help_content(self, topic):
        """Display help content for selected topic"""
        content = self.help_content.get(topic, f"<h2>{topic}</h2><p>Help content for {topic} is coming soon...</p>")
        self.content_display.setHtml(content)
    
    def show_welcome_content(self):
        """Show welcome/default help content"""
        welcome_content = """
            <h1>Welcome to Jarvis Help</h1>
            <p>Welcome to the Jarvis AI Assistant help system. Here you'll find comprehensive 
            documentation and guidance for using all system features.</p>
            
            <h2>Getting Help</h2>
            <ul>
                <li><strong>Navigation:</strong> Use the topic tree on the left to browse help topics</li>
                <li><strong>Search:</strong> Use the search box to quickly find specific information</li>
                <li><strong>Actions:</strong> Use the buttons below to print, export, or provide feedback</li>
            </ul>
            
            <h2>Quick Start</h2>
            <p>If you're new to Jarvis, we recommend starting with:</p>
            <ol>
                <li>System Overview - Understand the platform</li>
                <li>First Time Setup - Configure your system</li>
                <li>Quick Start Guide - Begin using core features</li>
            </ol>
            
            <h2>Need More Help?</h2>
            <p>If you can't find what you're looking for, use the "Send Feedback" button 
            to contact support or request additional documentation.</p>
        """
        self.content_display.setHtml(welcome_content)
    
    def search_help(self, search_text):
        """Search help content"""
        # Simple search implementation
        if not search_text.strip():
            return
            
        # Find matching topics
        for topic, content in self.help_content.items():
            if search_text.lower() in topic.lower() or search_text.lower() in content.lower():
                self.show_help_content(topic)
                break
        else:
            # No match found
            self.content_display.setHtml(f"""
                <h2>Search Results</h2>
                <p>No help topics found for: <strong>{search_text}</strong></p>
                <p>Try searching for:</p>
                <ul>
                    <li>System functions</li>
                    <li>Configuration</li>
                    <li>Troubleshooting</li>
                    <li>Processing</li>
                </ul>
            """)
    
    def print_help(self):
        """Print current help content"""
        print("[Help] Print functionality requested")
        # In a real implementation, this would open a print dialog
    
    def export_help(self):
        """Export help content to PDF"""
        print("[Help] PDF export functionality requested")
        # In a real implementation, this would generate and save a PDF
    
    def send_feedback(self):
        """Send feedback about help system"""
        print("[Help] Feedback functionality requested")
        # In a real implementation, this would open a feedback form

def create_help_tab():
    """Factory function to create help tab"""
    return HelpTab()

if __name__ == "__main__":
    # Test the component
    if PYQT_AVAILABLE:
        from PyQt5.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        tab = HelpTab()
        tab.show()
        sys.exit(app.exec_())
    else:
        print("PyQt5 not available for testing")