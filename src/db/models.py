from sqlalchemy import Column, String, Enum, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
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

    vacancies = relationship("VacancyModel", back_populates="employer")

    @property
    def role(self):
        return self._role.value  # Возвращаем строку

    @role.setter
    def role(self, value):
        self._role = UserRole(value)

class VacancyModel(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    employer = relationship("UserModel", back_populates="vacancies")

class ApplicationModel(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)

    applicant = relationship("UserModel")
    vacancy = relationship("VacancyModel")
