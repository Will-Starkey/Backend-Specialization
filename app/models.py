
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, Integer
from typing import Optional
import datetime
import decimal

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)




# ---- Models ----

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)

    service_tickets: Mapped[list["ServiceTicket"]] = relationship(back_populates="customer")


service_ticket_inventory = Table(
    'service_ticket_inventory',
    Base.metadata,
    Column('ticket_id', Integer, ForeignKey('service_tickets.id'), primary_key=True),
    Column('inventory_id', Integer, ForeignKey('inventory.id'), primary_key=True)
)


class ServiceTicket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[datetime.date] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[Optional[str]] = mapped_column(db.String(500))
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="service_tickets")
    mechanic_assignments: Mapped[list["ServiceMechanic"]] = relationship(back_populates="ticket")
    parts: Mapped[list["Inventory"]] = relationship(secondary=service_ticket_inventory, back_populates="service_tickets")


class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    salary: Mapped[decimal.Decimal] = mapped_column(db.Numeric(10, 2), nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)

    ticket_assignments: Mapped[list["ServiceMechanic"]] = relationship(back_populates="mechanic")


class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[list["ServiceTicket"]] = relationship(secondary=service_ticket_inventory, back_populates="parts")


class ServiceMechanic(Base):
    __tablename__ = 'service_mechanics'

    ticket_id: Mapped[int] = mapped_column(ForeignKey('service_tickets.id'), primary_key=True)
    mechanic_id: Mapped[int] = mapped_column(ForeignKey('mechanics.id'), primary_key=True)

    ticket: Mapped["ServiceTicket"] = relationship(back_populates="mechanic_assignments")
    mechanic: Mapped["Mechanic"] = relationship(back_populates="ticket_assignments")