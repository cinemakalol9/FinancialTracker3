from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create database engine
engine = create_engine('sqlite:///stock_data.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class StockPrice(Base):
    """Model for storing historical stock prices"""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    # Index for faster queries
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'date'),
    )

class StockInfo(Base):
    """Model for storing company information"""
    __tablename__ = 'stock_info'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    company_name = Column(String)
    sector = Column(String)
    industry = Column(String)
    market_cap = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session"""
    return Session()
