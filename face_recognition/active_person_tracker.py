from datetime import timedelta
from django.utils import timezone

class ActivePersonTracker:
    def __init__(self, cooldown_seconds=60):
        self.active_persons = {}  # Stores {person_id: last_log_timestamp}
        self.cooldown_period = timedelta(seconds=cooldown_seconds)

    def should_log_visit(self, person_id) -> bool:
        now = timezone.now()
        last_log_time = self.active_persons.get(person_id)

        if last_log_time is None:
            # Person not tracked yet in this session, or tracker was cleared
            return True
        
        if now - last_log_time > self.cooldown_period:
            # Cooldown period has passed
            return True
        
        return False  # Seen recently, within cooldown
    
    def record_person_logged(self, person_id):
        self.active_persons[person_id] = timezone.now()

    def clear_tracker(self):
        self.active_persons.clear()
