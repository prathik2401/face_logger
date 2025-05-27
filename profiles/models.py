import uuid
import pickle
import numpy as np
from django.db import models
from django.utils import timezone

class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    embedding = models.BinaryField(help_text="Pickled facial embedding vector")
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now, help_text="Last time this person was seen")
    visit_count = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = 'profiles'

    def set_embedding(self, vector: np.ndarray):
        self.embedding = pickle.dumps(vector)

    def get_embedding(self) -> np.ndarray:
        return pickle.loads(self.embedding)
    
    def __str__(self):
        return f"{self.name or self.id}"
    
class VisitLog(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='visits')
    timestamp = models.DateTimeField(auto_now_add=True)
    snapshot = models.ImageField(upload_to='faces/logs/', null=True, blank=True)

    def __str__(self):
        return f"Visit by {self.person} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    