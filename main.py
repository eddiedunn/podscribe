from podscribe.models import Base
from podscribe.database import engine
from podscribe.podcast_rss import parse_rss_feed
from podscribe.transcription import transcribe_episode

def init_db():
    Base.metadata.create_all(bind=engine)

def main():
    init_db()
    
    # Example usage
    rss_url = "https://feeds.twit.tv/twit.xml"
    parse_rss_feed(rss_url)
    
    # Assuming we know an episode ID
    transcribe_episode(1)

if __name__ == "__main__":
    main()
