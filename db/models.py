from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, LargeBinary, String
from uuid import UUID, uuid4
from .engine import Base

class Company(Base):
    __tablename__ = "company"
    company_name: Mapped[str] = mapped_column(String(255), nullable=False) 

    editors: Mapped[list["Editor"]] = relationship(
        "Editor", back_populates="company", cascade="all, delete-orphan"
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Editor(Base):
    __tablename__ = "editor"
    editor_email: Mapped[str] = mapped_column(String(255), nullable=False)  
    password: Mapped[str] = mapped_column(String(255), nullable=False) 
    company_id: Mapped[UUID] = mapped_column(ForeignKey("company.id"))
    company: Mapped["Company"] = relationship(
        "Company", back_populates="editors"
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="editor", cascade="all, delete-orphan"
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)

class City(Base):
    __tablename__ = "city"
    city_name: Mapped[str] = mapped_column(String(255), nullable=False)
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="city"
    )
    city_streets: Mapped[list["City_street"]] = relationship(
        "City_street", back_populates="city", cascade="all, delete-orphan"
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4) 

class Project(Base):
    __tablename__ = "project"
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    editor_id: Mapped[int] = mapped_column(ForeignKey("editor.id"))
    editor: Mapped["Editor"] = relationship(
        "Editor", back_populates="projects"
    )
    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"))
    city: Mapped["City"] = relationship("City", back_populates="projects")

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)




class Street(Base):
    __tablename__ = "street"
    street_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city_streets: Mapped[list["City_street"]] = relationship(
        "City_street", back_populates="street"
    )
    Coordinates: Mapped[list["Coordinate"]] = relationship("Coordinate", back_populates="street", cascade="all, delete-orphan")
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)

class City_street(Base):
    __tablename__ ="city_street"
    city_name: Mapped[str] = mapped_column(String(255), nullable=False)
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="city", cascade="all, delete-orphan"
    )
    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"))
    city: Mapped["City"] = relationship("City", back_populates="city_streets")
    street_id: Mapped[int] = mapped_column(ForeignKey("street.id"))
    street: Mapped["Street"] = relationship("Street", back_populates="city_streets")
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Coordinate(Base):
    __tablename__ = "coordinate"
    analyse_picture: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    street_id: Mapped[int] = mapped_column(ForeignKey("street.id"))
    street: Mapped["Street"] = relationship("Street", back_populates="Coordinates")
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)
