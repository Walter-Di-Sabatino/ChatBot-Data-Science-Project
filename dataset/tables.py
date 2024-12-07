from sqlalchemy import create_engine, Column, Integer, String, Date, Text, Boolean, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'

    app_id = Column(String(50), primary_key=True)
    name = Column(String(255))
    release_date = Column(Date)
    estimated_owners = Column(String(50))
    peak_ccu = Column(Integer)
    required_age = Column(Integer)
    price = Column(DECIMAL(10, 2))
    dlc_count = Column(Integer)
    detailed_description = Column(Text)
    short_description = Column(Text)
    supported_languages = Column(Text)
    full_audio_languages = Column(Text)
    reviews = Column(Text)
    header_image = Column(String(500))
    website = Column(String(500))
    support_url = Column(String(500))
    support_email = Column(String(255))
    support_windows = Column(Boolean)
    support_mac = Column(Boolean)
    support_linux = Column(Boolean)
    metacritic_score = Column(Integer)
    metacritic_url = Column(String(500))
    user_score = Column(Integer)
    positive = Column(Integer)
    negative = Column(Integer)
    score_rank = Column(String(50))
    achievements = Column(Integer)
    recommendations = Column(Integer)
    notes = Column(Text)
    average_playtime = Column(Integer)
    average_playtime_2weeks = Column(Integer)
    median_playtime = Column(Integer)
    median_playtime_2weeks = Column(Integer)

class Developer(Base):
    __tablename__ = 'developers'

    developer_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('games.app_id'))
    name = Column(String(255))
    game = relationship('Game')

class Genre(Base):
    __tablename__ = 'genres'

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('games.app_id'))
    name = Column(String(255))
    game = relationship('Game')

class Movie(Base):
    __tablename__ = 'movies'

    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('games.app_id'))
    url = Column(String(500))
    game = relationship('Game')

class Package(Base):
    __tablename__ = 'packages'

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('games.app_id'))
    title = Column(String(255))
    description = Column(Text)
    game = relationship('Game')

class Publisher(Base):
    __tablename__ = 'publishers'

    publisher_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('games.app_id'))
    name = Column(String(255))
    game = relationship('Game')

class Screenshot(Base):
    __tablename__ = 'screenshots'

    screenshot_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('games.app_id'))
    url = Column(String(500))
    game = relationship('Game')

class Subpackage(Base):
    __tablename__ = 'subpackages'

    subpackage_id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(Integer, ForeignKey('packages.package_id'))
    title = Column(String(255))
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    package = relationship('Package')

class Tag(Base):
    __tablename__ = 'tags'

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String(50), ForeignKey('games.app_id'))
    name = Column(String(255))
    game = relationship('Game')
