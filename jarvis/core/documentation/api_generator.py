#!/usr/bin/env python3
"""
API Reference Generator
Generates comprehensive API documentation for Jarvis modules.
"""

import inspect
import importlib
import pkgutil
from typing import Dict, Any, List, Optional

from .base_generator import BaseDocumentationGenerator

class APIReferenceGenerator(BaseDocumentationGenerator):
    """Generate API reference documentation"""
    
    def generate(self) -> Dict[str, Any]:
        """Generate API reference documentation"""
        print("[DOCS] Generating API reference...")
        
        api_doc = {
            "title": "Jarvis-1.0.0 API Reference",
            "generated": self.get_timestamp(),
            "version": "1.0.0",
            "modules": {},
            "classes": {},
            "functions": {}
        }
        
        # Document core modules
        core_modules = [
            "jarvis.core",
            "jarvis.backend", 
            "jarvis.interfaces",
            "jarvis.utils"
        ]
        
        for module_name in core_modules:
            try:
                module_doc = self._document_module(module_name)
                if module_doc:
                    api_doc["modules"][module_name] = module_doc
            except Exception as e:
                print(f"[DOCS] Error documenting module {module_name}: {e}")
        
        # Generate markdown
        api_doc["markdown_content"] = self._generate_api_markdown(api_doc)
        
        # Save documentation
        self.save_documentation(api_doc, "api_reference")
        
        return api_doc
    
    def _document_module(self, module_name: str) -> Dict[str, Any]:
        """Document a specific module"""
        try:
            module = importlib.import_module(module_name)
            
            module_doc = {
                "name": module_name,
                "docstring": inspect.getdoc(module) or "No documentation available",
                "classes": {},
                "functions": {},
                "constants": {}
            }
            
            # Document classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_name:  # Only classes defined in this module
                    module_doc["classes"][name] = self._document_class(obj)
            
            # Document functions  
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if obj.__module__ == module_name:  # Only functions defined in this module
                    module_doc["functions"][name] = self._document_function(obj)
            
            # Document module-level constants
            for name, obj in inspect.getmembers(module):
                if (not name.startswith('_') and 
                    not inspect.isclass(obj) and 
                    not inspect.isfunction(obj) and
                    not inspect.ismodule(obj)):
                    module_doc["constants"][name] = {
                        "value": str(obj),
                        "type": type(obj).__name__
                    }
            
            return module_doc
            
        except ImportError as e:
            print(f"[DOCS] Could not import module {module_name}: {e}")
            return None
        except Exception as e:
            print(f"[DOCS] Error documenting module {module_name}: {e}")
            return None
    
    def _document_class(self, cls) -> Dict[str, Any]:
        """Document a class"""
        class_doc = {
            "name": cls.__name__,
            "docstring": inspect.getdoc(cls) or "No documentation available",
            "methods": {},
            "properties": {}
        }
        
        # Document methods
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            if not name.startswith('_'):
                class_doc["methods"][name] = self._document_function(method)
        
        # Document functions defined in class (unbound methods)
        for name, func in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                class_doc["methods"][name] = self._document_function(func)
        
        return class_doc
    
    def _document_function(self, func) -> Dict[str, Any]:
        """Document a function or method"""
        try:
            signature = inspect.signature(func)
            return {
                "name": func.__name__,
                "docstring": inspect.getdoc(func) or "No documentation available",
                "signature": str(signature),
                "parameters": [param.name for param in signature.parameters.values()],
                "return_annotation": str(signature.return_annotation) if signature.return_annotation != inspect.Signature.empty else None
            }
        except Exception as e:
            return {
                "name": func.__name__,
                "docstring": inspect.getdoc(func) or "No documentation available",
                "signature": "Unable to parse signature",
                "error": str(e)
            }
    
    def _generate_api_markdown(self, api_doc: Dict[str, Any]) -> str:
        """Generate markdown documentation from API doc"""
        md_content = self.create_header(
            "Jarvis API Reference",
            "Comprehensive API documentation for all modules"
        )
        
        md_content += "## Table of Contents\n\n"
        
        # Generate table of contents
        for module_name in api_doc["modules"]:
            md_content += f"- [{module_name}](#{module_name.replace('.', '-')})\n"
        
        md_content += "\n"
        
        # Generate module documentation
        for module_name, module_info in api_doc["modules"].items():
            md_content += f"## {module_name}\n\n"
            md_content += f"{module_info['docstring']}\n\n"
            
            # Document classes
            if module_info["classes"]:
                md_content += "### Classes\n\n"
                for class_name, class_info in module_info["classes"].items():
                    md_content += f"#### {class_name}\n\n"
                    md_content += f"{class_info['docstring']}\n\n"
                    
                    # Document methods
                    if class_info["methods"]:
                        md_content += "**Methods:**\n\n"
                        for method_name, method_info in class_info["methods"].items():
                            md_content += f"- `{method_name}{method_info.get('signature', '')}`: {method_info['docstring']}\n"
                        md_content += "\n"
            
            # Document functions
            if module_info["functions"]:
                md_content += "### Functions\n\n"
                for func_name, func_info in module_info["functions"].items():
                    md_content += f"#### {func_name}\n\n"
                    md_content += f"```python\n{func_name}{func_info.get('signature', '')}\n```\n\n"
                    md_content += f"{func_info['docstring']}\n\n"
        
        return md_content