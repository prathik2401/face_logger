import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

class FaceEmbedder:
    def __init__(self):
        self.app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider'])
        self.app.prepare(ctx_id=0)

    def get_faces_and_embeddings(self, image: np.ndarray):
        """
        Returns detected faces and their 512-embeddings
        """
        faces = self.app.get(image)
        results = []
        for face in faces:
            embedding = face['embedding']
            bbox = face['bbox'].astype(int)
            aligned = face.get('aligned') # Use .get() for safe access
            results.append({
                'embedding': embedding,
                'bbox': bbox,
                'face_crop': aligned,
            })
        return results
