from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cuenta(Base):
    __tablename__ = 'cuentas'
    id = Column(Integer, primary_key=True, index=True)
    #nombre = Column(String(150, collation="Latin1_General_CI_AI"), nullable=False, index=True) # Probar en SQL Server - Es case y tildes insensitive
    nombre = Column(String(150, collation="NOCASE"), nullable=False, index=True)
    cuenta = Column(String(20), nullable=False)
    nivel = Column(Integer, nullable=False)
    path = Column(String(500), nullable=False)
    path_padre = Column(String(500), nullable=True)
    cuenta_minima = Column(Boolean, nullable=False)
    sinonimos = relationship("Sinonimo", back_populates="cuenta")

class Sinonimo(Base):
    __tablename__ = 'sinonimos'
    id = Column(Integer, primary_key=True, index=True)
    cuenta_id = Column(Integer, ForeignKey('cuentas.id'))
    #nombre = Column(String(150, collation="Latin1_General_CI_AI"), nullable=False, index=True) # Probar en SQL Server - Es case y tildes insensitive
    nombre = Column(String(150, collation="NOCASE"), nullable=False, index=True) # Solo valido en SQLite
    cuenta = relationship("Cuenta", back_populates="sinonimos")