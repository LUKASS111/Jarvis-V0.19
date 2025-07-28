#!/usr/bin/env python3
"""
Simplified Modern GUI for AutoGPT v0.4.1
Clean, maintainable interface focused on essential functionality
"""

import sys
import threading
import time

# Enhanced error handling for GUI
from error_handler import (
    error_handler, ErrorLevel
)

# GUI dependencies with error handling
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QTextEdit, QLineEdit, QComboBox,
        QSpinBox, QGroupBox, QFormLayout, QSlider
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("❌ PyQt5 not available. GUI cannot start.")
    
    # Create stub classes for testing when PyQt5 is not available
    class QWidget:
        def __init__(self, *args, **kwargs):
            pass
        def show(self):
            pass
        def close(self):
            pass
    
    class QApplication:
        def __init__(self, *args, **kwargs):
            pass
        def exec_(self):
            return 0
        @staticmethod 
        def processEvents():
            pass
    
    # Don't exit immediately - let the module load for testing

# LLM interface imports
try:
    from llm_interface import ask_local_llm, get_available_models, get_ollama_model
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Simplified styling
SIMPLE_STYLE = """
QWidget {
    background-color: #2a2d3a;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
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
    background-color: #5a67d8;
}

QPushButton#self_modify_btn {
    background-color: #e53e3e;
    color: white;
    font-weight: bold;
}

QPushButton#self_modify_btn:hover {
    background-color: #f56565;
}

QTextEdit, QLineEdit {
    background-color: #2d3748;
    border: 2px solid #4a5568;
    border-radius: 6px;
    padding: 8px;
    color: #ffffff;
}

QComboBox, QSpinBox {
    background-color: #2d3748;
    border: 2px solid #4a5568;
    border-radius: 6px;
    padding: 5px;
    color: #ffffff;
}

QSlider::groove:horizontal {
    background-color: #4a5568;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #48bb78;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}


"""

