"""
Comprehensive test suite for File Processors System
Tests all file format processors (PDF, Excel, TXT) with various scenarios.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open

import sys
sys.path.append('.')

from jarvis.utils.file_processors import (
    FileProcessor, TXTProcessor, PDFProcessor, ExcelProcessor,
    FileProcessorFactory, process_file, get_file_info, 
    is_file_supported, get_supported_formats
)


class TestFileProcessorBase(unittest.TestCase):
    """Test base FileProcessor functionality"""
    
    def setUp(self):
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_txt_file = os.path.join(self.temp_dir, "test.txt")
        self.test_pdf_file = os.path.join(self.temp_dir, "test.pdf")
        self.test_xlsx_file = os.path.join(self.temp_dir, "test.xlsx")
        self.test_xls_file = os.path.join(self.temp_dir, "test.xls")
        
        # Create test content
        with open(self.test_txt_file, 'w', encoding='utf-8') as f:
            f.write("This is a test file.\nIt has multiple lines.\nFor testing purposes.")
        
        # Create dummy binary files for PDF and Excel
        with open(self.test_pdf_file, 'wb') as f:
            f.write(b'%PDF-1.4\n%dummy PDF content for testing')
        
        with open(self.test_xlsx_file, 'wb') as f:
            f.write(b'PK\x03\x04dummy XLSX content for testing')
        
        with open(self.test_xls_file, 'wb') as f:
            f.write(b'\xd0\xcf\x11\xe0dummy XLS content for testing')
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_file_not_found(self):
        """Test behavior when file doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            TXTProcessor("/nonexistent/file.txt")
    
    def test_get_metadata(self):
        """Test metadata extraction"""
        processor = TXTProcessor(self.test_txt_file)
        metadata = processor.get_metadata()
        
        self.assertIn('file_name', metadata)
        self.assertIn('file_path', metadata)
        self.assertIn('file_extension', metadata)
        self.assertIn('file_size', metadata)
        self.assertIn('created_time', metadata)
        self.assertIn('modified_time', metadata)
        self.assertIn('accessed_time', metadata)
        
        self.assertEqual(metadata['file_name'], 'test.txt')
        self.assertEqual(metadata['file_extension'], '.txt')
        self.assertGreater(metadata['file_size'], 0)


class TestTXTProcessor(unittest.TestCase):
    """Test TXT file processing"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        
        self.test_content = """This is a comprehensive test file.
