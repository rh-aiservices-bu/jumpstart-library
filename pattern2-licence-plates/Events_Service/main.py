from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/event/", response_model=List[schemas.Event])
def get_event(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    event = crud.get_event(db, skip=skip, limit=limit)
    return event

@app.post("/event/", response_model=schemas.EventCreate)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db) ):
    #db_event = crud.create_event(db, event_id = payload.event_id, event_timestamp = payload.event_timestamp, event_vehicle_detected_plate_number = payload.event_vehicle_detected_plate_number, event_vehicle_detected_lat = payload.event_vehicle_detected_lat, event_vehicle_detected_long = payload.event_vehicle_detected_long, event_vehicle_lpn_detection_status = payload.event_vehicle_lpn_detection_status)
    return crud.create_event(db=db, payload=payload)
    #return db_event

