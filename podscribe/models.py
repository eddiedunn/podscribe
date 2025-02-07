from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Podcast(Base):
    """Represents a podcast feed and its metadata."""
    __tablename__ = "podcasts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    rss_url = Column(String, unique=True)
    last_updated = Column(DateTime)
    episodes = relationship("Episode", back_populates="podcast")

class Episode(Base):
    """Represents a podcast episode and its transcription."""
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"))
    title = Column(String)
    audio_url = Column(String)
    published_date = Column(DateTime)
    transcript = Column(Text)
    # Add any podcast-specific fields here
    podcast = relationship("Podcast", back_populates="episodes")
