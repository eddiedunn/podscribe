import logging
import feedparser
import requests
from datetime import datetime
from typing import Optional
from podscribe.models import Podcast, Episode
from podscribe.database import SessionLocal
from podscribe.config import logger

<<<<<<< HEAD
def parse_rss_feed(rss_url):
    """Parse a podcast RSS feed and store episodes in database."""

    try:
        # Fetch the RSS feed manually
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Charset": "utf-8",  # Request UTF-8
        }
        response = requests.get(rss_url, headers=headers, timeout=10)

        # Force UTF-8 encoding (ignoring errors if needed)
        response.encoding = "utf-8"
        feed_data = response.text  # Or response.content.decode("utf-8", errors="ignore")

        # Parse the feed with feedparser
        feed = feedparser.parse(feed_data)

        # Check for malformed feeds
        if feed.bozo:
            logger.error(f"Feed error for {rss_url}: {feed.bozo_exception}")



    except requests.RequestException as e:
        logger.error(f"Network error while fetching {rss_url}: {e}")
        return None

=======
logger = logging.getLogger(__name__)

def parse_rss_feed(rss_url: str) -> Optional[Podcast]:
    """
    Parse a podcast RSS feed and store episodes in database.
>>>>>>> f45f908 (from server)
    
    Args:
        rss_url: URL of the podcast RSS feed
        
    Returns:
        Optional[Podcast]: The created or updated Podcast object
    """
    try:
        feed = feedparser.parse(rss_url)
        if feed.bozo:  # feedparser's flag for malformed feeds
            logger.error(f"Feed error for {rss_url}: {feed.bozo_exception}")
            return None
            
        with SessionLocal() as session:
            # Get or create podcast
            podcast = session.query(Podcast).filter_by(rss_url=rss_url).first()
            
            if not podcast:
                logger.info(f"Creating new podcast from feed: {feed.feed.title}")
                podcast = Podcast(
                    title=feed.feed.title,
                    rss_url=rss_url,
                    last_updated=datetime.now()
                )
                session.add(podcast)
                session.commit()  # Commit to get podcast.id
            
            # Process episodes
            new_episodes = 0
            for entry in feed.entries:
                # Look for existing episode
                existing = session.query(Episode).filter_by(
                    podcast_id=podcast.id,
                    title=entry.title
                ).first()
                
                if not existing:
                    # Find audio URL
                    audio_url = None
                    for link in entry.links:
                        if hasattr(link, 'type') and link.type.startswith('audio/'):
                            audio_url = link.href
                            break
                    
                    if audio_url:
                        try:
                            published_date = datetime(*entry.published_parsed[:6])
                        except (TypeError, AttributeError):
                            published_date = datetime.now()
                        
                        new_episode = Episode(
                            podcast_id=podcast.id,
                            title=entry.title,
                            audio_url=audio_url,
                            published_date=published_date
                        )
                        session.add(new_episode)
                        new_episodes += 1
            
            if new_episodes > 0:
                logger.info(f"Added {new_episodes} new episodes for {podcast.title}")
                
            # Update podcast timestamp
            podcast.last_updated = datetime.now()
            session.commit()
            
            return podcast
            
    except Exception as e:
        logger.error(f"Failed to parse RSS feed {rss_url}: {str(e)}")
        return None