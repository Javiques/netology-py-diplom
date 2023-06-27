from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from core import Viewed

class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def add_viewed_profile(self, profile_id, worksheet_id):
        session = self.Session()
        viewed = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(viewed)
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def check_profile_viewed(self, profile_id):
        session = self.Session()
        viewed = session.query(Viewed).filter(Viewed.profile_id == profile_id).first()
        session.close()
        return viewed is not None