It contains multiple lines of text for testing.
Some words appear multiple times: test, testing, file, content.
This allows us to test word frequency analysis.
The file also tests various text processing features."""
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_extract_text(self):
        """Test text extraction from TXT file"""
        processor = TXTProcessor(self.test_file)
        extracted_text = processor.extract_text()
        
        self.assertEqual(extracted_text, self.test_content)
    
    def test_extract_data(self):
        """Test structured data extraction from TXT file"""
        processor = TXTProcessor(self.test_file)
        data = processor.extract_data()
        
        self.assertIn('total_lines', data)
        self.assertIn('total_characters', data)
        self.assertIn('total_words', data)
        self.assertIn('non_empty_lines', data)
        self.assertIn('lines', data)
        self.assertIn('encoding', data)
        
        self.assertEqual(data['total_lines'], 5)
        self.assertEqual(data['total_characters'], len(self.test_content))
        self.assertGreater(data['total_words'], 0)
        self.assertEqual(data['encoding'], 'utf-8')
    
    def test_get_summary(self):
        """Test summary generation for TXT file"""
        processor = TXTProcessor(self.test_file)
        summary = processor.get_summary()
        
        self.assertIn('description', summary)
        self.assertIn('statistics', summary)
        self.assertIn('common_words', summary)
        self.assertIn('preview', summary)
        
        stats = summary['statistics']
        self.assertIn('word_count', stats)
        self.assertIn('character_count', stats)
        self.assertIn('line_count', stats)
        self.assertIn('non_empty_lines', stats)
        
        # Check common words analysis
        common_words = summary['common_words']
        self.assertIsInstance(common_words, list)
        # Should find "test" as a common word
        word_list = [word for word, count in common_words]
        self.assertIn('test', word_list)
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        unicode_file = os.path.join(self.temp_dir, "unicode_test.txt")
        unicode_content = "Unicode test: café, naïve, résumé, 中文, русский"
        
        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write(unicode_content)
        
        processor = TXTProcessor(unicode_file)
        extracted_text = processor.extract_text()
        
        self.assertEqual(extracted_text, unicode_content)
    
    def test_process_outputs(self):
        """Test different processing output formats"""
        processor = TXTProcessor(self.test_file)
        
        # Test memory output
        memory_output = processor.process_for_memory()
        self.assertIn('content', memory_output)
        self.assertIn('structured_data', memory_output)
        self.assertIn('summary', memory_output)
        self.assertIn('metadata', memory_output)
        self.assertIn('processor_type', memory_output)
        self.assertIn('processing_timestamp', memory_output)
        
        # Test logs output
        logs_output = processor.process_for_logs()
        self.assertIn('file_info', logs_output)
        self.assertIn('processing_summary', logs_output)
        self.assertIn('processor', logs_output)
        self.assertIn('timestamp', logs_output)
        
        # Test agent output
        agent_output = processor.process_for_agent()
        self.assertIsInstance(agent_output, str)
        self.assertIn('File Analysis Report', agent_output)
        self.assertIn('test.txt', agent_output)


class TestPDFProcessor(unittest.TestCase):
    """Test PDF file processing (placeholder implementation)"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.pdf")
        
        # Create dummy PDF file
        with open(self.test_file, 'wb') as f:
            f.write(b'%PDF-1.4\n%dummy PDF content for testing')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_extract_text_placeholder(self):
        """Test PDF text extraction placeholder"""
        processor = PDFProcessor(self.test_file)
        extracted_text = processor.extract_text()
        
        self.assertIsInstance(extracted_text, str)
        self.assertIn('[PDF Processing Placeholder]', extracted_text)
        self.assertIn('test.pdf', extracted_text)
    
    def test_extract_data_placeholder(self):
        """Test PDF data extraction placeholder"""
        processor = PDFProcessor(self.test_file)
        data = processor.extract_data()
        
        self.assertIn('page_count', data)
        self.assertIn('text_extractable', data)
        self.assertIn('has_images', data)
        self.assertIn('has_tables', data)
        self.assertIn('security', data)
        self.assertIn('note', data)
    
    def test_get_summary_placeholder(self):
        """Test PDF summary generation placeholder"""
        processor = PDFProcessor(self.test_file)
        summary = processor.get_summary()
        
        self.assertIn('description', summary)
        self.assertIn('file_info', summary)
        self.assertIn('capabilities', summary)
        self.assertIn('todo', summary)
        self.assertIn('note', summary)


