# Journal AI Backend

A FastAPI-based backend service that provides AI-enhanced journaling capabilities with semantic search, summarization, and interactive chat features.

## ⚡ Tech Stack
-	FastAPI - High-performance Python backend
-	Google Gemini LLM - AI-driven journal insights
-	Qdrant + SentenceTransformers - Vector search for context retrieval
-	Versioning + Testing - Scalable API

## 🚀 Features

- Journal entry creation and management
- Semantic search using Qdrant vector database
- AI-powered journal summarization using Google's Gemini Pro
- Interactive chat with your journal entries
- Firebase authentication
- Structured error handling and logging
- API versioning

## 🛠 Tech Stack

- **Framework:** FastAPI
- **Authentication:** Firebase Admin SDK
- **Vector Database:** Qdrant
- **AI Models:**
  - Google Gemini 1.5 Pro (for chat and summarization)
  - Sentence Transformer (all-MiniLM-L6-v2 for embeddings)
- **Logging:** Custom colored logging with rotation
- **Validation:** Pydantic

## 📁 Project Structure

```plaintext
src/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   └── journals.py
│       └── router.py
├── core/
│   ├── config.py
│   ├── firebase.py
│   ├── logger.py
│   └── prompt_templates.py
├── models/
│   ├── journal.py
│   └── response.py
├── services/
│   ├── gemini_service.py
│   └── qdrant_service.py
├── utils/
│   └── journal_validator.py
└── main.py
```

## ⚙️ Environment Variables

Create a `.env` file with:

```plaintext
QDRANT_URL=http://localhost:6333
FIREBASE_CREDENTIALS_BASE64=<base64_encoded_firebase_credentials>
GEMINI_API_KEY=<your_gemini_api_key>
```

## 🚀 Getting Started

1. Clone the repository
```bash
git clone https://github.com/Badar25/Journal-backend
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Start Qdrant (using Docker)
```bash
docker run -p 6333:6333 qdrant/qdrant
```

4. Run the application
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📌 API Endpoints

### Authentication
All endpoints require Firebase authentication token in the header:
```
Authorization: Bearer <firebase_token>
```

### Journals

#### Create Journal
- **POST** `/v1/journals/`
- **Body:**
```json
{
    "title": "string",
    "content": "string"
}
```

#### Update Journal
- **PUT** `/v1/journals/{journal_id}`
- **Body:**
```json
{
    "title": "string (optional)",
    "content": "string (optional)"
}
```

#### Get Journals
- **GET** `/v1/journals/`
- **Query Params:** `days` (optional, int)

#### Get Summary
- **GET** `/v1/journals/summary`
- **Query Params:** `days` (optional, int, default=7)

#### Search Journals
- **GET** `/v1/journals/search`
- **Query Params:** `query` (required), `limit` (optional, default=3)

## 🔒 Validation Rules

### Journal Content
- Title: Max 200 characters
- Content: Max 999 words
- At least one field (title or content) must be provided

## ⚠️ Error Codes

| Code | Description |
|------|-------------|
| TOKEN_EXPIRED | Authentication token has expired |
| TOKEN_REVOKED | Authentication token has been revoked |
| TOKEN_INVALID | Invalid authentication token |
| AUTH_ERROR | General authentication failure |
| EMPTY_FIELDS | Required fields are empty |
| TITLE_TOO_LONG | Title exceeds 200 characters |
| CONTENT_TOO_LONG | Content exceeds 999 words |
| MISSING_FIELDS | Required fields are missing |
| JOURNAL_NOT_FOUND | Requested journal doesn't exist |
| UNAUTHORIZED | Not authorized to access the journal |
| GEMINI_ERROR | AI processing error |
| SEARCH_ERROR | Vector search failed |
| INITIALIZATION_ERROR | Service initialization failed |

## 📊 Response Format

All API responses follow this structure:
```json
{
    "success": boolean,
    "message": string,
    "data": object | null,
    "error": string | null
}
``` 
## 🧪 Testing

Run tests using pytest:
```bash
pytest tests -v
```
