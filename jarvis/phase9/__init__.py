#!/usr/bin/env python3
"""
Phase 9: Autonomous Intelligence & Predictive Systems
======================================================

Advanced autonomous intelligence with predictive capabilities, self-managing systems,
and proactive assistance for next-generation AI assistant experience.
"""

from .autonomous_intelligence_manager import AutonomousIntelligenceManager
from .predictive_analytics_engine import PredictiveAnalyticsEngine
from .self_management_system import SelfManagementSystem
from .proactive_assistance_engine import ProactiveAssistanceEngine
from .phase9_integration_manager import Phase9IntegrationManager

# Core Phase 9 functions
from .phase9_integration_manager import (
    process_phase9_request,
    get_phase9_dashboard,
    get_phase9_health,
    create_autonomous_assistant,
    enable_predictive_mode
)

__all__ = [
    'AutonomousIntelligenceManager',
    'PredictiveAnalyticsEngine', 
    'SelfManagementSystem',
    'ProactiveAssistanceEngine',
    'Phase9IntegrationManager',
    'process_phase9_request',
    'get_phase9_dashboard',
    'get_phase9_health',
    'create_autonomous_assistant',
    'enable_predictive_mode'
]

__version__ = "9.0.0"
__phase__ = "Autonomous Intelligence & Predictive Systems"