class TestExcelProcessor(unittest.TestCase):
    """Test Excel file processing (placeholder implementation)"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_xlsx_file = os.path.join(self.temp_dir, "test.xlsx")
        self.test_xls_file = os.path.join(self.temp_dir, "test.xls")
        
        # Create dummy Excel files
        with open(self.test_xlsx_file, 'wb') as f:
            f.write(b'PK\x03\x04dummy XLSX content for testing')
        
        with open(self.test_xls_file, 'wb') as f:
            f.write(b'\xd0\xcf\x11\xe0dummy XLS content for testing')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_excel_formats(self):
        """Test both Excel formats (.xls and .xlsx)"""
        # Test XLSX
        processor_xlsx = ExcelProcessor(self.test_xlsx_file)
        self.assertEqual(processor_xlsx.file_extension, '.xlsx')
        
        # Test XLS
        processor_xls = ExcelProcessor(self.test_xls_file)
        self.assertEqual(processor_xls.file_extension, '.xls')
    
    def test_extract_text_placeholder(self):
        """Test Excel text extraction placeholder"""
        processor = ExcelProcessor(self.test_xlsx_file)
        extracted_text = processor.extract_text()
        
        self.assertIsInstance(extracted_text, str)
        self.assertIn('[Excel Processing Placeholder]', extracted_text)
        self.assertIn('test.xlsx', extracted_text)
    
    def test_extract_data_placeholder(self):
        """Test Excel data extraction placeholder"""
        processor = ExcelProcessor(self.test_xlsx_file)
        data = processor.extract_data()
        
        self.assertIn('worksheet_count', data)
        self.assertIn('total_rows', data)
        self.assertIn('total_columns', data)
        self.assertIn('has_formulas', data)
        self.assertIn('has_charts', data)
        self.assertIn('file_format', data)
        self.assertIn('note', data)
    
    def test_get_summary_placeholder(self):
        """Test Excel summary generation placeholder"""
        processor = ExcelProcessor(self.test_xlsx_file)
        summary = processor.get_summary()
        
        self.assertIn('description', summary)
        self.assertIn('file_info', summary)
        self.assertIn('format', summary)
        self.assertIn('capabilities', summary)
        self.assertIn('todo', summary)
        self.assertIn('note', summary)


class TestFileProcessorFactory(unittest.TestCase):
    """Test FileProcessorFactory functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = {}
        
        # Create test files for each supported format
        formats = ['.txt', '.pdf', '.xlsx', '.xls']
        for fmt in formats:
            file_path = os.path.join(self.temp_dir, f"test{fmt}")
            self.test_files[fmt] = file_path
            
            if fmt == '.txt':
                with open(file_path, 'w') as f:
                    f.write("Test content")
            else:
                with open(file_path, 'wb') as f:
                    f.write(b'dummy content for testing')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_processor_txt(self):
        """Test creating TXT processor"""
        processor = FileProcessorFactory.create_processor(self.test_files['.txt'])
        self.assertIsInstance(processor, TXTProcessor)
    
    def test_create_processor_pdf(self):
        """Test creating PDF processor"""
        processor = FileProcessorFactory.create_processor(self.test_files['.pdf'])
        self.assertIsInstance(processor, PDFProcessor)
    
    def test_create_processor_xlsx(self):
        """Test creating XLSX processor"""
        processor = FileProcessorFactory.create_processor(self.test_files['.xlsx'])
        self.assertIsInstance(processor, ExcelProcessor)
    
    def test_create_processor_xls(self):
        """Test creating XLS processor"""
        processor = FileProcessorFactory.create_processor(self.test_files['.xls'])
        self.assertIsInstance(processor, ExcelProcessor)
    
    def test_unsupported_format(self):
        """Test handling of unsupported file format"""
        unsupported_file = os.path.join(self.temp_dir, "test.unsupported")
        with open(unsupported_file, 'w') as f:
            f.write("test")
        
        with self.assertRaises(ValueError):
            FileProcessorFactory.create_processor(unsupported_file)
    
    def test_file_not_found(self):
        """Test handling of non-existent file"""
        with self.assertRaises(FileNotFoundError):
            FileProcessorFactory.create_processor("/nonexistent/file.txt")
    
    def test_get_supported_formats(self):
        """Test getting supported formats"""
        formats = FileProcessorFactory.get_supported_formats()
        expected_formats = ['.txt', '.pdf', '.xls', '.xlsx']
        
        for fmt in expected_formats:
            self.assertIn(fmt, formats)
    
    def test_is_supported(self):
        """Test checking if format is supported"""
        self.assertTrue(FileProcessorFactory.is_supported(self.test_files['.txt']))
        self.assertTrue(FileProcessorFactory.is_supported(self.test_files['.pdf']))
        self.assertTrue(FileProcessorFactory.is_supported(self.test_files['.xlsx']))
        self.assertTrue(FileProcessorFactory.is_supported(self.test_files['.xls']))
        
        unsupported_file = os.path.join(self.temp_dir, "test.unsupported")
        with open(unsupported_file, 'w') as f:
            f.write("test")
        self.assertFalse(FileProcessorFactory.is_supported(unsupported_file))


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions for easy integration"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("Test content for convenience functions.")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_process_file_memory(self):
        """Test process_file with memory output"""
        result = process_file(self.test_file, 'memory')
        
        self.assertIsInstance(result, dict)
        self.assertIn('content', result)
        self.assertIn('structured_data', result)
        self.assertIn('summary', result)
        self.assertIn('metadata', result)
    
    def test_process_file_logs(self):
        """Test process_file with logs output"""
        result = process_file(self.test_file, 'logs')
        
        self.assertIsInstance(result, dict)
        self.assertIn('file_info', result)
        self.assertIn('processing_summary', result)
        self.assertIn('processor', result)
        self.assertIn('timestamp', result)
    
    def test_process_file_agent(self):
        """Test process_file with agent output"""
        result = process_file(self.test_file, 'agent')
        
        self.assertIsInstance(result, str)
        self.assertIn('File Analysis Report', result)
        self.assertIn('test.txt', result)
    
    def test_process_file_invalid_format(self):
        """Test process_file with invalid output format"""
        with self.assertRaises(ValueError):
            process_file(self.test_file, 'invalid_format')
    
    def test_get_file_info(self):
        """Test get_file_info function"""
        info = get_file_info(self.test_file)
        
        self.assertIsInstance(info, dict)
        self.assertIn('file_name', info)
        self.assertIn('file_path', info)
        self.assertIn('file_extension', info)
        self.assertIn('file_size', info)
    
    def test_is_file_supported(self):
        """Test is_file_supported function"""
        self.assertTrue(is_file_supported(self.test_file))
        
        unsupported_file = os.path.join(self.temp_dir, "test.unsupported")
        with open(unsupported_file, 'w') as f:
            f.write("test")
        self.assertFalse(is_file_supported(unsupported_file))
    
    def test_get_supported_formats(self):
        """Test get_supported_formats function"""
        formats = get_supported_formats()
        
        self.assertIsInstance(formats, list)
        self.assertIn('.txt', formats)
        self.assertIn('.pdf', formats)
        self.assertIn('.xlsx', formats)
        self.assertIn('.xls', formats)


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted or unreadable files"""
        # Create a file that can't be read as text
        corrupted_file = os.path.join(self.temp_dir, "corrupted.txt")
        with open(corrupted_file, 'wb') as f:
            f.write(b'\xff\xfe\x00\x00invalid_unicode_content')
        
        processor = TXTProcessor(corrupted_file)
        text = processor.extract_text()
        
        # Should handle the error gracefully
        self.assertIsInstance(text, str)
        # Should fall back to alternative encoding or error message
    
    def test_empty_file_handling(self):
        """Test handling of empty files"""
        empty_file = os.path.join(self.temp_dir, "empty.txt")
        with open(empty_file, 'w') as f:
            pass  # Create empty file
        
        processor = TXTProcessor(empty_file)
        text = processor.extract_text()
        data = processor.extract_data()
        summary = processor.get_summary()
        
        self.assertEqual(text, "")
        self.assertEqual(data['total_lines'], 1)  # Empty file has 1 line
        self.assertEqual(data['total_characters'], 0)
        self.assertEqual(data['total_words'], 0)
    
    def test_permission_denied_handling(self):
        """Test handling when file exists but can't be accessed"""
        # This test would require platform-specific permission manipulation
        # Skipping for now, but important for production deployment
        pass