class SimplifiedJarvisGUI(QWidget):
    """Simplified GUI for AutoGPT - focused on essential functionality"""
    
    def __init__(self):
        if not PYQT_AVAILABLE:
            # Create a dummy GUI for testing when PyQt5 is not available
            self.stats = {
                'interactions': 0,
                'start_time': time.time()
            }
            return
            
        super().__init__()
        
        # Signals for thread-safe updates (only if PyQt5 available)
        try:
            self.response_update_signal = pyqtSignal(str)
            self.status_update_signal = pyqtSignal(str)
        except NameError:
            # pyqtSignal not available when PyQt5 is missing
            pass
        
        # Initialize stats
        self.stats = {
            'interactions': 0,
            'start_time': time.time()
        }
        
        # Initialize GUI
        self.init_ui()
        self.connect_signals()
        self.load_initial_data()
    
    def init_ui(self):
        """Initialize simplified user interface"""
        self.setWindowTitle("Jarvis ver. 0.4.1 - Simplified Modern Interface")
        self.setGeometry(100, 100, 1200, 700)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # System Status at top (as requested)
        status_section = self.create_system_status_section()
        main_layout.addWidget(status_section)
        
        # Main horizontal layout
        horizontal_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = self.create_left_panel()
        horizontal_layout.addWidget(left_panel)
        
        # Center panel - Main interaction
        center_panel = self.create_center_panel()
        horizontal_layout.addWidget(center_panel)
        
        # Right panel - Analysis
        right_panel = self.create_right_panel()
        horizontal_layout.addWidget(right_panel)
        
        # Set proportions
        horizontal_layout.setStretch(0, 1)  # Left: 25%
        horizontal_layout.setStretch(1, 2)  # Center: 50%
        horizontal_layout.setStretch(2, 1)  # Right: 25%
        
        main_layout.addLayout(horizontal_layout)
        
        # Apply styling
        self.setStyleSheet(SIMPLE_STYLE)
    
    def create_system_status_section(self):
        """Create system status section at top"""
        group = QGroupBox("📊 System Status")
        layout = QFormLayout(group)
        
        # Status indicators
        self.uptime_label = QLabel("00:00:00")
        layout.addRow("Uptime:", self.uptime_label)
        
        self.interactions_label = QLabel("0")
        layout.addRow("Interactions:", self.interactions_label)
        
        if PSUTIL_AVAILABLE:
            self.memory_label = QLabel("0 MB")
            layout.addRow("Memory:", self.memory_label)
        
        # Auto-refresh timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_system_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        
        return group
    
    def create_left_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Model configuration
        model_group = QGroupBox("🤖 Model Configuration")
        model_layout = QFormLayout(model_group)
        
        # Model selector with refresh
        model_row = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(150)
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.clicked.connect(self.refresh_models)
        
        model_row.addWidget(self.model_combo)
        model_row.addWidget(self.refresh_btn)
        model_layout.addRow("Model:", model_row)
        
        self.model_status = QLabel("❓ Checking...")
        model_layout.addRow("Status:", self.model_status)
        
        layout.addWidget(model_group)
        
        # LLM parameters
        params_group = QGroupBox("⚙️ LLM Parameters")
        params_layout = QFormLayout(params_group)
        
        # Temperature
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(1, 200)
        self.temp_slider.setValue(70)
        self.temp_label = QLabel("0.7")
        temp_row = QHBoxLayout()
        temp_row.addWidget(self.temp_slider)
        temp_row.addWidget(self.temp_label)
        params_layout.addRow("Temperature:", temp_row)
        
        # Max tokens
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 8192)
        self.max_tokens.setValue(2000)
        params_layout.addRow("Max Tokens:", self.max_tokens)
        
        # Connect slider to label
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_label.setText(f"{v/100:.2f}"))
        
        layout.addWidget(params_group)
        
        # System actions
        actions_group = QGroupBox("🚀 System Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.modify_btn = QPushButton("🔧 Self Modify")
        self.modify_btn.setObjectName("self_modify_btn")
        self.modify_btn.clicked.connect(self.self_modify)
        actions_layout.addWidget(self.modify_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return panel
    
    def create_center_panel(self):
        """Create center interaction panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # AI Interaction
        chat_group = QGroupBox("💬 AI Interaction")
        chat_layout = QVBoxLayout(chat_group)
        
        # Input area
        input_layout = QHBoxLayout()
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Ask AutoGPT anything...")
        self.prompt_input.returnPressed.connect(self.process_input)
        
        self.send_btn = QPushButton("📤 Send")
        self.send_btn.clicked.connect(self.process_input)
        self.send_btn.setMaximumWidth(80)
        
        input_layout.addWidget(self.prompt_input)
        input_layout.addWidget(self.send_btn)
        chat_layout.addLayout(input_layout)
        
        # Response area
        self.response_area = QTextEdit()
        self.response_area.setMinimumHeight(400)
        self.response_area.setPlaceholderText("AI responses will appear here...")
        chat_layout.addWidget(self.response_area)
        
        layout.addWidget(chat_group)
        
        return panel
    
    def create_right_panel(self):
        """Create right panel with analysis"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Analysis & Reasoning section
        analysis_group = QGroupBox("🔍 Analysis & Reasoning")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # Chain of thought area
        self.analysis_area = QTextEdit()
        self.analysis_area.setMaximumHeight(300)
        self.analysis_area.setPlaceholderText("Analysis and reasoning will appear here...")
        analysis_layout.addWidget(self.analysis_area)
        
        layout.addWidget(analysis_group)
        
        # Communication area
        comm_group = QGroupBox("💬 Communication")
        comm_layout = QVBoxLayout(comm_group)
        
        self.comm_area = QTextEdit()
        self.comm_area.setMaximumHeight(200)
        self.comm_area.setPlaceholderText("System messages will appear here...")
        self.comm_area.setReadOnly(True)
        comm_layout.addWidget(self.comm_area)
        
        # Clear button
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setMaximumWidth(60)
        self.clear_btn.clicked.connect(self.clear_communication)
        comm_layout.addWidget(self.clear_btn)
        
        layout.addWidget(comm_group)
        layout.addStretch()
        
        return panel
    
    def connect_signals(self):
        """Connect signals for thread-safe updates"""
        self.response_update_signal.connect(self.update_response_safe)
        self.status_update_signal.connect(self.update_status_safe)
    
    def load_initial_data(self):
        """Load initial data"""
        self.refresh_models()
        self.update_system_status()
    
    def refresh_models(self):
        """Refresh available models"""
        try:
            if LLM_AVAILABLE:
                models = get_available_models()
                self.model_combo.clear()
                self.model_combo.addItems(models)
                
                current = get_ollama_model()
                if current in models:
                    self.model_combo.setCurrentText(current)
                
                self.model_status.setText("✅ Ready")
            else:
                self.model_status.setText("❌ LLM Unavailable")
        except Exception as e:
            self.model_status.setText("❌ Error")
            error_handler.log_error(e, "Model refresh", ErrorLevel.ERROR)
    
    def process_input(self):
        """Process user input"""
        prompt = self.prompt_input.text().strip()
        if not prompt:
            return
        
        self.prompt_input.clear()
        self.response_area.append(f"\n🗨️ **You:** {prompt}\n")
        self.response_area.append("🤔 **AutoGPT:** Thinking...\n")
        
        # Process in background
        thread = threading.Thread(target=self._process_background, args=(prompt,))
        thread.daemon = True
        thread.start()
        
        self.stats['interactions'] += 1
    
    def _process_background(self, prompt):
        """Process prompt in background thread"""
        try:
            if LLM_AVAILABLE:
                # Get parameters
                temp = self.temp_slider.value() / 100.0
                max_tokens = self.max_tokens.value()
                
                # Call LLM
                response = ask_local_llm(prompt, temperature=temp, max_tokens=max_tokens)
                
                # Update UI via signal
                self.response_update_signal.emit(response)
                
                # Simple analysis
                analysis = f"Processed prompt: {len(prompt)} chars, Response: {len(response)} chars"
                self.update_analysis(analysis)
                
            else:
                self.response_update_signal.emit("❌ LLM not available")
                
        except Exception as e:
            error_handler.log_error(e, "LLM processing", ErrorLevel.ERROR)
            self.response_update_signal.emit(f"❌ Error: {str(e)}")
    
    def update_response_safe(self, response):
        """Thread-safe response update"""
        # Clear the "Thinking..." message
        content = self.response_area.toPlainText()
        if "Thinking..." in content:
            lines = content.split('\n')
            lines = [line for line in lines if "Thinking..." not in line]
            self.response_area.setPlainText('\n'.join(lines))
        
        self.response_area.append(f"🤖 **AutoGPT:** {response}\n")
    
    def update_status_safe(self, status):
        """Thread-safe status update"""
        self.comm_area.append(f"📢 {time.strftime('%H:%M:%S')} - {status}")
    
    def update_analysis(self, analysis):
        """Update analysis area"""
        self.analysis_area.append(f"🧠 {time.strftime('%H:%M:%S')} - {analysis}")
    
    def update_system_status(self):
        """Update system status display"""
        try:
            # Uptime
            uptime_seconds = int(time.time() - self.stats['start_time'])
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Interactions
            self.interactions_label.setText(str(self.stats['interactions']))
            
            # Memory usage
            if PSUTIL_AVAILABLE:
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                self.memory_label.setText(f"{memory_mb:.1f} MB")
            
        except Exception as e:
            error_handler.log_error(e, "Status update", ErrorLevel.WARNING)
    
    def self_modify(self):
        """Self modification action"""
        try:
            import self_modify
            self.comm_area.append("🔧 Starting self-modification process...")
            thread = threading.Thread(target=self_modify.self_modify_all)
            thread.daemon = True
            thread.start()
        except ImportError:
            self.comm_area.append("❌ Self-modification module not available")
        except Exception as e:
            self.comm_area.append(f"❌ Error in self-modification: {str(e)}")
    
    def clear_communication(self):
        """Clear communication area"""
        self.comm_area.clear()
    
def main():
    """Main entry point for simplified GUI"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AutoGPT")
    app.setApplicationVersion("0.4.1-simplified")
    
    try:
        # Create and show the main window
        window = SimplifiedJarvisGUI()
        window.show()
        
        print("✅ Simplified Modern AutoGPT GUI v0.4.1 initialized successfully!")
        print("✅ Simplified Modern AutoGPT GUI v0.4.1 started successfully!")
        
        # Run the application
        sys.exit(app.exec_())
        
    except Exception as e:
        error_handler.log_error(e, "GUI startup", ErrorLevel.CRITICAL)
        print(f"❌ Critical error starting GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()