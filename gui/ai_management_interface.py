#!/usr/bin/env python3
"""
Advanced AI Management Interface - Stage 7
Professional AI model management and workflow automation
"""

import sys
import json
import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt5 not available, using fallback mode")

from gui.design_standards import (
    COLORS, TYPOGRAPHY, SPACING, DIMENSIONS, RADIUS, SHADOWS,
    COMPONENT_STYLES, create_professional_stylesheet
)

class AIManagementInterface(QWidget if PYQT_AVAILABLE else object):
    """Professional AI Management Interface for Stage 7"""
    
    def __init__(self, parent=None):
        if PYQT_AVAILABLE:
            super().__init__(parent)
            self.setup_ai_interface()
        else:
            print("AI Management Interface running in fallback mode")
    
    def setup_ai_interface(self):
        """Setup the AI management interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING.LARGE)
        layout.setContentsMargins(SPACING.LARGE, SPACING.LARGE, SPACING.LARGE, SPACING.LARGE)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content tabs
        tabs = self.create_ai_tabs()
        layout.addWidget(tabs)
        
        # Status bar
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
        
        self.setStyleSheet(create_professional_stylesheet())
    
    def create_header(self):
        """Create header section"""
        header = QFrame()
        header.setFrameStyle(QFrame.StyledPanel)
        header.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.PRIMARY};
                border-radius: {RADIUS.MEDIUM}px;
                padding: {SPACING.MEDIUM}px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        
        # Title and description
        title_layout = QVBoxLayout()
        
        title = QLabel("🤖 Advanced AI Management")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.ON_PRIMARY};
                font-family: {TYPOGRAPHY.FONT_FAMILY};
                font-size: {TYPOGRAPHY.SIZES.LARGE}px;
                font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
                margin: 0;
            }}
        """)
        
        subtitle = QLabel("Professional AI model management and workflow automation")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {COLORS.ON_PRIMARY};
                font-family: {TYPOGRAPHY.FONT_FAMILY};
                font-size: {TYPOGRAPHY.SIZES.SMALL}px;
                margin: 0;
                opacity: 0.8;
            }}
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        layout.addLayout(title_layout)
        
        layout.addStretch()
        
        # Quick stats
        stats = self.create_quick_stats()
        layout.addWidget(stats)
        
        return header
    
    def create_quick_stats(self):
        """Create quick statistics display"""
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        stats_data = [
            ("Models", "15", "🔧"),
            ("Active", "3", "⚡"),
            ("Workflows", "8", "🔄")
        ]
        
        for label, value, icon in stats_data:
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: {RADIUS.SMALL}px;
                    padding: {SPACING.SMALL}px;
                }}
            """)
            
            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setSpacing(2)
            
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet(f"font-size: {TYPOGRAPHY.SIZES.MEDIUM}px; color: {COLORS.ON_PRIMARY};")
            
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet(f"""
                color: {COLORS.ON_PRIMARY};
                font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
                font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            """)
            
            label_label = QLabel(label)
            label_label.setAlignment(Qt.AlignCenter)
            label_label.setStyleSheet(f"""
                color: {COLORS.ON_PRIMARY};
                font-size: {TYPOGRAPHY.SIZES.SMALL}px;
                opacity: 0.8;
            """)
            
            stat_layout.addWidget(icon_label)
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)
            
            stats_layout.addWidget(stat_frame)
        
        return stats_widget
    
    def create_ai_tabs(self):
        """Create AI management tabs"""
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS.BORDER};
                border-radius: {RADIUS.MEDIUM}px;
                background: {COLORS.SURFACE};
            }}
            QTabBar::tab {{
                background: {COLORS.SURFACE_VARIANT};
                color: {COLORS.ON_SURFACE_VARIANT};
                padding: {SPACING.MEDIUM}px {SPACING.LARGE}px;
                margin: 2px;
                border-radius: {RADIUS.SMALL}px;
                font-weight: {TYPOGRAPHY.WEIGHTS.MEDIUM};
            }}
            QTabBar::tab:selected {{
                background: {COLORS.PRIMARY};
                color: {COLORS.ON_PRIMARY};
            }}
            QTabBar::tab:hover {{
                background: {COLORS.PRIMARY_CONTAINER};
                color: {COLORS.ON_PRIMARY_CONTAINER};
            }}
        """)
        
        # Model Management Tab
        model_tab = self.create_model_management_tab()
        tabs.addTab(model_tab, "🔧 Model Management")
        
        # Workflow Automation Tab
        workflow_tab = self.create_workflow_automation_tab()
        tabs.addTab(workflow_tab, "🔄 Workflow Automation")
        
        # Model Comparison Tab
        comparison_tab = self.create_model_comparison_tab()
        tabs.addTab(comparison_tab, "📊 Model Comparison")
        
        # Training & Fine-tuning Tab
        training_tab = self.create_training_tab()
        tabs.addTab(training_tab, "🎯 Training & Fine-tuning")
        
        return tabs
    
    def create_model_management_tab(self):
        """Create model management tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(SPACING.LARGE)
        
        # Left panel - Model list
        left_panel = self.create_model_list_panel()
        layout.addWidget(left_panel, 1)
        
        # Right panel - Model details
        right_panel = self.create_model_details_panel()
        layout.addWidget(right_panel, 2)
        
        return widget
    
    def create_model_list_panel(self):
        """Create model list panel"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.SURFACE};
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.MEDIUM}px;
                padding: {SPACING.MEDIUM}px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Available Models")
        header.setStyleSheet(f"""
            font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
            font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            color: {COLORS.ON_SURFACE};
            margin-bottom: {SPACING.SMALL}px;
        """)
        layout.addWidget(header)
        
        # Search
        search = QLineEdit()
        search.setPlaceholderText("Search models...")
        search.setStyleSheet(f"""
            QLineEdit {{
                padding: {SPACING.SMALL}px;
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.SMALL}px;
                background: {COLORS.SURFACE};
                color: {COLORS.ON_SURFACE};
            }}
        """)
        layout.addWidget(search)
        
        # Model list
        model_list = QListWidget()
        model_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.SMALL}px;
                background: {COLORS.SURFACE};
                selection-background-color: {COLORS.PRIMARY_CONTAINER};
            }}
            QListWidget::item {{
                padding: {SPACING.MEDIUM}px;
                border-bottom: 1px solid {COLORS.OUTLINE};
                color: {COLORS.ON_SURFACE};
            }}
            QListWidget::item:hover {{
                background: {COLORS.SURFACE_VARIANT};
            }}
        """)
        
        # Add sample models
        models = [
            "GPT-4 Turbo",
            "Claude 3.5 Sonnet",
            "Gemini Pro",
            "LLaMA 2 70B",
            "Mistral 7B",
            "CodeLlama 34B",
            "BERT Large",
            "RoBERTa Base",
            "T5 Large",
            "BLOOM 176B"
        ]
        
        for model in models:
            item = QListWidgetItem(f"🤖 {model}")
            model_list.addItem(item)
        
        layout.addWidget(model_list)
        
        # Add model button
        add_btn = QPushButton("➕ Add New Model")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.PRIMARY};
                color: {COLORS.ON_PRIMARY};
                border: none;
                border-radius: {RADIUS.SMALL}px;
                padding: {SPACING.MEDIUM}px;
                font-weight: {TYPOGRAPHY.WEIGHTS.MEDIUM};
            }}
            QPushButton:hover {{
                background: {COLORS.PRIMARY_VARIANT};
            }}
        """)
        layout.addWidget(add_btn)
        
        return panel
    
    def create_model_details_panel(self):
        """Create model details panel"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.SURFACE};
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.MEDIUM}px;
                padding: {SPACING.MEDIUM}px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("Model Configuration")
        header.setStyleSheet(f"""
            font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
            font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            color: {COLORS.ON_SURFACE};
            margin-bottom: {SPACING.MEDIUM}px;
        """)
        layout.addWidget(header)
        
        # Configuration form
        form_layout = QFormLayout()
        
        # Model name
        name_input = QLineEdit("GPT-4 Turbo")
        name_input.setStyleSheet(f"""
            QLineEdit {{
                padding: {SPACING.SMALL}px;
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.SMALL}px;
                background: {COLORS.SURFACE};
                color: {COLORS.ON_SURFACE};
            }}
        """)
        form_layout.addRow("Model Name:", name_input)
        
        # Provider
        provider_combo = QComboBox()
        provider_combo.addItems(["OpenAI", "Anthropic", "Google", "Meta", "Mistral"])
        provider_combo.setStyleSheet(f"""
            QComboBox {{
                padding: {SPACING.SMALL}px;
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.SMALL}px;
                background: {COLORS.SURFACE};
                color: {COLORS.ON_SURFACE};
            }}
        """)
        form_layout.addRow("Provider:", provider_combo)
        
        # Temperature
        temp_slider = QSlider(Qt.Horizontal)
        temp_slider.setRange(0, 100)
        temp_slider.setValue(70)
        temp_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {COLORS.OUTLINE};
                height: 8px;
                background: {COLORS.SURFACE_VARIANT};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS.PRIMARY};
                border: 1px solid {COLORS.PRIMARY};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)
        form_layout.addRow("Temperature:", temp_slider)
        
        # Max tokens
        tokens_spin = QSpinBox()
        tokens_spin.setRange(1, 8192)
        tokens_spin.setValue(2048)
        tokens_spin.setStyleSheet(f"""
            QSpinBox {{
                padding: {SPACING.SMALL}px;
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.SMALL}px;
                background: {COLORS.SURFACE};
                color: {COLORS.ON_SURFACE};
            }}
        """)
        form_layout.addRow("Max Tokens:", tokens_spin)
        
        layout.addLayout(form_layout)
        
        # Performance metrics
        metrics_label = QLabel("Performance Metrics")
        metrics_label.setStyleSheet(f"""
            font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
            font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            color: {COLORS.ON_SURFACE};
            margin: {SPACING.LARGE}px 0 {SPACING.SMALL}px 0;
        """)
        layout.addWidget(metrics_label)
        
        metrics_grid = QGridLayout()
        
        metric_items = [
            ("Response Time", "1.2s", "⚡"),
            ("Accuracy", "94.5%", "🎯"),
            ("Tokens/min", "1,850", "📊"),
            ("Cost/1K", "$0.03", "💰")
        ]
        
        for i, (label, value, icon) in enumerate(metric_items):
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background: {COLORS.SURFACE_VARIANT};
                    border-radius: {RADIUS.SMALL}px;
                    padding: {SPACING.SMALL}px;
                }}
            """)
            
            metric_layout = QHBoxLayout(metric_frame)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;")
            
            text_layout = QVBoxLayout()
            text_layout.setSpacing(0)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"""
                font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
                color: {COLORS.ON_SURFACE_VARIANT};
            """)
            
            label_label = QLabel(label)
            label_label.setStyleSheet(f"""
                font-size: {TYPOGRAPHY.SIZES.SMALL}px;
                color: {COLORS.ON_SURFACE_VARIANT};
                opacity: 0.7;
            """)
            
            text_layout.addWidget(value_label)
            text_layout.addWidget(label_label)
            
            metric_layout.addWidget(icon_label)
            metric_layout.addLayout(text_layout)
            
            metrics_grid.addWidget(metric_frame, i // 2, i % 2)
        
        layout.addLayout(metrics_grid)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton("🧪 Test Model")
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.SECONDARY};
                color: {COLORS.ON_SECONDARY};
                border: none;
                border-radius: {RADIUS.SMALL}px;
                padding: {SPACING.MEDIUM}px;
                font-weight: {TYPOGRAPHY.WEIGHTS.MEDIUM};
            }}
            QPushButton:hover {{
                background: {COLORS.SECONDARY_VARIANT};
            }}
        """)
        
        save_btn = QPushButton("💾 Save Configuration")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.PRIMARY};
                color: {COLORS.ON_PRIMARY};
                border: none;
                border-radius: {RADIUS.SMALL}px;
                padding: {SPACING.MEDIUM}px;
                font-weight: {TYPOGRAPHY.WEIGHTS.MEDIUM};
            }}
            QPushButton:hover {{
                background: {COLORS.PRIMARY_VARIANT};
            }}
        """)
        
        button_layout.addWidget(test_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        return panel
    
    def create_workflow_automation_tab(self):
        """Create workflow automation tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(SPACING.LARGE)
        
        # Header
        header = QLabel("🔄 AI Workflow Automation")
        header.setStyleSheet(f"""
            font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
            font-size: {TYPOGRAPHY.SIZES.LARGE}px;
            color: {COLORS.ON_SURFACE};
            margin-bottom: {SPACING.MEDIUM}px;
        """)
        layout.addWidget(header)
        
        # Workflow grid
        grid_layout = QGridLayout()
        
        workflows = [
            ("Data Processing Pipeline", "Automated data preprocessing and analysis", "🔄", "Active"),
            ("Model Training Workflow", "Automated model training and evaluation", "🎯", "Scheduled"),
            ("Content Generation", "Automated content generation and review", "📝", "Active"),
            ("Quality Assurance", "Automated testing and validation", "✅", "Paused")
        ]
        
        for i, (name, description, icon, status) in enumerate(workflows):
            workflow_card = self.create_workflow_card(name, description, icon, status)
            grid_layout.addWidget(workflow_card, i // 2, i % 2)
        
        layout.addLayout(grid_layout)
        
        # Create workflow button
        create_btn = QPushButton("➕ Create New Workflow")
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.PRIMARY};
                color: {COLORS.ON_PRIMARY};
                border: none;
                border-radius: {RADIUS.SMALL}px;
                padding: {SPACING.LARGE}px;
                font-weight: {TYPOGRAPHY.WEIGHTS.MEDIUM};
                font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            }}
            QPushButton:hover {{
                background: {COLORS.PRIMARY_VARIANT};
            }}
        """)
        layout.addWidget(create_btn)
        
        return widget
    
    def create_workflow_card(self, name, description, icon, status):
        """Create workflow card"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.SURFACE};
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.MEDIUM}px;
                padding: {SPACING.MEDIUM}px;
            }}
            QFrame:hover {{
                border-color: {COLORS.PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Header
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: {TYPOGRAPHY.SIZES.LARGE}px;")
        
        title_label = QLabel(name)
        title_label.setStyleSheet(f"""
            font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
            font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            color: {COLORS.ON_SURFACE};
        """)
        
        status_colors = {
            "Active": COLORS.SUCCESS,
            "Scheduled": COLORS.WARNING,
            "Paused": COLORS.ERROR
        }
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"""
            background: {status_colors.get(status, COLORS.SURFACE_VARIANT)};
            color: {COLORS.TEXT_PRIMARY};
            padding: 2px 8px;
            border-radius: {RADIUS.SMALL}px;
            font-size: {TYPOGRAPHY.SIZES.SMALL}px;
            font-weight: {TYPOGRAPHY.WEIGHTS.MEDIUM};
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        
        layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            color: {COLORS.ON_SURFACE};
            opacity: 0.7;
            margin: {SPACING.SMALL}px 0;
        """)
        layout.addWidget(desc_label)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.SECONDARY};
                color: {COLORS.ON_SECONDARY};
                border: none;
                border-radius: {RADIUS.SMALL}px;
                padding: {SPACING.SMALL}px {SPACING.MEDIUM}px;
            }}
        """)
        
        run_btn = QPushButton("Run")
        run_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS.PRIMARY};
                color: {COLORS.ON_PRIMARY};
                border: none;
                border-radius: {RADIUS.SMALL}px;
                padding: {SPACING.SMALL}px {SPACING.MEDIUM}px;
            }}
        """)
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(run_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return card
    
    def create_model_comparison_tab(self):
        """Create model comparison tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("📊 Model Performance Comparison")
        header.setStyleSheet(f"""
            font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
            font-size: {TYPOGRAPHY.SIZES.LARGE}px;
            color: {COLORS.ON_SURFACE};
            margin-bottom: {SPACING.MEDIUM}px;
        """)
        layout.addWidget(header)
        
        # Comparison table placeholder
        table_label = QLabel("🚧 Model comparison interface will be implemented here")
        table_label.setAlignment(Qt.AlignCenter)
        table_label.setStyleSheet(f"""
            color: {COLORS.ON_SURFACE};
            font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            padding: {SPACING.XLARGE}px;
            border: 2px dashed {COLORS.OUTLINE};
            border-radius: {RADIUS.MEDIUM}px;
        """)
        layout.addWidget(table_label)
        
        return widget
    
    def create_training_tab(self):
        """Create training & fine-tuning tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("🎯 Model Training & Fine-tuning")
        header.setStyleSheet(f"""
            font-weight: {TYPOGRAPHY.WEIGHTS.BOLD};
            font-size: {TYPOGRAPHY.SIZES.LARGE}px;
            color: {COLORS.ON_SURFACE};
            margin-bottom: {SPACING.MEDIUM}px;
        """)
        layout.addWidget(header)
        
        # Training interface placeholder
        training_label = QLabel("🚧 Training and fine-tuning interface will be implemented here")
        training_label.setAlignment(Qt.AlignCenter)
        training_label.setStyleSheet(f"""
            color: {COLORS.ON_SURFACE};
            font-size: {TYPOGRAPHY.SIZES.MEDIUM}px;
            padding: {SPACING.XLARGE}px;
            border: 2px dashed {COLORS.OUTLINE};
            border-radius: {RADIUS.MEDIUM}px;
        """)
        layout.addWidget(training_label)
        
        return widget
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.StyledPanel)
        status_bar.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.SURFACE_VARIANT};
                border: 1px solid {COLORS.OUTLINE};
                border-radius: {RADIUS.SMALL}px;
                padding: {SPACING.SMALL}px {SPACING.MEDIUM}px;
            }}
        """)
        
        layout = QHBoxLayout(status_bar)
        
        status_label = QLabel("✅ AI Management System Ready")
        status_label.setStyleSheet(f"""
            color: {COLORS.ON_SURFACE_VARIANT};
            font-weight: {TYPOGRAPHY.WEIGHTS.MEDIUM};
        """)
        
        time_label = QLabel(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        time_label.setStyleSheet(f"""
            color: {COLORS.ON_SURFACE_VARIANT};
            opacity: 0.7;
        """)
        
        layout.addWidget(status_label)
        layout.addStretch()
        layout.addWidget(time_label)
        
        return status_bar

def main():
    """Main function for testing"""
    if PYQT_AVAILABLE:
        app = QApplication(sys.argv)
        window = AIManagementInterface()
        window.show()
        sys.exit(app.exec_())
    else:
        print("AI Management Interface initialized in fallback mode")

if __name__ == "__main__":
    main()