import whisperx
import torch
import os
from pyannote.audio import Pipeline
import gc
import tempfile
import soundfile as sf
from podscribe.database import SessionLocal
from podscribe.models import Episode
from podscribe.config import WHISPERX_MODEL
import logging
import sys
import pandas as pd
import json

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
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
    """Transcribe an episode using WhisperX with diarization"""
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
                result = model.transcribe(audio)
                
                logger.info("Aligning whisper output...")
                model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
                result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

                logger.info("Performing diarization...")
                diarize_model = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                                         use_auth_token=os.environ.get("HF_TOKEN"))
                diarize_model = diarize_model.to(torch.device(device))

                # Save audio to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                    sf.write(temp_audio.name, audio, 16000)  # 16000 is the sample rate, adjust if needed
                    temp_audio_path = temp_audio.name

                # Use the temporary file for diarization
                diarization = diarize_model(temp_audio_path)

                # Remove the temporary file
                os.unlink(temp_audio_path)

                logger.info("Assigning speaker labels...")
                try:
                    # Convert pyannote.Annotation to compatible DataFrame format
                    diarize_df = pd.DataFrame(columns=['start', 'end', 'speaker'])
                    
                    # Extract segments from pyannote diarization
                    for segment, _, speaker in diarization.itertracks(yield_label=True):
                        diarize_df = pd.concat([diarize_df, pd.DataFrame({
                            'start': [segment.start],
                            'end': [segment.end],
                            'speaker': [speaker]
                        })], ignore_index=True)

                    # Debug logging
                    logger.debug("Diarization DataFrame structure:")
                    logger.debug(diarize_df.head().to_string())
                    logger.debug("WhisperX result structure:")
                    logger.debug(json.dumps(result["segments"][0], indent=2))

                    # Verify result structure
                    if not isinstance(result, dict) or "segments" not in result:
                        raise ValueError("Invalid result structure - missing segments")
                    
                    # Assign speakers using DataFrame format
                    result = whisperx.assign_word_speakers(diarize_df, result)
                    
                except Exception as e:
                    logger.error(f"Error assigning speaker labels: {str(e)}")
                    logger.warning("Continuing without speaker diarization")
                    # Ensure result has basic structure even without diarization
                    if "segments" not in result:
                        result["segments"] = []

                # Free up GPU memory
                del model, model_a, diarize_model
                gc.collect()
                torch.cuda.empty_cache()

                # Process the result to include speaker labels
                transcript = ""
                current_speaker = None
                for segment in result["segments"]:
                    if "speaker" in segment and segment["speaker"] != current_speaker:
                        current_speaker = segment["speaker"]
                        transcript += f"\n\nSpeaker {current_speaker}:\n"
                    transcript += segment["text"] + " "

                episode.transcript = transcript.strip()
                session.commit()
                logger.info("Transcription with diarization completed and saved successfully")
                
            except Exception as e:
                logger.error(f"Transcription failed: {str(e)}")
                if hasattr(e, '__traceback__'):
                    logger.error(f"Traceback: {e.__traceback__}")
                raise RuntimeError(f"Transcription process failed: {str(e)}")
                
    except Exception as e:
        logger.error(f"Fatal error during transcription process: {str(e)}")
        raise
