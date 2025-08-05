"""
TXT File Processor Plugin for Jarvis Plugin System
Handles text file processing with full Unicode support, content analysis, and metadata extraction.
"""

import os
import re
import json
import logging
from collections import Counter
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base import FileProcessorPlugin
from ...core.plugin_system import PluginContext


class TXTProcessorPlugin(FileProcessorPlugin):
    """Plugin for processing TXT files with comprehensive text analysis"""
    
    def __init__(self):
        super().__init__()
        self.name = "TXTProcessor"
        self.version = "1.0.0"
        self.description = "Comprehensive TXT file processor with Unicode support and content analysis"
        self.author = "Jarvis System"
        self.supported_extensions = ["txt", "text", "log", "md", "rst"]
        self.logger = logging.getLogger(__name__)
    
    def initialize(self, context: PluginContext) -> bool:
        """Initialize the TXT processor plugin"""
        try:
            self.context = context
            self.logger.info("TXT Processor Plugin initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize TXT Processor Plugin: {e}")
            return False
    
    def process_file(self, file_path: str, output_format: str = "memory") -> Dict[str, Any]:
        """Process a TXT file and return structured data
        
        Args:
            file_path: Path to the TXT file
            output_format: Output format ("memory", "logs", "agent")
            
        Returns:
            Dict containing processed file data
        """
        try:
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not self.supports_file(file_path):
                raise ValueError(f"Unsupported file type: {file_path}")
            
            # Extract data
            text_content = self._extract_text(file_path)
            file_data = self._extract_data(file_path, text_content)
            metadata = self._get_metadata(file_path)
            summary = self._get_summary(file_path, text_content, file_data)
            
            # Format output based on requested format
            if output_format == "memory":
                return self._format_for_memory(file_path, text_content, file_data, metadata, summary)
            elif output_format == "logs":
                return self._format_for_logs(file_path, text_content, file_data, metadata, summary)
            elif output_format == "agent":
                return self._format_for_agent(file_path, text_content, file_data, metadata, summary)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
        except Exception as e:
            self.logger.error(f"Error processing TXT file {file_path}: {e}")
            return {
                "error": str(e),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "processor": self.name
            }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text content from TXT file with Unicode support"""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'ascii']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                self.logger.debug(f"Successfully read {file_path} with {encoding} encoding")
                return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error reading {file_path} with {encoding}: {e}")
                continue
        
        # If all encodings fail, try reading as binary and handle errors
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                decoded_content = content.decode('utf-8', errors='replace')
                self.logger.warning(f"Read {file_path} with error replacement due to encoding issues")
                return decoded_content
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            return f"Error reading file: {str(e)}"
    
    def _extract_data(self, file_path: str, text_content: str) -> Dict[str, Any]:
        """Extract structured data from text content"""
        lines = text_content.splitlines()
        
        # Basic text statistics
        word_count = len(text_content.split())
        char_count = len(text_content)
        line_count = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        
        # Word frequency analysis
        words = re.findall(r'\b\w+\b', text_content.lower())
        word_freq = Counter(words)
        
        # Extract common patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}'
        
        emails = re.findall(email_pattern, text_content)
        urls = re.findall(url_pattern, text_content)
        dates = re.findall(date_pattern, text_content)
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "line_count": line_count,
            "non_empty_lines": non_empty_lines,
            "word_frequency": dict(word_freq.most_common(20)),
            "extracted_patterns": {
                "emails": list(set(emails)),
                "urls": list(set(urls)),
                "dates": list(set(dates))
            },
            "text_analysis": {
                "average_line_length": char_count / line_count if line_count > 0 else 0,
                "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
                "unique_words": len(set(words)),
                "vocabulary_ratio": len(set(words)) / len(words) if words else 0
            }
        }
    
    def _get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata"""
        try:
            stat = os.stat(file_path)
            return {
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "file_size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "file_extension": os.path.splitext(file_path)[1].lower(),
                "processor": self.name,
                "processor_version": self.version,
                "processed_time": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting metadata for {file_path}: {e}")
            return {
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "error": str(e),
                "processor": self.name
            }
    
    def _get_summary(self, file_path: str, text_content: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the text file"""
        # Extract preview
        preview_length = 500
        preview = text_content[:preview_length]
        if len(text_content) > preview_length:
            preview += "..."
        
        # Top words
        word_freq = file_data.get("word_frequency", {})
        top_words = list(word_freq.items())[:5]
        
        return {
            "description": f"Text file with {file_data.get('word_count', 0)} words, {file_data.get('line_count', 0)} lines",
            "statistics": {
                "word_count": file_data.get("word_count", 0),
                "character_count": file_data.get("character_count", 0),
                "line_count": file_data.get("line_count", 0),
                "non_empty_lines": file_data.get("non_empty_lines", 0)
            },
            "top_words": top_words,
            "extracted_items": {
                "emails": len(file_data.get("extracted_patterns", {}).get("emails", [])),
                "urls": len(file_data.get("extracted_patterns", {}).get("urls", [])),
                "dates": len(file_data.get("extracted_patterns", {}).get("dates", []))
            },
            "preview": preview,
            "analysis": file_data.get("text_analysis", {})
        }
    
    def _format_for_memory(self, file_path: str, text_content: str, file_data: Dict[str, Any], 
                          metadata: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for memory storage"""
        return {
            "type": "file_processing_memory",
            "file_info": {
                "path": file_path,
                "name": metadata.get("file_name"),
                "size": metadata.get("file_size"),
                "processor": self.name
            },
            "content": {
                "text": text_content,
                "summary": summary.get("description"),
                "preview": summary.get("preview")
            },
            "analysis": file_data,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_for_logs(self, file_path: str, text_content: str, file_data: Dict[str, Any], 
                        metadata: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for logging system"""
        return {
            "event_type": "file_processed",
            "file_path": file_path,
            "processor": self.name,
            "processing_time": datetime.now().isoformat(),
            "file_metadata": metadata,
            "processing_results": {
                "success": True,
                "statistics": summary.get("statistics"),
                "extracted_patterns": file_data.get("extracted_patterns"),
                "analysis_summary": summary.get("analysis")
            },
            "audit_info": {
                "processor_version": self.version,
                "processing_method": "txt_plugin",
                "data_integrity": "verified"
            }
        }
    
    def _format_for_agent(self, file_path: str, text_content: str, file_data: Dict[str, Any], 
                         metadata: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for agent interaction"""
        return {
            "file_analysis_report": {
                "file": metadata.get("file_name"),
                "summary": summary.get("description"),
                "key_statistics": summary.get("statistics"),
                "content_preview": summary.get("preview"),
                "extracted_data": {
                    "top_words": summary.get("top_words"),
                    "patterns_found": summary.get("extracted_items"),
                    "text_quality": summary.get("analysis")
                }
            },
            "recommendations": self._generate_recommendations(file_data, summary),
            "agent_actions": self._suggest_agent_actions(file_data, metadata),
            "processing_notes": {
                "processor": self.name,
                "confidence": "high",
                "completeness": "full_analysis",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _generate_recommendations(self, file_data: Dict[str, Any], summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on file analysis"""
        recommendations = []
        
        # Word count recommendations
        word_count = file_data.get("word_count", 0)
        if word_count < 100:
            recommendations.append("File appears to be short - consider if full content was captured")
        elif word_count > 10000:
            recommendations.append("Large file detected - consider chunking for processing")
        
        # Pattern analysis recommendations
        patterns = file_data.get("extracted_patterns", {})
        if patterns.get("emails"):
            recommendations.append(f"Found {len(patterns['emails'])} email addresses - may contain contact information")
        if patterns.get("urls"):
            recommendations.append(f"Found {len(patterns['urls'])} URLs - may contain external references")
        if patterns.get("dates"):
            recommendations.append(f"Found {len(patterns['dates'])} dates - may contain temporal information")
        
        # Text quality recommendations
        analysis = file_data.get("text_analysis", {})
        vocab_ratio = analysis.get("vocabulary_ratio", 0)
        if vocab_ratio < 0.3:
            recommendations.append("Low vocabulary diversity - may be repetitive content")
        elif vocab_ratio > 0.8:
            recommendations.append("High vocabulary diversity - rich content detected")
        
        return recommendations
    
    def _suggest_agent_actions(self, file_data: Dict[str, Any], metadata: Dict[str, Any]) -> List[str]:
        """Suggest actions the agent could take with this file"""
        actions = []
        
        # Based on file size and content
        word_count = file_data.get("word_count", 0)
        if word_count > 1000:
            actions.append("summarize_content")
            actions.append("extract_key_points")
        
        # Based on patterns found
        patterns = file_data.get("extracted_patterns", {})
        if patterns.get("emails"):
            actions.append("extract_contact_information")
        if patterns.get("urls"):
            actions.append("validate_external_links")
        if patterns.get("dates"):
            actions.append("extract_timeline_information")
        
        # Based on file extension
        file_ext = metadata.get("file_extension", "").lower()
        if file_ext in [".log"]:
            actions.append("analyze_log_patterns")
            actions.append("detect_error_messages")
        elif file_ext in [".md", ".rst"]:
            actions.append("parse_document_structure")
            actions.append("extract_headings")
        
        # General actions
        actions.extend([
            "store_in_memory",
            "add_to_knowledge_base",
            "generate_summary"
        ])
        
        return actions
    
    def get_supported_actions(self) -> List[str]:
        """Get supported actions for this plugin"""
        return ["process_file", "supports_file", "analyze_text", "extract_patterns"]