"""
File Processor Integration Examples
Demonstrates how to use the file processing system with memory, logs, and agent interaction.
"""

import os
import sys
sys.path.append('.')

from jarvis.utils.file_processors import process_file, get_file_info, is_file_supported
from jarvis.utils.logs import log_event
from jarvis.memory.memory import remember_fact, recall_fact

def demo_file_processing():
    """
    Demonstrate file processing capabilities with various formats
    """
    print("="*60)
    print("FILE PROCESSOR INTEGRATION DEMO")
    print("="*60)
    
    # Create demo files for testing
    demo_dir = "demo_files"
    os.makedirs(demo_dir, exist_ok=True)
    
    # Create demo TXT file
    txt_file = os.path.join(demo_dir, "sample_document.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("""Project Requirements Document
========================================

Project Name: Jarvis AI Assistant Enhancement
Version: 1.0.0
Date: 2025-08-05

Overview:
This document outlines the requirements for implementing file processing capabilities
in the Jarvis AI Assistant system. The system should be able to process multiple
file formats including PDF, Excel, and text files.

Key Features:
- Universal file processing interface
- Integration with memory system
- Logging capabilities
- Agent interaction support

Technical Requirements:
1. Support for PDF files (with placeholder for full implementation)
2. Support for Excel files (.xls and .xlsx formats)
3. Full text processing for TXT files
4. Metadata extraction for all file types
5. Error handling for corrupted or inaccessible files

Success Criteria:
- All file processors pass comprehensive tests
- Integration with existing memory and logging systems
- User-friendly API for agent interaction
- Extensible architecture for future format support""")
    
    print(f"Created demo file: {txt_file}")
    
    try:
        # 1. Basic file processing
        print("\n1. BASIC FILE PROCESSING")
        print("-" * 40)
        
        if is_file_supported(txt_file):
            print(f"✓ File format supported: {txt_file}")
            
            # Get basic file information
            file_info = get_file_info(txt_file)
            print(f"File size: {file_info['file_size']} bytes")
            print(f"File type: {file_info['file_extension']}")
            
        # 2. Memory integration
        print("\n2. MEMORY SYSTEM INTEGRATION")
        print("-" * 40)
        
        memory_data = process_file(txt_file, 'memory')
        print(f"Processed content length: {len(memory_data['content'])} characters")
        print(f"Word count: {memory_data['structured_data']['total_words']}")
        print(f"Line count: {memory_data['structured_data']['total_lines']}")
        
        # Store in memory system (using the correct format: "key to value")
        memory_key = f"document_{file_info['file_name']}"
        memory_value = f"Processed document: {memory_data['summary']['description']}"
        remember_fact(f"{memory_key} to {memory_value}")
        print(f"✓ Stored in memory with key: {memory_key}")
        
        # Retrieve from memory
        retrieved_data = recall_fact(memory_key)
        if retrieved_data:
            print(f"✓ Retrieved from memory: {retrieved_data}")
        
        # 3. Logging integration
        print("\n3. LOGGING SYSTEM INTEGRATION")
        print("-" * 40)
        
        logs_data = process_file(txt_file, 'logs')
        
        # Log the file processing event
        log_event("file_processed", {
            "file_path": txt_file,
            "file_size": logs_data['file_info']['size'],
            "file_type": logs_data['file_info']['type'],
            "processor": logs_data['processor'],
            "processing_summary": logs_data['processing_summary']
        })
        print("✓ Logged file processing event")
        
        # 4. Agent interaction
        print("\n4. AGENT INTERACTION FORMAT")
        print("-" * 40)
        
        agent_report = process_file(txt_file, 'agent')
        print("Agent-ready file analysis:")
        print(agent_report[:300] + "..." if len(agent_report) > 300 else agent_report)
        
        # 5. Demonstrate with multiple file formats
        print("\n5. MULTIPLE FORMAT SUPPORT")
        print("-" * 40)
        
        # Create dummy files for other formats
        pdf_file = os.path.join(demo_dir, "sample.pdf")
        excel_file = os.path.join(demo_dir, "sample.xlsx")
        
        # Create dummy PDF
        with open(pdf_file, 'wb') as f:
            f.write(b'%PDF-1.4\n%Dummy PDF for demonstration')
        
        # Create dummy Excel
        with open(excel_file, 'wb') as f:
            f.write(b'PK\x03\x04Dummy Excel for demonstration')
        
        for test_file in [pdf_file, excel_file]:
            if is_file_supported(test_file):
                print(f"✓ Processing {os.path.basename(test_file)}...")
                summary = process_file(test_file, 'logs')
                print(f"  Processor: {summary['processor']}")
                print(f"  File size: {summary['file_info']['size']} bytes")
        
        print("\n6. ERROR HANDLING DEMONSTRATION")
        print("-" * 40)
        
        # Test with non-existent file
        try:
            process_file("nonexistent.txt", 'memory')
        except FileNotFoundError:
            print("✓ Properly handles non-existent files")
        
        # Test with unsupported format
        unsupported_file = os.path.join(demo_dir, "test.unsupported")
        with open(unsupported_file, 'w') as f:
            f.write("test")
        
        if not is_file_supported(unsupported_file):
            print("✓ Properly identifies unsupported file formats")
        
        print("\n" + "="*60)
        print("FILE PROCESSOR DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup demo files
        import shutil
        if os.path.exists(demo_dir):
            shutil.rmtree(demo_dir)
        print("Demo files cleaned up.")


def integration_workflow_example():
    """
    Example of a complete workflow using file processors in a real scenario
    """
    print("\nWORKFLOW EXAMPLE: Document Analysis Pipeline")
    print("-" * 50)
    
    # Simulate a document analysis workflow
    workflow_steps = [
        "1. User uploads document",
        "2. System checks file format support", 
        "3. File is processed based on type",
        "4. Content is analyzed and summarized",
        "5. Results stored in memory system",
        "6. Processing logged for audit",
        "7. Summary provided to agent/user"
    ]
    
    for step in workflow_steps:
        print(f"  {step}")
    
    print("\nThis workflow is now fully implemented with the file processor system!")


if __name__ == "__main__":
    demo_file_processing()
    integration_workflow_example()