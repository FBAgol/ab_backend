from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, LargeBinary
from uuid import UUID, uuid4
from .engine import Base


class Company(Base):
    __tablename__ = "company"
    company_name: Mapped[str] = mapped_column(nullable=False)

    editors: Mapped[list["Editor"]] = relationship(
        "Editor", back_populates="company", cascade="all, delete-orphan"
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Editor(Base):
    __tablename__ = "editor"
    editor_email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("company.id"))
    company: Mapped["Company"] = relationship(
        "Company", back_populates="editors"
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="editor", cascade="all, delete-orphan"
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Project(Base):
    __tablename__ = "project"
    project_name: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    editor_id: Mapped[int] = mapped_column(ForeignKey("editor.id"))
    editor: Mapped["Editor"] = relationship(
        "Editor", back_populates="projects"
    )

    areas: Mapped[list["Area"]] = relationship(
        "Area", back_populates="project", cascade="all, delete-orphan"
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Area(Base):
    __tablename__ = "area"
    street: Mapped[str] = mapped_column(nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(
        "Project", back_populates="areas"
    )

    coordinates: Mapped[list["Coordinate"]] = relationship(
        "Coordinate", back_populates="area", cascade="all, delete-orphan"
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Coordinate(Base):
    __tablename__ = "coordinate"
    analyse_picture: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    area_id: Mapped[int] = mapped_column(ForeignKey("area.id"))
    area: Mapped["Area"] = relationship("Area", back_populates="coordinates")
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)
