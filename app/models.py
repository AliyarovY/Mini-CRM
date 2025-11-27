from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=5)

    contacts = relationship("Contact", back_populates="operator")
    source_weights = relationship("OperatorSourceWeight", back_populates="operator")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    leads = relationship("Lead", back_populates="source")
    operator_weights = relationship("OperatorSourceWeight", back_populates="source")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    source = relationship("Source", back_populates="leads")
    contacts = relationship("Contact", back_populates="lead")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True)

    lead = relationship("Lead", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
    source = relationship("Source")


class OperatorSourceWeight(Base):
    __tablename__ = "operator_source_weights"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), index=True)
    weight = Column(Float, default=1.0)

    operator = relationship("Operator", back_populates="source_weights")
    source = relationship("Source", back_populates="operator_weights")
