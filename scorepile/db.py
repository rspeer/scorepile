from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_config import DB_CONFIG
ENGINE = create_engine(
    "postgresql://{username}:{password}@{host}/innovationgames"
    .format(**DB_CONFIG)
)
Session = sessionmaker(bind=ENGINE)

