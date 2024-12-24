from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, LargeBinary, String, Integer
from uuid import UUID, uuid4
from .engine import Base


class Super_Admin(Base):
    __tablename__ = "super_admin"
    email: Mapped[str] = mapped_column(String(255), nullable=False) 
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    company_editors: Mapped[list["Company_Editor"]] = relationship(
        "Company_Editor", back_populates="super_admin", cascade="all, delete-orphan"
    )

    telekom_editors: Mapped[list["Telekom_Editor"]] = relationship(
        "Telekom_Editor", back_populates="super_admin", cascade="all, delete-orphan"
    )
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))

class Company(Base):
    __tablename__ = "company"
    company_name: Mapped[str] = mapped_column(String(255), nullable=False) 

    company_editors: Mapped[list["Company_Editor"]] = relationship(
        "Company_Editor", back_populates="company", cascade="all, delete-orphan"
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="company", cascade="all, delete-orphan"
    )
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))

class Company_Editor(Base):
    __tablename__ = "company_editor"
    editor_email: Mapped[str] = mapped_column(String(255), nullable=False)  
    password: Mapped[str] = mapped_column(String(255), nullable=False) 
    secret_key: Mapped[str] = mapped_column(String(255), nullable=False)
    super_admin_id: Mapped[UUID] = mapped_column(ForeignKey("super_admin.id"))
    company_id: Mapped[UUID] = mapped_column(ForeignKey("company.id"))
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))

class Telekom_Editor(Base):
    __tablename__ = "telekom_editor"
    email: Mapped[str] = mapped_column(String(255), nullable=False)  
    password: Mapped[str] = mapped_column(String(255), nullable=False) 
    secret_key: Mapped[str] = mapped_column(String(255), nullable=False)
    super_admin_id: Mapped[UUID] = mapped_column(ForeignKey("super_admin.id"))
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="telekom_editor", cascade="all, delete-orphan"
    )
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))

class City(Base):
    __tablename__ = "city"
    city_name: Mapped[str] = mapped_column(String(255), nullable=False)
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="city", cascade="all, delete-orphan"
    )
    city_streets: Mapped[list["City_Street"]] = relationship(
        "City_Street", back_populates="city", cascade="all, delete-orphan"
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))


class Project(Base):
    __tablename__ = "project"
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("company.id"))
    telekom_editor_id: Mapped[UUID] = mapped_column(ForeignKey("telekom_editor.id"))
    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"))

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))


class Street(Base):
    __tablename__ = "street"
    street_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city_streets: Mapped[list["City_Street"]] = relationship(
        "City_Street", back_populates="street", cascade="all, delete-orphan"
    )
    Coordinates: Mapped[list["Coordinate"]] = relationship(
        "Coordinate", back_populates="street", cascade="all, delete-orphan"
    )
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))

class City_Street(Base):
    __tablename__ ="city_street"
    city_id: Mapped[UUID] = mapped_column(ForeignKey("city.id"))
    street_id: Mapped[UUID] = mapped_column(ForeignKey("street.id"))
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))


class Coordinate(Base):
    __tablename__ = "coordinate"
    coord_number: Mapped[int] = mapped_column(Integer, nullable=False)
    analyse_picture: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    result_materiallist: Mapped[str] = mapped_column(String(255), nullable=False)
    analyse_date: Mapped[str] = mapped_column(String(255), nullable=False)
    target_material: Mapped[str] = mapped_column(String(255), nullable=False)
    street_id: Mapped[UUID] = mapped_column(ForeignKey("street.id"))

    notification: Mapped["Notification"] = relationship(
        back_populates="coordinate", uselist=False
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))

class Notification(Base):
    __tablename__ = "notification"
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    coordinate_id: Mapped[str] = mapped_column(ForeignKey("coordinate.id"), unique=True)
    telekom_editor_id: Mapped[UUID] = mapped_column(ForeignKey("telekom_editor.id"))
    coordinate: Mapped[Coordinate] = relationship(back_populates="notification")

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid4()))


