from semantic_search import KnowledgeSearch


CASES = [
    {
        "name": "Payment and blocked account",
        "query": (
            "My subscription payment went through yesterday, "
            "but my account is still locked."
        ),
        "expected_id": "KB-001",
    },
    {
        "name": "Forgotten password",
        "query": (
            "I forgot my password. "
            "How can I get a link to create a new one?"
        ),
        "expected_id": "KB-002",
    },
    {
        "name": "Possible duplicate charge",
        "query": (
            "I can see two subscription charges "
            "on my bank statement for the same month."
        ),
        "expected_id": "KB-003",
    },
    {
        "name": "Application error",
        "query": (
            "The dashboard displays an error "
            "every time I try to open a report."
        ),
        "expected_id": "KB-004",
    },
    {
        "name": "Stopping subscription renewal",
        "query": (
            "I do not want my subscription to renew next month. "
            "Where can I stop the renewal?"
        ),
        "expected_id": "KB-005",
    },
    {
        "name": "Possible account compromise",
        "query": (
            "Someone I do not recognize signed into my account "
            "and changed my settings."
        ),
        "expected_id": "KB-006",
    },
]


def main():
    search_engine = KnowledgeSearch()

    top1_hits = 0
    top3_hits = 0

    for case in CASES:
        results = search_engine.search(case["query"], top_k=3)
        returned_ids = [result["id"] for result in results]

        top1_ok = returned_ids[0] == case["expected_id"]
        top3_ok = case["expected_id"] in returned_ids

        top1_hits += int(top1_ok)
        top3_hits += int(top3_ok)

        print(f"\n=== {case['name']} ===")
        print(f"Oczekiwany dokument: {case['expected_id']}")
        print(f"Pierwszy wynik poprawny: {top1_ok}")

        for result in results:
            print(f"  {result['id']}: {result['score']:.4f}")

    total = len(CASES)

    print("\n=== PODSUMOWANIE ===")
    print(f"Poprawny dokument na pierwszym miejscu: {top1_hits}/{total}")
    print(f"Poprawny dokument w pierwszej trójce: {top3_hits}/{total}")

    print("\n=== PYTANIE SPOZA BAZY ===")

    unrelated_query = (
        "How do I bake a chocolate cake without eggs?"
    )

    print(f"Zapytanie: {unrelated_query}")

    for result in search_engine.search(unrelated_query, top_k=3):
        print(f"  {result['id']}: {result['score']:.4f}")

    print(
        "\nWyniki dla pytania spoza bazy nie oznaczają, "
        "że dokumenty zawierają odpowiedź."
    )


if __name__ == "__main__":
    main()