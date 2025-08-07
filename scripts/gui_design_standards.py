#!/usr/bin/env python3
"""
Jarvis V0.19 - Stage 3: GUI-005 - GUI Design Standards
Engineering Rigor Implementation with consistent, modern interface design patterns

This script implements consistent, modern interface design patterns across all GUI components.
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path


class GUIDesignStandards:
    """GUI design standards implementation with modern interface patterns"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "stage": "Stage 3 - GUI-005",
            "title": "GUI Design Standards Implementation",
            "standards": {},
            "design_patterns": [],
            "consistency_metrics": {},
            "overall_status": "UNKNOWN"
        }
        
    def create_design_standards_config(self):
        """Create comprehensive GUI design standards configuration"""
        config_file = self.repo_root / "gui" / "design_standards.py"
        
        config_content = '''"""
Jarvis V0.19 - GUI Design Standards
Comprehensive design system for consistent, modern interface patterns
"""

# Color palette - Professional dark theme
COLORS = {
    # Primary colors
    "primary_dark": "#1a1a1a",      # Main background
    "primary_medium": "#2d2d2d",    # Secondary background
    "primary_light": "#404040",     # Elevated surfaces
    
    # Accent colors
    "accent_blue": "#0078d4",       # Primary actions
    "accent_green": "#16c60c",      # Success states
    "accent_orange": "#ff8c00",     # Warning states
    "accent_red": "#e74856",        # Error states
    
    # Text colors
    "text_primary": "#ffffff",      # Primary text
    "text_secondary": "#b3b3b3",    # Secondary text
    "text_disabled": "#666666",     # Disabled text
    
    # Border and separator colors
    "border_light": "#404040",      # Light borders
    "border_medium": "#595959",     # Medium borders
    "separator": "#333333",         # Separators
    
    # Special purpose
    "highlight": "#0078d4",         # Selections and highlights
    "hover": "#333333",             # Hover states
    "pressed": "#1a1a1a",          # Pressed states
    "transparent": "rgba(0,0,0,0)"  # Transparent
}

# Typography system
TYPOGRAPHY = {
    # Font families
    "font_primary": "Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
    "font_monospace": "Consolas, Monaco, 'Courier New', monospace",
    
    # Font sizes (in pixels)
    "text_xs": 10,      # Very small text
    "text_sm": 12,      # Small text
    "text_base": 14,    # Base text size
    "text_lg": 16,      # Large text
    "text_xl": 18,      # Extra large text
    "text_2xl": 24,     # Headers
    "text_3xl": 32,     # Large headers
    
    # Font weights
    "weight_normal": "normal",
    "weight_medium": "500",
    "weight_bold": "bold",
    
    # Line heights
    "line_height_tight": 1.2,
    "line_height_normal": 1.4,
    "line_height_relaxed": 1.6
}

# Spacing system (in pixels)
SPACING = {
    "xs": 4,    # 4px
    "sm": 8,    # 8px
    "md": 16,   # 16px
    "lg": 24,   # 24px
    "xl": 32,   # 32px
    "2xl": 48,  # 48px
    "3xl": 64   # 64px
}

# Component dimensions
DIMENSIONS = {
    # Button dimensions
    "button_height_sm": 28,
    "button_height_md": 36,
    "button_height_lg": 44,
    "button_min_width": 80,
    
    # Input dimensions
    "input_height": 36,
    "input_min_width": 120,
    
    # Icon sizes
    "icon_xs": 12,
    "icon_sm": 16,
    "icon_md": 20,
    "icon_lg": 24,
    "icon_xl": 32,
    
    # Layout dimensions
    "sidebar_width": 240,
    "header_height": 60,
    "footer_height": 40,
    "panel_min_width": 300,
    "panel_min_height": 200
}

# Border radius system
RADIUS = {
    "none": 0,
    "sm": 2,    # Small radius
    "md": 4,    # Medium radius
    "lg": 8,    # Large radius
    "xl": 12,   # Extra large radius
    "full": 9999  # Fully rounded
}

# Shadow system
SHADOWS = {
    "none": "none",
    "sm": "0 1px 2px rgba(0,0,0,0.1)",
    "md": "0 2px 4px rgba(0,0,0,0.1)",
    "lg": "0 4px 8px rgba(0,0,0,0.15)",
    "xl": "0 8px 16px rgba(0,0,0,0.2)"
}

# Animation system
ANIMATIONS = {
    # Duration (in milliseconds)
    "duration_fast": 150,
    "duration_normal": 200,
    "duration_slow": 300,
    
    # Easing functions
    "ease_in": "cubic-bezier(0.4, 0, 1, 1)",
    "ease_out": "cubic-bezier(0, 0, 0.2, 1)",
    "ease_in_out": "cubic-bezier(0.4, 0, 0.2, 1)"
}

# Component style templates
COMPONENT_STYLES = {
    # Button styles
    "button_primary": {
        "background": COLORS["accent_blue"],
        "color": COLORS["text_primary"],
        "border": "none",
        "border_radius": RADIUS["md"],
        "padding": f"{SPACING['sm']}px {SPACING['md']}px",
        "font_weight": TYPOGRAPHY["weight_medium"],
        "font_size": TYPOGRAPHY["text_base"]
    },
    
    "button_secondary": {
        "background": COLORS["primary_light"],
        "color": COLORS["text_primary"],
        "border": f"1px solid {COLORS['border_medium']}",
        "border_radius": RADIUS["md"],
        "padding": f"{SPACING['sm']}px {SPACING['md']}px",
        "font_weight": TYPOGRAPHY["weight_normal"],
        "font_size": TYPOGRAPHY["text_base"]
    },
    
    # Input styles
    "input_default": {
        "background": COLORS["primary_medium"],
        "color": COLORS["text_primary"],
        "border": f"1px solid {COLORS['border_light']}",
        "border_radius": RADIUS["md"],
        "padding": f"{SPACING['sm']}px {SPACING['md']}px",
        "font_size": TYPOGRAPHY["text_base"],
        "height": DIMENSIONS["input_height"]
    },
    
    # Panel styles
    "panel_default": {
        "background": COLORS["primary_medium"],
        "border": f"1px solid {COLORS['border_light']}",
        "border_radius": RADIUS["lg"],
        "padding": SPACING["lg"],
        "box_shadow": SHADOWS["md"]
    },
    
    # Header styles
    "header_default": {
        "background": COLORS["primary_dark"],
        "color": COLORS["text_primary"],
        "border_bottom": f"1px solid {COLORS['border_light']}",
        "padding": f"{SPACING['md']}px {SPACING['lg']}px",
        "height": DIMENSIONS["header_height"],
        "font_size": TYPOGRAPHY["text_lg"],
        "font_weight": TYPOGRAPHY["weight_medium"]
    }
}

# Layout grid system
GRID = {
    "columns": 12,
    "gutter": SPACING["md"],
    "margin": SPACING["lg"],
    "breakpoints": {
        "sm": 576,   # Small devices
        "md": 768,   # Medium devices
        "lg": 992,   # Large devices
        "xl": 1200   # Extra large devices
    }
}

# Accessibility standards
ACCESSIBILITY = {
    # Contrast ratios (WCAG AA compliant)
    "contrast_normal": 4.5,
    "contrast_large": 3.0,
    
    # Focus indicators
    "focus_outline": f"2px solid {COLORS['accent_blue']}",
    "focus_offset": "2px",
    
    # Touch targets (minimum 44x44px)
    "touch_target_min": 44,
    
    # Text sizing
    "text_min_size": 12,
    "text_scalable": True
}

def get_color(color_name):
    """Get color value by name"""
    return COLORS.get(color_name, COLORS["text_primary"])

def get_spacing(size_name):
    """Get spacing value by size name"""
    return SPACING.get(size_name, SPACING["md"])

def get_component_style(component_name):
    """Get component style by name"""
    return COMPONENT_STYLES.get(component_name, {})

def apply_style_to_widget(widget, style_dict):
    """Apply style dictionary to PyQt widget"""
    if not style_dict:
        return
    
    style_sheet = ""
    for property_name, value in style_dict.items():
        css_property = property_name.replace("_", "-")
        style_sheet += f"{css_property}: {value}; "
    
    widget.setStyleSheet(style_sheet)

def create_modern_stylesheet():
    """Create complete modern stylesheet for application"""
    return f"""
    /* Global application styles */
    QApplication {{
        background-color: {COLORS["primary_dark"]};
        color: {COLORS["text_primary"]};
        font-family: {TYPOGRAPHY["font_primary"]};
        font-size: {TYPOGRAPHY["text_base"]}px;
    }}
    
    /* Main window */
    QMainWindow {{
        background-color: {COLORS["primary_dark"]};
        border: none;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS["accent_blue"]};
        color: {COLORS["text_primary"]};
        border: none;
        border-radius: {RADIUS["md"]}px;
        padding: {SPACING["sm"]}px {SPACING["md"]}px;
        font-weight: {TYPOGRAPHY["weight_medium"]};
        min-height: {DIMENSIONS["button_height_md"]}px;
        min-width: {DIMENSIONS["button_min_width"]}px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS["highlight"]};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS["pressed"]};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS["primary_light"]};
        color: {COLORS["text_disabled"]};
    }}
    
    /* Secondary buttons */
    QPushButton[class="secondary"] {{
        background-color: {COLORS["primary_light"]};
        border: 1px solid {COLORS["border_medium"]};
    }}
    
    /* Input fields */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {COLORS["primary_medium"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border_light"]};
        border-radius: {RADIUS["md"]}px;
        padding: {SPACING["sm"]}px {SPACING["md"]}px;
        min-height: {DIMENSIONS["input_height"]}px;
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {COLORS["accent_blue"]};
        outline: none;
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS["text_primary"]};
        background: transparent;
    }}
    
    QLabel[class="secondary"] {{
        color: {COLORS["text_secondary"]};
    }}
    
    QLabel[class="header"] {{
        font-size: {TYPOGRAPHY["text_xl"]}px;
        font-weight: {TYPOGRAPHY["weight_medium"]};
        color: {COLORS["text_primary"]};
    }}
    
    /* Panels and containers */
    QFrame, QGroupBox {{
        background-color: {COLORS["primary_medium"]};
        border: 1px solid {COLORS["border_light"]};
        border-radius: {RADIUS["lg"]}px;
        padding: {SPACING["md"]}px;
    }}
    
    /* Tab widget */
    QTabWidget::pane {{
        background-color: {COLORS["primary_medium"]};
        border: 1px solid {COLORS["border_light"]};
        border-radius: {RADIUS["md"]}px;
    }}
    
    QTabBar::tab {{
        background-color: {COLORS["primary_light"]};
        color: {COLORS["text_secondary"]};
        border: 1px solid {COLORS["border_light"]};
        padding: {SPACING["sm"]}px {SPACING["md"]}px;
        margin-right: 2px;
        border-radius: {RADIUS["md"]}px {RADIUS["md"]}px 0 0;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS["primary_medium"]};
        color: {COLORS["text_primary"]};
        border-bottom: 1px solid {COLORS["primary_medium"]};
    }}
    
    QTabBar::tab:hover {{
        background-color: {COLORS["hover"]};
    }}
    
    /* Scroll bars */
    QScrollBar:vertical {{
        background-color: {COLORS["primary_light"]};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS["border_medium"]};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS["text_secondary"]};
    }}
    
    /* Menu bar */
    QMenuBar {{
        background-color: {COLORS["primary_dark"]};
        color: {COLORS["text_primary"]};
        border-bottom: 1px solid {COLORS["border_light"]};
    }}
    
    QMenuBar::item {{
        background: transparent;
        padding: {SPACING["sm"]}px {SPACING["md"]}px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS["hover"]};
    }}
    
    /* Status bar */
    QStatusBar {{
        background-color: {COLORS["primary_dark"]};
        color: {COLORS["text_secondary"]};
        border-top: 1px solid {COLORS["border_light"]};
    }}
    
    /* List and tree widgets */
    QListWidget, QTreeWidget {{
        background-color: {COLORS["primary_medium"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border_light"]};
        border-radius: {RADIUS["md"]}px;
        alternate-background-color: {COLORS["primary_light"]};
    }}
    
    QListWidget::item, QTreeWidget::item {{
        padding: {SPACING["sm"]}px;
        border-bottom: 1px solid {COLORS["separator"]};
    }}
    
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {COLORS["accent_blue"]};
        color: {COLORS["text_primary"]};
    }}
    
    /* Progress bars */
    QProgressBar {{
        background-color: {COLORS["primary_light"]};
        border: 1px solid {COLORS["border_light"]};
        border-radius: {RADIUS["md"]}px;
        text-align: center;
        color: {COLORS["text_primary"]};
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS["accent_blue"]};
        border-radius: {RADIUS["md"]}px;
    }}
    """

# Design pattern templates
DESIGN_PATTERNS = {
    "dashboard_layout": {
        "description": "Standard dashboard layout with sidebar and main content",
        "components": ["sidebar", "header", "main_content", "footer"],
        "grid": "sidebar: 240px, main: 1fr"
    },
    
    "form_layout": {
        "description": "Standard form layout with labels and inputs",
        "components": ["form_container", "input_groups", "action_buttons"],
        "spacing": "vertical: 16px, horizontal: 24px"
    },
    
    "card_layout": {
        "description": "Card-based content layout",
        "components": ["card_container", "card_header", "card_content", "card_actions"],
        "styling": "elevated, rounded corners, subtle shadow"
    }
}

# Validation rules
VALIDATION_RULES = {
    "color_contrast": "Minimum 4.5:1 ratio for normal text",
    "touch_targets": "Minimum 44x44px for interactive elements",
    "focus_indicators": "Visible focus indicators for keyboard navigation",
    "consistent_spacing": "Use spacing system values consistently",
    "consistent_typography": "Use typography system consistently"
}
'''
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            self.results["standards"]["design_config"] = {
                "status": "CREATED",
                "file_path": str(config_file.relative_to(self.repo_root)),
                "description": "Comprehensive design standards configuration"
            }
            self.results["design_patterns"].append("Created comprehensive design system")
            return True
            
        except Exception as e:
            self.results["standards"]["design_config"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    def apply_standards_to_dashboard(self):
        """Apply design standards to comprehensive dashboard"""
        dashboard_file = self.repo_root / "gui" / "enhanced" / "comprehensive_dashboard.py"
        
        if not dashboard_file.exists():
            self.results["standards"]["dashboard_styling"] = {
                "status": "ERROR",
                "error": "comprehensive_dashboard.py not found"
            }
            return False
        
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            improvements_applied = []
            modified_content = content
            
            # 1. Add design standards import
            if "from gui.design_standards import" not in content:
                import_code = '''
from gui.design_standards import (
    COLORS, TYPOGRAPHY, SPACING, DIMENSIONS, RADIUS, SHADOWS,
    COMPONENT_STYLES, create_modern_stylesheet, apply_style_to_widget
)
'''
                # Insert after existing imports
                lines = modified_content.split('\n')
                import_inserted = False
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        continue
                    else:
                        lines.insert(i, import_code)
                        import_inserted = True
                        break
                
                if import_inserted:
                    modified_content = '\n'.join(lines)
                    improvements_applied.append("Added design standards import")
            
            # 2. Add modern stylesheet application
            if "create_modern_stylesheet()" not in content:
                stylesheet_code = '''
    def apply_modern_styling(self):
        """Apply modern design standards to the dashboard"""
        # Apply global stylesheet
        self.setStyleSheet(create_modern_stylesheet())
        
        # Set professional window properties
        self.setWindowTitle("Jarvis AI Assistant - Comprehensive Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Apply consistent spacing
        if hasattr(self, 'central_widget'):
            self.central_widget.setContentsMargins(
                SPACING["lg"], SPACING["lg"], 
                SPACING["lg"], SPACING["lg"]
            )
'''
                
                # Insert in main class
                if "class" in modified_content:
                    lines = modified_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('class ') and 'Dashboard' in line:
                            # Find good insertion point
                            for j in range(i+1, len(lines)):
                                if lines[j].strip() and (lines[j].startswith('    def ') or lines[j].startswith('\tdef ')) and '__init__' in lines[j]:
                                    # Insert after __init__ method
                                    for k in range(j+1, len(lines)):
                                        if lines[k].strip() and not lines[k].startswith('        ') and not lines[k].startswith('\t\t'):
                                            lines.insert(k, stylesheet_code)
                                            break
                                    break
                            break
                    modified_content = '\n'.join(lines)
                    improvements_applied.append("Added modern stylesheet application")
            
            # 3. Add consistent color scheme
            if "COLORS[" not in content:
                color_application = '''
        # Apply consistent color scheme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS["primary_dark"]};
                color: {COLORS["text_primary"]};
            }}
            QTabWidget::pane {{
                background-color: {COLORS["primary_medium"]};
                border: 1px solid {COLORS["border_light"]};
                border-radius: {RADIUS["lg"]}px;
            }}
        """)
'''
                
                # Insert in __init__ method
                if "__init__" in modified_content:
                    lines = modified_content.split('\n')
                    for i, line in enumerate(lines):
                        if 'def __init__' in line:
                            # Find end of __init__ method
                            for j in range(i+1, len(lines)):
                                if lines[j].strip() and lines[j].startswith('    def ') and 'def __init__' not in lines[j]:
                                    lines.insert(j-1, color_application)
                                    break
                            break
                    modified_content = '\n'.join(lines)
                    improvements_applied.append("Added consistent color scheme")
            
            # 4. Add responsive layout principles
            if "responsive_layout" not in content:
                responsive_code = '''
    def setup_responsive_layout(self):
        """Setup responsive layout following design standards"""
        # Set minimum sizes according to design standards
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setMinimumSize(
                DIMENSIONS["panel_min_width"], 
                DIMENSIONS["panel_min_height"]
            )
        
        # Apply consistent spacing to all tabs
        for i in range(self.tab_widget.count() if hasattr(self, 'tab_widget') else 0):
            tab_widget = self.tab_widget.widget(i)
            if hasattr(tab_widget, 'layout'):
                layout = tab_widget.layout()
                if layout:
                    layout.setSpacing(SPACING["md"])
                    layout.setContentsMargins(
                        SPACING["lg"], SPACING["lg"], 
                        SPACING["lg"], SPACING["lg"]
                    )
'''
                
                if "class" in modified_content:
                    lines = modified_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('class ') and 'Dashboard' in line:
                            # Find good insertion point
                            for j in range(i+1, len(lines)):
                                if lines[j].strip() and lines[j].startswith('    def ') and not lines[j].strip().startswith('    def __init__'):
                                    lines.insert(j, responsive_code)
                                    break
                            break
                    modified_content = '\n'.join(lines)
                    improvements_applied.append("Added responsive layout principles")
            
            # Save improved file
            if improvements_applied:
                with open(dashboard_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.results["standards"]["dashboard_styling"] = {
                    "status": "IMPROVED",
                    "improvements_applied": improvements_applied,
                    "file_size_before": len(content),
                    "file_size_after": len(modified_content)
                }
                self.results["design_patterns"].extend(improvements_applied)
                return True
            else:
                self.results["standards"]["dashboard_styling"] = {
                    "status": "ALREADY_STANDARDIZED",
                    "message": "Design standards already applied"
                }
                return True
                
        except Exception as e:
            self.results["standards"]["dashboard_styling"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    def create_component_library(self):
        """Create reusable GUI component library"""
        component_file = self.repo_root / "gui" / "components" / "modern_components.py"
        component_file.parent.mkdir(exist_ok=True)
        
        component_content = '''"""
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
'''
        
        try:
            with open(component_file, 'w', encoding='utf-8') as f:
                f.write(component_content)
            
            # Create __init__.py for components module
            init_file = component_file.parent / "__init__.py"
            with open(init_file, 'w') as f:
                f.write('"""Modern GUI Components Module"""')
            
            self.results["standards"]["component_library"] = {
                "status": "CREATED",
                "file_path": str(component_file.relative_to(self.repo_root)),
                "description": "Reusable modern component library"
            }
            self.results["design_patterns"].append("Created modern component library")
            return True
            
        except Exception as e:
            self.results["standards"]["component_library"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    def validate_design_consistency(self):
        """Validate design consistency across GUI components"""
        gui_files = list(Path(self.repo_root / "gui").rglob("*.py"))
        
        consistency_metrics = {
            "total_files": len(gui_files),
            "files_with_standards": 0,
            "consistency_score": 0,
            "issues": [],
            "improvements_needed": []
        }
        
        design_patterns_found = {
            "color_usage": 0,
            "typography_usage": 0,
            "spacing_usage": 0,
            "component_usage": 0
        }
        
        for gui_file in gui_files:
            try:
                with open(gui_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_has_standards = False
                
                # Check for design standards usage
                if "design_standards" in content or "COLORS[" in content:
                    design_patterns_found["color_usage"] += 1
                    file_has_standards = True
                
                if "TYPOGRAPHY[" in content or "font-size" in content:
                    design_patterns_found["typography_usage"] += 1
                    file_has_standards = True
                
                if "SPACING[" in content or "padding" in content:
                    design_patterns_found["spacing_usage"] += 1
                    file_has_standards = True
                
                if "ModernButton" in content or "ModernLabel" in content:
                    design_patterns_found["component_usage"] += 1
                    file_has_standards = True
                
                if file_has_standards:
                    consistency_metrics["files_with_standards"] += 1
                
                # Check for potential issues
                if "color:" in content and "COLORS[" not in content:
                    consistency_metrics["issues"].append({
                        "file": str(gui_file.relative_to(self.repo_root)),
                        "issue": "Hardcoded colors instead of design system"
                    })
                
                if "font-size:" in content and "TYPOGRAPHY[" not in content:
                    consistency_metrics["issues"].append({
                        "file": str(gui_file.relative_to(self.repo_root)),
                        "issue": "Hardcoded font sizes instead of typography system"
                    })
                    
            except Exception:
                continue
        
        # Calculate consistency score
        total_files = consistency_metrics["total_files"]
        if total_files > 0:
            consistency_score = (
                (consistency_metrics["files_with_standards"] / total_files) * 40 +
                (design_patterns_found["color_usage"] / total_files) * 20 +
                (design_patterns_found["typography_usage"] / total_files) * 20 +
                (design_patterns_found["component_usage"] / total_files) * 20
            )
        else:
            consistency_score = 0
        
        consistency_metrics["consistency_score"] = round(consistency_score, 1)
        consistency_metrics["design_patterns_found"] = design_patterns_found
        
        # Determine status
        if consistency_score >= 90:
            consistency_metrics["status"] = "EXCELLENT"
        elif consistency_score >= 70:
            consistency_metrics["status"] = "GOOD"
        elif consistency_score >= 50:
            consistency_metrics["status"] = "ACCEPTABLE"
        else:
            consistency_metrics["status"] = "NEEDS_IMPROVEMENT"
        
        self.results["consistency_metrics"] = consistency_metrics
        
        return consistency_score >= 50
    
    def run_all_standards_implementation(self):
        """Run all GUI design standards implementation"""
        print("🎨 Implementing GUI Design Standards (GUI-005)...")
        print("=" * 70)
        
        implementations = [
            ("Design Standards Configuration", self.create_design_standards_config),
            ("Dashboard Styling", self.apply_standards_to_dashboard),
            ("Component Library", self.create_component_library),
            ("Design Consistency Validation", self.validate_design_consistency)
        ]
        
        all_successful = True
        for impl_name, impl_func in implementations:
            print(f"Implementing {impl_name}...")
            try:
                result = impl_func()
                status = "✅ IMPLEMENTED" if result else "⚠️  NEEDS ATTENTION"
                print(f"  {status}")
                if not result:
                    all_successful = False
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                all_successful = False
        
        print("\n" + "=" * 70)
        
        # Overall status
        pattern_count = len(self.results["design_patterns"])
        consistency_score = self.results.get("consistency_metrics", {}).get("consistency_score", 0)
        
        if pattern_count >= 4 and consistency_score >= 70:
            self.results["overall_status"] = "EXCELLENT"
        elif pattern_count >= 3 and consistency_score >= 50:
            self.results["overall_status"] = "GOOD"
        elif pattern_count >= 2:
            self.results["overall_status"] = "BASIC"
        else:
            self.results["overall_status"] = "NEEDS_WORK"
        
        print(f"📊 Design Patterns Implemented: {pattern_count}")
        print(f"🎯 Consistency Score: {consistency_score}%")
        print(f"📈 Overall Status: {self.results['overall_status']}")
        
        if self.results["design_patterns"]:
            print("\n🎨 Design Improvements:")
            for pattern in self.results["design_patterns"]:
                print(f"  • {pattern}")
        
        # Generate detailed report
        report_file = self.repo_root / f"gui_design_standards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📋 Detailed report saved: {report_file}")
        
        return all_successful and consistency_score >= 50


def main():
    """Main execution function"""
    standards = GUIDesignStandards()
    success = standards.run_all_standards_implementation()
    
    if success:
        print("\n✅ GUI-005 COMPLETED: Modern design standards implemented!")
        sys.exit(0)
    else:
        print("\n❌ GUI-005 NEEDS ATTENTION: Additional design standardization required")
        sys.exit(1)


if __name__ == "__main__":
    main()