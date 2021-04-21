# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
#from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class EventCreate(BaseModel):
    """ events table field"""
    event_id: int
    event_timestamp: datetime
    event_vehicle_detected_plate_number: str
    event_vehicle_detected_lat: int
    event_vehicle_detected_long: int
    event_vehicle_lpn_detection_status: str
    class Config:
        orm_mode = True

class Event(EventCreate):
    """ events table field"""
    pass
    