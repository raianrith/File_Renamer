"""
Gemini AI client with retry logic and JSON schema enforcement.
"""
import json
import time
from typing import Dict, Any, Optional, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import google.generativeai as genai
from PIL import Image
import io


class GeminiClient:
    """Client for interacting with Google Gemini Vision API."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Google Gemini API key
            model_name: Model name to use
        """
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the model."""
        return """Analyze this image and suggest a descriptive filename. Return ONLY valid JSON:
{"proposed_filename":"descriptive-name","reasons":"brief explanation","semantic_tags":["tag1","tag2"],"confidence":0.8}

Rules: Be specific but concise. No extension. Use kebab-case. Max 60 chars. No dates."""
    
    def _create_user_prompt(
        self,
        casing: str,
        max_len: int,
        ocr_tokens: str,
        threshold: float
    ) -> str:
        """
        Create the user prompt for a specific image (simplified for speed).
        
        Args:
            casing: Target casing style
            max_len: Maximum filename length
            ocr_tokens: OCR tokens to consider
            threshold: Confidence threshold
            
        Returns:
            Formatted prompt string
        """
        return f"Describe this image in a filename. Max {max_len} chars. Style: {casing}. Return JSON only."
    
    @retry(
        stop=stop_after_attempt(2),  # Reduced from 3 to 2 attempts
        wait=wait_exponential(multiplier=1, min=1, max=5),  # Faster retry
        retry=retry_if_exception_type((Exception,))
    )
    def analyze_image(
        self,
        image_bytes: bytes,
        casing: str = "kebab",
        max_len: int = 60,
        ocr_tokens: str = "None",
        threshold: float = 0.4
    ) -> Tuple[Dict[str, Any], float]:
        """
        Analyze an image and get filename suggestion.
        
        Args:
            image_bytes: Raw image bytes
            casing: Target casing style
            max_len: Maximum filename length
            ocr_tokens: OCR tokens string
            threshold: Confidence threshold
            
        Returns:
            Tuple of (result dictionary, latency in seconds)
        """
        start_time = time.time()
        
        try:
            # Load and resize image for faster processing
            image = Image.open(io.BytesIO(image_bytes))
            
            # Resize large images to max 1024px on longest side
            max_dimension = 1024
            if max(image.size) > max_dimension:
                ratio = max_dimension / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Create prompts
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(casing, max_len, ocr_tokens, threshold)
            
            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Call Gemini API with timeout
            import time as time_module
            api_start = time_module.time()
            
            try:
                # Generate content with optimized settings for speed
                response = self.model.generate_content(
                    [full_prompt, image],
                    generation_config={
                        'temperature': 0.3,  # Lower for faster, more consistent results
                        'top_p': 0.8,
                        'top_k': 20,
                        'max_output_tokens': 150,  # Reduced since we only need short JSON
                    },
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                )
                
                api_elapsed = time_module.time() - api_start
                print(f"API call took {api_elapsed:.2f}s")
                
                # Check if response was blocked
                if not response.text:
                    if hasattr(response, 'prompt_feedback'):
                        print(f"Response blocked: {response.prompt_feedback}")
                    raise Exception("Response was blocked or empty. Try a different image.")
                
                # Extract text from response
                response_text = response.text.strip()
                print(f"Got response: {response_text[:100]}...")
                
            except Exception as api_error:
                print(f"API Error after {time_module.time() - api_start:.2f}s: {api_error}")
                raise
            
            # Parse JSON
            result = self._parse_json_response(response_text)
            
            # Validate schema
            result = self._validate_and_fix_schema(result)
            
            latency = time.time() - start_time
            return result, latency
            
        except json.JSONDecodeError as e:
            # Try to repair the JSON
            repaired = self._attempt_json_repair(response_text)
            if repaired:
                latency = time.time() - start_time
                return repaired, latency
            
            # Fallback to heuristic
            return self._fallback_heuristic(image_bytes), time.time() - start_time
            
        except Exception as e:
            # Fallback to heuristic
            return self._fallback_heuristic(image_bytes), time.time() - start_time
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from response text.
        
        Args:
            response_text: Raw response text
            
        Returns:
            Parsed JSON dictionary
        """
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        return json.loads(response_text)
    
    def _validate_and_fix_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fix the JSON schema.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Validated/fixed data
        """
        required_keys = ['proposed_filename', 'reasons', 'semantic_tags', 'confidence']
        
        # Ensure all required keys exist
        for key in required_keys:
            if key not in data:
                if key == 'proposed_filename':
                    data[key] = 'unnamed-photo'
                elif key == 'reasons':
                    data[key] = 'No description available'
                elif key == 'semantic_tags':
                    data[key] = []
                elif key == 'confidence':
                    data[key] = 0.5
        
        # Validate types
        if not isinstance(data['proposed_filename'], str):
            data['proposed_filename'] = str(data['proposed_filename'])
        
        if not isinstance(data['reasons'], str):
            data['reasons'] = str(data['reasons'])
        
        if not isinstance(data['semantic_tags'], list):
            data['semantic_tags'] = []
        
        # Ensure confidence is between 0 and 1
        try:
            confidence = float(data['confidence'])
            data['confidence'] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            data['confidence'] = 0.5
        
        return data
    
    def _attempt_json_repair(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to repair malformed JSON.
        
        Args:
            response_text: Raw response text
            
        Returns:
            Repaired JSON dictionary or None
        """
        try:
            # Try to find JSON-like content
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response_text[start:end]
                data = json.loads(json_str)
                return self._validate_and_fix_schema(data)
        except Exception:
            pass
        
        return None
    
    def _fallback_heuristic(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Generate a fallback filename using simple heuristics.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Fallback result dictionary
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Get dominant color (very simple heuristic)
            image_small = image.resize((50, 50))
            pixels = list(image_small.getdata())
            
            r_avg = sum(p[0] if isinstance(p, tuple) else p for p in pixels) / len(pixels)
            g_avg = sum(p[1] if isinstance(p, tuple) else p for p in pixels) / len(pixels)
            b_avg = sum(p[2] if isinstance(p, tuple) else p for p in pixels) / len(pixels)
            
            # Determine dominant color
            if r_avg > g_avg and r_avg > b_avg:
                color = "red"
            elif g_avg > r_avg and g_avg > b_avg:
                color = "green"
            elif b_avg > r_avg and b_avg > g_avg:
                color = "blue"
            else:
                color = "neutral"
            
            # Check brightness
            brightness = (r_avg + g_avg + b_avg) / 3
            tone = "bright" if brightness > 128 else "dark"
            
            filename = f"{tone}-{color}-photo"
            
            return {
                'proposed_filename': filename,
                'reasons': 'Generated using fallback heuristic (AI analysis failed)',
                'semantic_tags': [tone, color, 'photo'],
                'confidence': 0.3
            }
            
        except Exception:
            return {
                'proposed_filename': 'unnamed-photo',
                'reasons': 'Could not analyze image',
                'semantic_tags': ['photo'],
                'confidence': 0.1
            }

