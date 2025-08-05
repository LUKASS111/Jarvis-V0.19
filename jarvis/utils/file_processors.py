"""
Universal File Processing System for Jarvis V0.19
Handles PDF, Excel (XLS/XLSX), and TXT file processing for memory, logs, and agent interaction.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class FileProcessor(ABC):
    """
    Abstract base class for all file processors.
    Provides universal interface for file processing operations.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the file processor.
        
        Args:
            file_path (str): Path to the file to be processed
        """
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_extension = os.path.splitext(file_path)[1].lower()
        self.processed_data = {}
        self.metadata = {}
        
        # Validate file existence
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
    
    @abstractmethod
    def extract_text(self) -> str:
        """
        Extract raw text content from the file.
        
        Returns:
            str: Extracted text content
        """
        pass
    
    @abstractmethod
    def extract_data(self) -> Dict[str, Any]:
        """
        Extract structured data from the file.
        
        Returns:
            Dict[str, Any]: Structured data from the file
        """
        pass
    
    @abstractmethod
    def get_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the file content.
        
        Returns:
            Dict[str, Any]: Summary information
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get file metadata including size, creation time, etc.
        
        Returns:
            Dict[str, Any]: File metadata
        """
        if not self.metadata:
            stat = os.stat(self.file_path)
            self.metadata = {
                "file_name": self.file_name,
                "file_path": self.file_path,
                "file_extension": self.file_extension,
                "file_size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat()
            }
        return self.metadata
    
    def process_for_memory(self) -> Dict[str, Any]:
        """
        Process file content for memory storage.
        
        Returns:
            Dict[str, Any]: Processed data suitable for memory storage
        """
        return {
            "content": self.extract_text(),
            "structured_data": self.extract_data(),
            "summary": self.get_summary(),
            "metadata": self.get_metadata(),
            "processor_type": self.__class__.__name__,
            "processing_timestamp": datetime.now().isoformat()
        }
    
    def process_for_logs(self) -> Dict[str, Any]:
        """
        Process file content for logging.
        
        Returns:
            Dict[str, Any]: Processed data suitable for logging
        """
        summary = self.get_summary()
        return {
            "file_info": {
                "name": self.file_name,
                "path": self.file_path,
                "size": self.get_metadata()["file_size"],
                "type": self.file_extension
            },
            "processing_summary": summary,
            "processor": self.__class__.__name__,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_for_agent(self) -> str:
        """
        Process file content for agent interaction.
        
        Returns:
            str: Human-readable summary for agent processing
        """
        summary = self.get_summary()
        metadata = self.get_metadata()
        
        return f"""File Analysis Report:
File: {metadata['file_name']}
Type: {self.file_extension.upper()}
Size: {metadata['file_size']} bytes
Processed by: {self.__class__.__name__}

Summary:
{summary.get('description', 'No description available')}

Key Information:
{json.dumps(summary, indent=2)}
"""


class TXTProcessor(FileProcessor):
    """
    Processor for TXT files.
    Handles plain text file analysis and processing.
    """
    
    def extract_text(self) -> str:
        """Extract text content from TXT file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(self.file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading TXT file {self.file_path}: {e}")
                return f"Error reading file: {str(e)}"
    
    def extract_data(self) -> Dict[str, Any]:
        """Extract structured data from TXT file."""
        text = self.extract_text()
        lines = text.split('\n')
        
        return {
            "total_lines": len(lines),
            "total_characters": len(text),
            "total_words": len(text.split()),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "lines": lines[:100],  # First 100 lines
            "encoding": "utf-8"
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate summary of TXT file."""
        text = self.extract_text()
        data = self.extract_data()
        
        # Basic text analysis
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        line_count = data["total_lines"]
        
        # Find most common words (simple analysis)
        word_freq = {}
        for word in words:
            clean_word = word.lower().strip('.,!?;:"()[]{}')
            if len(clean_word) > 3:  # Only count words longer than 3 chars
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "description": f"Text file with {word_count} words, {line_count} lines, {char_count} characters",
            "statistics": {
                "word_count": word_count,
                "character_count": char_count,
                "line_count": line_count,
                "non_empty_lines": data["non_empty_lines"]
            },
            "common_words": common_words,
            "preview": text[:500] + "..." if len(text) > 500 else text
        }


