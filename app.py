import os
import requests
import streamlit as st

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


#load_dotenv()
# -------------------------------------------------------------------
# Streamlit configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Currency Agent",
    page_icon="💱",
    layout="centered",
)


# -------------------------------------------------------------------
# Custom styling
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            text-align: center;
            color: #777;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }

        .result-card {
            padding: 1.5rem;
            border-radius: 18px;
            border: 1px solid rgba(128,128,128,0.25);
            text-align: center;
            margin: 1rem 0;
        }

        .result-number {
            font-size: 2.2rem;
            font-weight: 800;
        }

        .rate-text {
            color: #777;
            margin-top: 0.4rem;
        }

        .feature-card {
            padding: 1rem;
            border-radius: 14px;
            border: 1px solid rgba(128,128,128,0.2);
            height: 100%;
        }

        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Currency API tool
# -------------------------------------------------------------------
@st.cache_data(ttl=3600)
def get_supported_currencies() -> dict:
    api_key = st.secrets["EXCHANGE_RATE_API_KEY"]

    if not api_key:
        raise ValueError("EXCHANGE_RATE_API_KEY is missing.")

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/codes"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if data.get("result") != "success":
        raise ValueError(
            f"ExchangeRate-API error: {data.get('error-type', 'unknown error')}"
        )

    return {
        code: name
        for code, name in data["supported_codes"]
    }


