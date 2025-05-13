from sqlalchemy import Column, String, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
import enum


Base = declarative_base()

class UserRole(enum.Enum):
    APPLICANT = "соискатель"
    EMPLOYER = "работодатель"

class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    _role = Column("role", Enum(UserRole, native_enum=True))  # Храним как ENUM

    @property
    def role(self):
        return self._role.value  # Возвращаем строку

    @role.setter
    def role(self, value):
        self._role = UserRole(value)
