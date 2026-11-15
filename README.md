# Generative AI-Based Student Career Guidance Assistant

A simple AI-powered career guidance app. Enter your education, skills and interests to get career matches, a skill-gap review and a practical learning roadmap.

## Features

- Three personalised career suggestions.
- Existing skills and skills to develop.
- A guaranteed three-stage learning roadmap with projects and career preparation.
- Curated learning, certification and job-search links.
- Follow-up chat about your career plan.

## Setup (Windows)

```powershell
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
copy .env.example .env
```

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Run the app:

```powershell
streamlit run app.py
```

The first run downloads the local Sentence Transformers embedding model. ChromaDB creates `chroma_db/` automatically.

## Project files

```text
career_guidance_assistant/
├── app.py
├── career_guidance.py
├── llm.py
├── embeddings.py
├── vector_store.py
├── knowledge_base.py
├── config.py
├── requirements.txt
├── .env.example
├── data/
│   └── career_data.json
└── .streamlit/
    └── config.toml
```

## How it works

1. Streamlit collects the student's profile.
2. Sentence Transformers creates local embeddings.
3. ChromaDB retrieves relevant career information.
4. Groq returns a JSON career plan using JSON Object Mode, with validation and one retry if the response is incomplete.
5. The app builds a role-specific three-stage roadmap from the recommended role, skill gaps and curated project ideas.
6. Streamlit displays career matches, skill gaps, the roadmap and useful links.

Career guidance is informational and does not guarantee employment. Check course details and job openings with the providers and employers.

