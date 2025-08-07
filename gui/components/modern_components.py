"""
Modern GUI Components Library
Reusable components following design standards
"""

from PyQt5.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QFrame, QVBoxLayout, 
    QHBoxLayout, QGroupBox, QProgressBar
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from gui.design_standards import COLORS, TYPOGRAPHY, SPACING, DIMENSIONS, RADIUS


class ModernButton(QPushButton):
    """Modern button component with consistent styling"""
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern button styling"""
        base_style = f"""
            QPushButton {{
                border: none;
                border-radius: {RADIUS["md"]}px;
                padding: {SPACING["sm"]}px {SPACING["md"]}px;
                font-weight: {TYPOGRAPHY["weight_medium"]};
                font-size: {TYPOGRAPHY["text_base"]}px;
                min-height: {DIMENSIONS["button_height_md"]}px;
                min-width: {DIMENSIONS["button_min_width"]}px;
            }}
        """
        
        if self.button_type == "primary":
            style = base_style + f"""
                QPushButton {{
                    background-color: {COLORS["accent_blue"]};
                    color: {COLORS["text_primary"]};
                }}
                QPushButton:hover {{
                    background-color: {COLORS["highlight"]};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS["pressed"]};
                }}
            """
        elif self.button_type == "secondary":
            style = base_style + f"""
                QPushButton {{
                    background-color: {COLORS["primary_light"]};
                    color: {COLORS["text_primary"]};
                    border: 1px solid {COLORS["border_medium"]};
                }}
                QPushButton:hover {{
                    background-color: {COLORS["hover"]};
                }}
            """
        elif self.button_type == "success":
            style = base_style + f"""
                QPushButton {{
                    background-color: {COLORS["accent_green"]};
                    color: {COLORS["text_primary"]};
                }}
            """
        elif self.button_type == "warning":
            style = base_style + f"""
                QPushButton {{
                    background-color: {COLORS["accent_orange"]};
                    color: {COLORS["text_primary"]};
                }}
            """
        else:
            style = base_style
        
        self.setStyleSheet(style)


class ModernInput(QLineEdit):
    """Modern input field component"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern input styling"""
        style = f"""
            QLineEdit {{
                background-color: {COLORS["primary_medium"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border_light"]};
                border-radius: {RADIUS["md"]}px;
                padding: {SPACING["sm"]}px {SPACING["md"]}px;
                font-size: {TYPOGRAPHY["text_base"]}px;
                min-height: {DIMENSIONS["input_height"]}px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS["accent_blue"]};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {COLORS["text_disabled"]};
            }}
        """
        self.setStyleSheet(style)


class ModernLabel(QLabel):
    """Modern label component with typography standards"""
    
    def __init__(self, text="", label_type="normal", parent=None):
        super().__init__(text, parent)
        self.label_type = label_type
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern label styling"""
        base_style = f"""
            QLabel {{
                background: transparent;
                color: {COLORS["text_primary"]};
            }}
        """
        
        if self.label_type == "header":
            style = base_style + f"""
                QLabel {{
                    font-size: {TYPOGRAPHY["text_xl"]}px;
                    font-weight: {TYPOGRAPHY["weight_medium"]};
                    color: {COLORS["text_primary"]};
                }}
            """
        elif self.label_type == "secondary":
            style = base_style + f"""
                QLabel {{
                    color: {COLORS["text_secondary"]};
                    font-size: {TYPOGRAPHY["text_sm"]}px;
                }}
            """
        elif self.label_type == "caption":
            style = base_style + f"""
                QLabel {{
                    color: {COLORS["text_disabled"]};
                    font-size: {TYPOGRAPHY["text_xs"]}px;
                }}
            """
        else:
            style = base_style
        
        self.setStyleSheet(style)


class ModernPanel(QFrame):
    """Modern panel component with consistent styling"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_panel()
    
    def setup_panel(self):
        """Setup panel with modern styling"""
        self.setFrameStyle(QFrame.NoFrame)
        
        style = f"""
            QFrame {{
                background-color: {COLORS["primary_medium"]};
                border: 1px solid {COLORS["border_light"]};
                border-radius: {RADIUS["lg"]}px;
            }}
        """
        self.setStyleSheet(style)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING["md"])
        layout.setContentsMargins(
            SPACING["lg"], SPACING["lg"], 
            SPACING["lg"], SPACING["lg"]
        )
        
        # Add title if provided
        if self.title:
            title_label = ModernLabel(self.title, "header")
            layout.addWidget(title_label)


