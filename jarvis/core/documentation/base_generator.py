#!/usr/bin/env python3
"""
Base Documentation Generator
Provides common functionality for all documentation generators.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseDocumentationGenerator(ABC):
    """Base class for all documentation generators"""
    
    def __init__(self, docs_dir: str = "docs", output_dir: str = "tests/output/docs"):
        self.docs_dir = docs_dir
        self.output_dir = output_dir
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """Generate documentation - to be implemented by subclasses"""
        pass
    
    def save_documentation(self, content: Dict[str, Any], filename: str):
        """Save documentation to both docs and output directories"""
        # Save JSON version
        json_path = os.path.join(self.output_dir, f"{filename}.json")
        with open(json_path, 'w') as f:
            json.dump(content, f, indent=2)
        
        # Save markdown version if content has markdown
        if 'markdown_content' in content:
            md_path = os.path.join(self.docs_dir, f"{filename}.md")
            with open(md_path, 'w') as f:
                f.write(content['markdown_content'])
    
    def get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_header(self, title: str, subtitle: str = "") -> str:
        """Create consistent documentation header"""
        header = f"# {title}\n\n"
        if subtitle:
            header += f"*{subtitle}*\n\n"
        header += f"Generated on: {self.get_timestamp()}\n\n"
        header += "---\n\n"
        return header