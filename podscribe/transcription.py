import whisperx
from podscribe.config import WHISPERX_MODEL
from podscribe.database import SessionLocal
from podscribe.models import Episode

def transcribe_episode(episode_id):
    model = whisperx.load_model(WHISPERX_MODEL)
    
    with SessionLocal() as session:
        episode = session.query(Episode).filter_by(id=episode_id).first()
        if episode and episode.audio_url and not episode.transcript:
            audio = whisperx.load_audio(episode.audio_url)
            result = model.transcribe(audio)
            episode.transcript = result["text"]
            session.commit()
