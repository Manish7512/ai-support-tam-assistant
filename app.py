import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Support + TAM Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #888888;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .status-card {
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        text-align: center;
        margin-bottom: 1rem;
    }

    .status-value {
        font-size: 1.4rem;
        font-weight: 700;
    }

    .status-label {
        color: #888888;
        font-size: 0.9rem;
    }

    .footer {
        text-align: center;
        color: #777777;
        padding-top: 2rem;
        padding-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">🤖 AI Support + TAM Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered ticket triage, response drafting, and customer account intelligence"
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select capability",
    [
        "🏠 Dashboard",
        "🎫 Ticket Triage",
        "✍️ Response Drafting",
        "🏢 Account Health",
    ],
)

st.sidebar.divider()

st.sidebar.caption("Powered by")
st.sidebar.caption("FastAPI • Gemini • RAG")


# ---------------------------------------------------------
# API Helper
# ---------------------------------------------------------

def call_api(endpoint):

    try:

        response = requests.post(
            f"{API_URL}{endpoint}",
            timeout=60,
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"API Error {response.status_code}: "
            f"{response.text}"
        )

    except requests.exceptions.RequestException:

        st.error(
            "Unable to connect to the FastAPI server."
        )

        st.info(
            "Make sure the FastAPI server is running:"
        )

        st.code(
            "uvicorn src.api:app --reload"
        )

    return None


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">System Overview</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="status-card">
                <div class="status-value">🎫 Ticket Triage</div>
                <div class="status-label">
                    AI ticket classification
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="status-card">
                <div class="status-value">✍️ Response Drafting</div>
                <div class="status-label">
                    Customer response generation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            """
            <div class="status-card">
                <div class="status-value">🏢 TAM Health</div>
                <div class="status-label">
                    Customer account intelligence
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        '<div class="section-title">Architecture</div>',
        unsafe_allow_html=True,
    )

    st.code(
        """
Customer / Support Agent
          │
          ▼
     Streamlit UI
          │
          ▼
       FastAPI
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
 Triage Draft  TAM
    │     │     │
    └─────┼─────┘
          ▼
    Gemini + RAG
          │
          ▼
Knowledge Base
        """,
        language="text",
    )

    st.success(
        "Backend API is ready for ticket triage, "
        "response drafting, and account health analysis."
    )


# ---------------------------------------------------------
# Ticket Triage
# ---------------------------------------------------------

elif page == "🎫 Ticket Triage":

    st.markdown(
        '<div class="section-title">🎫 Ticket Triage</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Classify a support ticket using Gemini, RAG, "
        "and deterministic validation."
    )

    ticket_id = st.text_input(
        "Ticket ID",
        value="TKT-10005",
        placeholder="Example: TKT-10005",
    )

    if st.button(
        "🔍 Analyze Ticket",
        type="primary",
        use_container_width=True,
    ):

        result = call_api(
            f"/triage/{ticket_id}"
        )

        if result:

            st.success(
                "Ticket analyzed successfully."
            )

            st.divider()

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Category",
                    result["category"],
                )

            with col2:

                st.metric(
                    "Urgency",
                    result["urgency"],
                )

            with col3:

                st.metric(
                    "Product Area",
                    result["product_area"],
                )

            with col4:

                st.metric(
                    "Known Issue",
                    "Yes"
                    if result["known_issue"]
                    else "No",
                )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "🧠 AI Reasoning"
                )

                st.info(
                    result["reasoning"]
                )

            with col2:

                st.subheader(
                    "👥 Responder Team"
                )

                st.success(
                    result["responder_team"]
                )

            st.subheader(
                "✉️ First Response"
            )

            st.text_area(
                "Generated customer response",
                result["first_response"],
                height=180,
            )

            if result.get("kb_document"):

                st.subheader(
                    "📚 Knowledge Base"
                )

                st.write(
                    f"**Document:** "
                    f"{result['kb_document']}"
                )

                st.write(
                    f"**Section:** "
                    f"{result.get('kb_section', '')}"
                )


# ---------------------------------------------------------
# Response Drafting
# ---------------------------------------------------------

elif page == "✍️ Response Drafting":

    st.markdown(
        '<div class="section-title">✍️ Response Drafting</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Generate a professional customer-facing response "
        "from the ticket context."
    )

    ticket_id = st.text_input(
        "Ticket ID",
        value="TKT-10000",
        placeholder="Example: TKT-10000",
    )

    if st.button(
        "✉️ Generate Response",
        type="primary",
        use_container_width=True,
    ):

        result = call_api(
            f"/draft-response/{ticket_id}"
        )

        if result:

            st.success(
                "Response generated successfully."
            )

            st.divider()

            st.subheader(
                "Customer Response"
            )

            st.text_area(
                "Generated response",
                result["draft_response"],
                height=250,
            )

            st.caption(
                "Review the draft before sending it to the customer."
            )


# ---------------------------------------------------------
# Account Health
# ---------------------------------------------------------

elif page == "🏢 Account Health":

    st.markdown(
        '<div class="section-title">🏢 Account Health</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Analyze customer health using account metrics, "
        "ticket history, and escalation signals."
    )

    account_id = st.text_input(
        "Account ID",
        value="ACC-3336",
        placeholder="Example: ACC-3336",
    )

    if st.button(
        "📊 Analyze Account",
        type="primary",
        use_container_width=True,
    ):

        result = call_api(
            f"/account-health/{account_id}"
        )

        if result:

            st.success(
                "Account health analyzed successfully."
            )

            st.divider()

            # -------------------------------------------------
            # Determine Health Status
            # -------------------------------------------------

            summary = result["health_summary"]
            summary_lower = summary.lower()

            if "churning" in summary_lower:

                health_status = "🔴 CHURNING"

            elif "at risk" in summary_lower:

                health_status = "🟠 AT RISK"

            elif "healthy" in summary_lower:

                health_status = "🟢 HEALTHY"

            elif "new" in summary_lower:

                health_status = "🔵 NEW"

            else:

                health_status = "⚪ UNKNOWN"

            # -------------------------------------------------
            # Health Status
            # -------------------------------------------------

            st.markdown(
                f"""
                <div class="status-card">
                    <div class="status-label">
                        CUSTOMER HEALTH
                    </div>
                    <div class="status-value">
                        {health_status}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # -------------------------------------------------
            # Health Summary
            # -------------------------------------------------

            st.subheader(
                "📋 Health Summary"
            )

            st.info(
                result["health_summary"]
            )

            # -------------------------------------------------
            # Risk Signals
            # -------------------------------------------------

            st.subheader(
                "⚠️ Risk Signals"
            )

            if result["risk_signals"]:

                for signal in result["risk_signals"]:

                    st.warning(signal)

            else:

                st.success(
                    "No significant risk signals identified."
                )

            # -------------------------------------------------
            # Recommended Actions
            # -------------------------------------------------

            st.subheader(
                "🎯 Recommended Actions"
            )

            for action in result[
                "recommended_actions"
            ]:

                st.success(action)


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="footer">'
    "AI Support + TAM Assistant • FastAPI + Gemini + RAG"
    "</div>",
    unsafe_allow_html=True,
)