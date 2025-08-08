#!/usr/bin/env python3
"""
Configuration Interface Module
==============================
Professional GUI interface for system configuration management.

Features:
- Settings management with professional controls
- Configuration validation and error handling
- User preferences with intuitive interface
- System options with organized categories
- Advanced configuration with expert controls

Author: Jarvis 1.0.0 Engineering Team
Date: 2025-01-07
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from pathlib import Path

class ConfigurationInterface:
    """Professional configuration management interface"""
    
    def __init__(self, parent):
        self.parent = parent
        self.config_file = Path("config/settings.json")
        self.settings = self.load_settings()
        
        self.create_interface()
        self.load_current_settings()
    
    def create_interface(self):
        """Create comprehensive configuration interface"""
        # Main configuration frame
        self.config_frame = ttk.LabelFrame(self.parent, text="System Configuration", padding="10")
        self.config_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Create configuration sections
        self.create_general_settings()
        self.create_performance_settings()
        self.create_interface_settings()
        self.create_advanced_settings()
        self.create_action_buttons()
    
    def create_general_settings(self):
        """Create general settings section"""
        general_frame = ttk.LabelFrame(self.config_frame, text="General Settings", padding="5")
        general_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Application name setting
        ttk.Label(general_frame, text="Application Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.app_name_var = tk.StringVar(value="Jarvis 1.0.0")
        ttk.Entry(general_frame, textvariable=self.app_name_var, width=30).grid(row=0, column=1, sticky="w", pady=2)
        
        # Auto-save setting
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(general_frame, text="Enable Auto-Save", variable=self.auto_save_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)
        
        # Startup behavior
        ttk.Label(general_frame, text="Startup Behavior:").grid(row=2, column=0, sticky="w", pady=2)
        self.startup_var = tk.StringVar(value="dashboard")
        startup_combo = ttk.Combobox(general_frame, textvariable=self.startup_var, 
                                   values=["dashboard", "last_session", "welcome"], width=27, state="readonly")
        startup_combo.grid(row=2, column=1, sticky="w", pady=2)
        
        # Data directory setting
        ttk.Label(general_frame, text="Data Directory:").grid(row=3, column=0, sticky="w", pady=2)
        self.data_dir_var = tk.StringVar(value="data/")
        data_frame = ttk.Frame(general_frame)
        data_frame.grid(row=3, column=1, sticky="w", pady=2)
        ttk.Entry(data_frame, textvariable=self.data_dir_var, width=25).grid(row=0, column=0)
        ttk.Button(data_frame, text="Browse", command=self.browse_data_directory, width=8).grid(row=0, column=1, padx=(5,0))
    
    def create_performance_settings(self):
        """Create performance settings section"""
        perf_frame = ttk.LabelFrame(self.config_frame, text="Performance Settings", padding="5")
        perf_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Memory limit setting
        ttk.Label(perf_frame, text="Memory Limit (MB):").grid(row=0, column=0, sticky="w", pady=2)
        self.memory_limit_var = tk.StringVar(value="512")
        memory_spinbox = ttk.Spinbox(perf_frame, from_=128, to=2048, increment=128, 
                                   textvariable=self.memory_limit_var, width=28)
        memory_spinbox.grid(row=0, column=1, sticky="w", pady=2)
        
        # Cache size setting
        ttk.Label(perf_frame, text="Cache Size (MB):").grid(row=1, column=0, sticky="w", pady=2)
        self.cache_size_var = tk.StringVar(value="128")
        cache_spinbox = ttk.Spinbox(perf_frame, from_=32, to=512, increment=32,
                                  textvariable=self.cache_size_var, width=28)
        cache_spinbox.grid(row=1, column=1, sticky="w", pady=2)
        
        # Thread pool size
        ttk.Label(perf_frame, text="Thread Pool Size:").grid(row=2, column=0, sticky="w", pady=2)
        self.thread_pool_var = tk.StringVar(value="4")
        thread_spinbox = ttk.Spinbox(perf_frame, from_=1, to=16, increment=1,
                                   textvariable=self.thread_pool_var, width=28)
        thread_spinbox.grid(row=2, column=1, sticky="w", pady=2)
        
        # Enable performance monitoring
        self.perf_monitor_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(perf_frame, text="Enable Performance Monitoring", 
                       variable=self.perf_monitor_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
    
    def create_interface_settings(self):
        """Create interface settings section"""
        ui_frame = ttk.LabelFrame(self.config_frame, text="Interface Settings", padding="5")
        ui_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Theme setting
        ttk.Label(ui_frame, text="Theme:").grid(row=0, column=0, sticky="w", pady=2)
        self.theme_var = tk.StringVar(value="professional")
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var,
                                 values=["professional", "dark", "light", "classic"], width=27, state="readonly")
        theme_combo.grid(row=0, column=1, sticky="w", pady=2)
        
        # Font size setting
        ttk.Label(ui_frame, text="Font Size:").grid(row=1, column=0, sticky="w", pady=2)
        self.font_size_var = tk.StringVar(value="10")
        font_spinbox = ttk.Spinbox(ui_frame, from_=8, to=16, increment=1,
                                 textvariable=self.font_size_var, width=28)
        font_spinbox.grid(row=1, column=1, sticky="w", pady=2)
        
        # Window layout
        ttk.Label(ui_frame, text="Window Layout:").grid(row=2, column=0, sticky="w", pady=2)
        self.layout_var = tk.StringVar(value="tabbed")
        layout_combo = ttk.Combobox(ui_frame, textvariable=self.layout_var,
                                  values=["tabbed", "windowed", "split"], width=27, state="readonly")
        layout_combo.grid(row=2, column=1, sticky="w", pady=2)
        
        # Show tooltips
        self.tooltips_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ui_frame, text="Show Tooltips", 
                       variable=self.tooltips_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
    
    def create_advanced_settings(self):
        """Create advanced settings section"""
        adv_frame = ttk.LabelFrame(self.config_frame, text="Advanced Settings", padding="5")
        adv_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Debug mode
        self.debug_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_frame, text="Enable Debug Mode",
                       variable=self.debug_mode_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        
        # Logging level
        ttk.Label(adv_frame, text="Logging Level:").grid(row=1, column=0, sticky="w", pady=2)
        self.log_level_var = tk.StringVar(value="INFO")
        log_combo = ttk.Combobox(adv_frame, textvariable=self.log_level_var,
                               values=["DEBUG", "INFO", "WARNING", "ERROR"], width=27, state="readonly")
        log_combo.grid(row=1, column=1, sticky="w", pady=2)
        
        # Database backup interval
        ttk.Label(adv_frame, text="Backup Interval (hours):").grid(row=2, column=0, sticky="w", pady=2)
        self.backup_interval_var = tk.StringVar(value="24")
        backup_spinbox = ttk.Spinbox(adv_frame, from_=1, to=168, increment=1,
                                   textvariable=self.backup_interval_var, width=28)
        backup_spinbox.grid(row=2, column=1, sticky="w", pady=2)
        
        # Enable analytics
        self.analytics_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_frame, text="Enable Usage Analytics",
                       variable=self.analytics_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
    
    def create_action_buttons(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self.config_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Import Settings", command=self.import_settings, width=15).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Export Settings", command=self.export_settings, width=15).grid(row=0, column=3, padx=5)
    
    def load_settings(self):
        """Load settings from configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return self.get_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.get_default_settings()
    
    def get_default_settings(self):
        """Get default settings"""
        return {
            "general": {
                "app_name": "Jarvis 1.0.0",
                "auto_save": True,
                "startup_behavior": "dashboard",
                "data_directory": "data/"
            },
            "performance": {
                "memory_limit": 512,
                "cache_size": 128,
                "thread_pool_size": 4,
                "performance_monitoring": True
            },
            "interface": {
                "theme": "professional",
                "font_size": 10,
                "window_layout": "tabbed",
                "show_tooltips": True
            },
            "advanced": {
                "debug_mode": False,
                "logging_level": "INFO",
                "backup_interval": 24,
                "enable_analytics": False
            }
        }
    
    def load_current_settings(self):
        """Load current settings into interface"""
        if "general" in self.settings:
            general = self.settings["general"]
            self.app_name_var.set(general.get("app_name", "Jarvis 1.0.0"))
            self.auto_save_var.set(general.get("auto_save", True))
            self.startup_var.set(general.get("startup_behavior", "dashboard"))
            self.data_dir_var.set(general.get("data_directory", "data/"))
        
        if "performance" in self.settings:
            perf = self.settings["performance"]
            self.memory_limit_var.set(str(perf.get("memory_limit", 512)))
            self.cache_size_var.set(str(perf.get("cache_size", 128)))
            self.thread_pool_var.set(str(perf.get("thread_pool_size", 4)))
            self.perf_monitor_var.set(perf.get("performance_monitoring", True))
        
        if "interface" in self.settings:
            ui = self.settings["interface"]
            self.theme_var.set(ui.get("theme", "professional"))
            self.font_size_var.set(str(ui.get("font_size", 10)))
            self.layout_var.set(ui.get("window_layout", "tabbed"))
            self.tooltips_var.set(ui.get("show_tooltips", True))
        
        if "advanced" in self.settings:
            adv = self.settings["advanced"]
            self.debug_mode_var.set(adv.get("debug_mode", False))
            self.log_level_var.set(adv.get("logging_level", "INFO"))
            self.backup_interval_var.set(str(adv.get("backup_interval", 24)))
            self.analytics_var.set(adv.get("enable_analytics", False))
    
    def save_settings(self):
        """Save current settings"""
        try:
            settings = {
                "general": {
                    "app_name": self.app_name_var.get(),
                    "auto_save": self.auto_save_var.get(),
                    "startup_behavior": self.startup_var.get(),
                    "data_directory": self.data_dir_var.get()
                },
                "performance": {
                    "memory_limit": int(self.memory_limit_var.get()),
                    "cache_size": int(self.cache_size_var.get()),
                    "thread_pool_size": int(self.thread_pool_var.get()),
                    "performance_monitoring": self.perf_monitor_var.get()
                },
                "interface": {
                    "theme": self.theme_var.get(),
                    "font_size": int(self.font_size_var.get()),
                    "window_layout": self.layout_var.get(),
                    "show_tooltips": self.tooltips_var.get()
                },
                "advanced": {
                    "debug_mode": self.debug_mode_var.get(),
                    "logging_level": self.log_level_var.get(),
                    "backup_interval": int(self.backup_interval_var.get()),
                    "enable_analytics": self.analytics_var.get()
                }
            }
            
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.settings = settings
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings = self.get_default_settings()
            self.load_current_settings()
            messagebox.showinfo("Reset Complete", "Settings have been reset to defaults.")
    
    def import_settings(self):
        """Import settings from file"""
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_settings = json.load(f)
                
                self.settings = imported_settings
                self.load_current_settings()
                messagebox.showinfo("Success", "Settings imported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def export_settings(self):
        """Export settings to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                current_settings = {
                    "general": {
                        "app_name": self.app_name_var.get(),
                        "auto_save": self.auto_save_var.get(),
                        "startup_behavior": self.startup_var.get(),
                        "data_directory": self.data_dir_var.get()
                    },
                    "performance": {
                        "memory_limit": int(self.memory_limit_var.get()),
                        "cache_size": int(self.cache_size_var.get()),
                        "thread_pool_size": int(self.thread_pool_var.get()),
                        "performance_monitoring": self.perf_monitor_var.get()
                    },
                    "interface": {
                        "theme": self.theme_var.get(),
                        "font_size": int(self.font_size_var.get()),
                        "window_layout": self.layout_var.get(),
                        "show_tooltips": self.tooltips_var.get()
                    },
                    "advanced": {
                        "debug_mode": self.debug_mode_var.get(),
                        "logging_level": self.log_level_var.get(),
                        "backup_interval": int(self.backup_interval_var.get()),
                        "enable_analytics": self.analytics_var.get()
                    }
                }
                
                with open(file_path, 'w') as f:
                    json.dump(current_settings, f, indent=2)
                
                messagebox.showinfo("Success", "Settings exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def browse_data_directory(self):
        """Browse for data directory"""
        directory = filedialog.askdirectory(title="Select Data Directory")
        if directory:
            self.data_dir_var.set(directory)

def create_configuration_tab(notebook):
    """Create configuration tab for main application"""
    config_frame = ttk.Frame(notebook)
    notebook.add(config_frame, text="Configuration")
    
    # Create configuration interface
    config_interface = ConfigurationInterface(config_frame)
    
    return config_frame, config_interface

if __name__ == "__main__":
    # Test the configuration interface
    root = tk.Tk()
    root.title("Configuration Interface Test")
    root.geometry("800x600")
    
    config_interface = ConfigurationInterface(root)
    
    root.mainloop()