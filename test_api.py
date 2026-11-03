import os
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app
from triage_models import TriageResult


class ApiTests(unittest.TestCase):
    def setUp(self):
        # ExitStack zamknie klienta i wyłączy wszystkie atrapy
        # po każdym teście, również gdy test zakończy się błędem.
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            patch.dict(
                os.environ,
                {"TRIAGE_API_KEY": "test-only-key"},
            )
        )

        self.search_class = self.stack.enter_context(
            patch("api.KnowledgeSearch")
        )
        self.generate = self.stack.enter_context(
            patch("api.generate_triage")
        )

        self.search_engine = self.search_class.return_value
        self.search_engine.documents = [
            {
                "id": "KB-001",
                "title": "Blocked account",
                "content": "Billing review is required.",
            }
        ]
        self.search_engine.search.return_value = (
            self.search_engine.documents
        )

        self.generate.return_value = TriageResult(
            category="billing",
            priority="high",
            knowledge_sufficient=True,
            needs_human_review=True,
            review_reason="The billing team must verify the payment.",
            suggested_reply="Please provide your invoice number.",
            source_ids=["KB-001"],
        )

        # Uruchamia lifespan, ale z atrapą KnowledgeSearch.
        self.client = self.stack.enter_context(TestClient(app))
        self.client.headers["X-API-Key"] = "test-only-key"

        self.payload = {
            "id": "TICKET-TEST-001",
            "subject": "Account blocked",
            "message": "I paid yesterday but still cannot access my account.",
        }

    def test_health_returns_document_count_without_ai(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "knowledge_documents": 1},
        )
        self.generate.assert_not_called()
        self.search_engine.search.assert_not_called()

    def test_valid_ticket_returns_analysis(self):
        response = self.client.post("/triage", json=self.payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "billing")
        self.assertEqual(response.json()["source_ids"], ["KB-001"])
        self.assertEqual(
            response.json()["sources"],
            [
                {
                    "id": "KB-001",
                    "title": "Blocked account",
                    "content": "Billing review is required.",
                }
            ],
        )
        self.assertTrue(response.json()["needs_human_review"])

        self.search_engine.search.assert_called_once_with(
            f"{self.payload['subject']}\n{self.payload['message']}",
            top_k=3,
        )
        self.generate.assert_called_once()

        ticket, documents = self.generate.call_args.args
        self.assertEqual(ticket.id, self.payload["id"])
        self.assertEqual(documents, self.search_engine.documents)

    def test_empty_subject_is_rejected_before_search_and_ai(self):
        payload = {**self.payload, "subject": "   "}

        response = self.client.post("/triage", json=payload)

        self.assertEqual(response.status_code, 422)
        self.search_engine.search.assert_not_called()
        self.generate.assert_not_called()

    def test_extra_field_is_rejected_before_search_and_ai(self):
        payload = {**self.payload, "priority": "urgent"}

        response = self.client.post("/triage", json=payload)

        self.assertEqual(response.status_code, 422)
        self.search_engine.search.assert_not_called()
        self.generate.assert_not_called()

    def test_missing_message_is_rejected(self):
        payload = self.payload.copy()
        del payload["message"]

        response = self.client.post("/triage", json=payload)

        self.assertEqual(response.status_code, 422)
        self.generate.assert_not_called()

    def test_too_long_message_is_rejected(self):
        payload = {**self.payload, "message": "x" * 10001}

        response = self.client.post("/triage", json=payload)

        self.assertEqual(response.status_code, 422)
        self.generate.assert_not_called()

    def test_invalid_analysis_returns_502_without_internal_details(self):
        self.generate.side_effect = ValueError(
            "INTERNAL_TEST_DETAIL"
        )

        response = self.client.post("/triage", json=self.payload)

        self.assertEqual(response.status_code, 502)
        self.assertIn("detail", response.json())
        self.assertNotIn("INTERNAL_TEST_DETAIL", response.text)

    def test_search_engine_is_loaded_once_for_multiple_requests(self):
        self.client.post("/triage", json=self.payload)
        self.client.post("/triage", json=self.payload)

        self.search_class.assert_called_once()
        self.assertEqual(self.generate.call_count, 2)

        def test_missing_api_key_is_rejected(self):
            del self.client.headers["X-API-Key"]

            response = self.client.post("/triage", json=self.payload)

            self.assertEqual(response.status_code, 401)
            self.search_engine.search.assert_not_called()
            self.generate.assert_not_called()

        def test_wrong_api_key_is_rejected(self):
            response = self.client.post(
                "/triage",
                json=self.payload,
                headers={"X-API-Key": "wrong-key"},
            )

            self.assertEqual(response.status_code, 401)
            self.search_engine.search.assert_not_called()
            self.generate.assert_not_called()

    def test_missing_api_key_is_rejected(self):
        del self.client.headers["X-API-Key"]

        response = self.client.post("/triage", json=self.payload)

        self.assertEqual(response.status_code, 401)
        self.search_engine.search.assert_not_called()
        self.generate.assert_not_called()

    def test_wrong_api_key_is_rejected(self):
        response = self.client.post(
            "/triage",
            json=self.payload,
            headers={"X-API-Key": "wrong-key"},
        )

        self.assertEqual(response.status_code, 401)
        self.search_engine.search.assert_not_called()
        self.generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
