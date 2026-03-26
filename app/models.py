from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.database import Base


class SkillCategory(Base):
    __tablename__ = "skill_categories"
    id = Column(Integer, primary_key=True, index=True)

    icon_class = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "4"})
    order = Column(Integer, default=0, info={"type": "number", "group": "general-data", "size": "4"})
    is_featured = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "4"})

    title_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "12"})
    skills_list_it = Column(String, nullable=False, info={"type": "textarea", "group": "it", "size": "12"})

    title_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "12"})
    skills_list_en = Column(String, nullable=False, info={"type": "textarea", "group": "en", "size": "12"})


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)

    slug = Column(String, unique=True, index=True, nullable=False, info={"type": "text", "group": "general-data", "size": "4"})
    order = Column(Integer, default=0, info={"type": "number", "group": "general-data", "size": "4"})
    is_featured = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "2"})
    is_case_study = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "2"})

    image_url = Column(String, nullable=False, info={"type": "image_upload", "group": "general-data", "size": "6"})
    url = Column(String, nullable=True, info={"type": "text", "group": "general-data", "size": "6"})
    # If set, overrides `url` and opens an internal detail page at /{lang}{internal_url}
    internal_url = Column(String, nullable=True, info={"type": "text", "group": "general-data", "size": "6"})
    # Comma-separated tech stack tags displayed on the project card
    tags = Column(String, nullable=True, info={"type": "text", "group": "general-data", "size": "12"})

    title_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    link_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    description_it = Column(String, nullable=False, info={"type": "textarea", "group": "it", "size": "12"})

    title_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    link_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    description_en = Column(String, nullable=False, info={"type": "textarea", "group": "en", "size": "12"})


class Experience(Base):
    __tablename__ = "experiences"
    id = Column(Integer, primary_key=True, index=True)

    company = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "6"})
    location = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "6"})

    order = Column(Integer, default=0, info={"type": "number", "group": "general-data", "size": "4"})
    is_featured = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "4"})
    is_highlighted = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "4"})

    title_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    date_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    tasks_it = Column(JSON, nullable=False, info={"type": "textarea", "group": "it", "size": "12"})

    title_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    date_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    tasks_en = Column(JSON, nullable=False, info={"type": "textarea", "group": "en", "size": "12"})


class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True, index=True)

    school = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "6"})
    location = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "6"})

    order = Column(Integer, default=0, info={"type": "number", "group": "general-data", "size": "4"})
    is_featured = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "4"})
    is_highlighted = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "4"})

    title_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    date_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    tasks_it = Column(JSON, nullable=False, info={"type": "textarea", "group": "it", "size": "12"})

    title_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    date_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    tasks_en = Column(JSON, nullable=False, info={"type": "textarea", "group": "en", "size": "12"})


class Interest(Base):
    __tablename__ = "interests"
    id = Column(Integer, primary_key=True, index=True)

    organization = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "6"})
    location = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "6"})

    order = Column(Integer, default=0, info={"type": "number", "group": "general-data", "size": "6"})
    is_featured = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "6"})

    title_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    date_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    description_it = Column(String, nullable=False, info={"type": "textarea", "group": "it", "size": "12"})
    tasks_it = Column(JSON, nullable=False, info={"type": "textarea", "group": "it", "size": "12"})

    title_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    date_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    description_en = Column(String, nullable=False, info={"type": "textarea", "group": "en", "size": "12"})
    tasks_en = Column(JSON, nullable=False, info={"type": "textarea", "group": "en", "size": "12"})


class Language(Base):
    __tablename__ = "language"
    id = Column(Integer, primary_key=True, index=True)

    icon_class = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "4"})
    order = Column(Integer, default=0, info={"type": "number", "group": "general-data", "size": "4"})
    is_featured = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "4"})

    title_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})
    level_it = Column(String, nullable=False, info={"type": "text", "group": "it", "size": "6"})

    title_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})
    level_en = Column(String, nullable=False, info={"type": "text", "group": "en", "size": "6"})


class OpenToWork(Base):
    """Singleton-style table — always use .first(). is_enabled controls site visibility."""
    __tablename__ = "open_to_work"
    id = Column(Integer, primary_key=True, index=True)

    is_enabled = Column(Boolean, default=False, info={"type": "checkbox", "group": "general-data", "size": "12"})

    badge_it = Column(String, nullable=True, info={"type": "text", "group": "it", "size": "12"})
    title_it = Column(String, nullable=True, info={"type": "text", "group": "it", "size": "12"})
    message_it = Column(String, nullable=True, info={"type": "textarea", "group": "it", "size": "12"})

    badge_en = Column(String, nullable=True, info={"type": "text", "group": "en", "size": "12"})
    title_en = Column(String, nullable=True, info={"type": "text", "group": "en", "size": "12"})
    message_en = Column(String, nullable=True, info={"type": "textarea", "group": "en", "size": "12"})


class CVDocument(Base):
    """One record per language (lang='it' or lang='en'), holding the current CV file URL."""
    __tablename__ = "cv_documents"
    id = Column(Integer, primary_key=True, index=True)

    lang = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "4"})
    label = Column(String, nullable=False, info={"type": "text", "group": "general-data", "size": "8"})
    file_url = Column(String, nullable=False, info={"type": "pdf_upload", "group": "general-data", "size": "12"})
