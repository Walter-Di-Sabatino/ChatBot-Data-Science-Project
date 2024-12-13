from sqlalchemy.orm import Session
from database.models import *
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload


def get_game_by_name(session: Session, game_name: str):
    return session.query(Game).filter(Game.name.ilike(game_name)).first()


def get_publisher_by_game(session: Session, game_id):
    return session.query(Publisher).join(Game.publishers).filter(Game.app_id == game_id).all()

def get_developer_by_game(session: Session, game_id):
    return session.query(Developer).join(Game.developers).filter(Game.app_id == game_id).all()


def get_developers_and_publishers_by_games(session: Session, game_ids):

    if not isinstance(game_ids, list):
        game_ids = [game_ids]

    games = (
        session.query(Game)
        .filter(Game.app_id.in_(game_ids))  # Filtra per una lista di game_id
        .options(joinedload(Game.publishers), joinedload(Game.developers))
        .all()
    )
    
    # Organizza i risultati in un dizionario
    result = {}
    for game in games:
        result[game.app_id] = {
            "developers": game.developers,
            "publishers": game.publishers,
        }
    return result


def get_games_by_tag(session: Session, tag_id: int):
    return session.query(Game) \
        .join(GameTag, GameTag.app_id == Game.app_id) \
        .join(Tag, Tag.tag_id == GameTag.tag_id) \
        .filter(Tag.tag_id == tag_id) \
        .distinct() \
        .all()


def get_top_games_by_tag_and_score(session, tag_id, limit=5):
    score_expr = (
        (func.coalesce(Game.positive, 0) / func.coalesce(Game.positive + Game.negative, 1))
        * func.log(func.coalesce(Game.positive - Game.negative, 0) + 1)
    )

    return session.query(Game) \
        .join(GameTag, GameTag.app_id == Game.app_id) \
        .join(Tag, Tag.tag_id == GameTag.tag_id) \
        .filter(Tag.tag_id == tag_id) \
        .order_by(score_expr.desc()) \
        .limit(limit) \
        .all()

def get_top_games_by_publisher_and_tag(session, publisher_name, tag_name, limit=5):
    score_expr = (
        (func.coalesce(Game.positive, 0) / func.coalesce(Game.positive + Game.negative, 1))
        * func.log(func.coalesce(Game.positive - Game.negative, 0) + 1)
    )

    return (
        session.query(Game) 
        .join(Game.publishers) 
        .join(Game.tags) 
        .filter(Publisher.name.ilike(publisher_name)) 
        .filter(Tag.name.ilike(tag_name)) 
        .order_by(score_expr.desc()) 
        .limit(limit) 
        .all()
        )

def get_tag_by_name(session: Session, tag_name: str):
    return session.query(Tag).filter(Tag.name.ilike(tag_name)).first()

def get_top_tags(session: Session, limit: int = 5):
    subquery = session.query(
        GameTag.tag_id, 
        func.count(GameTag.app_id).label('game_count')
    ).group_by(GameTag.tag_id).subquery()

    return session.query(
        Tag, 
        subquery.c.game_count
    ).join(subquery, Tag.tag_id == subquery.c.tag_id) \
     .order_by(subquery.c.game_count.desc()) \
     .limit(limit) \
     .all()