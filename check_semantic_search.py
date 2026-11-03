from semantic_search import KnowledgeSearch


def main():
    search_engine = KnowledgeSearch()

    query = (
        "I paid for my subscription yesterday, "
        "but I still cannot access my account."
    )

    results = search_engine.search(query, top_k=3)

    print(f"\nZapytanie: {query}")
    print(f"Liczba wyników: {len(results)}")

    for position, result in enumerate(results, start=1):
        print(f"\n=== WYNIK {position} ===")
        print(f"Dokument: {result['id']}")
        print(f"Tytuł: {result['title']}")
        print(f"Kategoria: {result['category']}")
        print(f"Podobieństwo: {result['score']:.4f}")
        print(f"Treść: {result['content']}")


if __name__ == "__main__":
    main()