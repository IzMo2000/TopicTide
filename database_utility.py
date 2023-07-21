from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Create a SQLite database engine
engine = create_engine('sqlite:///topic_tide.db')
Base = declarative_base()

# Bookmarks class: holds articles to be saved for later
class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'), nullable=False)
    topic = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    thumbnail = Column(String)
    user = relationship('User', back_populates='bookmarks')


#Search class: holds data table for user searches
class Search(Base):
    __tablename__ = 'searches'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'), nullable=False)
    phrase = Column(String, nullable=False)
    user = relationship('User', back_populates='searches')

# Tracked Articles class: holds table data for tracked articles
class TrackedArticle(Base):
    __tablename__ = 'tracked_articles'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'), nullable=False)
    topic = Column(String, ForeignKey('tracked_topics.topic'),nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    thumbnail = Column(String)

    user = relationship('User', back_populates='tracked_articles')

    tracked_topics = relationship('TrackedTopic', back_populates='tracked_articles')

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

    tracked_articles = relationship('TrackedArticle', back_populates='tracked_topics')

# User class: holds table data for registered users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    tracked_articles = relationship('TrackedArticle', back_populates='user')

    tracked_topics = relationship('TrackedTopic', back_populates='user')

    bookmarks = relationship('Bookmark', back_populates='user')

    searches = relationship('Search', back_populates='user')



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

def add_bookmark(username, topic, url, title, description = None, thumbnail = None):
    session = start_session()
    new_bookmark = Bookmark(
        username = username,
        topic = topic,
        url = url,
        title = title,
        description = description,
        thumbnail = thumbnail
    )

    with session as session:
        session.add(new_bookmark)
        session.commit()

# Adds search result to search result database specific to the user
# Limited to 5 searches at a time, deletes last entry and replaces it with most recent search otherwise
def add_search(username, phrase):
    session = start_session()
    num_rows = session.query(Search).count()
    new_search = Search(
        username = username,
        phrase = phrase
    )
    with session as session:
        if num_rows < 5:
            session.add(new_search)
            session.commit()
        elif num_rows == 5:
            session.add(new_search)
            last_item = session.query(Search).order_by(Search.id.desc()).first()
            session.delete(last_item)
            session.commit()

# Adds topic to tracked topic database specific to the user
# Capped at 5 tracked topics, otherwise no more topics are added to the database
def add_topic(username, topic, nation = None, language = 'en', update_interval = 1, source = None):
    session = start_session()
    num_rows = session.query(TrackedTopic).count()
    new_topic = TrackedTopic(
        username = username,
        topic = topic,
        nation = nation,
        language = language,
        update_interval = update_interval,
        source = source
        )

    with session as session:
        if num_rows < 5:
            session.add(new_topic)
            session.commit()
            return True

        # Else flash that the max number of tracked topics exceeded
        elif num_rows == 5:
            return False

def add_user(username, email, password):
    session = start_session()
    new_user = User(username = username, email = email, password = password)

    with session as session:
        session.add(new_user)
        session.commit()

def check_value_exists(table, column, value):
    session = start_session()

    with session as session:
        query = select(table).where(column == value)
        result = session.execute(query).first()

    return result is not None

# Retrieves a user's 5 most recent searches
def get_recent_searches(username):
    session = start_session()
    with session as session:
        user = session.query(User).filter_by(username=username).first()
        searches = user.searches
    return searches

def get_tracked_articles(username):
    session = start_session()

    with session as session:
        user = session.query(User).filter_by(username=username).first()

        tracked_articles = user.tracked_articles
    
    return tracked_articles

def get_bookmarks(username):
    session = start_session()

    with session as session:
        user = session.query(User).filter_by(username=username).first()

        bookmarks = user.bookmarks
    
    return bookmarks

def get_user_info(username):
    session = start_session()

    with session as session:
        info = session.query(User).filter_by(username=username).first()
    
    return info

def remove_bookmark(id):
    session = start_session()

    with session as session:
        session.query(Bookmark).filter_by(id=id).delete()
        session.commit()

def remove_topic(id):
    session = start_session()

    with session as session:
        removed_topic = session.query(TrackedTopic).filter_by(id=id)

        remove_topic.tracked_articles.delete()

        remove_topic.delete()

        session.commit()


# starts session, enabling database interaction
def start_session():
    Session = sessionmaker(bind=engine)
    return Session()
