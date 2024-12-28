from sqlalchemy import or_
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

def get_top_games(session, limit=5):
    score_expr = (
        (func.coalesce(Game.positive, 0) / func.coalesce(Game.positive + Game.negative, 1))
        * func.log(func.coalesce(Game.positive - Game.negative, 0) + 1)
    )

    query = session.query(Game)

    return query.order_by(score_expr.desc()).limit(limit).all()

def get_top_games_filtered(session, publisher_names=None, tag_names=None, limit=5):
    score_expr = (
        (func.coalesce(Game.positive, 0) / func.coalesce(Game.positive + Game.negative, 1))
        * func.log(func.coalesce(Game.positive - Game.negative, 0) + 1)
    )

    query = session.query(Game)

    # Aggiungi il join con Publisher se ci sono publisher_names
    if publisher_names:
        query = query.join(Game.publishers).filter(
            or_(*[Publisher.name.ilike(publisher_name) for publisher_name in publisher_names])
        )

    # Aggiungi il join con Tag se ci sono tag_names
    if tag_names:
        query = query.join(Game.tags).filter(
            or_(*[Tag.name.ilike(tag_name) for tag_name in tag_names])
        )

    return query.order_by(score_expr.desc()).limit(limit).all()
