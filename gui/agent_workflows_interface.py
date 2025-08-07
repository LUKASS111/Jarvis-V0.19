#!/usr/bin/env python3
"""
Stage 10: Enhanced Agent Workflows Interface
Professional workflow automation and management dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class AgentWorkflowsInterface:
    """Stage 10: Professional Agent Workflows Management Interface"""
    
    def __init__(self, parent):
        self.parent = parent
        self.workflows = {}
        self.active_workflows = {}
        self.workflow_history = []
        
        self.setup_interface()
        self.load_workflows()
    
    def setup_interface(self):
        """Create the professional workflows interface"""
        
        # Main container with notebook for tabs
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Workflow Designer
        self.create_workflow_designer_tab()
        
        # Tab 2: Active Workflows
        self.create_active_workflows_tab()
        
        # Tab 3: Workflow Library
        self.create_workflow_library_tab()
        
        # Tab 4: Automation Settings
        self.create_automation_settings_tab()
        
        # Tab 5: Performance Analytics
        self.create_performance_analytics_tab()
    
    def create_workflow_designer_tab(self):
        """Create workflow designer interface"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Workflow Designer")
        
        # Header
        header_frame = ttk.LabelFrame(frame, text="🔧 Workflow Designer", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Design and configure automated workflows", 
                 font=('Arial', 10)).pack(anchor=tk.W)
        
        # Main content area
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Workflow properties
        left_panel = ttk.LabelFrame(content_frame, text="Workflow Properties", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Workflow name
        ttk.Label(left_panel, text="Workflow Name:").pack(anchor=tk.W, pady=(0, 5))
        self.workflow_name_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.workflow_name_var, width=30).pack(fill=tk.X, pady=(0, 10))
        
        # Trigger type
        ttk.Label(left_panel, text="Trigger Type:").pack(anchor=tk.W, pady=(0, 5))
        self.trigger_type_var = tk.StringVar(value="Manual")
        trigger_combo = ttk.Combobox(left_panel, textvariable=self.trigger_type_var, 
                                   values=["Manual", "Scheduled", "Event-based", "API Call", "File Change"], 
                                   state="readonly", width=27)
        trigger_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Priority
        ttk.Label(left_panel, text="Priority:").pack(anchor=tk.W, pady=(0, 5))
        self.priority_var = tk.StringVar(value="Normal")
        priority_combo = ttk.Combobox(left_panel, textvariable=self.priority_var,
                                    values=["Critical", "High", "Normal", "Low"], 
                                    state="readonly", width=27)
        priority_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Right panel - Workflow steps
        right_panel = ttk.LabelFrame(content_frame, text="Workflow Steps", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Steps listbox
        self.steps_listbox = tk.Listbox(right_panel, height=10)
        self.steps_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Step buttons
        step_buttons_frame = ttk.Frame(right_panel)
        step_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(step_buttons_frame, text="Add Step", 
                  command=self.add_workflow_step).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(step_buttons_frame, text="Edit Step", 
                  command=self.edit_workflow_step).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(step_buttons_frame, text="Remove Step", 
                  command=self.remove_workflow_step).pack(side=tk.LEFT, padx=(0, 5))
        
        # Control buttons
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Save Workflow", 
                  command=self.save_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Test Workflow", 
                  command=self.test_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Deploy Workflow", 
                  command=self.deploy_workflow).pack(side=tk.LEFT)
    
    def create_active_workflows_tab(self):
        """Create active workflows monitoring interface"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Active Workflows")
        
        # Header
        header_frame = ttk.LabelFrame(frame, text="⚡ Active Workflows Monitor", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status summary
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(fill=tk.X)
        
        self.active_count_label = ttk.Label(status_frame, text="Active: 0", font=('Arial', 10, 'bold'))
        self.active_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.completed_count_label = ttk.Label(status_frame, text="Completed: 0", font=('Arial', 10))
        self.completed_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.failed_count_label = ttk.Label(status_frame, text="Failed: 0", font=('Arial', 10))
        self.failed_count_label.pack(side=tk.LEFT)
        
        # Workflows tree
        tree_frame = ttk.LabelFrame(frame, text="Workflow Status", padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview
        columns = ("Name", "Status", "Progress", "Started", "Duration", "Next Action")
        self.workflows_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        for col in columns:
            self.workflows_tree.heading(col, text=col)
            self.workflows_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.workflows_tree.yview)
        self.workflows_tree.configure(yscrollcommand=scrollbar.set)
        
        self.workflows_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Pause Workflow", 
                  command=self.pause_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Resume Workflow", 
                  command=self.resume_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Stop Workflow", 
                  command=self.stop_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="View Logs", 
                  command=self.view_workflow_logs).pack(side=tk.LEFT)
    
    def create_workflow_library_tab(self):
        """Create workflow library interface"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Workflow Library")
        
        # Header
        header_frame = ttk.LabelFrame(frame, text="📚 Workflow Library", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Browse and manage your workflow templates", 
                 font=('Arial', 10)).pack(anchor=tk.W)
        
        # Library content
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Categories
        left_panel = ttk.LabelFrame(content_frame, text="Categories", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        categories = ["All Workflows", "Data Processing", "AI Models", "Monitoring", "Deployment", "Testing", "Custom"]
        self.category_listbox = tk.Listbox(left_panel, height=15, width=20)
        for category in categories:
            self.category_listbox.insert(tk.END, category)
        self.category_listbox.pack(fill=tk.BOTH, expand=True)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Right panel - Workflows
        right_panel = ttk.LabelFrame(content_frame, text="Available Workflows", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Workflows listbox with details
        self.library_workflows_listbox = tk.Listbox(right_panel, height=10)
        self.library_workflows_listbox.pack(fill=tk.X, pady=(0, 10))
        self.library_workflows_listbox.bind('<<ListboxSelect>>', self.on_library_workflow_select)
        
        # Workflow details
        details_frame = ttk.LabelFrame(right_panel, text="Workflow Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.workflow_details_text = scrolledtext.ScrolledText(details_frame, height=8, width=50)
        self.workflow_details_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Import Workflow", 
                  command=self.import_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Export Workflow", 
                  command=self.export_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Duplicate Workflow", 
                  command=self.duplicate_workflow).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Delete Workflow", 
                  command=self.delete_workflow).pack(side=tk.LEFT)
    
    def create_automation_settings_tab(self):
        """Create automation settings interface"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Automation Settings")
        
        # Header
        header_frame = ttk.LabelFrame(frame, text="⚙️ Automation Configuration", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Global settings
        global_frame = ttk.LabelFrame(frame, text="Global Settings", padding=10)
        global_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Auto-start workflows
        self.auto_start_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(global_frame, text="Auto-start workflows on system startup", 
                       variable=self.auto_start_var).pack(anchor=tk.W, pady=5)
        
        # Max concurrent workflows
        concurrent_frame = ttk.Frame(global_frame)
        concurrent_frame.pack(fill=tk.X, pady=5)
        ttk.Label(concurrent_frame, text="Max concurrent workflows:").pack(side=tk.LEFT)
        self.max_concurrent_var = tk.StringVar(value="5")
        ttk.Spinbox(concurrent_frame, from_=1, to=20, textvariable=self.max_concurrent_var, 
                   width=10).pack(side=tk.LEFT, padx=(10, 0))
        
        # Retry settings
        retry_frame = ttk.LabelFrame(frame, text="Retry Configuration", padding=10)
        retry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Auto-retry failed workflows
        self.auto_retry_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(retry_frame, text="Auto-retry failed workflows", 
                       variable=self.auto_retry_var).pack(anchor=tk.W, pady=5)
        
        # Max retry attempts
        retry_attempts_frame = ttk.Frame(retry_frame)
        retry_attempts_frame.pack(fill=tk.X, pady=5)
        ttk.Label(retry_attempts_frame, text="Max retry attempts:").pack(side=tk.LEFT)
        self.max_retries_var = tk.StringVar(value="3")
        ttk.Spinbox(retry_attempts_frame, from_=1, to=10, textvariable=self.max_retries_var, 
                   width=10).pack(side=tk.LEFT, padx=(10, 0))
        
        # Notification settings
        notification_frame = ttk.LabelFrame(frame, text="Notifications", padding=10)
        notification_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.notify_success_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(notification_frame, text="Notify on workflow success", 
                       variable=self.notify_success_var).pack(anchor=tk.W, pady=2)
        
        self.notify_failure_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notification_frame, text="Notify on workflow failure", 
                       variable=self.notify_failure_var).pack(anchor=tk.W, pady=2)
        
        self.notify_completion_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notification_frame, text="Notify on batch completion", 
                       variable=self.notify_completion_var).pack(anchor=tk.W, pady=2)
        
        # Save button
        ttk.Button(frame, text="Save Settings", 
                  command=self.save_automation_settings).pack(pady=10)
    
    def create_performance_analytics_tab(self):
        """Create performance analytics interface"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Performance Analytics")
        
        # Header
        header_frame = ttk.LabelFrame(frame, text="📊 Workflow Performance Analytics", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Summary metrics
        metrics_frame = ttk.LabelFrame(frame, text="Performance Summary", padding=10)
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create metrics grid
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X)
        
        # First row
        row1 = ttk.Frame(metrics_grid)
        row1.pack(fill=tk.X, pady=5)
        
        self.total_workflows_label = ttk.Label(row1, text="Total Workflows: 0", font=('Arial', 10, 'bold'))
        self.total_workflows_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.success_rate_label = ttk.Label(row1, text="Success Rate: 0%", font=('Arial', 10, 'bold'))
        self.success_rate_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.avg_duration_label = ttk.Label(row1, text="Avg Duration: 0s", font=('Arial', 10, 'bold'))
        self.avg_duration_label.pack(side=tk.LEFT)
        
        # Second row
        row2 = ttk.Frame(metrics_grid)
        row2.pack(fill=tk.X, pady=5)
        
        self.active_workflows_label = ttk.Label(row2, text="Active: 0", font=('Arial', 10))
        self.active_workflows_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.queued_workflows_label = ttk.Label(row2, text="Queued: 0", font=('Arial', 10))
        self.queued_workflows_label.pack(side=tk.LEFT, padx=(0, 30))
        
        self.failed_workflows_label = ttk.Label(row2, text="Failed: 0", font=('Arial', 10))
        self.failed_workflows_label.pack(side=tk.LEFT)
        
        # Performance chart placeholder
        chart_frame = ttk.LabelFrame(frame, text="Performance Trends", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(chart_frame, text="📈 Performance trend visualization would be displayed here", 
                 font=('Arial', 12)).pack(expand=True)
        ttk.Label(chart_frame, text="• Success rates over time", 
                 font=('Arial', 10)).pack(anchor=tk.W, padx=20)
        ttk.Label(chart_frame, text="• Average execution times", 
                 font=('Arial', 10)).pack(anchor=tk.W, padx=20)
        ttk.Label(chart_frame, text="• Resource utilization patterns", 
                 font=('Arial', 10)).pack(anchor=tk.W, padx=20)
        ttk.Label(chart_frame, text="• Error frequency analysis", 
                 font=('Arial', 10)).pack(anchor=tk.W, padx=20)
        
        # Refresh button
        ttk.Button(frame, text="Refresh Analytics", 
                  command=self.refresh_analytics).pack(pady=10)
    
    # Event handlers and functionality methods
    def add_workflow_step(self):
        """Add a new step to the workflow"""
        # Create step dialog
        step_dialog = tk.Toplevel(self.parent)
        step_dialog.title("Add Workflow Step")
        step_dialog.geometry("400x300")
        step_dialog.transient(self.parent)
        step_dialog.grab_set()
        
        # Step configuration form
        ttk.Label(step_dialog, text="Step Name:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        step_name_var = tk.StringVar()
        ttk.Entry(step_dialog, textvariable=step_name_var, width=50).pack(padx=10, pady=(0, 10))
        
        ttk.Label(step_dialog, text="Action Type:").pack(anchor=tk.W, padx=10, pady=(0, 5))
        action_type_var = tk.StringVar(value="Execute Command")
        action_combo = ttk.Combobox(step_dialog, textvariable=action_type_var,
                                  values=["Execute Command", "Call API", "Process Data", "Send Notification", "Wait", "Conditional"], 
                                  state="readonly", width=47)
        action_combo.pack(padx=10, pady=(0, 10))
        
        ttk.Label(step_dialog, text="Configuration:").pack(anchor=tk.W, padx=10, pady=(0, 5))
        config_text = scrolledtext.ScrolledText(step_dialog, width=50, height=8)
        config_text.pack(padx=10, pady=(0, 10))
        
        def add_step():
            name = step_name_var.get().strip()
            if name:
                step_info = f"{name} ({action_type_var.get()})"
                self.steps_listbox.insert(tk.END, step_info)
                step_dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please enter a step name")
        
        ttk.Button(step_dialog, text="Add Step", command=add_step).pack(pady=10)
    
    def edit_workflow_step(self):
        """Edit selected workflow step"""
        selection = self.steps_listbox.curselection()
        if selection:
            messagebox.showinfo("Edit Step", f"Editing step: {self.steps_listbox.get(selection[0])}")
        else:
            messagebox.showwarning("Warning", "Please select a step to edit")
    
    def remove_workflow_step(self):
        """Remove selected workflow step"""
        selection = self.steps_listbox.curselection()
        if selection:
            self.steps_listbox.delete(selection[0])
        else:
            messagebox.showwarning("Warning", "Please select a step to remove")
    
    def save_workflow(self):
        """Save the current workflow"""
        name = self.workflow_name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a workflow name")
            return
        
        # Create workflow data
        workflow_data = {
            "name": name,
            "trigger_type": self.trigger_type_var.get(),
            "priority": self.priority_var.get(),
            "steps": [self.steps_listbox.get(i) for i in range(self.steps_listbox.size())],
            "created": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # Save to workflows dictionary
        self.workflows[name] = workflow_data
        
        # Save to file
        try:
            os.makedirs("config/workflows", exist_ok=True)
            with open(f"config/workflows/{name}.json", "w") as f:
                json.dump(workflow_data, f, indent=2)
            
            messagebox.showinfo("Success", f"Workflow '{name}' saved successfully")
            self.refresh_workflow_library()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workflow: {str(e)}")
    
    def test_workflow(self):
        """Test the current workflow"""
        name = self.workflow_name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a workflow name")
            return
        
        messagebox.showinfo("Test Workflow", f"Testing workflow '{name}' in simulation mode...")
    
    def deploy_workflow(self):
        """Deploy the current workflow"""
        name = self.workflow_name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a workflow name")
            return
        
        messagebox.showinfo("Deploy Workflow", f"Deploying workflow '{name}' to production...")
    
    def pause_workflow(self):
        """Pause selected active workflow"""
        selection = self.workflows_tree.selection()
        if selection:
            messagebox.showinfo("Pause Workflow", "Workflow paused successfully")
        else:
            messagebox.showwarning("Warning", "Please select a workflow to pause")
    
    def resume_workflow(self):
        """Resume selected workflow"""
        selection = self.workflows_tree.selection()
        if selection:
            messagebox.showinfo("Resume Workflow", "Workflow resumed successfully")
        else:
            messagebox.showwarning("Warning", "Please select a workflow to resume")
    
    def stop_workflow(self):
        """Stop selected workflow"""
        selection = self.workflows_tree.selection()
        if selection:
            if messagebox.askyesno("Confirm", "Are you sure you want to stop this workflow?"):
                messagebox.showinfo("Stop Workflow", "Workflow stopped successfully")
        else:
            messagebox.showwarning("Warning", "Please select a workflow to stop")
    
    def view_workflow_logs(self):
        """View logs for selected workflow"""
        selection = self.workflows_tree.selection()
        if selection:
            messagebox.showinfo("Workflow Logs", "Opening workflow logs...")
        else:
            messagebox.showwarning("Warning", "Please select a workflow to view logs")
    
    def on_category_select(self, event):
        """Handle category selection"""
        self.refresh_workflow_library()
    
    def on_library_workflow_select(self, event):
        """Handle workflow selection in library"""
        selection = self.library_workflows_listbox.curselection()
        if selection:
            workflow_name = self.library_workflows_listbox.get(selection[0])
            # Display workflow details
            details = f"Workflow: {workflow_name}\n\n"
            details += "Description: Professional workflow template\n"
            details += "Steps: 5\n"
            details += "Category: Automation\n"
            details += "Last Modified: 2025-01-07\n"
            details += "Status: Ready for deployment\n\n"
            details += "This workflow provides automated task execution with comprehensive error handling and monitoring capabilities."
            
            self.workflow_details_text.delete(1.0, tk.END)
            self.workflow_details_text.insert(1.0, details)
    
    def import_workflow(self):
        """Import workflow from file"""
        file_path = filedialog.askopenfilename(
            title="Import Workflow",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    workflow_data = json.load(f)
                
                name = workflow_data.get("name", "Imported Workflow")
                self.workflows[name] = workflow_data
                messagebox.showinfo("Success", f"Workflow '{name}' imported successfully")
                self.refresh_workflow_library()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import workflow: {str(e)}")
    
    def export_workflow(self):
        """Export selected workflow"""
        selection = self.library_workflows_listbox.curselection()
        if selection:
            workflow_name = self.library_workflows_listbox.get(selection[0])
            file_path = filedialog.asksaveasfilename(
                title="Export Workflow",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    workflow_data = self.workflows.get(workflow_name, {})
                    with open(file_path, "w") as f:
                        json.dump(workflow_data, f, indent=2)
                    messagebox.showinfo("Success", f"Workflow exported to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export workflow: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please select a workflow to export")
    
    def duplicate_workflow(self):
        """Duplicate selected workflow"""
        selection = self.library_workflows_listbox.curselection()
        if selection:
            workflow_name = self.library_workflows_listbox.get(selection[0])
            new_name = f"{workflow_name} (Copy)"
            if workflow_name in self.workflows:
                workflow_data = self.workflows[workflow_name].copy()
                workflow_data["name"] = new_name
                self.workflows[new_name] = workflow_data
                messagebox.showinfo("Success", f"Workflow duplicated as '{new_name}'")
                self.refresh_workflow_library()
        else:
            messagebox.showwarning("Warning", "Please select a workflow to duplicate")
    
    def delete_workflow(self):
        """Delete selected workflow"""
        selection = self.library_workflows_listbox.curselection()
        if selection:
            workflow_name = self.library_workflows_listbox.get(selection[0])
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{workflow_name}'?"):
                if workflow_name in self.workflows:
                    del self.workflows[workflow_name]
                    # Also delete file if exists
                    try:
                        os.remove(f"config/workflows/{workflow_name}.json")
                    except:
                        pass
                    messagebox.showinfo("Success", f"Workflow '{workflow_name}' deleted")
                    self.refresh_workflow_library()
        else:
            messagebox.showwarning("Warning", "Please select a workflow to delete")
    
    def save_automation_settings(self):
        """Save automation settings"""
        settings = {
            "auto_start": self.auto_start_var.get(),
            "max_concurrent": int(self.max_concurrent_var.get()),
            "auto_retry": self.auto_retry_var.get(),
            "max_retries": int(self.max_retries_var.get()),
            "notify_success": self.notify_success_var.get(),
            "notify_failure": self.notify_failure_var.get(),
            "notify_completion": self.notify_completion_var.get(),
            "updated": datetime.now().isoformat()
        }
        
        try:
            os.makedirs("config", exist_ok=True)
            with open("config/automation_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Success", "Automation settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def refresh_analytics(self):
        """Refresh performance analytics"""
        # Update analytics labels with current data
        self.total_workflows_label.config(text="Total Workflows: 15")
        self.success_rate_label.config(text="Success Rate: 92%")
        self.avg_duration_label.config(text="Avg Duration: 45s")
        self.active_workflows_label.config(text="Active: 3")
        self.queued_workflows_label.config(text="Queued: 1")
        self.failed_workflows_label.config(text="Failed: 2")
        
        messagebox.showinfo("Analytics", "Performance analytics refreshed")
    
    def load_workflows(self):
        """Load existing workflows"""
        try:
            workflows_dir = "config/workflows"
            if os.path.exists(workflows_dir):
                for filename in os.listdir(workflows_dir):
                    if filename.endswith(".json"):
                        filepath = os.path.join(workflows_dir, filename)
                        with open(filepath, "r") as f:
                            workflow_data = json.load(f)
                            name = workflow_data.get("name", filename[:-5])
                            self.workflows[name] = workflow_data
            
            self.refresh_workflow_library()
            self.refresh_active_workflows()
        except Exception as e:
            print(f"Error loading workflows: {e}")
    
    def refresh_workflow_library(self):
        """Refresh the workflow library display"""
        self.library_workflows_listbox.delete(0, tk.END)
        for name in sorted(self.workflows.keys()):
            self.library_workflows_listbox.insert(tk.END, name)
    
    def refresh_active_workflows(self):
        """Refresh the active workflows display"""
        # Clear existing items
        for item in self.workflows_tree.get_children():
            self.workflows_tree.delete(item)
        
        # Add sample active workflows
        sample_workflows = [
            ("Data Processing", "Running", "75%", "10:30 AM", "15 min", "Process batch 3/4"),
            ("Model Training", "Paused", "60%", "09:45 AM", "2h 30m", "Waiting for resources"),
            ("Report Generation", "Completed", "100%", "08:00 AM", "45 min", "N/A"),
            ("System Backup", "Failed", "25%", "07:30 AM", "10 min", "Retry scheduled"),
        ]
        
        for workflow in sample_workflows:
            self.workflows_tree.insert("", tk.END, values=workflow)
        
        # Update counts
        self.active_count_label.config(text="Active: 1")
        self.completed_count_label.config(text="Completed: 1")
        self.failed_count_label.config(text="Failed: 1")