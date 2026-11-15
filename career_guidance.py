from knowledge_base import load_knowledge_base
from vector_store import get_collection, index_career_roles, retrieve_roles
from llm import generate_career_plan


def build_profile_text(profile):
    """Create a natural-language search query from the student's form values."""
    return "\n".join(
        [
            f"Qualification: {profile.get('qualification', '')}",
            f"Department: {profile.get('department', '')}",
            f"Current skills: {profile.get('skills', '')}",
            f"Interests: {profile.get('interests', '')}",
            f"Preferred industry: {profile.get('preferred_industry', '')}",
            f"Career goal: {profile.get('career_goal', '')}",
        ]
    )


def _get_primary_role(plan, knowledge_base):
    """Find the curated record for the first recommended career role."""
    roles_by_name = {
        role["role"].strip().casefold(): role
        for role in knowledge_base.get("roles", [])
    }

    for recommendation in plan.get("career_paths", []):
        role_name = recommendation.get("role", "").strip().casefold()
        if role_name in roles_by_name:
            return roles_by_name[role_name]

    return None


def build_learning_roadmap(profile, plan, knowledge_base):
    """Build a reliable three-stage roadmap using the recommended role data."""
    role = _get_primary_role(plan, knowledge_base)
    role_name = role["role"] if role else (profile.get("career_goal") or "your target career")

    role_skills = role.get("skills", []) if role else []
    gap_skills = [
        item.get("skill", "")
        for item in plan.get("skills_to_develop", [])
        if isinstance(item, dict) and item.get("skill")
    ]
    focus_skills = gap_skills[:3] or role_skills[:3]
    skill_text = ", ".join(focus_skills) if focus_skills else "the core skills for this role"

    project_ideas = role.get("project_ideas", []) if role else []
    portfolio_project = (
        project_ideas[0]
        if project_ideas
        else f"Build a small portfolio project that demonstrates the key skills for {role_name}."
    )
    practice_project = (
        project_ideas[1]
        if len(project_ideas) > 1
        else f"Complete a small practical exercise using {skill_text}."
    )

    return [
        {
            "stage": "1. Build your foundation",
            "duration": "Weeks 1–2",
            "focus": f"Understand the fundamentals of {role_name} and get comfortable with the essential concepts and tools.",
            "activities": [
                f"Learn the core concepts behind {role_name}.",
                f"Start developing these important skills: {skill_text}.",
                "Follow beginner lessons and practise a little each day.",
            ],
            "project": "Complete a small guided exercise to apply the basics you have learned.",
        },
        {
            "stage": "2. Practise and apply your skills",
            "duration": "Weeks 3–5",
            "focus": f"Move from basic understanding to practical work related to {role_name}.",
            "activities": [
                f"Practise {skill_text} through guided exercises and independent tasks.",
                "Work with realistic examples, data or scenarios from the chosen field.",
                "Review your work and note the areas that need more practice.",
            ],
            "project": practice_project,
        },
        {
            "stage": "3. Build your portfolio and prepare",
            "duration": "Weeks 6–8",
            "focus": f"Demonstrate your ability to perform practical work in {role_name}.",
            "activities": [
                "Complete one end-to-end project and document how you approached it.",
                "Prepare a short portfolio or project summary that shows your skills.",
                "Review relevant job descriptions and practise explaining your work.",
            ],
            "project": portfolio_project,
        },
    ]


def create_career_plan(profile):
    """Retrieve relevant roles, generate recommendations and add a 3-stage roadmap."""
    knowledge_base = load_knowledge_base()
    roles = knowledge_base["roles"]

    collection = get_collection()
    index_career_roles(collection, roles)

    profile_text = build_profile_text(profile)
    matches = retrieve_roles(collection, profile_text)

    if not matches:
        raise ValueError("The career knowledge base is empty. Please check career_data.json.")

    retrieved_context = "\n\n---\n\n".join(
        item["document"] for item in matches
    )

    plan = generate_career_plan(profile, retrieved_context)

    # The roadmap is built by the app, so it always has three clear learning stages.
    plan["roadmap"] = build_learning_roadmap(profile, plan, knowledge_base)
    plan["roadmap_for"] = (
        plan["career_paths"][0].get("role", "your recommended career")
        if plan.get("career_paths")
        else "your recommended career"
    )

    return plan, matches, knowledge_base, retrieved_context


def get_recommended_role_records(plan, knowledge_base):
    """Find the curated data records that match the roles chosen by the LLM."""
    role_lookup = {
        role["role"].strip().casefold(): role
        for role in knowledge_base["roles"]
    }

    selected = []
    for recommendation in plan.get("career_paths", [])[:3]:
        role = role_lookup.get(recommendation.get("role", "").strip().casefold())
        if role:
            selected.append(role)

    return selected
