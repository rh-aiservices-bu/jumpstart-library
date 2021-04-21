from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import func
#from sqlalchemy.orm import relationship
#from .database import Base
from database import Base

class Event(Base):
    __tablename__ = "event"
    event_id = Column(Integer, primary_key=True, index=True)
    event_timestamp = Column('date', DateTime(timezone=True), default=func.now())
    #event_timestamp = Column(String)
    event_vehicle_detected_plate_number = Column(String, index=True)
    event_vehicle_detected_lat = Column(Integer)
    event_vehicle_detected_long = Column(Integer)
    event_vehicle_lpn_detection_status = Column(String)