@tool
def get_conversion_factor(base_currency: str, target_currency: str) -> dict:
    """Get the latest available exchange rate between two currencies."""

    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        raise ValueError("EXCHANGE_RATE_API_KEY is missing.")

    base_currency = base_currency.strip().upper()
    target_currency = target_currency.strip().upper()

    if len(base_currency) != 3 or len(target_currency) != 3:
        raise ValueError(
            "Currencies must use three-letter currency codes such as USD, EUR or INR."
        )

    if base_currency == target_currency:
        return {
            "base_currency": base_currency,
            "target_currency": target_currency,
            "conversion_rate": 1.0,
            "rate_date": None,
        }
    url = (
        f"https://v6.exchangerate-api.com/v6/"
        f"{api_key}/pair/{base_currency}/{target_currency}"
    )

    response = requests.get(
        url,
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    if data.get("result") != "success":
        raise ValueError(
            f"ExchangeRate-API error: "
            f"{data.get('error-type', 'unknown error')}"
        )
    return {
        "base_currency": data["base_code"],
        "target_currency": data["target_code"],
        "conversion_rate": data["conversion_rate"],
        "last_update": data.get("time_last_update_utc"),
        "next_update": data.get("time_next_update_utc"),
    }


@tool
def convert(base_currency_value: float, conversion_rate: float) -> float:
    """Convert an amount using an exchange rate."""
    return round(base_currency_value * conversion_rate, 2)


# -------------------------------------------------------------------
# Cached Hugging Face model
# -------------------------------------------------------------------
@st.cache_resource
def get_llm():
    token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

    if not token:
        return None

    llm = HuggingFaceEndpoint(
        repo_id="openai/gpt-oss-120b",
        task="text-generation",
        huggingfacehub_api_token=token,
    )

    chat_model = ChatHuggingFace(llm=llm)

    return chat_model.bind_tools(
        [get_conversion_factor, convert]
    )


def format_amount(value: float) -> str:
    return f"{value:,.2f}"


# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.markdown(
    '<div class="main-title">💱 AI Currency Agent</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Convert currencies worldwide using live exchange-rate data + LangChain tool calling."
    "</div>",
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Load supported currencies
# -------------------------------------------------------------------
try:
    currency_data = get_supported_currencies()
    currencies = sorted(currency_data.keys())
except Exception as exc:
    st.error(f"Could not load supported currencies: {exc}")
    st.stop()


# -------------------------------------------------------------------
# Main converter
# -------------------------------------------------------------------
st.subheader("⚡ Quick Conversion")

col1, col2, col3 = st.columns([1.2, 0.7, 1.2])

with col1:
    amount = st.number_input(
        "Amount",
        min_value=0.01,
        value=100.0,
        step=1.0,
    )

    from_currency = st.selectbox(
        "From",
        currencies,
        index=currencies.index("USD") if "USD" in currencies else 0,
    )

with col2:
    st.write("")
    st.write("")
    if st.button("⇄ Swap"):
        st.session_state.swap = not st.session_state.get("swap", False)
        st.rerun()

with col3:
    target_default = (
        currencies.index("INR")
        if "INR" in currencies
        else (1 if len(currencies) > 1 else 0)
    )

    to_currency = st.selectbox(
        "To",
        currencies,
        index=target_default,
    )


if st.button("🚀 Convert Now", type="primary"):
    try:
        with st.spinner("Fetching the latest exchange rate..."):
            rate_result = get_conversion_factor.invoke(
                {
                    "base_currency": from_currency,
                    "target_currency": to_currency,
                }
            )

            converted_value = convert.invoke(
                {
                    "base_currency_value": amount,
                    "conversion_rate": rate_result["conversion_rate"],
                }
            )

        st.session_state.last_conversion = {
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "rate": rate_result["conversion_rate"],
            "result": converted_value,
            "date": rate_result.get("rate_date"),
        }

    except Exception as exc:
        st.error(f"Conversion failed: {exc}")


# -------------------------------------------------------------------
# Result
# -------------------------------------------------------------------
if "last_conversion" in st.session_state:
    result = st.session_state.last_conversion

    st.markdown(
        f"""
        <div class="result-card">
            <div>{format_amount(result["amount"])} {result["from"]}</div>
            <div style="font-size:1.5rem; margin:0.4rem;">↓</div>
            <div class="result-number">
                {format_amount(result["result"])} {result["to"]}
            </div>
            <div class="rate-text">
                1 {result["from"]} = {result["rate"]:,.6f} {result["to"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result["date"]:
        st.caption(
            f"Exchange-rate data date: {result['date']} · "
            "Rates are reference rates, not live trading quotes."
        )


# -------------------------------------------------------------------
# AI natural-language interface
# -------------------------------------------------------------------
st.divider()

st.subheader("🤖 Ask the AI Agent")

st.caption(
    'Try: "Convert 250 USD to EUR" or '
    '"How much is 5000 INR in JPY?"'
)

query = st.text_input(
    "Your currency question",
    placeholder="Convert 100 USD to EUR...",
)

if st.button("✨ Ask AI", key="ask_ai"):
    if not query.strip():
        st.warning("Please enter a currency question.")
    else:
        llm_with_tools = get_llm()

        if llm_with_tools is None:
            st.error(
                "HUGGINGFACEHUB_API_TOKEN is missing. "
                "Add it to your .env file to use the AI agent."
            )
        else:
            try:
                messages = [HumanMessage(content=query)]

                with st.spinner("AI is deciding which tools to use..."):
                    ai_message_1 = llm_with_tools.invoke(messages)

                messages.append(ai_message_1)

                if not ai_message_1.tool_calls:
                    st.info(ai_message_1.content)
                else:
                    # First tool call: get_conversion_factor
                    for tool_call in ai_message_1.tool_calls:
                        if tool_call["name"] == "get_conversion_factor":
                            rate_result = get_conversion_factor.invoke(
                                tool_call["args"]
                            )

                            messages.append(
                                ToolMessage(
                                    content=str(rate_result),
                                    tool_call_id=tool_call["id"],
                                )
                            )

                    # Second LLM step: use the retrieved rate.
                    with st.spinner("AI is using the exchange rate..."):
                        ai_message_2 = llm_with_tools.invoke(messages)

                    messages.append(ai_message_2)

                    # Second tool call: convert
                    for tool_call in ai_message_2.tool_calls:
                        if tool_call["name"] == "convert":
                            conversion_result = convert.invoke(
                                tool_call["args"]
                            )

                            messages.append(
                                ToolMessage(
                                    content=str(conversion_result),
                                    tool_call_id=tool_call["id"],
                                )
                            )

                    # Final response
                    with st.spinner("Generating final answer..."):
                        final_response = llm_with_tools.invoke(messages)

                    st.success(final_response.content)

                    with st.expander("🔍 See the tool-calling process"):
                        for index, message in enumerate(messages, start=1):
                            st.markdown(
                                f"**Step {index} — "
                                f"{message.__class__.__name__}**"
                            )

                            if getattr(message, "tool_calls", None):
                                for call in message.tool_calls:
                                    st.code(
                                        str(call),
                                        language="python",
                                    )
                            else:
                                st.code(
                                    str(message.content),
                                    language="text",
                                )

            except Exception as exc:
                st.error(f"AI tool-calling failed: {exc}")


# -------------------------------------------------------------------
# Features
# -------------------------------------------------------------------
st.divider()

st.subheader("🌍 What makes this project interesting?")

feature_cols = st.columns(3)

with feature_cols[0]:
    st.markdown(
        """
        <div class="feature-card">
        <h4>🌐 Global Currencies</h4>
        <p>Choose from the currencies available through the exchange-rate provider.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_cols[1]:
    st.markdown(
        """
        <div class="feature-card">
        <h4>🧠 AI Tool Calling</h4>
        <p>The Hugging Face model decides which LangChain tool to call.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_cols[2]:
    st.markdown(
        """
        <div class="feature-card">
        <h4>🔗 Sequential Tools</h4>
        <p>The exchange rate returned by one tool becomes input for the next.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(
    "Powered by Streamlit, LangChain, Hugging Face and ExchangeRate-API."
)
