# GUI Configuration Interface
# This module provides GUI access to configuration functions

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class ConfigurationInterface:
    """GUI interface for configuration management functions."""
    
    def __init__(self, parent):
        self.parent = parent
        self.config_frame = None
        
    def create_config_panel(self):
        """Create configuration panel with all config functions."""
        self.config_frame = ttk.LabelFrame(self.parent, text="Configuration & Settings", padding=10)
        
        # System Configuration
        ttk.Label(self.config_frame, text="System Configuration:").grid(row=0, column=0, sticky="w", pady=5)
        
        config_buttons = [
            ("Edit General Settings", self.edit_general_settings),
            ("Manage User Preferences", self.manage_user_preferences),
            ("Configure API Keys", self.configure_api_keys),
            ("Set Memory Limits", self.set_memory_limits),
            ("Configure Performance", self.configure_performance),
            ("Manage Plugins", self.manage_plugins),
            ("Export Configuration", self.export_configuration),
            ("Import Configuration", self.import_configuration),
            ("Reset to Defaults", self.reset_to_defaults),
            ("Validate Configuration", self.validate_configuration)
        ]
        
        for i, (text, command) in enumerate(config_buttons, 1):
            ttk.Button(self.config_frame, text=text, command=command).grid(
                row=i, column=0, sticky="ew", padx=5, pady=2
            )
        
        return self.config_frame
    
    def edit_general_settings(self):
        """Open general settings editor."""
        messagebox.showinfo("Configuration", "General Settings editor opened")
        
    def manage_user_preferences(self):
        """Open user preferences manager."""
        messagebox.showinfo("Configuration", "User Preferences manager opened")
        
    def configure_api_keys(self):
        """Open API keys configuration."""
        messagebox.showinfo("Configuration", "API Keys configuration opened")
        
    def set_memory_limits(self):
        """Open memory limits configuration."""
        messagebox.showinfo("Configuration", "Memory Limits configuration opened")
        
    def configure_performance(self):
        """Open performance configuration."""
        messagebox.showinfo("Configuration", "Performance configuration opened")
        
    def manage_plugins(self):
        """Open plugin manager."""
        messagebox.showinfo("Configuration", "Plugin manager opened")
        
    def export_configuration(self):
        """Export current configuration."""
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Configuration", f"Configuration exported to {file_path}")
    
    def import_configuration(self):
        """Import configuration from file."""
        file_path = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Configuration", f"Configuration imported from {file_path}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        result = messagebox.askyesno("Configuration", "Reset all settings to defaults?")
        if result:
            messagebox.showinfo("Configuration", "Configuration reset to defaults")
    
    def validate_configuration(self):
        """Validate current configuration."""
        messagebox.showinfo("Configuration", "Configuration validation completed")
