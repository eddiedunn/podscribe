# podscribe/transcription.py
import whisperx
import torch
import os
from podscribe.database import SessionLocal
from podscribe.models import Episode
from podscribe.config import WHISPERX_MODEL
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def verify_gpu_requirements():
    """Verify GPU requirements and provide detailed feedback"""
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is not available. Please ensure:\n"
            "1. You have an NVIDIA GPU\n"
            "2. CUDA toolkit is installed\n"
            "3. PyTorch with CUDA support is installed\n"
            f"Current PyTorch CUDA status:\n"
            f"- torch.version.cuda: {torch.version.cuda}\n"
            f"- torch.__version__: {torch.__version__}"
        )
    
    gpu_name = torch.cuda.get_device_name(0)
    cuda_version = torch.version.cuda
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9  # Convert to GB
    
    logger.info(f"GPU detected: {gpu_name}")
    logger.info(f"CUDA version: {cuda_version}")
    logger.info(f"Available GPU memory: {gpu_memory:.2f} GB")
    
    return "cuda"

def transcribe_episode(episode_id):
    """Transcribe an episode using WhisperX with enhanced error handling"""
    try:
        # Verify GPU setup
        device = verify_gpu_requirements()
        compute_type = "float16"  # Best for GPU performance
        
        logger.info(f"Loading model {WHISPERX_MODEL}")
        try:
            model = whisperx.load_model(
                WHISPERX_MODEL,
                device=device,
                compute_type=compute_type
            )
        except Exception as e:
            logger.error(f"Failed to load WhisperX model. Error: {str(e)}")
            logger.error(f"Model: {WHISPERX_MODEL}")
            logger.error(f"Device: {device}")
            logger.error(f"Compute type: {compute_type}")
            raise RuntimeError(f"Model loading failed: {str(e)}")

        with SessionLocal() as session:
            episode = session.query(Episode).filter_by(id=episode_id).first()
            
            if not episode:
                raise ValueError(f"Episode {episode_id} not found in database")
            
            if not episode.audio_url:
                raise ValueError(f"No audio URL found for episode {episode_id}")
            
            if episode.transcript:
                logger.warning(f"Episode {episode_id} already has a transcript")
                return
            
            logger.info(f"Loading audio from: {episode.audio_url}")
            try:
                audio = whisperx.load_audio(episode.audio_url)
            except Exception as e:
                logger.error(f"Failed to load audio file: {str(e)}")
                raise RuntimeError(f"Audio loading failed: {str(e)}")

            logger.info("Starting transcription...")
            try:
                logger.info("Starting transcription with WhisperX...")
                result = model.transcribe(audio)
                
                # Debug the result structure
                logger.info("Transcription completed. Analyzing result structure...")
                logger.info(f"Result type: {type(result)}")
                logger.info(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dictionary'}")
                logger.info(f"Full result: {result}")
                
                if not result:
                    raise ValueError("Transcription returned empty result")
                    
                if isinstance(result, dict):
                    if "text" not in result:
                        # Check for alternative key structures
                        if "segments" in result:
                            # Some whisperx versions return segments
                            text = " ".join([seg.get("text", "") for seg in result["segments"]])
                            if text.strip():
                                result["text"] = text
                            else:
                                raise ValueError("No text found in segments")
                        else:
                            raise ValueError(f"Expected 'text' in result. Found keys: {result.keys()}")
                else:
                    raise ValueError(f"Expected dict result, got {type(result)}")
                
                episode.transcript = result["text"]
                session.commit()
                logger.info("Transcription completed and saved successfully")
                
            except Exception as e:
                logger.error(f"Transcription failed: {str(e)}")
                if hasattr(e, '__traceback__'):
                    logger.error(f"Traceback: {e.__traceback__}")
                raise RuntimeError(f"Transcription process failed: {str(e)}")
                
    except Exception as e:
        logger.error(f"Fatal error during transcription process: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python transcription.py <episode_id>")
        sys.exit(1)
    
    episode_id = sys.argv[1]
    transcribe_episode(episode_id)
