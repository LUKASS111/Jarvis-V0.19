"""
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
