from sqlalchemy.orm import Session
#from . import models, schemas
import models, schemas

def get_event(db: Session, skip: int = 0, limit: int = 100):
    """ get events from DB """
    return db.query(models.Event).offset(skip).limit(limit).all()


def create_event(db: Session, payload: schemas.EventCreate):
    """ add events to DB """
    db_event = models.Event(event_id = payload.event_id, event_timestamp = payload.event_timestamp, event_vehicle_detected_plate_number = payload.event_vehicle_detected_plate_number, event_vehicle_detected_lat = payload.event_vehicle_detected_lat, event_vehicle_detected_long = payload.event_vehicle_detected_long, event_vehicle_lpn_detection_status = payload.event_vehicle_lpn_detection_status)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

    