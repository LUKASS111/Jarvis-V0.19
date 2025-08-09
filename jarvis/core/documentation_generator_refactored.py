#!/usr/bin/env python3
"""
Refactored Documentation Generator for Jarvis-1.0.0
Modular architecture replacing the monolithic 1686-line implementation.
"""

import os
from typing import Dict, Any, List

from .documentation.base_generator import BaseDocumentationGenerator
from .documentation.api_generator import APIReferenceGenerator

class DocumentationGenerator:
    """
    Refactored documentation generator with modular architecture.
    Replaces the 1686-line monolithic implementation.
    """
    
    def __init__(self):
        self.docs_dir = "docs"
        self.output_dir = "tests/output/docs"
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize specialized generators
        self.api_generator = APIReferenceGenerator(self.docs_dir, self.output_dir)
    
    def generate_comprehensive_documentation(self):
        """Generate all documentation components using modular generators"""
        print("[DOCS] Generating comprehensive documentation...")
        
        documentation_results = {}
        
        # Generate API reference
        try:
            api_docs = self.api_generator.generate()
            documentation_results["api_reference"] = api_docs
            print("[DOCS] ✅ API reference generated")
        except Exception as e:
            print(f"[DOCS] ❌ API reference generation failed: {e}")
        
        # Generate development guide
        try:
            dev_guide = self.generate_development_guide()
            documentation_results["development_guide"] = dev_guide
            print("[DOCS] ✅ Development guide generated")
        except Exception as e:
            print(f"[DOCS] ❌ Development guide generation failed: {e}")
        
        # Generate architecture overview
        try:
            architecture = self.generate_architecture_overview()
            documentation_results["architecture"] = architecture
            print("[DOCS] ✅ Architecture documentation generated")
        except Exception as e:
            print(f"[DOCS] ❌ Architecture documentation generation failed: {e}")
        
        print("[DOCS] Documentation generation complete!")
        return documentation_results
    
    def generate_development_guide(self) -> Dict[str, Any]:
        """Generate streamlined development guide"""
        dev_guide = {
            "title": "Jarvis Development Guide",
            "sections": {
                "getting_started": {
                    "title": "Getting Started",
                    "content": """
## Quick Start

1. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Tests**:
   ```bash
   python run_tests.py
   ```

3. **Launch Application**:
   ```bash
   python main.py              # GUI dashboard
   python main.py --cli        # CLI interface
   python main.py --backend    # Backend service
   ```
                    """
                },
                "architecture": {
                    "title": "System Architecture", 
                    "content": """
## Core Components

- **Backend**: Core AI processing and data management
- **GUI**: Professional dashboard with modular tabs
- **CLI**: Command-line interface for automation
- **Vector Database**: Semantic search and AI memory
- **CRDT System**: Real-time collaborative features
- **Agent Framework**: Multi-agent workflow management
                    """
                },
                "development": {
                    "title": "Development Workflow",
                    "content": """
## Code Standards

- **Testing**: Maintain 90%+ test coverage
- **Linting**: Use Black, Flake8, MyPy
- **Branching**: Use `copilot/*` branch naming
- **Documentation**: Update docs with code changes

## Contributing

1. Create feature branch: `git checkout -b copilot/feature-name`
2. Make changes with tests
3. Run quality checks: `python -m black . && python -m flake8`
4. Submit PR with clear description
                    """
                }
            }
        }
        
        # Generate markdown
        markdown_content = self._create_development_guide_markdown(dev_guide)
        dev_guide["markdown_content"] = markdown_content
        
        # Save documentation
        self._save_documentation(dev_guide, "development_guide")
        
        return dev_guide
    
    def generate_architecture_overview(self) -> Dict[str, Any]:
        """Generate architecture documentation"""
        architecture = {
            "title": "Jarvis System Architecture",
            "components": {
                "frontend": {
                    "gui": "PyQt5-based professional dashboard",
                    "cli": "Command-line interface for automation"
                },
                "backend": {
                    "core": "AI processing and business logic",
                    "api": "FastAPI REST service",
                    "database": "SQLite with vector extensions"
                },
                "ai_systems": {
                    "llm": "Multi-model LLM integration",
                    "vector_db": "Semantic search and memory",
                    "agents": "Multi-agent workflow system"
                }
            }
        }
        
        # Generate markdown
        markdown_content = self._create_architecture_markdown(architecture)
        architecture["markdown_content"] = markdown_content
        
        # Save documentation
        self._save_documentation(architecture, "architecture")
        
        return architecture
    
    def _create_development_guide_markdown(self, guide: Dict[str, Any]) -> str:
        """Create markdown for development guide"""
        content = f"# {guide['title']}\n\n"
        content += "A comprehensive guide for Jarvis development.\n\n"
        content += f"Generated: {self._get_timestamp()}\n\n---\n\n"
        
        for section_key, section in guide["sections"].items():
            content += f"# {section['title']}\n\n"
            content += section["content"].strip() + "\n\n"
        
        return content
    
    def _create_architecture_markdown(self, arch: Dict[str, Any]) -> str:
        """Create markdown for architecture documentation"""
        content = f"# {arch['title']}\n\n"
        content += "System architecture overview and component relationships.\n\n"
        content += f"Generated: {self._get_timestamp()}\n\n---\n\n"
        
        for category, components in arch["components"].items():
            content += f"## {category.title()}\n\n"
            for component, description in components.items():
                content += f"- **{component}**: {description}\n"
            content += "\n"
        
        return content
    
    def _save_documentation(self, content: Dict[str, Any], filename: str):
        """Save documentation to files"""
        import json
        
        # Save JSON version
        json_path = os.path.join(self.output_dir, f"{filename}.json")
        with open(json_path, 'w') as f:
            json.dump(content, f, indent=2)
        
        # Save markdown version
        if 'markdown_content' in content:
            md_path = os.path.join(self.docs_dir, f"{filename}.md")
            with open(md_path, 'w') as f:
                f.write(content['markdown_content'])
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Backward compatibility functions
def generate_comprehensive_documentation():
    """Maintain backward compatibility with original interface"""
    generator = DocumentationGenerator()
    return generator.generate_comprehensive_documentation()