# podscribe/transcription.py
import whisperx
import torch
import os

def check_cuda():
    print("\nCUDA Environment Check:")
    print("-" * 50)
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        #print(f"CUDA device count: {torch.cuda.device_count()}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
    print("-" * 50)

def transcribe_episode(episode_id):
    # Run CUDA check first
    check_cuda()
    
    # Try to force CPU if CUDA is acting up
    device = os.getenv("FORCE_CPU", "false").lower() == "true"
    if device:
        device = "cpu"
        compute_type = "int8"
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
    
    print(f"\nTranscription settings:")
    print(f"Using device: {device}")
    print(f"Compute type: {compute_type}")
    print(f"Model: {WHISPERX_MODEL}")
    
    try:
        model = whisperx.load_model(
            WHISPERX_MODEL,
            device=device,
            compute_type=compute_type
        )
        
        with SessionLocal() as session:
            episode = session.query(Episode).filter_by(id=episode_id).first()
            if episode and episode.audio_url and not episode.transcript:
                print(f"Loading audio from: {episode.audio_url}")
                try:
                    audio = whisperx.load_audio(episode.audio_url)
                    result = model.transcribe(audio)
                    episode.transcript = result["text"]
                    session.commit()
                    print("Transcription completed successfully")
                except Exception as e:
                    print(f"Error during transcription: {str(e)}")
                    raise
            else:
                if not episode:
                    print(f"Episode {episode_id} not found")
                elif not episode.audio_url:
                    print(f"No audio URL for episode {episode_id}")
                else:
                    print(f"Episode {episode_id} already has a transcript")
    except Exception as e:
        print(f"\nError loading model: {str(e)}")
        print("\nTrying fallback to CPU...")
        os.environ["FORCE_CPU"] = "true"
        transcribe_episode(episode_id)