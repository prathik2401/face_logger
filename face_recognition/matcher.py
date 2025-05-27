import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
# Defer import of Person to avoid issues during app loading
# from profiles.models import Person

class FaceMatcher:
    def __init__(self, threshold=0.55):
        self.threshold = threshold
        self.known_persons = []  # Initialize as empty list
        self._known_embeddings = np.empty((0, 512)) # Default embedding size, adjust if necessary
        self._loaded = False 
        self._load_data() # Initial load of known persons from DB

    def _load_data(self):
        if not self._loaded: # Only load if not already loaded or explicitly refreshed
            from profiles.models import Person # Import here to ensure models are ready
            
            db_persons = list(Person.objects.all())
            
            embeddings_list = []
            valid_persons = []
            if db_persons:
                for person in db_persons:
                    if person.embedding: # Ensure embedding data exists
                        try:
                            emb = person.get_embedding()
                            # Ensure embedding is a 1D array before appending
                            if emb.ndim == 1:
                                embeddings_list.append(emb)
                                valid_persons.append(person)
                            # else: log or handle multi-dimensional embedding if it's an error
                        except Exception:
                            # Skip person if embedding is invalid or cannot be loaded
                            pass # Optionally log this error
                
            self.known_persons = valid_persons
            if embeddings_list:
                # Stack 1D arrays into a 2D array
                self._known_embeddings = np.array(embeddings_list)
                if self._known_embeddings.ndim == 1 and len(embeddings_list) == 1: # Handle single embedding case
                    self._known_embeddings = self._known_embeddings.reshape(1, -1)
            else:
                # Ensure _known_embeddings is a 2D array even if empty
                # Use a specific embedding dimension (e.g., 512) or get from first valid embedding
                # For now, assuming 512 if empty.
                emb_dim = 512 if not embeddings_list else embeddings_list[0].shape[0]
                self._known_embeddings = np.empty((0, emb_dim))
            
            self._loaded = True

    def add_known_person(self, person, embedding: np.ndarray):
        """Dynamically adds a new person to the matcher's known list."""
        if not self._loaded: # Should ideally be loaded by __init__
            self._load_data()

        self.known_persons.append(person)
        
        new_embedding = np.asarray(embedding).reshape(1, -1) # Ensure 2D

        if self._known_embeddings is None or self._known_embeddings.shape[0] == 0:
            self._known_embeddings = new_embedding
        else:
            if self._known_embeddings.shape[1] != new_embedding.shape[1]:
                # Handle mismatched embedding dimensions if necessary
                # For now, this would cause vstack to fail.
                # Consider logging an error or re-initializing if dimensions change.
                print(f"Warning: Mismatched embedding dimensions. Known: {self._known_embeddings.shape[1]}, New: {new_embedding.shape[1]}")
                # Fallback: could re-initialize or skip adding. For now, let vstack raise error or handle as needed.
                # As a simple fix, if _known_embeddings was (0, 512) and new is (1, X), re-init _known_embeddings
                if self._known_embeddings.shape[0] == 0: # If it was an empty placeholder
                    self._known_embeddings = np.empty((0, new_embedding.shape[1]))


            self._known_embeddings = np.vstack([self._known_embeddings, new_embedding])

    def find_best_match(self, embedding: np.ndarray):
        """
        Returns the matched Person object or None if no match is found
        """
        # _load_data() is called in __init__ and refresh_known_persons
        if not self.known_persons or self._known_embeddings is None or self._known_embeddings.shape[0] == 0:
            return None

        query_embedding = np.asarray(embedding).reshape(1, -1)
        
        if query_embedding.shape[1] != self._known_embeddings.shape[1]:
            # print(f"Query embedding dim {query_embedding.shape[1]} != known_embeddings dim {self._known_embeddings.shape[1]}")
            return None # Cannot compare if dimensions mismatch

        similarity_scores = cosine_similarity(query_embedding, self._known_embeddings)[0]
        
        if len(similarity_scores) == 0:
            return None
            
        best_idx = np.argmax(similarity_scores)
        best_score = similarity_scores[best_idx]

        if best_score >= self.threshold:
            return self.known_persons[best_idx]
        return None

    def refresh_known_persons(self):
        """
        Allows explicitly refreshing the list of known persons and their embeddings from the database.
        """
        self._loaded = False 
        self.known_persons = []
        # Reset embeddings, ensure it's 2D with correct dimension or a placeholder
        emb_dim = self._known_embeddings.shape[1] if self._known_embeddings.size > 0 else 512
        self._known_embeddings = np.empty((0, emb_dim)) 
        self._load_data()
