# 🌍 AI Currency Converter — LangChain Tool Calling + Streamlit

> **An interactive AI-powered currency converter that combines LangChain tool calling, Hugging Face LLMs, ExchangeRate-API, and Streamlit to perform real-world currency conversions.**

<p align="center">

  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-Tool%20Calling-green?logo=chainlink" alt="LangChain">
  <img src="https://img.shields.io/badge/Hugging%20Face-LLM-yellow?logo=huggingface" alt="Hugging Face">
  <img src="https://img.shields.io/badge/Streamlit-App-red?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/ExchangeRate--API-Currency%20Data-orange" alt="ExchangeRate-API">

</p>

---

## ✨ What Makes This Project Interesting?

This isn't just a traditional currency converter.

Instead of hard-coding exchange rates, the application allows an LLM to **decide which tools it needs to call** to complete a user's request.

For example:

> 💬 **"Convert 500 USD to INR"**

The AI performs the following workflow:

```text
                    👤 User
                       │
                       ▼
              🤖 Hugging Face LLM
                       │
                       ▼
             🔧 Tool: Get Rate
                       │
                       ▼
             🌐 ExchangeRate-API
                       │
                       ▼
                Exchange Rate
                       │
                       ▼
             🔧 Tool: Convert
                       │
                       ▼
                💰 Result
                       │
                       ▼
              🤖 Final AI Response
```

This demonstrates a practical **LLM → Tool → API → Tool → Response** architecture.

---

# 🚀 Features

### 💱 Smart Currency Conversion

Convert currencies from around the world using the latest available exchange-rate data.

Example:

```text
100 USD → INR
500 EUR → USD
1000 INR → GBP
250 CAD → JPY
```

---

### 🤖 AI-Powered Tool Calling

The application uses a Hugging Face-hosted LLM with LangChain's tool-calling capabilities.

The model can decide when to call:

```python
get_conversion_factor()
```

and:

```python
convert()
```

This makes the application more than a simple API wrapper.

---

### 🌎 Global Currency Support

Currency options are loaded dynamically from ExchangeRate-API rather than being manually hard-coded.

You can select:

* 🇺🇸 USD — US Dollar
* 🇮🇳 INR — Indian Rupee
* 🇪🇺 EUR — Euro
* 🇬🇧 GBP — British Pound
* 🇯🇵 JPY — Japanese Yen
* 🇨🇦 CAD — Canadian Dollar
* 🇦🇺 AUD — Australian Dollar
* and many more.

---

### 🎨 Interactive Streamlit Interface

The application provides an interactive UI with:

* Currency selectors
* Amount input
* Currency swap
* One-click conversion
* AI natural-language queries
* Exchange-rate information
* Tool-calling process visualization
* Error handling

---

### 🔄 Currency Swap

Quickly switch:

```text
USD → INR
```

to:

```text
INR → USD
```

with the swap control.

---

### 🧠 Natural Language Conversion

You don't always need to manually select currencies.

You can ask the AI:

> "Convert 250 dollars to Indian rupees."

or:

> "How much is 100 euros in Japanese yen?"

The LLM interprets the request and uses the available tools.

---

# 🛠️ Tech Stack

| Technology          | Purpose                            |
| ------------------- | ---------------------------------- |
| 🐍 Python           | Core programming language          |
| 🎈 Streamlit        | Interactive web application        |
| 🦜 LangChain        | LLM orchestration and tool calling |
| 🤗 Hugging Face     | LLM inference                      |
| 🌐 ExchangeRate-API | Currency and exchange-rate data    |
| 🔐 python-dotenv    | Environment variable management    |
| 🌍 Requests         | API communication                  |

---

# 🏗️ Project Architecture

```text
┌─────────────────────────────────────┐
│             Streamlit UI            │
│                                     │
│  Currency Selection + AI Chat       │
└──────────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Hugging Face LLM   │
        │  openai/gpt-oss-120b │
        └──────────┬───────────┘
                   │
                   │ Tool Call
                   ▼
       ┌────────────────────────┐
       │ get_conversion_factor  │
       └────────────┬───────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ ExchangeRate-API │
          └────────┬─────────┘
                   │
                   ▼
            Conversion Rate
                   │
                   ▼
          ┌──────────────────┐
          │     convert()    │
          └────────┬─────────┘
                   │
                   ▼
             Final Result
```

---

# 🔧 LangChain Tool Calling

The project defines two tools.

### 1️⃣ Get Conversion Rate

```python
@tool
def get_conversion_factor(
    base_currency: str,
    target_currency: str
) -> dict:
    ...
```

This tool retrieves the exchange rate from ExchangeRate-API.

---

### 2️⃣ Convert Amount

```python
@tool
def convert(
    base_currency_value: float,
    conversion_rate: float
) -> float:
    ...
```

This tool performs the actual mathematical conversion.

---

## 🔗 Why Two Tools?

The tools have a dependency.

The application first needs:

```text
Currency Pair
      ↓
Exchange Rate
```

before it can calculate:

```text
Amount × Exchange Rate
```

