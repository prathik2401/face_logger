import cv2
import numpy as np
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from profiles.models import Person, VisitLog
from .embedder import FaceEmbedder
from .matcher import FaceMatcher
from .active_person_tracker import ActivePersonTracker

class RecognizerPipeline:
    def __init__(self, visit_cooldown_seconds=60, matcher_threshold=0.55): # Added matcher_threshold
        self.embedder = FaceEmbedder()
        self.matcher = FaceMatcher(threshold=matcher_threshold) # Pass threshold to FaceMatcher
        self.active_tracker = ActivePersonTracker(cooldown_seconds=visit_cooldown_seconds)

    def _create_snapshot(self, frame: np.ndarray, bbox: np.ndarray) -> ContentFile:
        """Helper to create a snapshot ContentFile from a frame and bbox."""
        x1, y1, x2, y2 = bbox.astype(int)
        face_img = frame[y1:y2, x1:x2]
        if face_img.size == 0: # Check if crop is empty
            return None
        is_success, buffer = cv2.imencode('.jpg', face_img)
        if not is_success:
            return None
        return ContentFile(buffer.tobytes(), name=f"face_{datetime.now().timestamp()}.jpg")

    def process_frame(self, frame: np.ndarray):
        """
        - Detects faces
        - Finds match or registers new person
        - Logs visit selectively based on ActivePersonTracker
        """
        face_data_list = self.embedder.get_faces_and_embeddings(frame)
        results_for_frame = []

        for face_data in face_data_list:
            embedding = face_data['embedding']
            bbox = face_data['bbox']
            
            person_obj = self.matcher.find_best_match(embedding)

            if person_obj:
                # Known person found
                if self.active_tracker.should_log_visit(person_obj.id):
                    person_obj.last_seen = timezone.now()
                    person_obj.visit_count += 1
                    person_obj.save(update_fields=['last_seen', 'visit_count'])
                    
                    snapshot_file = self._create_snapshot(frame, bbox)
                    if snapshot_file:
                        VisitLog.objects.create(person=person_obj, snapshot=snapshot_file)
                    
                    self.active_tracker.record_person_logged(person_obj.id)
            else:
                # New person detected
                person_obj = Person() # Name will be blank by default
                person_obj.set_embedding(embedding)
                person_obj.save() # Save to get an ID

                # Add this new person to the live matcher instance
                self.matcher.add_known_person(person_obj, embedding)
                
                # Log their first visit (should_log_visit will be true for a new ID)
                if self.active_tracker.should_log_visit(person_obj.id): # Ensure logging logic is consistent
                    snapshot_file = self._create_snapshot(frame, bbox)
                    if snapshot_file:
                        VisitLog.objects.create(person=person_obj, snapshot=snapshot_file)
                    self.active_tracker.record_person_logged(person_obj.id)

            results_for_frame.append({
                'person_id': str(person_obj.id),
                'name': person_obj.name,
                'visit_count': person_obj.visit_count,
                'bbox': bbox.tolist(), # Convert bbox to list for potential JSON serialization
            })

        return results_for_frame
