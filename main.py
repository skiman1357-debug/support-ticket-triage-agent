from ticket_models import Ticket


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

    print("Support Ticket Triage Agent")
    print(f"Ticket: {ticket.id}")
    print(f"Subject: {ticket.subject}")
    print(f"Message: {ticket.message}")

    print("\n=== SPRAWDZENIE WALIDACJI ===")

    try:
        Ticket(
            id="TICKET-002",
            subject="   ",
            message="I cannot log in.",
        )
    except ValueError as error:
        print(f"Kontrolowany błąd: {error}")


if __name__ == "__main__":
    main()