class TestIntegrationWithExistingSystem(unittest.TestCase):
    """Test integration with existing Jarvis system components"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "integration_test.txt")
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("Integration test content for memory and logging systems.")
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_memory_integration_format(self):
        """Test that memory output format is compatible with existing memory system"""
        result = process_file(self.test_file, 'memory')
        
        # Check that the output structure is suitable for memory storage
        self.assertIn('content', result)  # Raw content for search
        self.assertIn('structured_data', result)  # Structured for indexing
        self.assertIn('summary', result)  # Quick reference
        self.assertIn('metadata', result)  # File information
        self.assertIn('processing_timestamp', result)  # When processed
        
        # Verify data types are JSON-serializable
        import json
        try:
            json.dumps(result)
        except (TypeError, ValueError):
            self.fail("Memory output is not JSON-serializable")
    
    def test_logs_integration_format(self):
        """Test that logs output format is compatible with existing logging system"""
        result = process_file(self.test_file, 'logs')
        
        # Check that the output structure follows logging conventions
        self.assertIn('file_info', result)
        self.assertIn('processing_summary', result)
        self.assertIn('processor', result)
        self.assertIn('timestamp', result)
        
        # Verify data types are JSON-serializable for log storage
        import json
        try:
            json.dumps(result)
        except (TypeError, ValueError):
            self.fail("Logs output is not JSON-serializable")
    
    def test_agent_integration_format(self):
        """Test that agent output format is suitable for LLM processing"""
        result = process_file(self.test_file, 'agent')
        
        # Agent output should be human-readable string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Should contain file information for context
        self.assertIn('integration_test.txt', result)
        self.assertIn('File Analysis Report', result)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)