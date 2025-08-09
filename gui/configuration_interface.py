#!/usr/bin/env python3
"""
Stage 6: Enhanced Configuration Interface
Professional settings management with comprehensive functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class ConfigurationInterface:
    """Stage 6: Enhanced configuration management interface"""
    
    def __init__(self, parent):
        self.parent = parent
        self.config_data = {}
        self.load_configuration()
        self.create_interface()
    
    def load_configuration(self):
        """Load configuration from file"""
        config_path = "config/settings.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config_data = json.load(f)
            except:
                self.config_data = self.get_default_config()
        else:
            self.config_data = self.get_default_config()
    
    def get_default_config(self):
        """Default configuration settings"""
        return {
            "system": {
                "debug_mode": False,
                "auto_save": True,
                "backup_enabled": True,
                "log_level": "INFO"
            },
            "ui": {
                "theme": "Professional",
                "font_size": 12,
                "animation_enabled": True,
                "confirm_actions": True
            },
            "performance": {
                "memory_optimization": True,
                "cpu_optimization": True,
                "cache_enabled": True,
                "background_processing": True
            }
        }
    
    def save_configuration(self):
        """Save configuration to file"""
        os.makedirs("config", exist_ok=True)
        try:
            with open("config/settings.json", 'w') as f:
                json.dump(self.config_data, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def create_interface(self):
        """Create enhanced configuration management interface"""
        
        # Create notebook for organized settings
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # System Settings Tab
        self.create_system_tab(notebook)
        
        # UI Settings Tab
        self.create_ui_tab(notebook)
        
        # Performance Settings Tab
        self.create_performance_tab(notebook)
        
        # Control buttons
        self.create_control_buttons()
    
    def create_system_tab(self, notebook):
        """Create system configuration tab"""
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="System Settings")
        
        # Debug mode
        self.debug_var = tk.BooleanVar(value=self.config_data["system"]["debug_mode"])
        ttk.Checkbutton(system_frame, text="Debug Mode", variable=self.debug_var,
                       command=self.update_system_config).pack(anchor=tk.W, pady=5)
        
        # Auto-save
        self.autosave_var = tk.BooleanVar(value=self.config_data["system"]["auto_save"])
        ttk.Checkbutton(system_frame, text="Auto-save Enabled", variable=self.autosave_var,
                       command=self.update_system_config).pack(anchor=tk.W, pady=5)
        
        # Backup
        self.backup_var = tk.BooleanVar(value=self.config_data["system"]["backup_enabled"])
        ttk.Checkbutton(system_frame, text="Backup Enabled", variable=self.backup_var,
                       command=self.update_system_config).pack(anchor=tk.W, pady=5)
        
        # Log level
        ttk.Label(system_frame, text="Log Level:").pack(anchor=tk.W, pady=(15,5))
        self.loglevel_var = tk.StringVar(value=self.config_data["system"]["log_level"])
        log_combo = ttk.Combobox(system_frame, textvariable=self.loglevel_var,
                                values=["DEBUG", "INFO", "WARNING", "ERROR"])
        log_combo.pack(anchor=tk.W, pady=5)
        log_combo.bind("<<ComboboxSelected>>", lambda e: self.update_system_config())
    
    def create_ui_tab(self, notebook):
        """Create UI configuration tab"""
        ui_frame = ttk.Frame(notebook)
        notebook.add(ui_frame, text="UI Settings")
        
        # Theme selection
        ttk.Label(ui_frame, text="Theme:").pack(anchor=tk.W, pady=(5,5))
        self.theme_var = tk.StringVar(value=self.config_data["ui"]["theme"])
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var,
                                  values=["Professional", "Dark", "Light", "High Contrast"])
        theme_combo.pack(anchor=tk.W, pady=5)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.update_ui_config())
        
        # Font size
        ttk.Label(ui_frame, text="Font Size:").pack(anchor=tk.W, pady=(15,5))
        self.fontsize_var = tk.IntVar(value=self.config_data["ui"]["font_size"])
        font_scale = ttk.Scale(ui_frame, from_=8, to=20, variable=self.fontsize_var,
                              orient=tk.HORIZONTAL, command=self.update_ui_config)
        font_scale.pack(anchor=tk.W, pady=5, fill=tk.X, padx=(0,100))
        
        # Animations
        self.animation_var = tk.BooleanVar(value=self.config_data["ui"]["animation_enabled"])
        ttk.Checkbutton(ui_frame, text="Enable Animations", variable=self.animation_var,
                       command=self.update_ui_config).pack(anchor=tk.W, pady=5)
        
        # Confirm actions
        self.confirm_var = tk.BooleanVar(value=self.config_data["ui"]["confirm_actions"])
        ttk.Checkbutton(ui_frame, text="Confirm Destructive Actions", variable=self.confirm_var,
                       command=self.update_ui_config).pack(anchor=tk.W, pady=5)
    
    def create_performance_tab(self, notebook):
        """Create performance configuration tab"""
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="Performance")
        
        # Memory optimization
        self.memory_var = tk.BooleanVar(value=self.config_data["performance"]["memory_optimization"])
        ttk.Checkbutton(perf_frame, text="Memory Optimization", variable=self.memory_var,
                       command=self.update_performance_config).pack(anchor=tk.W, pady=5)
        
        # CPU optimization
        self.cpu_var = tk.BooleanVar(value=self.config_data["performance"]["cpu_optimization"])
        ttk.Checkbutton(perf_frame, text="CPU Optimization", variable=self.cpu_var,
                       command=self.update_performance_config).pack(anchor=tk.W, pady=5)
        
        # Cache
        self.cache_var = tk.BooleanVar(value=self.config_data["performance"]["cache_enabled"])
        ttk.Checkbutton(perf_frame, text="Cache Enabled", variable=self.cache_var,
                       command=self.update_performance_config).pack(anchor=tk.W, pady=5)
        
        # Background processing
        self.background_var = tk.BooleanVar(value=self.config_data["performance"]["background_processing"])
        ttk.Checkbutton(perf_frame, text="Background Processing", variable=self.background_var,
                       command=self.update_performance_config).pack(anchor=tk.W, pady=5)
    
    def create_control_buttons(self):
        """Create control buttons"""
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Save Configuration", 
                  command=self.save_configuration).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Configuration", 
                  command=self.export_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import Configuration", 
                  command=self.import_config).pack(side=tk.LEFT, padx=5)
    
    def update_system_config(self):
        """Update system configuration"""
        self.config_data["system"]["debug_mode"] = self.debug_var.get()
        self.config_data["system"]["auto_save"] = self.autosave_var.get()
        self.config_data["system"]["backup_enabled"] = self.backup_var.get()
        self.config_data["system"]["log_level"] = self.loglevel_var.get()
    
    def update_ui_config(self, event=None):
        """Update UI configuration"""
        self.config_data["ui"]["theme"] = self.theme_var.get()
        self.config_data["ui"]["font_size"] = self.fontsize_var.get()
        self.config_data["ui"]["animation_enabled"] = self.animation_var.get()
        self.config_data["ui"]["confirm_actions"] = self.confirm_var.get()
    
    def update_performance_config(self):
        """Update performance configuration"""
        self.config_data["performance"]["memory_optimization"] = self.memory_var.get()
        self.config_data["performance"]["cpu_optimization"] = self.cpu_var.get()
        self.config_data["performance"]["cache_enabled"] = self.cache_var.get()
        self.config_data["performance"]["background_processing"] = self.background_var.get()
    
    def reset_defaults(self):
        """Reset to default configuration"""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.config_data = self.get_default_config()
            # Update all variables
            self.debug_var.set(self.config_data["system"]["debug_mode"])
            self.autosave_var.set(self.config_data["system"]["auto_save"])
            self.backup_var.set(self.config_data["system"]["backup_enabled"])
            self.loglevel_var.set(self.config_data["system"]["log_level"])
            self.theme_var.set(self.config_data["ui"]["theme"])
            self.fontsize_var.set(self.config_data["ui"]["font_size"])
            self.animation_var.set(self.config_data["ui"]["animation_enabled"])
            self.confirm_var.set(self.config_data["ui"]["confirm_actions"])
            self.memory_var.set(self.config_data["performance"]["memory_optimization"])
            self.cpu_var.set(self.config_data["performance"]["cpu_optimization"])
            self.cache_var.set(self.config_data["performance"]["cache_enabled"])
            self.background_var.set(self.config_data["performance"]["background_processing"])
    
    def export_config(self):
        """Export configuration to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.config_data, f, indent=4)
                messagebox.showinfo("Success", "Configuration exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def import_config(self):
        """Import configuration from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported_config = json.load(f)
                self.config_data.update(imported_config)
                messagebox.showinfo("Success", "Configuration imported successfully!")
                # Refresh the interface
                self.reset_defaults()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {e}")
