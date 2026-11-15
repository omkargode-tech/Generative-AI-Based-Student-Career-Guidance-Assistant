import html

import streamlit as st

from career_guidance import (
    build_learning_roadmap,
    create_career_plan,
    get_recommended_role_records,
)
from llm import answer_followup


st.set_page_config(
    page_title="Career Compass",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    :root {
        --ink: #193746;
        --muted: #6D7D86;
        --line: #E3EBED;
        --paper: #FFFFFF;
        --canvas: #F5F8F8;
        --sidebar: #F0F6F5;
        --teal: #267A73;
        --teal-dark: #1D655F;
        --teal-soft: #E3F2EF;
        --peach-soft: #FFF0E8;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--canvas);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
    .main .block-container {
        max-width: 1080px;
        padding-top: 1.65rem;
        padding-bottom: 2.4rem;
    }

    h1, h2, h3, h4, label { color: var(--ink); }
    h1 {
        font-size: 2.05rem;
        font-weight: 720;
        letter-spacing: -0.045em;
        margin-bottom: .25rem;
    }
    h2, h3 { letter-spacing: -0.025em; font-weight: 680; }
    [data-testid="stCaptionContainer"] p { color: var(--muted); }

    h1, .subheading{
        text-align: center;
    }

    
    .brand {
        display: flex;
        align-items: center;
        gap: .65rem;
        margin: .1rem 0 1.5rem;
        color: var(--ink);
        font-size: 1.05rem;
        font-weight: 750;
    }
    .brand-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.1rem;
        height: 2.1rem;
        border-radius: .75rem;
        background: var(--teal);
        color: #fff;
        font-size: 1.1rem;
    }
    .eyebrow {
        color: var(--teal);
        font-size: .72rem;
        font-weight: 750;
        letter-spacing: .13em;
        margin-bottom: .35rem;
        text-transform: uppercase;
    }
    .subheading {
        color: var(--muted);
        font-size: .98rem;
        margin-top: -.15rem;
        margin-bottom: 2rem;
    }
    .empty-state {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        margin-top: 1.1rem;
    }
    .empty-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 3rem;
        height: 3rem;
        border-radius: 1rem;
        background: var(--teal-soft);
        color: var(--teal-dark);
        font-size: 1.45rem;
        margin-bottom: .7rem;
    }
    .skill-chip {
        display: inline-block;
        background: var(--teal-soft);
        color: var(--teal-dark);
        border: 1px solid #D2E9E4;
        padding: .32rem .68rem;
        margin: .16rem .16rem .16rem 0;
        border-radius: 999px;
        font-size: .82rem;
        font-weight: 600;
    }
    .job-link {
        display: inline-block;
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: .5rem .8rem;
        margin: .2rem .25rem .2rem 0;
        color: var(--teal-dark) !important;
        font-size: .88rem;
        font-weight: 650;
        text-decoration: none;
    }
    .job-link:hover {
        background: var(--teal-soft);
        border-color: #C7E3DD;
        text-decoration: none;
    }

    [data-testid="stForm"] {
        border: 0;
        padding: 0;
        background: transparent;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #FFFFFF;
        border: 1px solid #DCE7E6;
        border-radius: 10px;
    }
    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus {
        border-color: var(--teal);
        box-shadow: 0 0 0 1px var(--teal);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: .35rem;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background: #FFFFFF;
        border: 1px solid #DCE7E6;
        border-radius: 999px;
        padding: .2rem .58rem;
        margin: 0;
        min-height: 1.9rem;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: var(--teal-soft);
        border-color: #B9DCD5;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: var(--teal-dark);
        font-weight: 700;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: .78rem;
        margin: 0;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none; }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background: var(--teal);
        color: #FFFFFF;
        border: 1px solid var(--teal);
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.65rem;
        box-shadow: 0 3px 9px rgba(38, 122, 115, .12);
        transition: background .15s ease, transform .15s ease;
    }
    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: var(--teal-dark);
        border-color: var(--teal-dark);
        color: #FFFFFF;
        transform: translateY(-1px);
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(25, 55, 70, .025);
    }
    [data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 11px;
    }
    [data-testid="stTabs"] button { font-weight: 650; }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--teal-dark);
        background: var(--teal-soft);
        border-radius: 9px 9px 0 0;
    }
    [data-testid="stChatMessage"] {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 13px;
        padding: .7rem .9rem;
    }
    [data-testid="stAlert"] { border-radius: 11px; }
    a { color: var(--teal-dark) !important; font-weight: 600; }
    a:hover { color: #124A45 !important; }
    hr { border-color: var(--line); }

    @media (max-width: 760px) {
        .main .block-container { padding: 1rem 1rem 2rem; }
        h1 { font-size: 1.75rem; }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


QUALIFICATIONS = ["Diploma", "Undergraduate", "Graduate", "Postgraduate", "Other"]
INDUSTRIES = [
    "Technology",
    "Finance and Banking",
    "Automotive",
    "Business and Consulting",
    "Manufacturing",
    "Healthcare",
    "Design and Media",
    "Other / Not sure",
]


def render_sidebar_form():
    """Collect only the profile information needed for career guidance."""
    with st.sidebar:
        st.markdown(
            '<div class="brand"><span class="brand-icon">✦</span>'
            '<span>Career Compass</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown("**Your profile**")

        with st.form("student_profile"):
            qualification = st.radio(
                "Qualification",
                QUALIFICATIONS,
                horizontal=True,
                label_visibility="visible",
            )
            department = st.text_input(
                "Field of study",
                placeholder="e.g. Computer Science, B.Com",
            )
            skills = st.text_area(
                "Skills (optional)",
                placeholder="e.g. Python, Excel, communication",
                height=62,
            )
            interests = st.text_area(
                "Interests",
                placeholder="e.g. AI, finance, automobiles",
                height=62,
            )
            preferred_industry = st.selectbox("Preferred industry", INDUSTRIES)
            career_goal = st.text_input(
                "Career goal (optional)",
                placeholder="e.g. Become a data analyst",
            )
            submitted = st.form_submit_button(
                "Create my career plan",
                use_container_width=True,
            )

    profile = {
        "qualification": qualification,
        "department": department.strip(),
        "skills": skills.strip(),
        "interests": interests.strip(),
        "preferred_industry": preferred_industry,
        "career_goal": career_goal.strip(),
    }
    return submitted, profile


# def render_header(has_plan=False):
#     if has_plan:
#         st.markdown('<div class="eyebrow">YOUR PERSONAL CAREER PLAN</div>', unsafe_allow_html=True)
#         st.title("Your next step, mapped out.")
#         st.markdown('<div class="subheading">Career options and practical steps based on your profile.</div>', unsafe_allow_html=True)
#     else:
#         st.markdown('<div class="eyebrow">CAREER COMPASS</div>', unsafe_allow_html=True)
#         st.title("Find a direction that fits.")
#         st.markdown('<div class="subheading">A few details can help you find your next career step.</div>', unsafe_allow_html=True)


def render_header(has_plan=False):
    if has_plan:
        # st.markdown('<div class="eyebrow">YOUR PERSONAL CAREER PLAN</div>', unsafe_allow_html=True)
        st.title("CAREER COMPASS")
        st.markdown('<div class="subheading">Career options and practical steps based on your profile.</div>', unsafe_allow_html=True)
    else:
        # st.markdown('<div class="eyebrow">CAREER COMPASS</div>', unsafe_allow_html=True)
        st.title("CAREER COMPASS")
        st.markdown('<div class="subheading">A few details can help you find your next career step.</div>', unsafe_allow_html=True)




def render_empty_state():
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-icon">✦</div>'
        '<h3 style="margin:.1rem 0 .35rem;color:#193746">Your career plan starts here</h3>'
        '<p style="margin:0;color:#6D7D86">Fill in your profile on the left and select <b>Create my career plan</b>.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_role_cards(plan):
    recommendations = plan.get("career_paths", [])[:3]
    if not recommendations:
        st.caption("No career paths were returned. Please generate the plan again.")
        return

    st.subheader("Career matches")
    columns = st.columns(len(recommendations))
    for index, (column, recommendation) in enumerate(zip(columns, recommendations), start=1):
        with column:
            with st.container(border=True):
                st.markdown(
                    f'<div class="eyebrow" style="margin-bottom:.35rem">OPTION {index}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"#### {recommendation.get('role', 'Career option')}")
                st.write(recommendation.get("why_it_fits", ""))
                responsibilities = recommendation.get("responsibilities", [])
                if responsibilities:
                    with st.expander("What you could do"):
                        for item in responsibilities[:4]:
                            st.markdown(f"- {item}")


def render_skill_chips(skills):
    if not skills:
        st.caption("No current skills were entered.")
        return
    chips = "".join(
        f'<span class="skill-chip">{html.escape(str(skill))}</span>'
        for skill in skills
    )
    st.markdown(chips, unsafe_allow_html=True)


def render_skill_gap(plan):
    st.subheader("Your skills")
    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown("**Already in your profile**")
            render_skill_chips(plan.get("existing_skills", []))

    with right:
        with st.container(border=True):
            st.markdown("**Skills to build next**")
            missing = plan.get("skills_to_develop", [])
            if not missing:
                st.caption("No additional skill gaps were returned.")
            else:
                for item in missing:
                    st.markdown(f"**{item.get('skill', 'Skill')}**")
                    if item.get("why_it_matters"):
                        st.caption(item["why_it_matters"])
                    if item.get("how_to_develop"):
                        with st.expander("How to develop it"):
                            st.write(item["how_to_develop"])


def render_roadmap(plan):
    roadmap = plan.get("roadmap", [])
    if not roadmap:
        st.caption("No roadmap stages were returned.")
        return

    for index, item in enumerate(roadmap, start=1):
        number_col, content_col = st.columns([0.08, 0.92])
        with number_col:
            st.markdown(
                f'<div style="background:#E3F2EF;color:#1D655F;'
                f'border-radius:10px;padding:.48rem .35rem;text-align:center;'
                f'font-weight:750;margin-top:.35rem">{index:02d}</div>',
                unsafe_allow_html=True,
            )
        with content_col:
            with st.container(border=True):
                duration = item.get("duration", "")
                st.markdown(f"#### {item.get('stage', 'Learning stage')}")
                if duration:
                    st.caption(duration)
                if item.get("focus"):
                    st.markdown(item["focus"])
                activities = item.get("activities", [])
                if activities:
                    for activity in activities:
                        st.markdown(f"- {activity}")
                if item.get("project"):
                    st.info(f"Project: {item['project']}", icon="💡")


def render_learning_resources(role_records, knowledge_base):
    portal_lookup = {
        item["name"]: item for item in knowledge_base.get("learning_portals", [])
    }

    if not role_records:
        st.caption("No matching learning resources found.")
        return

    for role in role_records:
        with st.expander(role["role"]):
            links = []
            for portal_name in role.get("learning_resources", []):
                portal = portal_lookup.get(portal_name)
                if portal:
                    links.append(f"- [{portal['name']}]({portal['url']})")
            if links:
                st.markdown("**Learn**\n" + "\n".join(links))

            certifications = role.get("certifications", [])
            if certifications:
                st.markdown("**Certifications to explore**")
                for certification in certifications:
                    st.markdown(f"- [{certification['name']}]({certification['url']})")


def render_job_resources(knowledge_base):
    resources = knowledge_base.get("job_search_resources", [])
    if not resources:
        return

    links = "".join(
        f'<a class="job-link" href="{html.escape(item["url"], quote=True)}" '
        f'target="_blank" rel="noopener noreferrer">{html.escape(item["name"])}</a>'
        for item in resources
    )
    st.markdown(links, unsafe_allow_html=True)


def render_chat(profile, plan, retrieved_context):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.session_state.chat_history:
        clear_col, _ = st.columns([1, 5])
        with clear_col:
            if st.button("Clear conversation", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask about your career plan...")
    if question:
        previous_history = st.session_state.chat_history.copy()
        st.session_state.chat_history.append({"role": "user", "content": question})

        try:
            with st.spinner("Thinking..."):
                answer = answer_followup(
                    question,
                    profile,
                    plan,
                    retrieved_context,
                    history=previous_history,
                )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )
        except Exception as error:
            st.session_state.chat_history.append(
                {"role": "assistant", "content": f"I couldn't answer that: {error}"}
            )
        st.rerun()


def render_career_plan():
    plan = st.session_state.plan
    profile = st.session_state.profile
    knowledge_base = st.session_state.knowledge_base
    retrieved_context = st.session_state.retrieved_context

    if len(plan.get("roadmap", [])) < 3:
        plan["roadmap"] = build_learning_roadmap(profile, plan, knowledge_base)
        plan["roadmap_for"] = (
            plan.get("career_paths", [{}])[0].get("role", "your recommended career")
            if plan.get("career_paths")
            else "your recommended career"
        )

    if plan.get("profile_summary"):
        st.caption(plan["profile_summary"])

    matches_tab, roadmap_tab, resources_tab, chat_tab = st.tabs(
        ["Career matches", "Learning roadmap", "Resources", "Ask AI"]
    )

    with matches_tab:
        render_role_cards(plan)
        st.divider()
        render_skill_gap(plan)
        next_steps = plan.get("next_steps", [])[:3]
        if next_steps:
            st.divider()
            st.subheader("Your next steps")
            for item in next_steps:
                st.markdown(f"- {item}")

    with roadmap_tab:
        roadmap_role = plan.get("roadmap_for", "your recommended career")
        st.subheader(f"Learning roadmap for {roadmap_role}")
        st.caption("A simple three-stage path from learning the basics to building a portfolio.")
        render_roadmap(plan)

    with resources_tab:
        role_records = get_recommended_role_records(plan, knowledge_base)
        st.subheader("Learning and certification")
        render_learning_resources(role_records, knowledge_base)
        st.divider()
        st.subheader("Job search")
        st.markdown(
            '<p style="color:#6D7D86;font-size:.9rem;margin-top:-.5rem">'
            'Search current openings on these platforms.</p>',
            unsafe_allow_html=True,
        )
        render_job_resources(knowledge_base)

    with chat_tab:
        st.subheader("Ask about your plan")
        st.caption("Get more detail about a role, skill or learning step.")
        render_chat(profile, plan, retrieved_context)


def main():
    submitted, profile = render_sidebar_form()
    has_plan = "plan" in st.session_state
    render_header(has_plan=has_plan)

    if submitted:
        if not profile["department"] or not profile["interests"]:
            st.warning("Please enter your field of study and interests.")
        else:
            try:
                with st.spinner("Putting your career plan together..."):
                    plan, matches, knowledge_base, retrieved_context = create_career_plan(profile)

                st.session_state.profile = profile
                st.session_state.plan = plan
                st.session_state.matches = matches
                st.session_state.knowledge_base = knowledge_base
                st.session_state.retrieved_context = retrieved_context
                st.session_state.chat_history = []
                st.rerun()
            except Exception as error:
                st.error(f"Could not generate your career plan: {error}")

    if "plan" in st.session_state:
        render_career_plan()
    else:
        render_empty_state()


if __name__ == "__main__":
    main()
