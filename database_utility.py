from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Create a SQLite database engine
engine = create_engine('sqlite:///topic_tide.db')
Base = declarative_base()

# User class: holds table data for registered users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    tracked_articles = relationship('TrackedArticle', back_populates='user')

    tracked_topics = relationship('TrackedTopic', back_populates='user')

# Tracked Articles class: holds table data for tracked articles
class TrackedArticle(Base):
    __tablename__ = 'tracked_articles'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'), nullable=False)
    topic = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    thumbnail = Column(String)

    user = relationship('User', back_populates='tracked_articles')

# Tracked Topics class: holds table data for tracked Topics
class TrackedTopic(Base):
    __tablename__ = 'tracked_topics'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'), nullable=False)
    topic = Column(String, nullable=False)
    nation = Column(String)
    language = Column(String, nullable=False)
    update_interval = Column(Integer, nullable=False)
    source = Column(String)

    user = relationship('User', back_populates='tracked_topics')

# create all tables
Base.metadata.create_all(engine)

def add_article(username, topic, url, title, description = None, thumbnail = None):
    session = start_session()
    new_article = TrackedArticle(
        username = username,
        topic = topic,
        url = url,
        title = title,
        description = description,
        thumbnail = thumbnail
    )

    with session as session:
        session.add(new_article)
        session.commit()

def add_topic(username, topic, nation = None, language = 'en', update_interval = 1, source = None):
    session = start_session()
    new_topic = TrackedTopic(
        username = username, 
        topic = topic,
        nation = nation,
        language = language,
        update_interval = update_interval,
        source = source
        )

    with session as session:
        session.add(new_topic)
        session.commit()

def add_user(username, email, password):
    session = start_session()
    new_user = User(username = username, email = email, password = password)

    with session as session:
        session.add(new_user)
        session.commit()

def get_tracked_articles(username):
    session = start_session()

    with session as session:
        user = session.query(User).filter_by(username=username).first()

        tracked_articles = user.tracked_articles
    
    return tracked_articles

def get_user_info(username):
    session = start_session()

    with session as session:
        info = session.query(User).filter_by(username=username).first()
    
    return info


# starts session, enabling database interaction
def start_session():
    Session = sessionmaker(bind=engine)
    return Session()