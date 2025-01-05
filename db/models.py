from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, LargeBinary, String, JSON,Integer
from uuid import UUID, uuid4
from .engine import Base


class Super_Admin(Base):
    __tablename__ = "super_admin"
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True) 
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    companys: Mapped[list["Company"]] = relationship(
        "Company", back_populates="super_admin", cascade="all, delete-orphan", init=False, lazy="selectin"
    )

    telekom_editors: Mapped[list["Telekom_Editor"]] = relationship(
        "Telekom_Editor", back_populates="super_admin", cascade="all, delete-orphan", init=False, lazy="selectin"
    )
    id: Mapped[UUID] = mapped_column( primary_key=True, default_factory=uuid4)



class Company(Base):
    __tablename__ = "company"
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    super_admin_id: Mapped[UUID] = mapped_column(ForeignKey("super_admin.id"))
    super_admin: Mapped["Super_Admin"] = relationship("Super_Admin", back_populates="companys", init=False, lazy="joined") 

    company_editors: Mapped[list["Company_Editor"]] = relationship(
        "Company_Editor", back_populates="company", cascade="all, delete-orphan", init=False, lazy="selectin"
    )
    id: Mapped[UUID] = mapped_column( primary_key=True, default_factory=uuid4)

class Company_Editor(Base):
    
    __tablename__ = "company_editor"
    company_id: Mapped[UUID] = mapped_column(ForeignKey("company.id"))
    editor_email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  
    secret_key: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    company: Mapped["Company"] = relationship("Company", back_populates="company_editors", init=False, lazy="joined")
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="company_editor", cascade="all, delete-orphan", init=False, lazy="selectin"
    )

    id: Mapped[UUID] = mapped_column( primary_key=True, default_factory=uuid4)

class Telekom_Editor(Base):
    __tablename__ = "telekom_editor"
    super_admin_id: Mapped[UUID] = mapped_column(ForeignKey("super_admin.id"))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  
    secret_key: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True, default=None) 
    super_admin: Mapped["Super_Admin"] = relationship("Super_Admin", back_populates="telekom_editors", init=False, lazy="joined")
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="telekom_editor", cascade="all, delete-orphan", init=False, lazy="selectin"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="telekom_editor", cascade="all, delete-orphan", init=False, lazy="selectin"
    )
    
    id: Mapped[UUID] = mapped_column( primary_key=True, default_factory=uuid4)

class City(Base):
    __tablename__ = "city"
    city_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="city", cascade="all, delete-orphan", init=False, lazy="selectin"
    )
    city_streets: Mapped[list["City_Street"]] = relationship(
        "City_Street", back_populates="city", cascade="all, delete-orphan", init=False,lazy="selectin"
    )

    id: Mapped[UUID] = mapped_column( primary_key=True, default_factory=uuid4)


class Project(Base):
    __tablename__ = "project"
    project_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    telekom_editor_id: Mapped[UUID] = mapped_column(ForeignKey("telekom_editor.id"))
    company_editor_id: Mapped[UUID] = mapped_column(ForeignKey("company_editor.id"))
    city_id: Mapped[UUID] = mapped_column(ForeignKey("city.id"))
    telekom_editor: Mapped["Telekom_Editor"] = relationship("Telekom_Editor",back_populates="projects", init=False, lazy="joined")
    company_editor: Mapped["Company_Editor"] = relationship("Company_Editor", back_populates="projects", init=False,lazy="joined")
    city: Mapped["City"] = relationship("City", back_populates="projects", init=False, lazy="joined")   

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Street(Base):
    __tablename__ = "street"
    street_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city_streets: Mapped[list["City_Street"]] = relationship(
        "City_Street", back_populates="street", cascade="all, delete-orphan", init=False, lazy="selectin"
    )
    coordinates: Mapped[list["Coordinate"]] = relationship(
        "Coordinate", back_populates="street", cascade="all, delete-orphan", init=False, lazy="selectin"
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class City_Street(Base):
    __tablename__ ="city_street"
    city_id: Mapped[UUID] = mapped_column(ForeignKey("city.id"))
    street_id: Mapped[UUID] = mapped_column(ForeignKey("street.id"))
    city: Mapped["City"] = relationship("City", back_populates="city_streets", init=False, lazy="joined")
    street: Mapped["Street"] = relationship("Street", back_populates="city_streets", init=False, lazy="joined")

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)


class Coordinate(Base):
    __tablename__ = "coordinate"
    
    street_id: Mapped[UUID] = mapped_column(ForeignKey("street.id"))
    zone_id: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude_longitude: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    result_materiallist: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[bytes] = mapped_column(LargeBinary, nullable=True, default=None)
    analyse_picture: Mapped[bytes] = mapped_column(LargeBinary, nullable=True, default=None)
    analyse_date: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    
    street: Mapped["Street"] = relationship("Street", back_populates="coordinates", init=False, lazy="joined")
    notification: Mapped["Notification"] = relationship(
        back_populates="coordinate", uselist=False, init=False, lazy="joined"
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)

    

class Notification(Base):
    __tablename__ = "notification"
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    coordinate_id: Mapped[UUID] = mapped_column(ForeignKey("coordinate.id"))
    telekom_editor_id: Mapped[UUID] = mapped_column(ForeignKey("telekom_editor.id"))
    coordinate: Mapped[Coordinate] = relationship("Coordinate", back_populates="notification", init=False, lazy="joined")
    telekom_editor: Mapped["Telekom_Editor"] = relationship("Telekom_Editor", back_populates="notifications", init=False, lazy="joined")

    id: Mapped[UUID] = mapped_column( primary_key=True, default_factory=uuid4)


