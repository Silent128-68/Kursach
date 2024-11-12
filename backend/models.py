from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from base_class import Base

class DetailTypes(Base):
    __tablename__ = "detail_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    quantity = Column(Integer)

    # Связь с таблицей SchemeDetails
    schemes = relationship("SchemeDetails", back_populates="detail_type")


class Schemes(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True, index=True)
    scheme_name = Column(String, unique=True, index=True)

    # Связь с таблицей SchemeDetails
    scheme_details = relationship("SchemeDetails", back_populates="scheme", cascade="all, delete")


class SchemeDetails(Base):
    __tablename__ = "scheme_details"
    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"))
    detail_type_id = Column(Integer, ForeignKey("detail_types.id"))
    quantity = Column(Integer)

    # Связи с Schemes и DetailTypes
    scheme = relationship("Schemes", back_populates="scheme_details")
    detail_type = relationship("DetailTypes", back_populates="schemes")
