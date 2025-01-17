from data.schemas.event import Event
from data.session import create_session
import data.models as models

from sqlalchemy.exc import IntegrityError
from data.exceptions import BadRequest, Missing


# Create an event
def create_event(event: Event) -> int:
    try:
        db = create_session()
        new_event = models.Events(
            user=event.user,
            position=event.position,
            when=event.when,
            time_of_day=event.time_of_day,
            day_of_week=event.day_of_week,
            guidance=event.guidance,
            group=event.group,
            factors=event.factors,
            familiarity=event.familiarity,
            context=event.context,
            explain=event.explain,
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        id = new_event.id
        return id
    except IntegrityError:
        db.rollback()
        raise BadRequest("bad request body")
    finally:
        db.close()


def update_event(event_id: int, event: Event) -> Event:
    if event_id < 0:
        raise BadRequest("Bad ID")
    try:
        db = create_session()
        e = db.query(models.Events).filter(models.Events.id == event_id).first()
        if not e:
            db.close()
            raise Missing(f"Event id {event_id} not found")
        e.user = event.user
        e.position = event.position
        e.when = event.when
        e.time_of_day = event.time_of_day
        e.day_of_week = event.day_of_week
        e.guidance = event.guidance
        e.group = event.group
        e.factors = event.factors
        e.familiarity = str(event.familiarity)
        e.context = event.context
        e.explain = event.explain
        db.commit()
        db.refresh(e)
        e.familiarity = str(e.familiarity)
        return e
    except IntegrityError:
        db.rollback()
        raise BadRequest("bad request body")
    finally:
        db.close()
