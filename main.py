import logging
import os
import yaml
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from podscribe.models import Base, Podcast, Episode
from podscribe.database import engine, SessionLocal
from podscribe.podcast_rss import parse_rss_feed
from podscribe.transcription import transcribe_episode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)

def list_episodes(podcast_rss: Optional[str] = None) -> List[Episode]:
    """
    List all episodes, optionally filtered by podcast RSS URL.
    
    Args:
        podcast_rss: Optional RSS URL to filter by
        
    Returns:
        List[Episode]: List of matching episodes
    """
    with SessionLocal() as session:
        query = session.query(Episode)
        if podcast_rss:
            query = query.join(Podcast).filter(Podcast.rss_url == podcast_rss)
        
        episodes = query.all()
        
        logger.info("\nEpisode List:")
        logger.info("-" * 50)
        for ep in episodes:
            logger.info(f"ID: {ep.id}")
            logger.info(f"Title: {ep.title}")
            logger.info(f"Published: {ep.published_date}")
            logger.info(f"Has Transcript: {'Yes' if ep.transcript else 'No'}")
            logger.info("-" * 50)
        
        return episodes

def process_feed(rss_url: str) -> Optional[Podcast]:
    """
    Process a single RSS feed.
    
    Args:
        rss_url: RSS feed URL to process
        
    Returns:
        Optional[Podcast]: The processed podcast or None if failed
    """
    logger.info(f"Processing feed: {rss_url}")
    
    podcast = parse_rss_feed(rss_url)
    if not podcast:
        return None
        
    episodes = list_episodes(rss_url)
    if episodes:
        # Find first episode without transcript
        for episode in episodes:
            if not episode.transcript:
                logger.info(f"Transcribing episode: {episode.title}")
                try:
                    transcribe_episode(episode.id)
                    break
                except Exception as e:
                    logger.error(f"Failed to transcribe episode {episode.id}: {str(e)}")
                    continue
    else:
        logger.warning("No episodes found for this feed")
    
    return podcast

def main() -> None:
    """Main entry point for podscribe."""
    # Load environment variables
    load_dotenv()
    
    # Initialize database
    init_db()
    
    # Load RSS feed URLs
    feeds_path = os.path.join(os.path.dirname(__file__), 'feeds.yaml')
    try:
        with open(feeds_path, 'r') as f:
            feeds_data = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Error: {feeds_path} not found")
        return

    rss_feeds = feeds_data.get("rss_feeds", [])
    if not rss_feeds:
        logger.error("No RSS feeds found in the YAML file")
        return

    # Process each feed
    for rss_url in rss_feeds:
        process_feed(rss_url)

if __name__ == "__main__":
    main()