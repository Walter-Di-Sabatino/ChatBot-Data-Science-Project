from sqlalchemy import create_engine, Column, Integer, String, Date, Text, Boolean, DECIMAL, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Modello per la tabella dei giochi (Games)
class Game(Base):
    __tablename__ = 'games'

    app_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True)  # Indice per la ricerca dei giochi per nome
    release_date = Column(Date)
    estimated_owners = Column(String(50))
    peak_ccu = Column(Integer)
    required_age = Column(Integer)
    price = Column(DECIMAL(10, 2))
    dlc_count = Column(Integer)
    detailed_description = Column(Text)
    short_description = Column(Text)
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

    # Relazioni molti a molti
    developers = relationship('Developer', secondary='game_developers')
    genres = relationship('Genre', secondary='game_genres')
    publishers = relationship('Publisher', secondary='game_publishers')
    tags = relationship('Tag', secondary='game_tags')
    
    # Relazioni aggiuntive per le lingue
    supported_languages = relationship('Language', secondary='game_supported_languages')
    full_audio_languages = relationship('Language', secondary='game_full_audio_languages')

Index('idx_game_price', Game.price)
Index('idx_game_positive_negative', Game.positive, Game.negative)

class Language(Base):
    __tablename__ = 'languages'

    language_id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(255))
    name = Column(String(255), unique=True, index=True)  # Indice per la ricerca delle lingue

class GameSupportedLanguage(Base):
    __tablename__ = 'game_supported_languages'

    app_id = Column(Integer, ForeignKey('games.app_id'), primary_key=True)
    language_id = Column(Integer, ForeignKey('languages.language_id'), primary_key=True)

# Indice per la relazione tra giochi e lingue supportate
Index('idx_game_supported_language', GameSupportedLanguage.app_id, GameSupportedLanguage.language_id)

class GameFullAudioLanguage(Base):
    __tablename__ = 'game_full_audio_languages'

    app_id = Column(Integer, ForeignKey('games.app_id'), primary_key=True)
    language_id = Column(Integer, ForeignKey('languages.language_id'), primary_key=True)

# Indice per la relazione tra giochi e lingue audio
Index('idx_game_full_audio_language', GameFullAudioLanguage.app_id, GameFullAudioLanguage.language_id)

# Modello per gli sviluppatori (Developers)
class Developer(Base):
    __tablename__ = 'developers'

    developer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True)  # Indice per la ricerca degli sviluppatori

# Modello per le categorie (Categories)
class Category(Base):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True)  # Indice per la ricerca dei generi

# Modello per i generi (Genres)
class Genre(Base):
    __tablename__ = 'genres'

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True)  # Indice per la ricerca dei generi

# Modello per gli editori (Publishers)
class Publisher(Base):
    __tablename__ = 'publishers'

    publisher_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True)  # Indice per la ricerca degli editori

# Modello per i tag (Tags)
class Tag(Base):
    __tablename__ = 'tags'

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True)  # Indice per la ricerca dei tag

class Movie(Base):
    __tablename__ = 'movies'

    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, ForeignKey('games.app_id'))
    url = Column(String(500))
    game = relationship('Game')

# Modello per i pacchetti (Packages)
class Package(Base):
    __tablename__ = 'packages'

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, ForeignKey('games.app_id')) 
    title = Column(String(255), index=True)  # Indice per la ricerca dei pacchetti
    description = Column(Text)
    game = relationship('Game')

# Modello per gli screenshot (Screenshots)
class Screenshot(Base):
    __tablename__ = 'screenshots'

    screenshot_id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(Integer, ForeignKey('games.app_id')) 
    url = Column(String(500))
    game = relationship('Game')

# Modello per i subpacchetti (Subpackages)
class Subpackage(Base):
    __tablename__ = 'subpackages'

    subpackage_id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(Integer, ForeignKey('packages.package_id'))
    title = Column(String(255), index=True)  # Indice per la ricerca dei subpacchetti
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    package = relationship('Package')

# Tabelle intermedie per le relazioni molti a molti
class GameDeveloper(Base):
    __tablename__ = 'game_developers'

    app_id = Column(Integer, ForeignKey('games.app_id'), primary_key=True) 
    developer_id = Column(Integer, ForeignKey('developers.developer_id'), primary_key=True)

# Indici per la tabella di relazione molti a molti tra giochi e sviluppatori
Index('idx_game_developer', GameDeveloper.app_id, GameDeveloper.developer_id)
Index('idx_game_developer_app_id', GameDeveloper.app_id)
Index('idx_game_developer_developer_id', GameDeveloper.developer_id)

class GameCategory(Base):
    __tablename__ = 'game_categories'

    app_id = Column(Integer, ForeignKey('games.app_id'), primary_key=True)  
    category_id = Column(Integer, ForeignKey('categories.category_id'), primary_key=True)

# Indici per la tabella di relazione molti a molti tra giochi e generi
Index('idx_game_genre', GameCategory.app_id, GameCategory.category_id)
Index('idx_game_category_app_id', GameCategory.app_id)
Index('idx_game_category_category_id', GameCategory.category_id)


class GameGenre(Base):
    __tablename__ = 'game_genres'

    app_id = Column(Integer, ForeignKey('games.app_id'), primary_key=True)  
    genre_id = Column(Integer, ForeignKey('genres.genre_id'), primary_key=True)

# Indici per la tabella di relazione molti a molti tra giochi e generi
Index('idx_game_genre', GameGenre.app_id, GameGenre.genre_id)
Index('idx_game_genre_app_id', GameGenre.app_id)
Index('idx_game_genre_genre_id', GameGenre.genre_id)


class GamePublisher(Base):
    __tablename__ = 'game_publishers'

    app_id = Column(Integer, ForeignKey('games.app_id'), primary_key=True) 
    publisher_id = Column(Integer, ForeignKey('publishers.publisher_id'), primary_key=True)

# Indici per la tabella di relazione molti a molti tra giochi e editori
Index('idx_game_publisher', GamePublisher.app_id, GamePublisher.publisher_id)
Index('idx_game_publisher_app_id', GamePublisher.app_id)
Index('idx_game_publisher_publisher_id', GamePublisher.publisher_id)


class GameTag(Base):
    __tablename__ = 'game_tags'

    app_id = Column(Integer, ForeignKey('games.app_id'), primary_key=True) 
    tag_id = Column(Integer, ForeignKey('tags.tag_id'), primary_key=True)
    tag_value = Column(Integer)

# Indici per la tabella di relazione molti a molti tra giochi e tag
Index('idx_game_tag', GameTag.app_id, GameTag.tag_id)
Index('idx_game_tag_app_id', GameTag.app_id)
Index('idx_game_tag_tag_id', GameTag.tag_id)