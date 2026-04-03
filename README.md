# SATYA — Truth Detection Platform

> **सत्यमेव जयते — Truth Alone Triumphs**

![Version](https://img.shields.io/badge/version-2.0-orange)
![Phase](https://img.shields.io/badge/phase-2%20complete-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)
![License](https://img.shields.io/badge/license-MIT-yellow)

SATYA is an AI-powered real-time misinformation detection platform that analyzes text, news headlines, and WhatsApp forwards across 40+ sources using semantic AI verification.

---

## Demo

Paste any text → SATYA cross-checks across 40+ sources → Credibility Score + Truth Report Card

| Score | Risk Level | Meaning |
|-------|-----------|---------|
| 90–100 | 🟢 LOW RISK | Likely Authentic |
| 70–89 | 🟡 MEDIUM RISK | Mixed / Uncertain |
| 0–69 | 🔴 HIGH RISK | Likely Fake |

---

## How it works

Input  
→ AI Detection  
→ Fact Check  
→ Semantic Analysis  
→ Scoring Engine  
→ Output

---

## Features

- **AI Text Detection** — HuggingFace RoBERTa model detects AI-generated content
- **Google Fact Check** — Cross-references verified fact-check databases
- **40+ RSS News Feeds** — Indian national, Karnataka regional, and international sources
- **DuckDuckGo Search** — Real-time web evidence collection
- **Wikipedia Validation** — Factual knowledge base verification
- **Semantic Similarity** — Sentence Transformers for evidence stance classification
- **Multi-signal Scoring** — 6 signals combined into a 0–100 credibility score
- **Truth Report Card** — Beautiful dark-themed UI with animated score ring

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI |
| Frontend | HTML + CSS + JavaScript |
| AI Detection | HuggingFace RoBERTa (`openai-community/roberta-base-openai-detector`) |
| Semantic AI | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Fact Check | Google Fact Check Tools API |
| News Sources | 40+ RSS Feeds (BBC, NDTV, The Hindu, AltNews, BoomLive...) |
| Web Search | DuckDuckGo Search (free, no API key) |
| Knowledge | Wikipedia API (free, no API key) |
| Server | Uvicorn (ASGI) |

---

## Project Structure

```
satya-ai-misinformation-detector/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── routes/
│   │   └── text.py                # POST /api/text/analyze
│   ├── services/
│   │   ├── ai_detect.py           # HuggingFace AI detection
│   │   ├── fact_check.py          # Google Fact Check API
│   │   ├── evidence_collector.py  # RSS + DDG + Wikipedia
│   │   ├── semantic_check.py      # Sentence Transformers
│   │   └── verifier.py            # Orchestration layer
│   └── utils/
│       └── scorer.py              # Multi-signal scoring engine
├── frontend/
|      └── index.html                # Web frontend
├── run.py                         # Uvicorn server entry
├── requirements.txt
└── .env                           # API keys (not committed)
```

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vagish23ps/satya-ai-misinformation-detector.git
cd satya-ai-misinformation-detector
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
HF_API_KEY=your_huggingface_token_here
GOOGLE_FACT_CHECK_KEY=your_google_api_key_here
APP_ENV=development
```

**Get your API keys:**
- HuggingFace token → [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Google Fact Check API → [Google Cloud Console](https://console.cloud.google.com)

### 5. Run the server

```bash
python run.py
```

Server starts at: `http://127.0.0.1:8000`

### 6. Open the frontend

Open `frontend/index.html` using VS Code Live Server or any local server.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Live backend health check |
| POST | `/api/text/analyze` | Main text analysis |
| GET | `/docs` | Swagger UI documentation |

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/api/text/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "5G towers cause COVID-19 and governments are hiding this."}'
```

### Example Response

```json
{
  "input_text": "5G towers cause COVID-19...",
  "ai_detection": {
    "ai_probability": 0.21,
    "confidence": "low"
  },
  "fact_check": {
    "verdict": "NO DATA FOUND"
  },
  "semantic": {
    "verdict": "NO EVIDENCE",
    "supports": 0,
    "contradicts": 0
  },
  "truth_report": {
    "credibility_score": 35,
    "risk_level": "HIGH RISK",
    "verdict": "SUSPICIOUS CLAIM — Cannot be verified anywhere"
  }
}
```
---

## UI Preview (Coming Soon)

---

## News Sources (40+)

| Category | Sources |
|----------|---------|
| Indian National | NDTV, Times of India, The Hindu, Indian Express, Hindustan Times, News18, Aaj Tak, Republic TV, DD News |
| Fact Checkers | AltNews, BoomLive, AFP Fact Check, Vishvas News |
| Karnataka | Deccan Herald, Prajavani, Udayavani, OneIndia Kannada, Sahil Online |
| Government | PIB, RBI, ISRO, MEA |
| International | BBC World, Reuters, WION, Channel NewsAsia, Sputnik |
| Science/Health | WHO, NASA, USGS Earthquake Feed |
| Technology | TechCrunch, The Hacker News, Ars Technica |

---

## Scoring Engine

SATYA combines 6 signals:

1. **AI Detection** — Max -30 points (HuggingFace RoBERTa)
2. **Fact Check Verdict** — Max -40 points (Google API)
3. **Semantic Evidence** — Max ±35 points (SUPPORTS/CONTRADICTS)
4. **Evidence Quantity** — +5 bonus (3+ sources found)
5. **Danger Keywords** — Max -20 points (conspiracy patterns)
6. **Absurd Detection** — -40 points (impossible claims)


---

## Limitations

- Google Fact Check API only covers previously fact-checked viral claims
- HuggingFace RoBERTa may score short sentences as high AI probability (known model bias)
- Response time is 5-10 seconds due to parallel multi-source evidence collection
- No image, video, or audio analysis in current phase

---
## Future Improvements

- Real-time deployment (Render / Railway)
- Image & video misinformation detection
- Browser extension for instant verification
  
---
**Philosophy:** This project is inspired by the ancient Sanskrit principle *Satyameva Jayate* (Truth Alone Triumphs) — inscribed on India's national emblem. Just as Krishna served as the strategic guide to truth in the Mahabharata, SATYA aims to be the digital guide in an era of AI-generated misinformation.

---

## License

MIT License — free to use, modify, and distribute.

---

*सत्यमेव जयते — Truth Alone Triumphs*
