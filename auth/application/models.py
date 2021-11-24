from sqlalchemy import Column, DateTime, Integer, String, TEXT, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import bcrypt
from . import Session
from sqlalchemy import event

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    update_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        fields = ""
        for c in self.__table__.columns:
            if fields == "":
                fields = "{}='{}'".format(c.name, getattr(self, c.name))
            else:
                fields = "{}, {}='{}'".format(fields, c.name, getattr(self, c.name))
        return "<{}({})>".format(self.__class__.__name__, fields)

    @staticmethod
    def list_as_dict(items):
        return [i.as_dict() for i in items]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Client(BaseModel):
    
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    username = Column(String(256), nullable=False, default="Unknown")
    password = Column(String(256), nullable=False, default="123123")
    role = Column(String(256), nullable=False, default="operator")
    refresh_token = Column(String(256), nullable=False, default=" ")


@event.listens_for(Client.__table__, 'after_create')
def create_admin(*args, **kwargs):
    session = Session()
    session.add(Client(username='admin', password=bcrypt.hashpw('admin'.encode(), bcrypt.gensalt()).decode('utf-8'), role='admin', refresh_token=' '))
    session.commit()
    session.close()
