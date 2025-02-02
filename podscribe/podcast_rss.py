import feedparser
from datetime import datetime
from podscribe.models import Podcast, Episode
from podscribe.database import SessionLocal

def parse_rss_feed(rss_url):
    feed = feedparser.parse(rss_url)
    
    with SessionLocal() as session:
        podcast = session.query(Podcast).filter_by(rss_url=rss_url).first()
        if not podcast:
            podcast = Podcast(title=feed.feed.title, rss_url=rss_url)
            session.add(podcast)
        
        for entry in feed.entries:
            existing_episode = session.query(Episode).filter_by(
                podcast=podcast,
                title=entry.title
            ).first()
            
            if not existing_episode:
                audio_url = next((link.href for link in entry.links if link.type.startswith('audio/')), None)
                if audio_url:
                    new_episode = Episode(
                        podcast=podcast,
                        title=entry.title,
                        audio_url=audio_url,
                        published_date=datetime(*entry.published_parsed[:6])
                    )
                    session.add(new_episode)
        
        podcast.last_updated = datetime.now()
        session.commit()
import feedparser
from datetime import datetime
from podscribe.models import Podcast, Episode
from podscribe.database import SessionLocal

def parse_rss_feed(rss_url):
    feed = feedparser.parse(rss_url)
    
    with SessionLocal() as session:
        podcast = session.query(Podcast).filter_by(rss_url=rss_url).first()
        if not podcast:
            podcast = Podcast(title=feed.feed.title, rss_url=rss_url)
            session.add(podcast)
        
        for entry in feed.entries:
            existing_episode = session.query(Episode).filter_by(
                podcast=podcast,
                title=entry.title
            ).first()
            
            if not existing_episode:
                audio_url = next((link.href for link in entry.links if link.type.startswith('audio/')), None)
                if audio_url:
                    new_episode = Episode(
                        podcast=podcast,
                        title=entry.title,
                        audio_url=audio_url,
                        published_date=datetime(*entry.published_parsed[:6])
                    )
                    session.add(new_episode)
        
        podcast.last_updated = datetime.now()
        session.commit()
