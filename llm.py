import json
import re

import streamlit as st
from openai import OpenAI

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL


@st.cache_resource
def get_llm_client():
    """Create the OpenAI client configured to use Groq's API."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Add your Groq API key to the .env file."
        )

    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
    )


def parse_json_response(content):
    """Parse a JSON object, including responses wrapped in Markdown fences."""
    if not content or not content.strip():
        raise ValueError("The model returned an empty response.")

    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Be tolerant of a short sentence accidentally placed before/after JSON.
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("The model did not return a valid JSON object.")
        data = json.loads(text[start : end + 1])

    if not isinstance(data, dict):
        raise ValueError("The model response must be a JSON object.")

    return data


def normalize_career_plan(data):
    """Check required fields and normalise simple list values for the UI."""
    required_fields = [
        "profile_summary",
        "career_paths",
        "existing_skills",
        "skills_to_develop",
        "next_steps",
    ]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"Missing fields in model response: {', '.join(missing)}")

    if not isinstance(data["career_paths"], list) or not data["career_paths"]:
        raise ValueError("The model did not return any career recommendations.")

    for career in data["career_paths"]:
        if not isinstance(career, dict) or not career.get("role"):
            raise ValueError("A career recommendation is missing its role name.")
        career.setdefault("why_it_fits", "")
        career.setdefault("responsibilities", [])
        if not isinstance(career["responsibilities"], list):
            career["responsibilities"] = [str(career["responsibilities"])]

    if not isinstance(data["existing_skills"], list):
        data["existing_skills"] = []
    data["existing_skills"] = [str(skill) for skill in data["existing_skills"]]

    raw_skill_gaps = data["skills_to_develop"]
    if not isinstance(raw_skill_gaps, list):
        raw_skill_gaps = []

    skill_gaps = []
    for item in raw_skill_gaps:
        if isinstance(item, str):
            skill_gaps.append({
                "skill": item,
                "why_it_matters": "",
                "how_to_develop": "",
            })
        elif isinstance(item, dict):
            skill_gaps.append({
                "skill": str(item.get("skill", "Skill")),
                "why_it_matters": str(item.get("why_it_matters", "")),
                "how_to_develop": str(item.get("how_to_develop", "")),
            })
    data["skills_to_develop"] = skill_gaps

    if not isinstance(data["next_steps"], list):
        data["next_steps"] = []
    data["next_steps"] = [str(step) for step in data["next_steps"]]

    data["profile_summary"] = str(data.get("profile_summary", ""))
    return data


def _build_messages(profile, retrieved_context, retry=False):
    """Create a compact prompt that explicitly requests a JSON object."""
    system_prompt = """
You are a practical student career guidance assistant.
Use only the student's profile and the supplied career knowledge.

Return ONE valid JSON object only. Do not use Markdown or code fences.
The object must contain these fields:
- profile_summary: string
- career_paths: array of objects with role, why_it_fits, responsibilities
- existing_skills: array of strings
- skills_to_develop: array of objects with skill, why_it_matters, how_to_develop
- next_steps: array of strings

Recommend exactly three distinct roles. Use role names exactly as written in the
career knowledge. Explain why each fits the student's education, interests and goal.
Only list skills the student explicitly entered as existing skills. Never assume
skills they did not mention. Give practical skill gaps and clear next steps.
Do not invent certifications, course names, URLs, salaries, job vacancies or guarantees.
The learning roadmap is created by the application, so do not include a roadmap field.
Keep the language concise, useful and student-friendly.
""".strip()

    user_prompt = f"""
STUDENT PROFILE:
{json.dumps(profile, ensure_ascii=False)}

RETRIEVED CAREER KNOWLEDGE:
{retrieved_context}

Return JSON in this exact general structure:
{{
  "profile_summary": "Short profile summary",
  "career_paths": [
    {{"role": "Exact role name", "why_it_fits": "Reason", "responsibilities": ["Task"]}}
  ],
  "existing_skills": ["Skill entered by student"],
  "skills_to_develop": [
    {{"skill": "Skill", "why_it_matters": "Reason", "how_to_develop": "Practical action"}}
  ],
  "next_steps": ["Action"]
}}

Use exactly three career_paths. Return arrays even when they are empty.
""".strip()

    if retry:
        system_prompt += (
            "\nBe especially careful: the previous response was not accepted. "
            "Return valid JSON with double quotes, no trailing commas, and all five fields."
        )
        user_prompt += "\nDo not add any text before or after the JSON object."

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def generate_career_plan(profile, retrieved_context):
    """Generate and validate a career plan, retrying once if JSON is invalid."""
    client = get_llm_client()
    last_error = None

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=_build_messages(profile, retrieved_context, retry=bool(attempt)),
                # JSON Object Mode avoids brittle schema-constrained generation.
                response_format={"type": "json_object"},
                temperature=0.2,
                max_completion_tokens=3500,
            )

            content = response.choices[0].message.content
            plan = parse_json_response(content)
            return normalize_career_plan(plan)

        except Exception as error:
            last_error = error

    raise RuntimeError(
        "Groq could not return a valid career-plan response after two attempts. "
        "Please try again. Check that your selected model is available in Groq and "
        "that your API key is valid."
    ) from last_error


def answer_followup(question, profile, plan, retrieved_context, history=None):
    """Answer follow-up questions using the student's plan and career knowledge."""
    client = get_llm_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful career guidance assistant. Answer in clear, "
                "human language using the student's profile, generated career plan, "
                "and supplied career knowledge. Do not invent course links, live "
                "vacancies, salaries, or guaranteed outcomes. If information is "
                "missing, say so and suggest what the student should verify."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Student profile:\n{json.dumps(profile, ensure_ascii=False)}\n\n"
                f"Career plan:\n{json.dumps(plan, ensure_ascii=False)}\n\n"
                f"Career knowledge:\n{retrieved_context}"
            ),
        },
    ]

    if history:
        messages.extend(history[-8:])

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.5,
        max_completion_tokens=1500,
    )

    return response.choices[0].message.content or "I could not generate a response."
