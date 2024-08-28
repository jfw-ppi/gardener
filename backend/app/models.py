from typing import Optional, List

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel

Base = declarative_base()


class Plant(Base):
    __tablename__ = "plants"

    EcoPortCode = Column(Integer, primary_key=True, index=True, nullable=False)
    ScientificName = Column(String, nullable=False, index=True)
    AUTH = Column(String, nullable=True)
    FAMNAME = Column(String, nullable=True)
    SYNO = Column(String, nullable=True)
    COMNAME = Column(String, nullable=True)
    LIFO = Column(String, nullable=True)
    HABI = Column(String, nullable=True)
    LISPA = Column(String, nullable=True)
    PHYS = Column(String, nullable=True)
    CAT = Column(String, nullable=True)
    PLAT = Column(String, nullable=True)
    TOPMN = Column(Float, nullable=False)  # Optimal minimum temperature
    TOPMX = Column(Float, nullable=False)  # Optimal maximum temperature
    TMIN = Column(Float, nullable=False)  # Absolute minimum temperature
    TMAX = Column(Float, nullable=False)  # Absolute maximum temperature
    ROPMN = Column(Float, nullable=False)  # Optimal minimum rainfall
    ROPMX = Column(Float, nullable=False)  # Optimal maximum rainfall
    RMIN = Column(Float, nullable=False)  # Absolute minimum rainfall
    RMAX = Column(Float, nullable=False)  # Absolute maximum rainfall
    KTMP = Column(Float, nullable=False)  # Killing temperature
    GMIN = Column(Float, nullable=False)  # Minimum crop cycle
    GMAX = Column(Float, nullable=False)  # Maximum crop cycle
    LATOPMN = Column(Float, nullable=True)
    LATOPMX = Column(Float, nullable=True)
    LATMN = Column(Float, nullable=True)
    LATMX = Column(Float, nullable=True)
    ALTMX = Column(Float, nullable=True)
    LIOPMN = Column(String, nullable=True)
    LIOPMX = Column(String, nullable=True)
    LIMN = Column(String, nullable=True)
    LIMX = Column(String, nullable=True)
    DEP = Column(String, nullable=True)
    DEPR = Column(String, nullable=True)
    TEXT = Column(String, nullable=True)
    TEXTR = Column(String, nullable=True)
    FER = Column(String, nullable=True)
    FERR = Column(String, nullable=True)
    TOX = Column(String, nullable=True)
    TOXR = Column(String, nullable=True)
    SAL = Column(String, nullable=True)
    SALR = Column(String, nullable=True)
    DRA = Column(String, nullable=True)
    DRAR = Column(String, nullable=True)
    KTMPR = Column(Float, nullable=True)
    PHOTO = Column(String, nullable=True)
    CLIZ = Column(String, nullable=True)
    ABITOL = Column(String, nullable=True)
    ABISUS = Column(String, nullable=True)
    INTRI = Column(String, nullable=True)
    PROSY = Column(String, nullable=True)


class PlantResponse(BaseModel):
    EcoPortCode: int
    ScientificName: str
    AUTH: Optional[str]
    FAMNAME: Optional[str]
    SYNO: Optional[str]
    COMNAME: Optional[str]
    LIFO: Optional[str]
    HABI: Optional[str]
    LISPA: Optional[str]
    PHYS: Optional[str]
    CAT: Optional[str]
    PLAT: Optional[str]
    TOPMN: float
    TOPMX: float
    TMIN: float
    TMAX: float
    ROPMN: float
    ROPMX: float
    RMIN: float
    RMAX: float
    KTMP: float
    GMIN: float
    GMAX: float
    LATOPMN: Optional[float] = None
    LATOPMX: Optional[float] = None
    LATMN: Optional[float] = None
    LATMX: Optional[float] = None
    ALTMX: Optional[float] = None
    LIOPMN: Optional[str] = None
    LIOPMX: Optional[str] = None
    LIMN: Optional[str] = None
    LIMX: Optional[str] = None
    DEP: Optional[str] = None
    DEPR: Optional[str] = None
    TEXT: Optional[str] = None
    TEXTR: Optional[str] = None
    FER: Optional[str] = None
    FERR: Optional[str] = None
    TOX: Optional[str] = None
    TOXR: Optional[str] = None
    SAL: Optional[str] = None
    SALR: Optional[str] = None
    DRA: Optional[str] = None
    DRAR: Optional[str] = None
    KTMPR: Optional[float] = None
    PHOTO: Optional[str] = None
    CLIZ: Optional[str] = None
    ABITOL: Optional[str] = None
    ABISUS: Optional[str] = None
    INTRI: Optional[str] = None
    PROSY: Optional[str] = None

    class Config:
        from_attributes = True


class SuitabilityDetails(BaseModel):
    suitability_score: float
    warnings: List[str]
    interval_used: int


class WeatherData(BaseModel):
    temperature_2m_mean: Optional[List[float]] = None
    precipitation_sum: Optional[List[float]] = None


class PlantSuitabilityResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    plant_name: str
    suitability_details: SuitabilityDetails
    weather_data: WeatherData

    class Config:
        from_attributes = True
