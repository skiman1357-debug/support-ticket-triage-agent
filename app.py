import hmac
import os
from pathlib import Path

from dotenv import load_dotenv
from uuid import uuid4

import httpx
import streamlit as st
from pydantic import ValidationError

from api_models import TriageResponse


load_dotenv(
    Path(__file__).resolve().parent / ".env",
    override=False,
)


def get_setting(name, default=""):
    try:
        value = st.secrets.get(name)
    except FileNotFoundError:
        value = None

    if value is None:
        value = os.getenv(name, default)

    return str(value).strip()


API_URL = get_setting(
    "TRIAGE_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

API_KEY = get_setting("TRIAGE_API_KEY")
DEMO_ACCESS_CODE = get_setting("DEMO_ACCESS_CODE")

st.set_page_config(
    page_title="Support Ticket Triage Agent",
    page_icon="🎫",
    layout="centered",
)

st.title("Support Ticket Triage Agent")
st.caption(
    "Classify a support ticket and prepare a reply "
    "using the fictional CloudDesk knowledge base."
)
st.info(
    "Demo application. Use synthetic tickets only. "
    "Replies are drafts and are never sent automatically."
)
if not API_KEY or not DEMO_ACCESS_CODE:
    st.warning("Demo access has not been configured.")
    st.stop()

entered_code = st.text_input(
    "Demo access code",
    type="password",
    key="demo_access_input",
)

authorized = hmac.compare_digest(
    entered_code.encode("utf-8"),
    DEMO_ACCESS_CODE.encode("utf-8"),
)

if not authorized:
    st.info("Enter the demo access code and press Enter.")
    st.stop()

with st.form("ticket_form"):
    subject = st.text_input(
        "Subject",
        value="Payment completed, account still blocked",
        max_chars=200,
    )

    message = st.text_area(
        "Customer message",
        value=(
            "I paid for my subscription yesterday, "
            "but my account is still blocked. "
            "Could you help me regain access?"
        ),
        height=160,
        max_chars=10000,
    )

    submitted = st.form_submit_button("Analyze ticket")

if submitted:
    # Usuwamy poprzedni wynik, aby nie pomylić go z nową analizą.
    st.session_state.pop("triage_result", None)
    st.session_state.pop("analyzed_ticket", None)

    if not subject.strip() or not message.strip():
        st.warning("Enter a subject and a customer message.")
    else:
        payload = {
            "id": f"TICKET-{uuid4().hex[:12]}",
            "subject": subject.strip(),
            "message": message.strip(),
        }

        try:
            with st.spinner("Searching knowledge and preparing a draft..."):
                response = httpx.post(
                    f"{API_URL}/triage",
                    json=payload,
                    headers={"X-API-Key": API_KEY},
                    timeout=120.0,
                )

            if response.status_code == 200:
                result = TriageResponse.model_validate(response.json())

                st.session_state["triage_result"] = result.model_dump()
                st.session_state["analyzed_ticket"] = payload

            elif response.status_code == 422:
                st.error("The API rejected the ticket data.")
                st.json(response.json())

            else:
                st.error(
                    f"Analysis failed. API status: {response.status_code}. "
                    "Check the terminal running FastAPI."
                )

        except httpx.ConnectError:
            st.error(
                "Cannot connect to FastAPI. "
                "Start the API server on port 8000."
            )

        except httpx.TimeoutException:
            st.error(
                "The request timed out. The server may still be processing it. "
                "Check the API terminal before trying again."
            )

        except httpx.RequestError:
            st.error("A network error occurred while contacting the API.")

        except (ValidationError, ValueError):
            st.error("The API returned an unexpected response format.")

if "triage_result" in st.session_state:
    result = st.session_state["triage_result"]
    ticket = st.session_state["analyzed_ticket"]

    st.divider()
    st.subheader("Analysis")

    st.caption(
        "This result applies to the last submitted ticket. "
        "Editing the form does not update it automatically."
    )

    with st.expander("Analyzed ticket"):
        st.write(f"Subject: {ticket['subject']}")
        st.text(ticket["message"])

    left, right = st.columns(2)
    left.metric("Category", result["category"])
    right.metric("Priority", result["priority"])

    if result["knowledge_sufficient"]:
        st.write("Knowledge assessment: sufficient according to the model.")
    else:
        st.warning(
            "The retrieved knowledge does not support a sufficient answer."
        )

    if result["needs_human_review"]:
        st.warning("Human review or action required.")
        st.write(result["review_reason"])
    else:
        st.info(
            "No additional escalation was identified by the model. "
            "The draft still requires review before use."
        )

    st.subheader("Suggested reply")
    st.text(result["suggested_reply"])

    st.download_button(
        "Download reply draft",
        data=result["suggested_reply"],
        file_name=f"{ticket['id']}_draft.txt",
        mime="text/plain",
    )

    st.subheader("Cited knowledge sources")

    if not result["sources"]:
        st.write("No sources cited.")
    else:
        for source in result["sources"]:
            with st.expander(
                    f"{source['id']}: {source['title']}"
            ):
                st.text(source["content"])

    st.caption(
        "Source identifiers do not guarantee that every sentence "
        "is supported. Review the draft against the documents."
    )