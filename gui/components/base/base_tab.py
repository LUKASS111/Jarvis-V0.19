#!/usr/bin/env python3
"""
Base Tab Component for Jarvis Dashboard
Provides common functionality for all dashboard tabs to reduce code duplication.
"""

try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QGridLayout
    from PyQt5.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QWidget = object

class BaseTab(QWidget if PYQT_AVAILABLE else object):
    """Base class for all dashboard tabs with common functionality"""
    
    def __init__(self, title: str, icon: str = ""):
        if not PYQT_AVAILABLE:
            return
            
        super().__init__()
        self.title = title
        self.icon = icon
        self.init_ui()
    
    def init_ui(self):
        """Initialize the basic UI structure"""
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        self.add_title()
        
        # Call setup method for subclasses
        self.setup_content()
    
    def add_title(self):
        """Add consistent title styling"""
        title_text = f"{self.icon} {self.title}" if self.icon else self.title
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #2196F3; 
            margin: 15px;
            padding: 10px;
        """)
        self.layout.addWidget(title_label)
    
    def create_group_box(self, title: str, icon: str = "") -> 'QGroupBox':
        """Create consistently styled group box"""
        group_title = f"{icon} {title}" if icon else title
        group_box = QGroupBox(group_title)
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin: 10px 0px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        return group_box
    
    def setup_content(self):
        """Override this method to add tab-specific content"""
        pass