from sqlalchemy.orm import Session
from database.models import *
from sqlalchemy import func, case


def get_game_by_name(session: Session, game_name: str):
    return session.query(Game).filter(Game.name.ilike(game_name)).first()

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


def get_tag_by_name(session: Session, tag_name: str):
    return session.query(Tag).filter(Tag.name.ilike(tag_name)).first()

def get_top_tags(session: Session):
    return session.query(
        Tag, 
        func.count(GameTag.app_id).label('game_count')
            ).join(GameTag, Tag.tag_id == GameTag.tag_id) \
            .group_by(Tag.tag_id) \
            .order_by(func.count(GameTag.app_id).desc()).all()


def get_developers_by_game(session: Session, app_id: int):
    return session.query(Developer) \
        .join(GameDeveloper, GameDeveloper.developer_id == Developer.developer_id) \
        .join(Game, Game.app_id == GameDeveloper.app_id) \
        .filter(Game.app_id == app_id) \
        .distinct() \
        .all()
