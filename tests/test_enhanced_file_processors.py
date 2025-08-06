"""
Comprehensive tests for enhanced file processing system.
Tests the improved PDF, Excel, DOCX, JSON, and Image processors.
"""

import unittest
import tempfile
import os
import json
import sys
from unittest.mock import patch, MagicMock

# Add the project path to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.utils.file_processors import (
    FileProcessorFactory,
    TXTProcessor,
    PDFProcessor,
    ExcelProcessor,
    DocxProcessor,
    JSONProcessor,
    ImageProcessor,
    process_file,
    get_file_info,
    is_file_supported,
    get_supported_formats
)


class TestEnhancedFileProcessors(unittest.TestCase):
    """Test enhanced file processing capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = {}
        self._create_test_files()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_files(self):
        """Create test files for different formats."""
        # Create TXT file
        txt_path = os.path.join(self.temp_dir, "test.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("This is a test text file.\nIt contains multiple lines.\nWith various content.")
        self.test_files['txt'] = txt_path
        
        # Create JSON file
        json_path = os.path.join(self.temp_dir, "test.json")
        test_data = {
            "name": "Test Document",
            "version": "1.0",
            "features": ["file_processing", "testing", "validation"],
            "metadata": {
                "created": "2025-01-01",
                "author": "Test Suite"
            }
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        self.test_files['json'] = json_path
        
        # Create invalid JSON file
        invalid_json_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_json_path, 'w', encoding='utf-8') as f:
            f.write('{"invalid": json content without closing brace')
        self.test_files['invalid_json'] = invalid_json_path
        
        # Create dummy PDF file (for testing without PyPDF2)
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%dummy PDF content for testing')
        self.test_files['pdf'] = pdf_path
        
        # Create dummy Excel file (for testing without openpyxl)
        xlsx_path = os.path.join(self.temp_dir, "test.xlsx")
        with open(xlsx_path, 'wb') as f:
            f.write(b'PK\x03\x04dummy Excel content for testing')
        self.test_files['xlsx'] = xlsx_path
        
        # Create dummy DOCX file (for testing without python-docx)
        docx_path = os.path.join(self.temp_dir, "test.docx")
        with open(docx_path, 'wb') as f:
            f.write(b'PK\x03\x04dummy Word content for testing')
        self.test_files['docx'] = docx_path
        
        # Create dummy image file (for testing without PIL)
        jpg_path = os.path.join(self.temp_dir, "test.jpg")
        with open(jpg_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0dummy JPEG content for testing')
        self.test_files['jpg'] = jpg_path
    
    def test_factory_supported_formats(self):
        """Test that factory supports all expected formats."""
        supported = get_supported_formats()
        expected_formats = ['.txt', '.pdf', '.xls', '.xlsx', '.docx', '.json', 
                          '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']
        
        for fmt in expected_formats:
            self.assertIn(fmt, supported, f"Format {fmt} should be supported")
    
    def test_factory_create_processors(self):
        """Test that factory creates correct processor types."""
        test_cases = [
            (self.test_files['txt'], TXTProcessor),
            (self.test_files['pdf'], PDFProcessor),
            (self.test_files['xlsx'], ExcelProcessor),
            (self.test_files['docx'], DocxProcessor),
            (self.test_files['json'], JSONProcessor),
            (self.test_files['jpg'], ImageProcessor)
        ]
        
        for file_path, expected_type in test_cases:
            processor = FileProcessorFactory.create_processor(file_path)
            self.assertIsInstance(processor, expected_type)
    
    def test_txt_processor_enhanced(self):
        """Test enhanced TXT processor functionality."""
        processor = TXTProcessor(self.test_files['txt'])
        
        # Test text extraction
        text = processor.extract_text()
        self.assertIn("test text file", text)
        self.assertIn("multiple lines", text)
        
        # Test data extraction
        data = processor.extract_data()
        self.assertGreater(data['total_lines'], 0)
        self.assertGreater(data['total_words'], 0)
        self.assertGreater(data['total_characters'], 0)
        self.assertEqual(data['encoding'], 'utf-8')
        
        # Test summary
        summary = processor.get_summary()
        self.assertIn('statistics', summary)
        self.assertIn('common_words', summary)
        self.assertIn('preview', summary)
    
    def test_pdf_processor_fallback(self):
        """Test PDF processor fallback when PyPDF2 not available."""
        processor = PDFProcessor(self.test_files['pdf'])
        
        # Test text extraction (should use fallback)
        text = processor.extract_text()
        self.assertIn("PDF", text)
        
        # Test data extraction
        data = processor.extract_data()
        self.assertTrue(isinstance(data, dict))
        
        # Test summary
        summary = processor.get_summary()
        self.assertIn('description', summary)
        self.assertIn('file_info', summary)
    
    @patch('jarvis.utils.file_processors.logger')
    def test_pdf_processor_with_pypdf2(self, mock_logger):
        """Test PDF processor with mocked PyPDF2."""
        with patch.dict('sys.modules', {'PyPDF2': MagicMock()}):
            # Mock PyPDF2 functionality
            mock_pypdf2 = sys.modules['PyPDF2']
            mock_reader = MagicMock()
            mock_reader.pages = [MagicMock(), MagicMock()]
            mock_reader.pages[0].extract_text.return_value = "Page 1 content"
            mock_reader.pages[1].extract_text.return_value = "Page 2 content"
            mock_reader.is_encrypted = False
            mock_reader.metadata = {"Title": "Test PDF"}
            mock_pypdf2.PdfReader.return_value = mock_reader
            
            processor = PDFProcessor(self.test_files['pdf'])
            
            # Test text extraction
            text = processor.extract_text()
            self.assertIn("Page 1 content", text)
            self.assertIn("Page 2 content", text)
            
            # Test data extraction
            data = processor.extract_data()
            self.assertEqual(data['page_count'], 2)
            self.assertEqual(data['is_encrypted'], False)
    
    def test_excel_processor_fallback(self):
        """Test Excel processor fallback when openpyxl not available."""
        processor = ExcelProcessor(self.test_files['xlsx'])
        
        # Test text extraction (should use fallback)
        text = processor.extract_text()
        self.assertIn("Excel", text)
        
        # Test data extraction
        data = processor.extract_data()
        self.assertIn("openpyxl not available", str(data))
        
        # Test summary
        summary = processor.get_summary()
        self.assertIn('limitation', summary)
    
    def test_docx_processor_fallback(self):
        """Test DOCX processor fallback when python-docx not available."""
        processor = DocxProcessor(self.test_files['docx'])
        
        # Test text extraction (should use fallback)
        text = processor.extract_text()
        self.assertIn("DOCX", text)
        
        # Test data extraction
        data = processor.extract_data()
        self.assertIn("python-docx not available", str(data))
        
        # Test summary
        summary = processor.get_summary()
        self.assertIn('limitation', summary)
    
    def test_json_processor_valid(self):
        """Test JSON processor with valid JSON."""
        processor = JSONProcessor(self.test_files['json'])
        
        # Test text extraction
        text = processor.extract_text()
        self.assertIn("JSON File", text)
        self.assertIn("Formatted Content", text)
        
        # Test data extraction
        data = processor.extract_data()
        self.assertTrue(data['valid_json'])
        self.assertEqual(data['root_type'], 'dict')
        self.assertIn('structure', data)
        
        # Test summary
        summary = processor.get_summary()
        self.assertIn('Valid JSON file', summary['description'])
        self.assertTrue(summary['json_info']['valid'])
    
    def test_json_processor_invalid(self):
        """Test JSON processor with invalid JSON."""
        processor = JSONProcessor(self.test_files['invalid_json'])
        
        # Test text extraction
        text = processor.extract_text()
        self.assertIn("JSON Parse Error", text)
        
        # Test data extraction
        data = processor.extract_data()
        self.assertFalse(data['valid_json'])
        self.assertIn('parse_error', data)
        
        # Test summary
        summary = processor.get_summary()
        self.assertIn('Invalid JSON file', summary['description'])
        self.assertFalse(summary['json_info']['valid'])
    
    def test_image_processor_fallback(self):
        """Test Image processor fallback when PIL not available."""
        processor = ImageProcessor(self.test_files['jpg'])
        
        # Test text extraction (should use fallback)
        text = processor.extract_text()
        self.assertIn("Image Processing - Limited Mode", text)
        
        # Test data extraction
        data = processor.extract_data()
        self.assertIn("Pillow not available", str(data))
        
        # Test summary
        summary = processor.get_summary()
        self.assertIn('limitation', summary)
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test process_file function
        result = process_file(self.test_files['txt'], 'memory')
        self.assertIn('content', result)
        self.assertIn('metadata', result)
        
        result = process_file(self.test_files['txt'], 'logs')
        self.assertIn('file_info', result)
        
        result = process_file(self.test_files['txt'], 'agent')
        self.assertIsInstance(result, str)
        self.assertIn('File Analysis Report', result)
        
        # Test get_file_info function
        info = get_file_info(self.test_files['txt'])
        self.assertIn('file_name', info)
        self.assertIn('file_size', info)
        
        # Test is_file_supported function
        self.assertTrue(is_file_supported(self.test_files['txt']))
        self.assertTrue(is_file_supported(self.test_files['json']))
        
        # Test unsupported file
        unsupported_path = os.path.join(self.temp_dir, "test.xyz")
        with open(unsupported_path, 'w') as f:
            f.write("test")
        self.assertFalse(is_file_supported(unsupported_path))
    
    def test_error_handling(self):
        """Test error handling for various scenarios."""
        # Test non-existent file
        with self.assertRaises(FileNotFoundError):
            FileProcessorFactory.create_processor("/nonexistent/file.txt")
        
        # Test unsupported file type
        unsupported_path = os.path.join(self.temp_dir, "test.xyz")
        with open(unsupported_path, 'w') as f:
            f.write("test")
        
        with self.assertRaises(ValueError):
            FileProcessorFactory.create_processor(unsupported_path)
        
        # Test invalid output format
        with self.assertRaises(ValueError):
            process_file(self.test_files['txt'], 'invalid_format')
    
    def test_metadata_extraction(self):
        """Test metadata extraction for all processor types."""
        for file_type, file_path in self.test_files.items():
            processor = FileProcessorFactory.create_processor(file_path)
            metadata = processor.get_metadata()
            
            self.assertIn('file_name', metadata)
            self.assertIn('file_path', metadata)
            self.assertIn('file_extension', metadata)
            self.assertIn('file_size', metadata)
            self.assertIn('created_time', metadata)
            self.assertIn('modified_time', metadata)
            
            # Check that file size is positive
            self.assertGreater(metadata['file_size'], 0)
    
    def test_processing_modes(self):
        """Test all processing modes for each file type."""
        modes = ['memory', 'logs', 'agent']
        
        for file_type, file_path in self.test_files.items():
            processor = FileProcessorFactory.create_processor(file_path)
            
            for mode in modes:
                if mode == 'memory':
                    result = processor.process_for_memory()
                    self.assertIsInstance(result, dict)
                    self.assertIn('content', result)
                    self.assertIn('metadata', result)
                    self.assertIn('processor_type', result)
                
                elif mode == 'logs':
                    result = processor.process_for_logs()
                    self.assertIsInstance(result, dict)
                    self.assertIn('file_info', result)
                    self.assertIn('processing_summary', result)
                
                elif mode == 'agent':
                    result = processor.process_for_agent()
                    self.assertIsInstance(result, str)
                    self.assertIn('File Analysis Report', result)
    
    def test_backward_compatibility(self):
        """Test backward compatibility functions."""
        from jarvis.utils.file_processors import get_file_processor_manager
        
        manager = get_file_processor_manager()
        
        # Test manager methods
        result = manager.process_file(self.test_files['txt'])
        self.assertIsInstance(result, str)
        
        supported = manager.is_supported(self.test_files['txt'])
        self.assertTrue(supported)
        
        formats = manager.get_supported_formats()
        self.assertIn('.txt', formats)


class TestFileProcessorIntegration(unittest.TestCase):
    """Integration tests for file processor system."""
    
    def test_system_integration(self):
        """Test integration with the broader Jarvis system."""
        # Test that the file processor integrates with other system components
        from jarvis.utils.file_processors import get_supported_formats
        
        supported_formats = get_supported_formats()
        
        # Verify we support a comprehensive set of formats
        expected_minimum_formats = ['.txt', '.pdf', '.xlsx', '.json']
        for fmt in expected_minimum_formats:
            self.assertIn(fmt, supported_formats)
        
        # Verify we have reasonable coverage
        self.assertGreaterEqual(len(supported_formats), 10)
    
    def test_performance_characteristics(self):
        """Test performance characteristics of file processing."""
        import time
        
        # Create a larger test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write 1000 lines of text
            for i in range(1000):
                f.write(f"This is line {i} with some content to make it longer.\n")
            large_file_path = f.name
        
        try:
            # Time the processing
            start_time = time.time()
            result = process_file(large_file_path, 'memory')
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Verify result is correct
            self.assertIn('content', result)
            self.assertIn('structured_data', result)
            
            # Verify reasonable performance (should process in under 5 seconds)
            self.assertLess(processing_time, 5.0)
            
        finally:
            os.unlink(large_file_path)


def run_enhanced_file_processor_tests():
    """Run all enhanced file processor tests."""
    print("Running Enhanced File Processor Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestEnhancedFileProcessors))
    test_suite.addTest(unittest.makeSuite(TestFileProcessorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return results
    return {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success': result.wasSuccessful()
    }


if __name__ == '__main__':
    results = run_enhanced_file_processor_tests()
    print(f"\nTest Results: {results}")
    
    if results['success']:
        print("✅ All enhanced file processor tests passed!")
    else:
        print(f"❌ Tests failed: {results['failures']} failures, {results['errors']} errors")