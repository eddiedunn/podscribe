from diarized_transcriber import (
    TranscriptionEngine,
    MediaContent,
    MediaSource,
    TranscriptionError
)

import sys
from podscribe.database import SessionLocal
from podscribe.models import Episode
from podscribe.config import WHISPERX_MODEL



def transcribe_episode(episode_id: int) -> None:
    """Transcribe an episode using diarized_transcriber."""
    try:
        engine = TranscriptionEngine(model_size=WHISPERX_MODEL)
        
        with SessionLocal() as session:
            episode = session.query(Episode).filter_by(id=episode_id).first()
            
            if not episode:
                raise ValueError(f"Episode {episode_id} not found in database")
            
            if not episode.audio_url:
                raise ValueError(f"No audio URL found for episode {episode_id}")
            
            if episode.transcript:
                logger.warning(f"Episode {episode_id} already has a transcript")
                return
            
            # Create MediaContent object
            content = MediaContent(
                id=str(episode.id),
                title=episode.title,
                media_url=episode.audio_url,
                source=MediaSource(
                    type="podcast",
                    metadata={"podcast_id": episode.podcast_id}
                )
            )
            
            # Perform transcription
            logger.info(f"Starting transcription for episode: {episode.title}")
            result = engine.transcribe(content)
            
            # Format transcript
            from diarized_transcriber.utils.formatting import format_transcript
            transcript = format_transcript(
                result,
                output_format="text",
                group_by_speaker=True
            )
            
            # Save to database
            episode.transcript = transcript
            session.commit()
            
            logger.info("Transcription completed and saved successfully")
            
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise