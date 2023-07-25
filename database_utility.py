from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from news import search_keyword

# from flask_sqlalchemy import SQLAlchemy


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

# Class for storing user settings/preferences 
class User_Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    language = Column(String, nullable=False)
    nation = Column(String, nullable=False)
    source = Column(String, nullable=False)


# User class: holds table data for registered users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    lang = Column(String, nullable=True)
    nation = Column(String, nullable=True)
    source = Column(String, nullable=True)

    tracked_articles = relationship('TrackedArticle', back_populates='user')

    tracked_topics = relationship('TrackedTopic', back_populates='user')

    bookmarks = relationship('Bookmark', back_populates='user')

    searches = relationship('Search', back_populates='user')



# create all tables
Base.metadata.create_all(engine)

def add_settings(username, language, nation, source):
    session = start_session()
    
    with session as session:
        user = session.query(User).filter_by(username=username).first()

        user.lang = language
        user.nation = nation
        user.source = source
        session.commit()

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

def add_bookmark(username, url, title, topic = None, description = None, thumbnail = None):
    session = start_session()

    existing_bookmark = session.query(Bookmark).filter_by(username=username, url=url).first()
    
    if existing_bookmark:
        return False
    
    num_rows = session.query(Bookmark).filter(Bookmark.username == username).count()
    if num_rows > 10:
        return False

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
    
    return True

# Adds search result to search result database specific to the user
# Limited to 5 searches at a time, deletes last entry and replaces it with most recent search otherwise
def add_search(username, phrase):
    session = start_session()
    user = session.query(User).filter_by(username=username).first()
    num_rows = session.query(Search).filter(Search.user == user).count()
    new_search = Search(
        username = username,
        phrase = phrase
    )

    with session as session:
        if num_rows < 5:
            session.add(new_search)
            session.commit()
        elif num_rows == 5:
            oldest_search = session.query(Search).filter(Search.user == user).order_by(Search.id).first()
            session.delete(oldest_search)
            session.add(new_search)
            session.commit()

# Adds topic to tracked topic database specific to the user
# Capped at 5 tracked topics, otherwise no more topics are added to the database
def add_topic(username, topic, nation = None, language = 'en', update_interval = 1, source = None):
    session = start_session()
    user = session.query(User).filter_by(username=username).first()
    num_rows = session.query(TrackedTopic).filter(TrackedTopic.user == user).count()
    new_topic = TrackedTopic(
        username = username,
        topic = topic,
        nation = nation,
        language = language,
        update_interval = update_interval,
        source = source
        )
    
    # Check if the topic already exists for the user
    existing_topic = session.query(TrackedTopic).filter_by(user=user, topic=topic).first()

    if existing_topic:
        return False

    with session as session:
        if num_rows < 5:
            session.add(new_topic)
            session.commit()

            return True

        # Else flash that the max number of tracked topics exceeded
        elif num_rows == 5:
            return False

def add_user(username, email, password, language='en', nation='us', source=None):
    metadata = MetaData()
    metadata.clear()
    session = start_session()
    new_user = User(
        username = username, 
        email = email, 
        password = password,
        lang = language,
        nation = nation,
        source = source
    )
    
    with session as session:
        session.add(new_user)
        session.commit()

def check_value_exists(table, column, value):
    session = start_session()

    with session as session:
        query = select(table).where(column == value)
        result = session.execute(query).first()

    return result is not None

def clear_recent_searches(username):
    session = start_session()
    with session as session:
        session.query(Search).filter(Search.username == username).delete()
        session.commit()

# get first few articles for topic previews
def get_topic_articles(username, topic, preview = False):
    session = start_session()

    with session as session:
        topic = session.query(TrackedTopic).filter_by(username=username, topic=topic).first()

        if preview:
            tracked_articles = topic.tracked_articles[:3]
        
        else:
            tracked_articles = topic.tracked_articles
    
    return tracked_articles

# Retrieves a user's 5 most recent searches
def get_recent_searches(username):
    session = start_session()

    searches = None

    with session as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            searches = user.searches[::-1]
    return searches

def get_tracked_articles(username):
    session = start_session()

    tracked_articles = None

    with session as session:
        user = session.query(User).filter_by(username=username).first()

        if user:
            tracked_articles = user.tracked_articles
    
    return tracked_articles

def get_tracked_topics(username):
    session = start_session()

    tracked_topics = None

    with session as session:
        user = session.query(User).filter_by(username=username).first()

        if user:
            tracked_topics = user.tracked_topics
    
    return tracked_topics

def get_bookmarks(username):
    session = start_session()

    bookmarks = None

    with session as session:
        user = session.query(User).filter_by(username=username).first()

        if user:
            bookmarks = user.bookmarks
    
    return bookmarks

def get_user_info(username):
    session = start_session()

    with session as session:
        info = session.query(User).filter_by(username=username).first()
    
    return info

def get_user_settings(username):
    session = start_session()

    with session as session:
        settings = session.query(User_Settings).filter_by(username=username).first()
    
    return settings

def remove_bookmark(username, url):
    session = start_session()

    with session as session:
        session.query(Bookmark).filter_by(username=username, url=url).delete()
        session.commit()

def remove_topic(username, topic):
    session = start_session()

    with session as session:
        removed_topic = session.query(TrackedTopic).filter_by(topic=topic, username=username).first()

        if removed_topic: 
            session.query(TrackedArticle).filter_by(topic=topic, username=username).delete()

            session.delete(removed_topic)

            session.commit()


# starts session, enabling database interaction
def start_session():
    Session = sessionmaker(bind=engine)
    return Session()

def update_tracked_topics():
    session = start_session()

    with session as session:
        topics = session.query(TrackedTopic).all()

        session.query(TrackedArticle).delete()

        session.commit()

        for topic in topics:
                topic_name = topic.topic
                username = topic.username

                new_articles = search_keyword(topic_name)

                for article in new_articles:
                    add_article(username, topic_name, article['url'], article['title'], 
                                article['description'], article['urlToImage'])

        session.commit()

    with session as session:           
        
        
        session.commit()