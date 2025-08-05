import os
import uuid
import logging
from werkzeug.utils import secure_filename

# Only import these heavy dependencies if not in Vercel environment
if not os.environ.get('VERCEL') and not os.environ.get('VERCEL_ENV'):
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
    except ImportError:
        sr = None
        AudioSegment = None
else:
    sr = None
    AudioSegment = None

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for handling voice recordings and transcription"""
    
    def __init__(self):
        self.upload_folder = "voice_recordings"
        self.allowed_extensions = {'wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'}
        
        # Create upload directory if not in serverless environment
        if not os.environ.get('VERCEL') and not os.environ.get('VERCEL_ENV'):
            os.makedirs(self.upload_folder, exist_ok=True)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer() if sr else None
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_voice_recording(self, file) -> str:
        """Save uploaded voice file and return path"""
        try:
            if not file or not self.allowed_file(file.filename):
                return None
            
            # Generate unique filename
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # Save file
            file.save(file_path)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving voice recording: {e}")
            return None
    
    def convert_to_wav(self, input_path: str) -> str:
        """Convert audio file to WAV format for speech recognition"""
        if not AudioSegment:
            logger.error("AudioSegment not available in serverless environment")
            return None
        
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono WAV at 16kHz (optimal for speech recognition)
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # Generate WAV filename
            wav_path = input_path.rsplit('.', 1)[0] + '_converted.wav'
            
            # Export as WAV
            audio.export(wav_path, format="wav")
            
            return wav_path
            
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {e}")
            return input_path  # Return original if conversion fails
    
    def transcribe_audio(self, file_path: str) -> str:
        """Transcribe audio file to text using speech recognition"""
        if not self.recognizer or not sr:
            logger.error("Speech recognition not available in serverless environment")
            return None
        
        try:
            # Convert to WAV if needed
            wav_path = self.convert_to_wav(file_path)
            
            # Transcribe using speech recognition
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record audio
                audio = self.recognizer.record(source)
                
                # Recognize speech using Google Speech Recognition
                try:
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    logger.warning("Speech recognition could not understand audio")
                    return "Could not transcribe audio - speech unclear"
                except sr.RequestError as e:
                    logger.error(f"Could not request results from speech recognition service: {e}")
                    return "Transcription service temporarily unavailable"
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return "Error during transcription"
    
    def get_audio_duration(self, file_path: str) -> float:
        """Get duration of audio file in seconds"""
        if not AudioSegment:
            logger.error("AudioSegment not available in serverless environment")
            return 0.0
        
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    def validate_audio_file(self, file_path: str) -> dict:
        """Validate audio file and return metadata"""
        if not AudioSegment:
            logger.error("AudioSegment not available in serverless environment")
            return {'valid': False, 'error': 'Audio processing not available'}
        
        try:
            audio = AudioSegment.from_file(file_path)
            
            duration = len(audio) / 1000.0  # seconds
            file_size = os.path.getsize(file_path)  # bytes
            
            # Validation rules
            max_duration = 300  # 5 minutes
            max_file_size = 50 * 1024 * 1024  # 50MB
            
            return {
                'valid': duration <= max_duration and file_size <= max_file_size,
                'duration': duration,
                'file_size': file_size,
                'channels': audio.channels,
                'frame_rate': audio.frame_rate,
                'max_duration': max_duration,
                'max_file_size': max_file_size
            }
            
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def cleanup_old_files(self, days_old: int = 30):
        """Clean up voice recording files older than specified days"""
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            for filename in os.listdir(self.upload_folder):
                file_path = os.path.join(self.upload_folder, filename)
                
                if os.path.isfile(file_path):
                    file_created = os.path.getctime(file_path)
                    
                    if file_created < cutoff_time:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old voice file: {filename}")
            
        except Exception as e:
            logger.error(f"Error during voice file cleanup: {e}")

# Global instance
voice_service = VoiceService()