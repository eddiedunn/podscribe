from podscribe.models import Base, Podcast, Episode
from podscribe.database import engine, SessionLocal
from podscribe.podcast_rss import parse_rss_feed
from podscribe.transcription import transcribe_episode
from datetime import datetime
from dotenv import load_dotenv
import os
import yaml

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

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

    # Load the YAML file containing RSS feed URLs
    feeds_path = os.path.join(os.path.dirname(__file__), 'feeds.yaml')
    try:
        with open(feeds_path, 'r') as f:
            feeds_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {feeds_path} not found.")
        return

    rss_feeds = feeds_data.get("rss_feeds", [])
    if not rss_feeds:
        print("No RSS feeds found in the YAML file.")
        return

    # Process each RSS feed
    for rss_url in rss_feeds:
        print(f"\nProcessing feed: {rss_url}")

        # Parse the podcast RSS feed
        podcast = parse_rss_feed(rss_url)

        # List all episodes for this podcast
        episodes = list_episodes(rss_url)

        if episodes:
            # Transcribe the first episode that hasn't been transcribed yet
            for episode in episodes:
                if not episode.transcript:
                    print(f"\nTranscribing episode: {episode.title}")
                    transcribe_episode(episode.id)
                    break
        else:
            print("No episodes found for this feed.")

if __name__ == "__main__":
    main()
