# Architecture Assistant Backend

Step 1 backend for testing a FastAPI server with Azure OpenAI.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Add your Azure OpenAI credentials to `.env`:

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=
```

Run the server:

```bash
uvicorn app.main:app --reload
```

## Test

Open:

```text
http://localhost:8000
http://localhost:8000/test-llm
```
