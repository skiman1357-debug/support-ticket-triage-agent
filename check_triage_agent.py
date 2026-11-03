from semantic_search import KnowledgeSearch
from ticket_models import Ticket
from triage_agent import generate_triage


def main():
    ticket = Ticket(
        id="TICKET-001",
        subject="Payment completed, account still blocked",
        message=(
            "I paid for my subscription yesterday, "
            "but my account is still blocked. "
            "Could you help me regain access?"
        ),
    )

    search_engine = KnowledgeSearch()

    query = f"{ticket.subject}\n{ticket.message}"
    documents = search_engine.search(query, top_k=3)

    print("\n=== DOKUMENTY PRZEKAZANE DO AI ===")
    for document in documents:
        print(
            f"{document['id']} | "
            f"{document['title']} | "
            f"{document['score']:.4f}"
        )

    print("\nWysyłam zgłoszenie i dokumenty do xAI...")
    result = generate_triage(ticket, documents)

    print("\n=== WYNIK ANALIZY ===")
    print(result.model_dump_json(indent=2))

    print("\n=== ŹRÓDŁA WSKAZANE W ODPOWIEDZI ===")
    for document in documents:
        if document["id"] in result.source_ids:
            print(f"{document['id']}: {document['title']}")

    print("\nTo propozycja odpowiedzi. Nie wysłano jej do klienta.")


if __name__ == "__main__":
    main()