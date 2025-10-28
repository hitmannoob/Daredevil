
import cv2
import base64
import time
import asyncio
import json
from openai import AsyncOpenAI
from io import BytesIO
from PIL import Image
import numpy as np
import edge_tts
import io
import os 
import subprocess # Use standard subprocess for the native afplay command

class AsyncEdgeTTS:
    def __init__(self, voice="en-US-JennyNeural"):
        self.voice = voice
        self.temp_file = "temp_tts_audio.mp3"

    def _play_afplay_blocking(self, filepath):
        """This function runs in a separate thread and blocks until playback is done using macOS's afplay."""
        try:
            # afplay is a system command available on all MacBooks
            subprocess.run(["afplay", filepath], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error playing sound via afplay: {e}")

    async def speak(self, text):
        """
        Saves the audio file and plays it in a non-blocking way 
        using asyncio.to_thread and the native afplay command.
        """
        print(f"🤖 Speaking: {text}")
        
        communicate = edge_tts.Communicate(text, self.voice)
        
        try:

            await communicate.save(self.temp_file)
            
            await asyncio.to_thread(self._play_afplay_blocking, self.temp_file)
            
        except Exception as e:

            print(f"Error during TTS saving or thread creation: {e}")
            await asyncio.sleep(len(text) / 30)
        finally:
            # 3. Clean up the temporary file
            if os.path.exists(self.temp_file):
                 os.remove(self.temp_file)




class OpenAIVisionAnalyzer:
    def __init__(self, api_key, analysis_interval=2.0):
        """
        Initialize the OpenAI Vision Analyzer
        
        Args:
            api_key: OpenAI API key
            analysis_interval: Time between frame analyses in seconds
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.analysis_interval = analysis_interval
        self.last_analysis_time = 0
        self.is_analyzing = False
        self.tts_engine = AsyncEdgeTTS(voice="en-US-JennyNeural")
        
    def encode_frame_to_base64(self, frame):
        """Convert OpenCV frame to base64 string for API"""

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        

        max_dimension = 512
        if pil_image.width > max_dimension or pil_image.height > max_dimension:
            pil_image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        

        buffer = BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return image_base64
    
    async def analyze_frame(self, frame):
        """Send frame to OpenAI Vision API for analysis"""
        if self.is_analyzing:
            return None
            
        self.is_analyzing = True
        
        try:

            base64_image = self.encode_frame_to_base64(frame)

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
Assist a blind person in navigating safely. Describe the scene clearly and concisely, including only safety-critical details that can be understood within 2–3 seconds:

Immediate obstacles or hazards (highest priority)

Open or safe pathways and directions

Approximate distance to key objects (near/far)

Positions of people (e.g., left, right, ahead)

Doorways, stairs, or elevation changes.
Avoid extra or descriptive details — focus only on navigation-relevant information."


"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "low"  
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            description = response.choices[0].message.content
            return description
            
        except Exception as e:
            print(f"Error analyzing frame: {e}")
            return None
        finally:
            self.is_analyzing = False


    async def text_to_speech(self, text):
        """Convert text to speech using the Edge TTS engine."""
        if text:
            await self.tts_engine.speak(text)
    
    async def start_continuous_capture(self):
        """Start capturing and analyzing webcam frames continuously"""
        cap = cv2.VideoCapture(1)
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Starting webcam capture... Press 'q' to quit")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture frame")
                    continue
                
                cv2.imshow('Webcam Feed', frame)
                

                current_time = time.time()
                if current_time - self.last_analysis_time >= self.analysis_interval:

                    print(f"\nAnalyzing frame at {current_time:.2f}...")
                    description = await self.analyze_frame(frame)
                    
                    if description:
                        await self.text_to_speech(description)
                    
                    self.last_analysis_time = current_time
                

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    

                await asyncio.sleep(0.06)  # ~30 FPS
                
        finally:
            cap.release()
            cv2.destroyAllWindows()

async def main():
    # Configuration
    API_KEY = os.environ['OPENAI_API_KEY']
    ANALYSIS_INTERVAL = 3.0  # Analyze every 3 seconds
    
    # Create analyzer
    analyzer = OpenAIVisionAnalyzer(
        api_key=API_KEY,
        analysis_interval=ANALYSIS_INTERVAL
    )
    
    # Start continuous capture and analysis
    await analyzer.start_continuous_capture()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())