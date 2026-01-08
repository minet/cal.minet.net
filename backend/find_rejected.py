from sqlmodel import Session, select
from app.database import engine
from app.models import Event, EventVisibility

def find_rejected_events():
    with Session(engine) as session:
        events = session.exec(select(Event).where(Event.visibility == EventVisibility.PUBLIC_REJECTED)).all()
        print(f"Found {len(events)} rejected events.")
        for e in events:
            print(f" - {e.title} (ID: {e.id})")

if __name__ == "__main__":
    find_rejected_events()
