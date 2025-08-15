"""
Image Processor
Handles image processing and preview generation
"""

import tempfile
from pathlib import Path
from PIL import Image


class ImageProcessor:
    """Image processing utilities"""
    
    def __init__(self, config):
        self.config = config
        self.preview_config = config.get('preview', {})
        self.max_width = self.preview_config.get('max_width', 300)
        self.max_height = self.preview_config.get('max_height', 200)
        self.quality = self.preview_config.get('quality', 85)
    
    def find_preview_file(self, folder_path):
        """Find preview file in wallpaper folder"""
        # Priority order for preview files
        preview_files = [
            ('preview.jpg', 'image'),
            ('preview.jpeg', 'image'),
            ('preview.png', 'image'),
            ('preview.gif', 'gif'),
            ('preview.webp', 'image'),
            ('preview.bmp', 'image')
        ]
        
        for filename, file_type in preview_files:
            preview_path = folder_path / filename
            if preview_path.exists():
                return str(preview_path), file_type
        
        # Look for any image files as fallback
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tga']
        for ext in image_extensions:
            for img_file in folder_path.rglob(f'*{ext}'):
                # Skip large files (probably main wallpaper files)
                try:
                    if img_file.stat().st_size > 50 * 1024 * 1024:  # 50MB
                        continue
                except:
                    continue
                
                file_type = 'gif' if ext.lower() == '.gif' else 'image'
                return str(img_file), file_type
        
        return None, None
    
    def get_preview_path(self, folder_path):
        """Get preview image path"""
        preview_path, preview_type = self.find_preview_file(folder_path)
        return preview_path
    
    def process_image_for_web(self, image_path, output_path=None):
        """Process image for web display (resize, optimize)"""
        try:
            if not Path(image_path).exists():
                return None
            
            # If no output path specified, create temporary file
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                output_path = temp_file.name
                temp_file.close()
            
            # Open and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate new size maintaining aspect ratio
                img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(output_path, 'JPEG', quality=self.quality, optimize=True)
            
            return output_path
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def extract_gif_frame(self, gif_path, frame_number=None):
        """Extract a frame from GIF for preview"""
        try:
            with Image.open(gif_path) as gif:
                if not hasattr(gif, 'n_frames') or gif.n_frames <= 1:
                    # Single frame GIF, just convert
                    frame = gif.convert('RGB')
                else:
                    # Multi-frame GIF, select best frame
                    if frame_number is None:
                        # Try different frame positions to find a good one
                        frame_positions = [
                            min(3, gif.n_frames - 1),  # 4th frame
                            gif.n_frames // 4,         # 1/4 position
                            gif.n_frames // 2,         # Middle
                            0                           # First frame as fallback
                        ]
                        
                        best_frame = None
                        best_brightness = -1
                        
                        for pos in frame_positions:
                            try:
                                gif.seek(pos)
                                frame = gif.convert('RGB')
                                
                                # Calculate average brightness
                                grayscale = frame.convert('L')
                                pixels = list(grayscale.getdata())
                                avg_brightness = sum(pixels) / len(pixels)
                                
                                # Select frame with highest brightness (avoid black frames)
                                if avg_brightness > best_brightness and avg_brightness > 30:
                                    best_frame = frame.copy()
                                    best_brightness = avg_brightness
                                    
                            except:
                                continue
                        
                        frame = best_frame if best_frame else gif.convert('RGB')
                    else:
                        gif.seek(frame_number)
                        frame = gif.convert('RGB')
                
                # Create temporary file for the frame
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                frame.save(temp_file.name, 'JPEG', quality=self.quality)
                temp_file.close()
                
                return temp_file.name
                
        except Exception as e:
            print(f"Error extracting GIF frame: {e}")
            return None
    
    def create_placeholder_image(self, width=None, height=None, text="No Preview"):
        """Create a placeholder image"""
        try:
            w = width or self.max_width
            h = height or self.max_height
            
            # Create gray placeholder
            img = Image.new('RGB', (w, h), color=(128, 128, 128))
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            img.save(temp_file.name, 'JPEG')
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error creating placeholder: {e}")
            return None
