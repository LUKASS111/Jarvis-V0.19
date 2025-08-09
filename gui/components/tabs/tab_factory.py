#!/usr/bin/env python3
"""
Tab Factory - Creates and manages dashboard tab instances
Implements Factory pattern to reduce complexity in main dashboard class.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

try:
    from PyQt5.QtWidgets import QWidget
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QWidget = object

class TabFactory:
    """Factory for creating dashboard tab instances"""
    
    @staticmethod
    def create_ai_models_tab():
        """Create AI Models tab"""
        try:
            from gui.components.tabs.ai_models_tab import AIModelsTab
            return AIModelsTab()
        except Exception as e:
            print(f"[TabFactory] Error creating AI models tab: {e}")
            return TabFactory._create_fallback_tab("AI Models", "🤖")
    
    @staticmethod
    def create_system_monitoring_tab():
        """Create System Monitoring tab"""
        try:
            from gui.components.tabs.system_monitoring_tab import SystemMonitoringTab
            return SystemMonitoringTab()
        except Exception as e:
            print(f"[TabFactory] Error creating monitoring tab: {e}")
            return TabFactory._create_fallback_tab("System Monitoring", "📊")
    
    @staticmethod
    def create_vector_database_tab():
        """Create Vector Database tab"""
        try:
            from gui.vector_database_interface import VectorDatabaseInterface
            return VectorDatabaseInterface()
        except Exception as e:
            print(f"[TabFactory] Error creating vector DB tab: {e}")
            return TabFactory._create_fallback_tab("Vector Database", "🗄️")
    
    @staticmethod
    def create_memory_management_tab():
        """Create Memory Management tab"""
        try:
            from gui.memory_management_interface import MemoryManagementInterface
            return MemoryManagementInterface()
        except Exception as e:
            print(f"[TabFactory] Error creating memory tab: {e}")
            return TabFactory._create_fallback_tab("Memory Management", "🧠")
    
    @staticmethod
    def create_agent_workflows_tab():
        """Create Agent Workflows tab"""
        try:
            from gui.agent_workflows_interface import AgentWorkflowsInterface
            return AgentWorkflowsInterface()
        except Exception as e:
            print(f"[TabFactory] Error creating agent workflows tab: {e}")
            return TabFactory._create_fallback_tab("Agent Workflows", "🤖")
    
    @staticmethod
    def create_development_tools_tab():
        """Create Development Tools tab"""
        try:
            from gui.development_tools_interface import DevelopmentToolsInterface
            return DevelopmentToolsInterface()
        except Exception as e:
            print(f"[TabFactory] Error creating dev tools tab: {e}")
            return TabFactory._create_fallback_tab("Development Tools", "🛠️")
    
    @staticmethod
    def create_configuration_tab():
        """Create Configuration tab"""
        try:
            from gui.configuration_interface import ConfigurationInterface
            return ConfigurationInterface()
        except Exception as e:
            print(f"[TabFactory] Error creating config tab: {e}")
            return TabFactory._create_fallback_tab("Configuration", "⚙️")
    
    @staticmethod
    def _create_fallback_tab(title: str, icon: str):
        """Create a simple fallback tab when the main interface fails"""
        if not PYQT_AVAILABLE:
            return None
            
        from gui.components.base.base_tab import BaseTab
        
        class FallbackTab(BaseTab):
            def setup_content(self):
                from PyQt5.QtWidgets import QLabel
                label = QLabel(f"Tab '{title}' is under construction.\nPlease check back later.")
                label.setStyleSheet("color: #666; font-size: 14px; padding: 20px;")
                self.layout.addWidget(label)
        
        return FallbackTab(title, icon)
    
    @staticmethod
    def get_all_tab_creators():
        """Get all available tab creator methods"""
        return [
            ("ai_models", TabFactory.create_ai_models_tab),
            ("system_monitoring", TabFactory.create_system_monitoring_tab),
            ("vector_database", TabFactory.create_vector_database_tab),
            ("memory_management", TabFactory.create_memory_management_tab),
            ("agent_workflows", TabFactory.create_agent_workflows_tab),
            ("development_tools", TabFactory.create_development_tools_tab),
            ("configuration", TabFactory.create_configuration_tab),
        ]