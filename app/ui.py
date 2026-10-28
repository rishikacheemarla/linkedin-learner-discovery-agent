import json, os, streamlit as st
from dotenv import load_dotenv
from app.services.search_service import search_profiles
from app.services.persona_scorer import score_profile
from app.database.db import daily_count, MAX_DAILY_SENDS, is_contacted, record_contact, contact_history
from app.utils.query_builder import suggested_queries

load_dotenv()
st.set_page_config(page_title="Learner Discovery Agent", page_icon="🎓", layout="wide")
st.title("LinkedIn Learner Discovery & AI Outreach Agent")
st.caption("Public-search discovery • AI-assisted personalization • Human-reviewed outreach")
with st.sidebar:
    persona = st.selectbox("Target persona", ["Fresher", "1-2_YOE", "Career_Switcher"])
    keywords = st.text_input("Optional search keyword")
    use_mock = st.toggle("Offline demo mode", value=os.getenv("USE_MOCK_DATA","true").lower()=="true")
    st.info("No LinkedIn login, scraping of authenticated pages, or automated sending.")
    st.write("Suggested X-ray queries")
    for q in suggested_queries(persona): st.code(q)
if "profiles" not in st.session_state: st.session_state.profiles = []
if "payloads" not in st.session_state: st.session_state.payloads = []
if st.button("Discover profiles", type="primary"):
    try:
        profiles, source = search_profiles(persona, keywords, use_mock)
        st.session_state.profiles, st.session_state.payloads = profiles, []
        st.success(f"Loaded {len(profiles)} profiles from {source}.")
    except Exception as e: st.error(f"Search failed: {e}")
if st.session_state.profiles:
    if st.button("Score profiles and draft messages"):
        st.session_state.payloads = [score_profile(p) for p in st.session_state.profiles]
    for i, p in enumerate(st.session_state.profiles):
        with st.container(border=True):
            st.subheader(p.name); st.write(p.headline); st.write(p.snippet)
            st.link_button("Open LinkedIn profile", p.url)
            if i < len(st.session_state.payloads):
                x = st.session_state.payloads[i]
                st.write(f"Persona: {x.detected_persona} | Relevance: {x.relevance_score}/10")
                st.caption(x.reasoning)
                note = st.text_area("Connection note (under 300 characters)", x.connection_note, key=f"note{i}", max_chars=299)
                dm = st.text_area("Follow-up DM (under 100 words)", x.follow_up_dm, key=f"dm{i}")
                st.caption(f"Note: {len(note)} characters • DM: {len(dm.split())} words")
                st.info("Copy the note, open the profile, review it, and send manually if appropriate.")
                if is_contacted(p.url): st.warning("Already recorded as contacted.")
                elif daily_count() >= MAX_DAILY_SENDS: st.error("Daily contact-recording limit reached.")
                else:
                    checked = st.checkbox("I manually sent this message", key=f"sent{i}")
                    if st.button("Record completed outreach", key=f"record{i}", disabled=not checked):
                        try:
                            record_contact(p.url, p.name); st.success("Recorded."); st.rerun()
                        except ValueError as e: st.error(str(e))
with st.expander("Contact history"):
    rows = contact_history()
    st.dataframe([{"Name":r[0],"URL":r[1],"Status":r[2],"Recorded":r[3]} for r in rows], use_container_width=True)
with st.expander("Export generated payloads"):
    if st.session_state.payloads:
        st.download_button("Download JSON", json.dumps([x.model_dump() for x in st.session_state.payloads], indent=2),
                           "outreach_payloads.json", "application/json")
