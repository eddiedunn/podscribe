from podscribe.models import Base, Podcast, Episode
from podscribe.database import engine, SessionLocal
from podscribe.podcast_rss import parse_rss_feed
from podscribe.transcription import transcribe_episode
from datetime import datetime

def init_db():
    Base.metadata.create_all(bind=engine)

def list_episodes(podcast_rss=None):
    """
    List all episodes, optionally filtered by podcast RSS URL.
    Returns a list of episodes.
    """
    with SessionLocal() as session:
        query = session.query(Episode)
        if podcast_rss:
            query = query.join(Podcast).filter(Podcast.rss_url == podcast_rss)
        
        episodes = query.all()
        
        print("\nEpisode List:")
        print("-" * 50)
        for ep in episodes:
            print(f"ID: {ep.id}")
            print(f"Title: {ep.title}")
            print(f"Published: {ep.published_date}")
            print(f"Has Transcript: {'Yes' if ep.transcript else 'No'}")
            print("-" * 50)
        
        return episodes

def main():
    init_db()
    
    # Example usage
    rss_url = "https://feeds.twit.tv/twit.xml"
    podcast = parse_rss_feed(rss_url)
    
    # List all episodes for this podcast
    episodes = list_episodes(rss_url)
    
    if episodes:
        # Get the most recent episode that hasn't been transcribed yet
        for episode in episodes:
            if not episode.transcript:
                print(f"\nTranscribing episode: {episode.title}")
                transcribe_episode(episode.id)
                break
    else:
        print("No episodes found")

if __name__ == "__main__":
    main()