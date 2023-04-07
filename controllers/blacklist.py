from sqlalchemy.orm import Session

from models.blacklist import Blacklist


def get_blacklist_token(db: Session, token: str):
    return db.query(Blacklist).filter(Blacklist.key == token).first()


def create_blacklist_token(db: Session, token: str):
    db_blacklist = Blacklist(key=token)
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist
