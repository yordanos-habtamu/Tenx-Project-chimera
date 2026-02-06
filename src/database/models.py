import uuid

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    TypeDecorator,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# Generic UUID type for SQLite compatibility
class GUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True)  # Agent ID (e.g., trend_fetcher_001)
    name = Column(String(100), nullable=False)
    role = Column(String(50))
    status = Column(String(20))
    capabilities = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Agent(id='{self.id}', status='{self.status}')>"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(100), primary_key=True)  # Task ID
    type = Column(String(50))
    status = Column(String(20))
    payload = Column(JSON)
    result = Column(JSON)
    assigned_to = Column(String(50), ForeignKey("agents.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Task(id='{self.id}', status='{self.status}')>"


class Video(Base):
    __tablename__ = "videos"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    script = Column(Text)
    video_url = Column(Text)
    platform = Column(String(50))
    status = Column(String(20))  # 'draft', 'approved', 'published'
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Video(title='{self.title}', status='{self.status}')>"


class Trend(Base):
    __tablename__ = "trends"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    time = Column(DateTime(timezone=True), nullable=False)
    keyword = Column(String(100), nullable=False)
    volume = Column(Integer)
    sentiment_score = Column(Float)

    def __repr__(self):
        return f"<Trend(keyword='{self.keyword}', volume={self.volume})>"


class VideoTrend(Base):
    __tablename__ = "video_trends"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    video_id = Column(GUID, ForeignKey("videos.id", ondelete="CASCADE"))
    trend_id = Column(GUID, ForeignKey("trends.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<VideoTrend(video_id='{self.video_id}', trend_id='{self.trend_id}')>"
