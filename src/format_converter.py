"""
Format Converter Module
Handles conversion of various image/document formats (HEIC, PNG, SVG, PDF) to PIL Image objects.
"""

from typing import Tuple, Optional
from PIL import Image
import io


class FormatConverter:
    """Converts various file formats to PIL Images for AI analysis."""
    
    @staticmethod
    def get_format_from_filename(filename: str) -> str:
        """Extract file format from filename."""
        ext = filename.lower().split('.')[-1]
        return ext
    
    @staticmethod
    def convert_heic_to_pil(file_bytes: bytes) -> Image.Image:
        """
        Convert HEIC file to PIL Image.
        
        Args:
            file_bytes: HEIC file bytes
            
        Returns:
            PIL Image object
        """
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
            image = Image.open(io.BytesIO(file_bytes))
            # Convert to RGB if needed
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            return image
        except ImportError:
            raise ImportError("pillow-heif not installed. Run: pip install pillow-heif")
        except Exception as e:
            raise Exception(f"Failed to convert HEIC: {e}")
    
    @staticmethod
    def convert_svg_to_pil(file_bytes: bytes, target_size: Tuple[int, int] = (1024, 1024)) -> Image.Image:
        """
        Convert SVG file to PIL Image.
        
        Args:
            file_bytes: SVG file bytes
            target_size: Target dimensions for rasterization
            
        Returns:
            PIL Image object
        """
        try:
            import cairosvg
            # Convert SVG to PNG bytes
            png_bytes = cairosvg.svg2png(
                bytestring=file_bytes,
                output_width=target_size[0],
                output_height=target_size[1]
            )
            image = Image.open(io.BytesIO(png_bytes))
            return image
        except ImportError:
            raise ImportError("cairosvg not installed. Run: pip install cairosvg")
        except Exception as e:
            raise Exception(f"Failed to convert SVG: {e}")
    
    @staticmethod
    def convert_pdf_to_pil(file_bytes: bytes, page_num: int = 0) -> Image.Image:
        """
        Convert PDF page to PIL Image.
        
        Args:
            file_bytes: PDF file bytes
            page_num: Page number to convert (0-indexed)
            
        Returns:
            PIL Image object
        """
        try:
            import fitz  # PyMuPDF
            # Open PDF from bytes
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            
            if page_num >= pdf_document.page_count:
                page_num = 0
            
            # Get the page
            page = pdf_document[page_num]
            
            # Render page to image (300 DPI for good quality)
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for ~200 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            
            pdf_document.close()
            return image
        except ImportError:
            raise ImportError("PyMuPDF not installed. Run: pip install PyMuPDF")
        except Exception as e:
            raise Exception(f"Failed to convert PDF: {e}")
    
    @staticmethod
    def convert_to_pil(file_bytes: bytes, filename: str) -> Tuple[Image.Image, str]:
        """
        Convert any supported format to PIL Image.
        
        Args:
            file_bytes: File bytes
            filename: Original filename (used to determine format)
            
        Returns:
            Tuple of (PIL Image, format name)
        """
        file_format = FormatConverter.get_format_from_filename(filename)
        
        try:
            if file_format in ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'):
                # Standard formats supported by PIL
                image = Image.open(io.BytesIO(file_bytes))
                if image.mode not in ('RGB', 'RGBA', 'L'):
                    image = image.convert('RGB')
                return image, file_format
            
            elif file_format in ('heic', 'heif'):
                image = FormatConverter.convert_heic_to_pil(file_bytes)
                return image, file_format
            
            elif file_format == 'svg':
                image = FormatConverter.convert_svg_to_pil(file_bytes)
                return image, file_format
            
            elif file_format == 'pdf':
                image = FormatConverter.convert_pdf_to_pil(file_bytes)
                return image, file_format
            
            else:
                raise ValueError(f"Unsupported format: {file_format}")
                
        except Exception as e:
            raise Exception(f"Failed to process {filename}: {e}")
    
    @staticmethod
    def convert_pil_to_bytes(image: Image.Image, target_format: str = 'JPEG') -> bytes:
        """
        Convert PIL Image back to bytes.
        
        Args:
            image: PIL Image object
            target_format: Target format (JPEG, PNG, etc.)
            
        Returns:
            Image bytes
        """
        output = io.BytesIO()
        
        # Handle format-specific conversions
        if target_format.upper() == 'JPEG':
            # JPEG doesn't support transparency
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(output, format='JPEG', quality=95, optimize=True)
        
        elif target_format.upper() == 'PNG':
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGBA')
            image.save(output, format='PNG', optimize=True)
        
        else:
            # Default to JPEG
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            image.save(output, format='JPEG', quality=95)
        
        return output.getvalue()
    
    @staticmethod
    def should_convert_output_format(original_format: str) -> str:
        """
        Determine output format based on original format.
        
        Args:
            original_format: Original file format
            
        Returns:
            Output format (maintains original where possible)
        """
        # Keep original format for standard image formats
        if original_format in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
            return original_format
        
        # Convert HEIC to JPEG (more compatible)
        elif original_format in ('heic', 'heif'):
            return 'jpg'
        
        # Convert SVG and PDF to PNG (preserves quality better)
        elif original_format in ('svg', 'pdf'):
            return 'png'
        
        else:
            return 'jpg'  # Default fallback

