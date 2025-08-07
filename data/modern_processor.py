#!/usr/bin/env python3
"""
Modern Data Processor
====================
Enhanced data processing with modern Python patterns and optimization.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
import csv
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logger = logging.getLogger(__name__)

class ModernDataProcessor:
    """Modern data processing with enhanced capabilities"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.processing_stats = {
            'files_processed': 0,
            'records_processed': 0,
            'start_time': None
        }
        
        logger.info(f"Data processor initialized with {max_workers} workers")
    
    def process_file(self, file_path: Path, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process single file with modern error handling"""
        options = options or {}
        
        try:
            logger.info(f"Processing file: {file_path.name}")
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Determine file type and process accordingly
            if file_path.suffix.lower() == '.json':
                return self._process_json_file(file_path, options)
            elif file_path.suffix.lower() == '.csv':
                return self._process_csv_file(file_path, options)
            elif file_path.suffix.lower() == '.txt':
                return self._process_text_file(file_path, options)
            else:
                return self._process_generic_file(file_path, options)
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'file': str(file_path)
            }
    
    def process_batch(self, file_paths: List[Path], options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Process multiple files with modern parallel processing"""
        options = options or {}
        results = []
        
        self.processing_stats['start_time'] = datetime.now()
        
        logger.info(f"Starting batch processing of {len(file_paths)} files")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for file_path in file_paths:
                future = executor.submit(self.process_file, file_path, options)
                futures.append(future)
            
            for future in futures:
                try:
                    result = future.result(timeout=30)  # 30 second timeout per file
                    results.append(result)
                    self.processing_stats['files_processed'] += 1
                except Exception as e:
                    logger.error(f"Batch processing error: {e}")
                    results.append({
                        'status': 'error',
                        'error': str(e)
                    })
        
        end_time = datetime.now()
        duration = (end_time - self.processing_stats['start_time']).total_seconds()
        
        logger.info(f"Batch processing completed in {duration:.2f} seconds")
        
        return results
    
    def _process_json_file(self, file_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON file with modern parsing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Apply processing options
            if options.get('validate', True):
                self._validate_json_structure(data)
            
            if options.get('normalize', False):
                data = self._normalize_data(data)
            
            return {
                'status': 'success',
                'type': 'json',
                'records': len(data) if isinstance(data, list) else 1,
                'data': data,
                'file': str(file_path)
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    def _process_csv_file(self, file_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process CSV file with modern parsing"""
        try:
            rows = []
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if options.get('clean', True):
                        row = self._clean_row_data(row)
                    rows.append(row)
            
            self.processing_stats['records_processed'] += len(rows)
            
            return {
                'status': 'success',
                'type': 'csv',
                'records': len(rows),
                'data': rows,
                'file': str(file_path)
            }
            
        except Exception as e:
            raise ValueError(f"CSV processing error: {e}")
    
    def _process_text_file(self, file_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process text file with modern encoding handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply text processing options
            if options.get('clean', True):
                content = self._clean_text_content(content)
            
            lines = content.split('\n')
            
            return {
                'status': 'success',
                'type': 'text',
                'records': len(lines),
                'content': content,
                'lines': len(lines),
                'file': str(file_path)
            }
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Text encoding error: {e}")
    
    def _process_generic_file(self, file_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic file with modern handling"""
        try:
            file_size = file_path.stat().st_size
            
            return {
                'status': 'success',
                'type': 'generic',
                'size_bytes': file_size,
                'file': str(file_path)
            }
            
        except Exception as e:
            raise ValueError(f"Generic file processing error: {e}")
    
    def _validate_json_structure(self, data: Any) -> bool:
        """Validate JSON data structure with modern checks"""
        if isinstance(data, dict):
            # Check for required fields, structure, etc.
            return True
        elif isinstance(data, list):
            # Validate list structure
            return True
        else:
            logger.warning("Unexpected JSON structure")
            return False
    
    def _normalize_data(self, data: Any) -> Any:
        """Normalize data with modern transformation"""
        if isinstance(data, dict):
            # Normalize dictionary keys and values
            normalized = {}
            for key, value in data.items():
                # Convert keys to lowercase, normalize values
                normalized_key = key.lower().replace(' ', '_')
                normalized[normalized_key] = self._normalize_data(value)
            return normalized
        elif isinstance(data, list):
            return [self._normalize_data(item) for item in data]
        else:
            return data
    
    def _clean_row_data(self, row: Dict[str, str]) -> Dict[str, str]:
        """Clean CSV row data with modern string handling"""
        cleaned = {}
        for key, value in row.items():
            # Strip whitespace, handle None values
            cleaned_key = key.strip() if key else ''
            cleaned_value = value.strip() if value else ''
            cleaned[cleaned_key] = cleaned_value
        return cleaned
    
    def _clean_text_content(self, content: str) -> str:
        """Clean text content with modern processing"""
        # Remove excessive whitespace, normalize line endings
        content = '\n'.join(line.strip() for line in content.split('\n'))
        return content.strip()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics with modern metrics"""
        stats = self.processing_stats.copy()
        
        if stats['start_time']:
            duration = (datetime.now() - stats['start_time']).total_seconds()
            stats['duration_seconds'] = duration
            
            if duration > 0:
                stats['files_per_second'] = stats['files_processed'] / duration
                stats['records_per_second'] = stats['records_processed'] / duration
        
        return stats
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.processing_stats = {
            'files_processed': 0,
            'records_processed': 0,
            'start_time': None
        }
        logger.info("Processing statistics reset")

# Initialize global data processor
data_processor = ModernDataProcessor()

def get_data_processor() -> ModernDataProcessor:
    """Get global data processor instance"""
    return data_processor