Therefore, the tool execution looks like:

```text
HumanMessage
      ↓
AIMessage
      ↓
get_conversion_factor()
      ↓
ToolMessage
      ↓
AIMessage
      ↓
convert()
      ↓
ToolMessage
      ↓
Final AIMessage
```

This demonstrates **multi-step tool orchestration**.

---

# 💻 Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/global-currency-tool-calling.git
```

Move into the project:

```bash
cd global-currency-tool-calling
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 API Configuration

Create a `.env` file in the project root:

```env
EXCHANGE_RATE_API_KEY=your_exchangerate_api_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

### ⚠️ Important

Never upload `.env` to GitHub.

The project already includes `.gitignore` to prevent accidental commits.

You can use `.env.example` as a template:

```env
EXCHANGE_RATE_API_KEY=your_exchangerate_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
```

---

# ▶️ Run the Application

Start Streamlit:

```bash
streamlit run app.py
```

The application will open in your browser.

Usually:

```text
http://localhost:8501
```

---

# 💬 Example Queries

Try asking the AI:

```text
Convert 100 USD to INR
```

```text
How much is 500 EUR in USD?
```

```text
Convert 2500 INR to GBP
```

```text
What is the exchange rate between USD and JPY?
```

```text
Convert 100 CAD to AUD
```

---

# 📊 Example Workflow

Suppose the user enters:

```text
Convert 100 USD to INR
```

The application performs:

### Step 1 — LLM identifies the required tool

```text
get_conversion_factor
```

### Step 2 — API request

```text
USD → INR
```

### Step 3 — ExchangeRate-API returns the rate

```text
conversion_rate = ...
```

### Step 4 — Conversion tool executes

```text
100 × conversion_rate
```

### Step 5 — Final AI response

```text
100 USD = ... INR
```

---

# 📁 Project Structure

```text
global-currency-tool-calling/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .env.example            # Environment variable template
├── .gitignore              # Files ignored by Git
└── .env                    # Local secrets - NOT committed
```

---

# 🌐 Deployment

This application if deployed using **Streamlit Community Cloud**.

### Basic deployment process

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Connect your GitHub repository.
4. Select:

```text
app.py
```

as the main file.
5. Add your secrets.
6. Deploy.

For Streamlit Cloud secrets, add:

```toml
EXCHANGE_RATE_API_KEY = "your_api_key"
HUGGINGFACEHUB_API_TOKEN = "your_huggingface_token"
```

---

# 🔒 Security

API keys should **never** be hard-coded.

❌ Don't do this:

```python
api_key = "abc123..."
```

✅ Use environment variables:

```python
api_key = os.getenv("EXCHANGE_RATE_API_KEY")
```

and keep:

```text
.env
```

inside `.gitignore`.

---

# 🧪 Error Handling

The application handles common problems such as:

* Missing API keys
* Invalid currency codes
* API failures
* Network errors
* Unsupported currency pairs
* Missing Hugging Face credentials

This prevents API failures from crashing the entire application.

---

# 🚧 Future Improvements

Some possible improvements:

* 📈 Historical exchange-rate charts
* 📊 Currency trend visualization
* 🌎 Country flags
* ⭐ Favorite currencies
* 🕘 Conversion history
* 💬 Persistent AI chat history
* 🧮 Multi-currency conversion
* 📱 Improved mobile UI
* ⚡ Streaming AI responses
* 💾 Database-backed conversion history
* 🪙 Cryptocurrency support
* 🔔 Exchange-rate alerts

---

# 🎯 What I Learned

Building this project helped me understand and practice:

* LLM tool calling
* LangChain tools
* Multi-step agent workflows
* Hugging Face inference
* REST API integration
* Streamlit application development
* Environment-variable management
* API error handling
* Git and GitHub workflows
* Building AI applications around real-world APIs

---

# 🌟 Why This Project?

Many AI demos only show:

```text
User → LLM → Answer
```

This project explores a more practical pattern:

```text
User
 ↓
LLM
 ↓
Tool
 ↓
External API
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

This architecture is useful for building AI applications that need access to **real-world data and external services**.

---

# 📌 Project Highlights

```text
🤖 AI-powered
🔧 Tool calling
🌎 Global currencies
🌐 Real API integration
🎨 Interactive UI
🦜 LangChain
🤗 Hugging Face
🎈 Streamlit
🔐 Secure API configuration
```

---

# 👨‍💻 Author

**Yash Rajan**

AI/ML Enthusiast | Python | LangChain | Generative AI | Machine Learning

I'm actively building projects around:

* 🤖 Artificial Intelligence
* 🧠 Machine Learning
* 🦜 LangChain
* 🤗 Hugging Face
* 🔎 RAG
* 💬 LLM Applications
* 🐍 Python

---

## ⭐ If You Found This Project Interesting

Give the repository a ⭐ and feel free to explore the code!

If you have suggestions or ideas for improving the project, feel free to open an issue or submit a pull request.

---

<p align="center">

### 🚀 Built with Python + LangChain + Hugging Face + Streamlit

</p>
