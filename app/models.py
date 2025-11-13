from .database import Base
from sqlalchemy  import Column, Integer, String, ForeignKey, func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

class PostsTable(Base):
    __tablename__ = "posts"

    id = Column(Integer, autoincrement=True, primary_key=True, nullable = False)
    title = Column(String, nullable = False)
    text = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    account_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable = False)
    account = relationship("UsersTable")

class UsersTable(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True, nullable = False)
    email = Column(String,nullable = False, unique = True)
    password = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    