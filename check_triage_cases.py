from semantic_search import KnowledgeSearch
from ticket_models import Ticket
from triage_agent import generate_triage


def main():
    search_engine = KnowledgeSearch()

    tickets = [
        Ticket(
            id="TICKET-002",
            subject="Chocolate cake recipe",
            message="How do I bake a chocolate cake without eggs?",
        ),
        Ticket(
            id="TICKET-003",
            subject="Unknown person accessed my account",
            message=(
                "I noticed a sign-in I do not recognize. "
                "Someone changed my account settings without permission. "
                "I can still access my account. What should I do?"
            ),
        ),
    ]

    for ticket in tickets:
        print(f"\n=== {ticket.id}: {ticket.subject} ===")

        query = f"{ticket.subject}\n{ticket.message}"
        documents = search_engine.search(query, top_k=3)

        print("Dokumenty znalezione przez wyszukiwarkę:")
        for document in documents:
            print(f"{document['id']}: {document['score']:.4f}")

        print("\nWysyłam zapytanie do xAI...")

        try:
            result = generate_triage(ticket, documents)
        except Exception as error:
            print(f"Błąd: {type(error).__name__}: {error}")
            continue

        print(result.model_dump_json(indent=2))

    print("\nZakończono sprawdzanie. Nie wysłano wiadomości do klientów.")


if __name__ == "__main__":
    main()