class PDFProcessor(FileProcessor):
    """
    Processor for PDF files.
    Handles PDF text extraction and analysis.
    Note: This implementation provides a framework. Full PDF processing 
    would require additional libraries like PyPDF2 or pdfplumber.
    """
    
    def extract_text(self) -> str:
        """
        Extract text content from PDF file.
        This is a placeholder implementation - would need PDF library for full functionality.
        """
        try:
            # Placeholder implementation
            # In production, would use PyPDF2, pdfplumber, or similar
            return self._extract_pdf_text_placeholder()
        except Exception as e:
            logger.error(f"Error reading PDF file {self.file_path}: {e}")
            return f"Error reading PDF file: {str(e)}"
    
    def _extract_pdf_text_placeholder(self) -> str:
        """
        Placeholder for PDF text extraction.
        TODO: Implement with proper PDF library when available.
        """
        metadata = self.get_metadata()
        return f"""[PDF Processing Placeholder]
File: {metadata['file_name']}
Size: {metadata['file_size']} bytes

Note: Full PDF text extraction requires PDF processing library.
This is a placeholder implementation that can be extended with:
- PyPDF2 for basic text extraction
- pdfplumber for advanced table/layout analysis
- pdfminer for detailed text positioning

Current implementation provides file metadata and structure analysis."""
    
    def extract_data(self) -> Dict[str, Any]:
        """Extract structured data from PDF file."""
        # Placeholder implementation
        return {
            "page_count": "Unknown (requires PDF library)",
            "text_extractable": "Unknown (requires PDF library)",
            "has_images": "Unknown (requires PDF library)",
            "has_tables": "Unknown (requires PDF library)",
            "security": "Unknown (requires PDF library)",
            "note": "Full PDF analysis requires PyPDF2 or pdfplumber library"
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate summary of PDF file."""
        metadata = self.get_metadata()
        
        return {
            "description": f"PDF file: {metadata['file_name']} ({metadata['file_size']} bytes)",
            "file_info": metadata,
            "capabilities": [
                "File metadata extraction",
                "Basic file validation",
                "Framework for PDF processing"
            ],
            "todo": [
                "Install PyPDF2 or pdfplumber for text extraction",
                "Implement page-by-page processing",
                "Add table and image detection",
                "Implement OCR for scanned PDFs"
            ],
            "note": "This is a framework implementation ready for PDF library integration"
        }


class ExcelProcessor(FileProcessor):
    """
    Processor for Excel files (XLS/XLSX).
    Handles Excel spreadsheet analysis and data extraction.
    Note: This implementation provides a framework. Full Excel processing 
    would require additional libraries like openpyxl or pandas.
    """
    
    def extract_text(self) -> str:
        """
        Extract text content from Excel file.
        This is a placeholder implementation - would need Excel library for full functionality.
        """
        try:
            return self._extract_excel_text_placeholder()
        except Exception as e:
            logger.error(f"Error reading Excel file {self.file_path}: {e}")
            return f"Error reading Excel file: {str(e)}"
    
    def _extract_excel_text_placeholder(self) -> str:
        """
        Placeholder for Excel text extraction.
        TODO: Implement with proper Excel library when available.
        """
        metadata = self.get_metadata()
        return f"""[Excel Processing Placeholder]
File: {metadata['file_name']}
Size: {metadata['file_size']} bytes
Type: {self.file_extension.upper()}

Note: Full Excel processing requires spreadsheet library.
This is a placeholder implementation that can be extended with:
- openpyxl for XLSX files (modern Excel format)
- xlrd for XLS files (legacy Excel format)
- pandas for advanced data analysis and manipulation

Current implementation provides file metadata and structure analysis."""
    
    def extract_data(self) -> Dict[str, Any]:
        """Extract structured data from Excel file."""
        # Placeholder implementation
        return {
            "worksheet_count": "Unknown (requires Excel library)",
            "total_rows": "Unknown (requires Excel library)",
            "total_columns": "Unknown (requires Excel library)",
            "has_formulas": "Unknown (requires Excel library)",
            "has_charts": "Unknown (requires Excel library)",
            "file_format": self.file_extension.upper(),
            "note": "Full Excel analysis requires openpyxl or pandas library"
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate summary of Excel file."""
        metadata = self.get_metadata()
        
        return {
            "description": f"Excel file: {metadata['file_name']} ({metadata['file_size']} bytes)",
            "file_info": metadata,
            "format": self.file_extension.upper(),
            "capabilities": [
                "File metadata extraction",
                "Basic file validation",
                "Framework for Excel processing"
            ],
            "todo": [
                "Install openpyxl for XLSX processing",
                "Install xlrd for XLS processing", 
                "Implement worksheet enumeration",
                "Add data type detection",
                "Implement formula analysis",
                "Add chart and pivot table detection"
            ],
            "note": "This is a framework implementation ready for Excel library integration"
        }


class FileProcessorFactory:
    """
    Factory class for creating appropriate file processors based on file type.
    """
    
    PROCESSOR_MAP = {
        '.txt': TXTProcessor,
        '.pdf': PDFProcessor,
        '.xls': ExcelProcessor,
        '.xlsx': ExcelProcessor
    }
    
    @classmethod
    def create_processor(cls, file_path: str) -> FileProcessor:
        """
        Create appropriate processor for the given file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            FileProcessor: Appropriate processor instance
            
        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in cls.PROCESSOR_MAP:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        processor_class = cls.PROCESSOR_MAP[file_extension]
        return processor_class(file_path)
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List[str]: List of supported file extensions
        """
        return list(cls.PROCESSOR_MAP.keys())
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        Check if file format is supported.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if supported, False otherwise
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in cls.PROCESSOR_MAP


# Convenience functions for easy integration
def process_file(file_path: str, output_format: str = 'memory') -> Union[Dict[str, Any], str]:
    """
    Process a file using the appropriate processor.
    
    Args:
        file_path (str): Path to the file to process
        output_format (str): Output format ('memory', 'logs', 'agent')
        
    Returns:
        Union[Dict[str, Any], str]: Processed data in requested format
        
    Raises:
        ValueError: If output format or file type is not supported
        FileNotFoundError: If file does not exist
    """
    processor = FileProcessorFactory.create_processor(file_path)
    
    if output_format == 'memory':
        return processor.process_for_memory()
    elif output_format == 'logs':
        return processor.process_for_logs()
    elif output_format == 'agent':
        return processor.process_for_agent()
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic information about a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Dict[str, Any]: File information and metadata
    """
    processor = FileProcessorFactory.create_processor(file_path)
    return processor.get_metadata()


def is_file_supported(file_path: str) -> bool:
    """
    Check if a file format is supported by the processing system.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if supported, False otherwise
    """
    return FileProcessorFactory.is_supported(file_path)


def get_supported_formats() -> List[str]:
    """
    Get list of all supported file formats.
    
    Returns:
        List[str]: List of supported file extensions
    """
    return FileProcessorFactory.get_supported_formats()