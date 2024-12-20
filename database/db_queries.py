from sqlalchemy.orm import Session
from database.models import *
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload

def get_all_tag_names(session: Session):
    return session.query(Tag.name).all()

def get_all_publisher_names(session: Session):
    return session.query(Publisher.name).all()

def get_game_by_name(session: Session, game_name: str):
    return session.query(Game).filter(Game.name.ilike(game_name)).first()

def get_top_publishers(session: Session):
    return (
    session.query(Publisher, func.count(GamePublisher.app_id).label('game_count'))
    .join(GamePublisher, GamePublisher.publisher_id == Publisher.publisher_id)
    .group_by(Publisher.publisher_id)
    .order_by(func.count(GamePublisher.app_id).desc())
    .all()
)

def get_top_tags(session: Session):
    return (
    session.query(Tag, func.count(GameTag.app_id).label('game_count'))
    .join(GameTag, GameTag.tag_id == Tag.tag_id)
    .group_by(Tag.tag_id)
    .order_by(func.count(GameTag.app_id).desc())
    .all()
)

def get_top_games_by_publisher_and_tag(session, publisher_name, tag_name, limit=5):
    score_expr = (
        (func.coalesce(Game.positive, 0) / func.coalesce(Game.positive + Game.negative, 1))
        * func.log(func.coalesce(Game.positive - Game.negative, 0) + 1)
    )

    query = session.query(Game).join(Game.publishers).join(Game.tags)

    if publisher_name:
        query = query.filter(Publisher.name.ilike(publisher_name))
    if tag_name:
        query = query.filter(Tag.name.ilike(tag_name))

    return query.order_by(score_expr.desc()).limit(limit).all()

def get_top_games_by_publisher(session, publisher_name, limit=5):
    score_expr = (
        (func.coalesce(Game.positive, 0) / func.coalesce(Game.positive + Game.negative, 1))
        * func.log(func.coalesce(Game.positive - Game.negative, 0) + 1)
    )

    return (
        session.query(Game) 
        .join(Game.publishers) 
        .filter(Publisher.name.ilike(publisher_name)) 
        .order_by(score_expr.desc()) 
        .limit(limit) 
        .all()
        )