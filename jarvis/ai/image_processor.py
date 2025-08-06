#!/usr/bin/env python3
"""
Image Processor for Jarvis V0.19
Specialized image processing capabilities
"""

import os
import sys
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jarvis.core.error_handler import error_handler, ErrorLevel, safe_execute

class ImageProcessor:
    """
    Specialized image processing component
    """
    
    def __init__(self):
        self.setup_processors()
    
    def setup_processors(self):
        """Setup image processing components"""
        try:
            from PIL import Image
            self.pil_available = True
        except ImportError:
            self.pil_available = False
    
    @safe_execute(fallback_value=None, context="Image Processing")
    def process_image_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Process an image file and return analysis"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Basic file info
        result = {
            "success": True,
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_extension": file_path.suffix.lower()
        }
        
        # Check if it's an image file
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        if file_path.suffix.lower() not in image_extensions:
            result.update({
                "is_image": False,
                "message": "File is not a supported image format"
            })
            return result
        
        result["is_image"] = True
        
        if self.pil_available:
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    result.update({
                        "dimensions": {
                            "width": img.width,
                            "height": img.height
                        },
                        "format": img.format,
                        "mode": img.mode,
                        "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                        "analysis": f"Successfully analyzed {file_path.name}: {img.width}x{img.height} {img.format} image"
                    })
            except Exception as e:
                result.update({
                    "error": f"Failed to process image: {str(e)}",
                    "success": False
                })
        else:
            result.update({
                "analysis": f"Image file detected: {file_path.name}. Install PIL/Pillow for detailed analysis.",
                "note": "Basic image detection without PIL/Pillow"
            })
        
        return result