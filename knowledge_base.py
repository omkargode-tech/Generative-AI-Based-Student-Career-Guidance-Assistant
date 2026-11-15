import json

from config import CAREER_DATA_PATH


def load_knowledge_base():
    """Read the career roles and resource links from the JSON file."""
    with open(CAREER_DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def role_to_document(role):
    """Turn one career-role record into searchable text for ChromaDB."""
    certifications = [item["name"] for item in role.get("certifications", [])]
    resources = role.get("learning_resources", [])

    return f"""
Career role: {role['role']}
Industries: {', '.join(role.get('industries', []))}
Typical qualifications: {'; '.join(role.get('qualifications', []))}
Responsibilities: {'; '.join(role.get('responsibilities', []))}
Required and useful skills: {', '.join(role.get('skills', []))}
Certifications to explore: {'; '.join(certifications) if certifications else 'No single certification is essential for this role.'}
Learning resources: {', '.join(resources)}
Portfolio project ideas: {'; '.join(role.get('project_ideas', []))}
""".strip()
