# podscribe/podcast_rss.py
import feedparser
from datetime import datetime
from podscribe.models import Podcast, Episode
from podscribe.database import SessionLocal

def parse_rss_feed(rss_url):
    """Parse a podcast RSS feed and store episodes in database."""
    feed = feedparser.parse(rss_url)
    
    with SessionLocal() as session:
        # First, get or create the podcast
        podcast = session.query(Podcast).filter_by(rss_url=rss_url).first()
        
        if not podcast:
            # Create new podcast
            podcast = Podcast(
                title=feed.feed.title,
                rss_url=rss_url,
                last_updated=datetime.now()
            )
            session.add(podcast)
            # Commit to get the podcast ID
            session.commit()
        
        # Now process episodes
        for entry in feed.entries:
            # Query using podcast_id instead of podcast object
            existing_episode = session.query(Episode).filter_by(
                podcast_id=podcast.id,
                title=entry.title
            ).first()
            
            if not existing_episode:
                # Find audio URL in links
                audio_url = None
                for link in entry.links:
                    if hasattr(link, 'type') and link.type.startswith('audio/'):
                        audio_url = link.href
                        break
                
                if audio_url:
                    try:
                        published_date = datetime(*entry.published_parsed[:6])
                    except (TypeError, AttributeError):
                        # Fallback to current time if date parsing fails
                        published_date = datetime.now()
                    
                    new_episode = Episode(
                        podcast_id=podcast.id,
                        title=entry.title,
                        audio_url=audio_url,
                        published_date=published_date
                    )
                    session.add(new_episode)
        
        # Update podcast last_updated timestamp
        podcast.last_updated = datetime.now()
        session.commit()
        
        return podcast
