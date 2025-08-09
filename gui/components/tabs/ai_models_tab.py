#!/usr/bin/env python3
"""
AI Models Management Tab - Modular component extracted from comprehensive dashboard
Handles AI model selection, configuration, and management functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                                QListWidget, QSlider, QSpinBox, QPushButton, 
                                QComboBox, QTextEdit, QProgressBar, QWidget)
    from PyQt5.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from gui.components.base.base_tab import BaseTab

class AIModelsTab(BaseTab):
    """AI Models & LLM Management tab component"""
    
    def __init__(self):
        super().__init__("AI Models & LLM Management", "🤖")
    
    def setup_content(self):
        """Setup AI models specific content"""
        try:
            # Try to use the enhanced AI management interface
            from gui.ai_management_interface import AIManagementInterface
            ai_interface = AIManagementInterface()
            self._main_layout.addWidget(ai_interface)
            print("[AIModelsTab] Using enhanced AI management interface")
        except Exception as e:
            print(f"[AIModelsTab] Enhanced interface not available: {e}")
            self.setup_fallback_interface()
    
    def setup_fallback_interface(self):
        """Setup fallback AI models interface"""
        # Model selection section
        self.add_model_selection()
        
        # Model configuration section
        self.add_model_configuration()
        
        # Model testing section
        self.add_model_testing()
    
    def add_model_selection(self):
        """Add model selection interface"""
        models_group = self.create_group_box("Model Selection & Configuration", "🔧")
        models_layout = QGridLayout(models_group)
        
        # Available models list
        model_list = QListWidget()
        model_list.addItems([
            "🧠 OpenAI GPT-4 (Available)",
            "🤖 Anthropic Claude (Available)", 
            "⚡ Local LLaMA Model (Available)",
            "🔬 Google PaLM (Available)"
        ])
        models_layout.addWidget(QLabel("Available Models:"), 0, 0)
        models_layout.addWidget(model_list, 1, 0)
        
        # Model info panel
        info_panel = QTextEdit()
        info_panel.setMaximumHeight(100)
        info_panel.setPlainText("Select a model to see details and configuration options.")
        models_layout.addWidget(QLabel("Model Information:"), 0, 1)
        models_layout.addWidget(info_panel, 1, 1)
        
        self._main_layout.addWidget(models_group)
    
    def add_model_configuration(self):
        """Add model configuration controls"""
        config_group = self.create_group_box("Model Configuration", "⚙️")
        config_layout = QGridLayout(config_group)
        
        # Temperature control
        config_layout.addWidget(QLabel("Temperature:"), 0, 0)
        temp_layout = QHBoxLayout()
        temp_slider = QSlider(Qt.Horizontal)
        temp_slider.setRange(0, 100)
        temp_slider.setValue(70)
        temp_value = QLabel("0.7")
        temp_slider.valueChanged.connect(lambda v: temp_value.setText(f"{v/100:.1f}"))
        temp_layout.addWidget(temp_slider)
        temp_layout.addWidget(temp_value)
        temp_widget = QWidget()
        temp_widget.setLayout(temp_layout)
        config_layout.addWidget(temp_widget, 0, 1)
        
        # Max tokens control
        config_layout.addWidget(QLabel("Max Tokens:"), 1, 0)
        tokens_spin = QSpinBox()
        tokens_spin.setRange(1, 4096)
        tokens_spin.setValue(1024)
        config_layout.addWidget(tokens_spin, 1, 1)
        
        # Model selection dropdown
        config_layout.addWidget(QLabel("Active Model:"), 2, 0)
        model_combo = QComboBox()
        model_combo.addItems(["GPT-4", "Claude", "LLaMA", "PaLM"])
        config_layout.addWidget(model_combo, 2, 1)
        
        self._main_layout.addWidget(config_group)
    
    def add_model_testing(self):
        """Add model testing interface"""
        test_group = self.create_group_box("Model Testing", "🧪")
        test_layout = QVBoxLayout(test_group)
        
        # Test prompt area
        test_layout.addWidget(QLabel("Test Prompt:"))
        prompt_input = QTextEdit()
        prompt_input.setMaximumHeight(80)
        prompt_input.setPlainText("Enter a test prompt to evaluate the model...")
        test_layout.addWidget(prompt_input)
        
        # Test controls
        controls_layout = QHBoxLayout()
        test_button = QPushButton("🚀 Test Model")
        clear_button = QPushButton("🗑️ Clear")
        controls_layout.addWidget(test_button)
        controls_layout.addWidget(clear_button)
        controls_layout.addStretch()
        test_layout.addLayout(controls_layout)
        
        # Results area
        test_layout.addWidget(QLabel("Model Response:"))
        response_area = QTextEdit()
        response_area.setMaximumHeight(120)
        response_area.setPlainText("Model responses will appear here...")
        test_layout.addWidget(response_area)
        
        # Performance metrics
        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(QLabel("Response Time:"))
        time_label = QLabel("0ms")
        metrics_layout.addWidget(time_label)
        metrics_layout.addStretch()
        metrics_layout.addWidget(QLabel("Tokens Used:"))
        tokens_label = QLabel("0")
        metrics_layout.addWidget(tokens_label)
        test_layout.addLayout(metrics_layout)
        
        self._main_layout.addWidget(test_group)