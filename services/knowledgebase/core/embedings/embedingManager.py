from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the EmbeddingManager with a specified pre-trained model.
        """
        self.model = SentenceTransformer(model_name)

    def calculate_embedding(self, text):
        """
        Calculate the embedding for the given text.
        Args:
            text (str): The input text for which to calculate the embedding.
        Returns:
            list: A list representing the embedding vector.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def calculate_similarity(self, embedding1, embedding2):
        """
        Calculate cosine similarity between two embeddings.
        Args:
            embedding1 (list): First embedding vector.
            embedding2 (list): Second embedding vector.
        Returns:
            float: The cosine similarity score between the two embeddings.
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def normalize_embedding(self, embedding):
        """
        Normalize the embedding vector to have a unit norm.
        Args:
            embedding (list): The embedding vector to normalize.
        Returns:
            list: The normalized embedding vector.
        """
        vec = np.array(embedding)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist() if norm != 0 else vec.tolist()

