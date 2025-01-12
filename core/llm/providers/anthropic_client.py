import anthropic
from core.config import Config
import base64
from pathlib import Path
import mimetypes
from typing import Dict, Any
import imghdr
from PIL import Image
import io

SUPPORTED_MEDIA_TYPES = {
    'image/jpeg': ['jpeg', 'jpg'],
    'image/png': ['png'],
    'image/gif': ['gif'],
    'image/webp': ['webp']
}

MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

class anthropicclient:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def _validate_image(self, image_path: Path) -> tuple[str, bytes]:
        """Validate image format and size"""
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        # Check file size
        file_size = image_path.stat().st_size
        if file_size > MAX_IMAGE_SIZE:
            raise ValueError(f"Image too large: {file_size/1024/1024:.1f}MB. Max size: 20MB")
            
        # Read image
        img_data = image_path.read_bytes()
        
        # Validate format
        img_format = imghdr.what(None, img_data)
        if not img_format:
            raise ValueError(f"Unable to determine image format for {image_path}")
            
        # Match format to mime type
        mime_type = None
        for mime, formats in SUPPORTED_MEDIA_TYPES.items():
            if img_format in formats:
                mime_type = mime
                break
                
        if not mime_type:
            raise ValueError(
                f"Unsupported image format: {img_format}. "
                f"Supported types: {', '.join(SUPPORTED_MEDIA_TYPES.keys())}"
            )
            
        return mime_type, img_data

    def _load_media(self, media_path: str) -> Dict[str, Any]:
        """Load image or document with validation and encode as base64."""
        path = Path(media_path)
        if not path.exists():
            raise FileNotFoundError(f"Media not found: {media_path}")

        # Handle PDFs
        if path.suffix.lower() == ".pdf":
            media_data = path.read_bytes()
            return {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64.b64encode(media_data).decode("utf-8")
                }
            }

        # Otherwise, handle images (existing logic)
        file_size = path.stat().st_size
        if file_size > MAX_IMAGE_SIZE:
            raise ValueError(f"Image too large: {file_size/1024/1024:.1f}MB. Max size: 20MB")

        img_data = path.read_bytes()
        img_format = imghdr.what(None, img_data)
        if not img_format:
            raise ValueError(f"Unable to determine image format for {media_path}")

        mime_type = None
        for mime, formats in SUPPORTED_MEDIA_TYPES.items():
            if img_format in formats:
                mime_type = mime
                break
        if not mime_type:
            raise ValueError(f"Unsupported image format: {img_format}. "
                             f"Supported types: {', '.join(SUPPORTED_MEDIA_TYPES.keys())}")

        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_type,
                "data": base64.b64encode(img_data).decode('utf-8')
            }
        }

    def llm_call(self, prompt_text: str, operation_params: dict) -> str:
        model = Config.MODEL or "claude-3-5-sonnet-20241022"
        max_tokens = Config.CONTEXT_SIZE or 8192
        temperature = Config.TEMPERATURE or 0.6
        system_prompt = Config.SYSTEM_PROMPT or ""

        # Prepare content array
        content = []
        
        # Add images if media field exists in operation params
        if operation_params and 'media' in operation_params:
            for media_path in operation_params['media']:
                content.append(self._load_media(media_path))

        # Add text prompt
        content.append({
            "type": "text",
            "text": prompt_text
        })

        # Make API call
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature, 
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        if isinstance(response.content, list):
            return ''.join([block.text for block in response.content if hasattr(block, 'text')])
        return str(response.content)
