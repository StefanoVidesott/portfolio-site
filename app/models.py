from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from app.database import Base

class SkillCategory(Base):
    __tablename__ = "skill_categories"
    id = Column(Integer, primary_key=True, index=True)

    title_it = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    icon_class = Column(String, nullable=False)
    skills_list_it = Column(String, nullable=False)
    skills_list_en = Column(String, nullable=False)

    is_featured = Column(Boolean, default=True)
    order = Column(Integer, default=0)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)

    title_it = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    description_it = Column(String, nullable=False)
    description_en = Column(String, nullable=False)
    link_it = Column(String, nullable=False)
    link_en = Column(String, nullable=False)

    image_url = Column(String, nullable=False)
    url = Column(String, nullable=True)

    is_featured = Column(Boolean, default=True)
    order = Column(Integer, default=0)

class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)

    title_it = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    company = Column(String, nullable=False)

    date_it = Column(String, nullable=False)
    date_en = Column(String, nullable=False)
    location = Column(String, nullable=False)

    tasks_it = Column(JSON, nullable=False)
    tasks_en = Column(JSON, nullable=False)

    is_highlighted = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=True)
    order = Column(Integer, default=0)

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)

    title_it = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    school = Column(String, nullable=False)

    date_it = Column(String, nullable=False)
    date_en = Column(String, nullable=False)
    location = Column(String, nullable=False)

    tasks_it = Column(JSON, nullable=False)
    tasks_en = Column(JSON, nullable=False)

    is_highlighted = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=True)
    order = Column(Integer, default=0)

class Interest(Base):
    __tablename__ = "interests"
    id = Column(Integer, primary_key=True, index=True)

    title_it = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    date_it = Column(String, nullable=False)
    date_en = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description_it = Column(String, nullable=False)
    description_en = Column(String, nullable=False)
    tasks_it = Column(JSON, nullable=False)
    tasks_en = Column(JSON, nullable=False)

    is_featured = Column(Boolean, default=True)
    order = Column(Integer, default=0)

class Language(Base):
    __tablename__ = "language"
    id = Column(Integer, primary_key=True, index=True)

    title_it = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    level_it = Column(String, nullable=False)
    level_en = Column(String, nullable=False)
    icon_class = Column(String, nullable=False)

    is_featured = Column(Boolean, default=True)
    order = Column(Integer, default=0)
