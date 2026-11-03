from sentence_transformers import SentenceTransformer

from knowledge_base import load_knowledge_base


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class KnowledgeSearch:
    def __init__(self):
        self.documents = load_knowledge_base()

        print("Ładuję model embeddingów...")
        self.model = SentenceTransformer(
            MODEL_NAME,
            device="cpu",
        )

        texts = [
            f"{document['title']}\n{document['content']}"
            for document in self.documents
        ]

        self.document_embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    def search(self, query, top_k=3):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Zapytanie musi być niepustym tekstem.")

        if type(top_k) is not int or top_k < 1:
            raise ValueError("top_k musi być dodatnią liczbą całkowitą.")

        query_embedding = self.model.encode(
            query.strip(),
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        # Dla znormalizowanych wektorów iloczyn skalarny
        # odpowiada podobieństwu kosinusowemu.
        scores = self.document_embeddings @ query_embedding

        ranked_indices = sorted(
            range(len(self.documents)),
            key=lambda index: float(scores[index]),
            reverse=True,
        )

        results = []

        for index in ranked_indices[:top_k]:
            results.append(
                {
                    **self.documents[index],
                    "score": float(scores[index]),
                }
            )

        return results