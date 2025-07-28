#!/usr/bin/env python3
"""
Simplified self-modification module for AutoGPT
Basic code analysis and improvement suggestions
"""

import os
from error_handler import error_handler, ErrorLevel

# Poprawne dostępne modele zgodnie z ollama list
AVAILABLE_MODELS = [
    "llama3:8b",
    "codellama:13b", 
    "codellama:34b",
    "llama3:70b"
]

def self_modify_all():
    """Simplified self-modification process"""
    try:
        print("🔧 Starting simplified self-modification...")
        
        # Basic code analysis
        python_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    python_files.append(os.path.join(root, file))
        
        print(f"📊 Found {len(python_files)} Python files to analyze")
        
        # Simple analysis report
        total_lines = 0
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    print(f"   📄 {file_path}: {lines} lines")
            except Exception as e:
                print(f"   ❌ Error reading {file_path}: {e}")
        
        print(f"\n📈 Total lines of code: {total_lines}")
        print("✅ Self-modification analysis complete")
        
        # Log the analysis
        error_handler.log_error(None, "Self modification", ErrorLevel.INFO, 
                               f"Code analysis completed: {len(python_files)} files, {total_lines} lines")
        
    except Exception as e:
        error_handler.log_error(e, "Self modification", ErrorLevel.ERROR)
        print(f"❌ Error in self-modification: {e}")

def process_self_modify_request(request: str) -> dict:
    """Process self-modification requests with comprehensive handling"""
    try:
        if not request or not request.strip():
            return {"error": "Empty request", "success": False}
        
        request = request.strip().lower()
        
        if "analyze" in request or "check" in request:
            # Run self-modification analysis
            python_files = []
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.py') and not file.startswith('test_'):
                        python_files.append(os.path.join(root, file))
            
            total_lines = 0
            file_info = []
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_info.append({"file": file_path, "lines": lines})
                except Exception as e:
                    file_info.append({"file": file_path, "error": str(e)})
            
            return {
                "success": True,
                "analysis": {
                    "total_files": len(python_files),
                    "total_lines": total_lines,
                    "files": file_info
                },
                "message": f"Analyzed {len(python_files)} files with {total_lines} total lines"
            }
        
        elif "modify" in request or "update" in request:
            return {
                "success": False,
                "message": "Automated code modification not implemented for safety",
                "suggestion": "Please review and modify code manually"
            }
        
        else:
            return {
                "success": False,
                "message": "Unknown self-modification request",
                "available_commands": ["analyze", "check"]
            }
            
    except Exception as e:
        error_handler.log_error(e, "Self modify request", ErrorLevel.ERROR)
        return {
            "success": False,
            "error": str(e),
            "message": "Error processing self-modification request"
        }

if __name__ == "__main__":
    self_modify_all()