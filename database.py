import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

metadata = MetaData()
Base = declarative_base()


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


engine = create_engine(db_url_object)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

to_db = Viewed(profile_id=1, worksheet_id=1)
session.add(to_db)
session.commit()

from_db = session.query(Viewed).filter(Viewed.profile_id == 1).all()
for item in from_db:
    print(item.worksheet_id)