class ModernProgressBar(QProgressBar):
    """Modern progress bar component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_styling()
    
    def setup_styling(self):
        """Apply modern progress bar styling"""
        style = f"""
            QProgressBar {{
                background-color: {COLORS["primary_light"]};
                border: 1px solid {COLORS["border_light"]};
                border-radius: {RADIUS["md"]}px;
                text-align: center;
                color: {COLORS["text_primary"]};
                font-size: {TYPOGRAPHY["text_sm"]}px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS["accent_blue"]};
                border-radius: {RADIUS["md"]}px;
            }}
        """
        self.setStyleSheet(style)


class CardLayout(QFrame):
    """Card layout component for content organization"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_card()
    
    def setup_card(self):
        """Setup card layout"""
        self.setFrameStyle(QFrame.NoFrame)
        
        style = f"""
            QFrame {{
                background-color: {COLORS["primary_medium"]};
                border: 1px solid {COLORS["border_light"]};
                border-radius: {RADIUS["lg"]}px;
            }}
        """
        self.setStyleSheet(style)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        if self.title:
            self.header = QFrame()
            self.header.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS["primary_light"]};
                    border-bottom: 1px solid {COLORS["border_light"]};
                    border-radius: {RADIUS["lg"]}px {RADIUS["lg"]}px 0 0;
                }}
            """)
            
            header_layout = QHBoxLayout(self.header)
            header_layout.setContentsMargins(
                SPACING["lg"], SPACING["md"], 
                SPACING["lg"], SPACING["md"]
            )
            
            title_label = ModernLabel(self.title, "header")
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            
            self.main_layout.addWidget(self.header)
        
        # Content area
        self.content = QFrame()
        self.content.setStyleSheet("QFrame { background: transparent; border: none; }")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(
            SPACING["lg"], SPACING["lg"], 
            SPACING["lg"], SPACING["lg"]
        )
        self.content_layout.setSpacing(SPACING["md"])
        
        self.main_layout.addWidget(self.content)
    
    def add_content(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)


# Utility functions for component creation
def create_button_group(buttons_config, parent=None):
    """Create a group of buttons with consistent styling"""
    container = QFrame(parent)
    layout = QHBoxLayout(container)
    layout.setSpacing(SPACING["sm"])
    
    for button_config in buttons_config:
        button = ModernButton(
            text=button_config.get("text", ""),
            button_type=button_config.get("type", "primary"),
            parent=container
        )
        if "callback" in button_config:
            button.clicked.connect(button_config["callback"])
        layout.addWidget(button)
    
    return container


def create_form_row(label_text, input_widget, parent=None):
    """Create a form row with label and input"""
    container = QFrame(parent)
    layout = QHBoxLayout(container)
    layout.setSpacing(SPACING["md"])
    
    label = ModernLabel(label_text)
    label.setMinimumWidth(120)
    layout.addWidget(label)
    layout.addWidget(input_widget)
    
    return container


def create_info_panel(title, content_items, parent=None):
    """Create an information panel with title and content"""
    panel = ModernPanel(title, parent)
    
    for item in content_items:
        if isinstance(item, str):
            label = ModernLabel(item)
            panel.layout().addWidget(label)
        else:
            panel.layout().addWidget(item)
    
    return panel
