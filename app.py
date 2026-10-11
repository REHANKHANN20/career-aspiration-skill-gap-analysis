"""
Career Aspiration & Skill Gap Analysis for Youth — Interactive Web Application
Community Engagement Project (CEP) — Final Semester Data Science Capstone
Architecture: Dual-Layer Decision Support System (Stateless Cloud-Native Web Application)
Deployment: GitHub Repository -> Streamlit Community Cloud (24x7 Public Access)
"""

import os
import sys
import json
import re
import pandas as pd
import streamlit as st

# Configure relative project paths (Cloud-Safe, Zero Hardcoded Workstation Paths)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
MODEL_DIR = os.path.join(APP_DIR, "model")

if MODEL_DIR not in sys.path:
    sys.path.append(MODEL_DIR)

from career_readiness_model import CareerReadinessModel

# -----------------------------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Youth Career Readiness & Skill Gap Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CACHED DATA & MODEL LOADERS
# -----------------------------------------------------------------------------
@st.cache_resource
def load_readiness_model():
    catalog_path = os.path.join(MODEL_DIR, "career_skills_catalog.json")
    matrix_path = os.path.join(MODEL_DIR, "interactive_role_competency_matrix.json")
    return CareerReadinessModel(catalog_path, matrix_path)

@st.cache_data
def load_survey_data():
    csv_path = os.path.join(DATA_DIR, "survey_cleaned_public.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

@st.cache_data
def load_role_matrix_data():
    csv_path = os.path.join(DATA_DIR, "role_competency_matrix.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

model = load_readiness_model()
df_survey = load_survey_data()
df_role_matrix = load_role_matrix_data()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.title("🎓 Career Navigator")
st.sidebar.markdown("**Community Engagement Project (CEP)**")
st.sidebar.caption("An explainable, decision-support tool bridging youth career ambitions with industry competencies.")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Navigation Menu:",
    [
        "🎯 Career Readiness Assessment",
        "📊 Survey Analytics & Insights",
        "🗺️ Career Competency Framework",
        "ℹ️ Research Methodology & Framework"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Project Classification:** Final-Year Capstone\n\n"
    "**Architecture:** Dual-Layer MCDA System\n\n"
    "**Status:** Cloud Deployed (24×7 Access)"
)

# =============================================================================
# MODULE 1: CAREER READINESS ASSESSMENT (LAYER 2: ROLE-SPECIFIC BENCHMARKS)
# =============================================================================
if app_mode == "🎯 Career Readiness Assessment":
    st.title("🎯 Role-Specific Career Readiness & Skill Gap Assessment")
    st.markdown(
        "Evaluate your self-declared competencies against standardized industry role benchmarks. "
        "Receive an explainable **Readiness Index**, identify prioritized skill gaps, and explore tailored development milestones."
    )
    st.markdown("---")

    col_cfg1, col_cfg2 = st.columns([1, 1], gap="large")

    with col_cfg1:
        st.subheader("1. Target Career Role")
        role_options = model.available_roles
        selected_role = st.selectbox(
            "Select your target career role / specialization:",
            options=role_options,
            index=0 if role_options else 0,
            help="Choose the specific occupational role you aspire to pursue."
        )

        role_info = model.interactive_roles[selected_role]
        req_skills_info = role_info["skills"]
        req_skills_names = [s["skill"] for s in req_skills_info]
        total_career_points = role_info["total_weighted_points"]
        parent_track = role_info.get("career_track", "Broad Career Track")

        st.caption(
            f"📌 **Track:** {parent_track} | **Role Benchmark:** requires **{len(req_skills_names)} competencies** "
            f"totaling **{total_career_points} weighted points**."
        )
        if role_info.get("description"):
            st.info(f"💡 **Role Overview:** {role_info['description']}")

    with col_cfg2:
        st.subheader("2. Self-Assessed Skill Proficiency")
        proficiency_level = st.select_slider(
            "Rate your overall practical proficiency in the skills you possess:",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: {
                1: "Level 1: Novice (50% credit)",
                2: "Level 2: Developing (50% credit)",
                3: "Level 3: Competent / Intermediate (80% credit)",
                4: "Level 4: Proficient (100% credit)",
                5: "Level 5: Advanced (100% credit)"
            }[x],
            help="Higher proficiency earns full credit multipliers under the deterministic evaluation model."
        )
        st.caption("ℹ️ *Self-reported score represents a weighted competency coverage index based on self-declaration.*")

    st.markdown("---")
    st.subheader("3. Current Competency Inventory")
    st.markdown(f"Select all competencies you currently possess for **{selected_role}**:")

    # Quick action buttons for easy selection
    q_btn1, q_btn2, q_btn3 = st.columns([1, 1, 3])
    with q_btn1:
        btn_all = st.button("Select All", use_container_width=True)
    with q_btn2:
        btn_core = st.button("Select Core Only", use_container_width=True)
    with q_btn3:
        btn_clear = st.button("Clear Selection", use_container_width=False)

    # Session state initialization for skill selection
    state_key = f"skills_sel_{selected_role}"
    if state_key not in st.session_state or btn_clear:
        st.session_state[state_key] = []
    if btn_all:
        st.session_state[state_key] = list(req_skills_names)
    if btn_core:
        st.session_state[state_key] = [s["skill"] for s in req_skills_info if s["weight"] == 3]

    # Formatted options with tier tags
    skill_display_map = {}
    for s in req_skills_info:
        w_tag = "[Core — Weight 3]" if s["weight"] == 3 else ("[Important — Weight 2]" if s["weight"] == 2 else "[Foundational — Weight 1]")
        label = f"{s['skill']}  {w_tag}"
        skill_display_map[label] = s["skill"]

    default_selected = [
        label for label, s_name in skill_display_map.items()
        if s_name in st.session_state[state_key]
    ]

    selected_labels = st.multiselect(
        "Possessed Competencies:",
        options=list(skill_display_map.keys()),
        default=default_selected,
        help="Search and pick all skills you currently have hands-on familiarity with."
    )
    chosen_skills = [skill_display_map[lbl] for lbl in selected_labels]
    st.session_state[state_key] = chosen_skills

    st.markdown("<br>", unsafe_allow_html=True)

    # Calculate Evaluation Results in Real Time (Layer 2)
    results = model.evaluate_interactive_role(selected_role, chosen_skills, proficiency_level)

    score = results["readiness_score"]
    tier = results["readiness_tier"]
    tier_desc = results["tier_description"]
    strong_skills = results["strong_skills"]
    skills_to_strengthen = results["skills_to_strengthen"]
    skill_gaps = results["skill_gaps"]
    roadmap_1m = results["roadmap_1_month"]
    roadmap_3m = results["roadmap_3_month"]

    # Assessment Results Cards
    st.subheader("📊 Diagnostic Evaluation Results")

    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    with res_col1:
        st.metric("Readiness Index", f"{score:.1f}%")
    with res_col2:
        st.metric("Readiness Tier", tier)
    with res_col3:
        st.metric("Matched Competencies", f"{len(strong_skills) + len(skills_to_strengthen)} / {len(req_skills_names)}")
    with res_col4:
        st.metric("Critical Gaps", f"{len(skill_gaps)}")

    st.progress(score / 100.0)
    st.caption(f"**Interpretation:** {tier_desc}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Two-Column Detailed Breakdown
    col_diag1, col_diag2 = st.columns(2, gap="large")

    with col_diag1:
        st.success("### ✅ Possessed Competencies")
        if strong_skills:
            st.markdown("**Full Credit Earned (Proficient/Advanced):**")
            for s in strong_skills:
                st.markdown(f"- **{s['skill']}** `(Weight: {s['weight']}, Earned: {s['points_earned']:.1f} pts)`")
        if skills_to_strengthen:
            st.markdown(f"**Partial Credit Earned (Level {proficiency_level} Multiplier):**")
            for s in skills_to_strengthen:
                st.markdown(f"- **{s['skill']}** `(Weight: {s['weight']}, Earned: {s['points_earned']:.1f} / {s['max_points']} pts)`")
        if not strong_skills and not skills_to_strengthen:
            st.info("No matching competencies currently selected for this role.")

    with col_diag2:
        st.error("### ⚠️ Critical Competency Gaps")
        if skill_gaps:
            for gap in skill_gaps:
                p_badge = "🔴 Core Priority" if gap["weight"] == 3 else ("🟡 Important" if gap["weight"] == 2 else "🔵 Foundational")
                with st.expander(f"{p_badge}: **{gap['skill']}** (Weight {gap['weight']})", expanded=(gap["weight"] == 3)):
                    st.write(f"**Category:** {gap['category']}")
                    st.write(f"**Occupational Rationale:** {gap['rationale']}")
        else:
            st.success("🎉 Excellent! You have covered 100% of benchmark competencies for this role.")

    # Actionable Career Improvement Roadmap
    st.markdown("---")
    st.subheader(f"🗺️ Tailored Learning Roadmap for {selected_role}")

    rd_col1, rd_col2 = st.columns(2, gap="medium")
    with rd_col1:
        st.markdown("#### ⚡ 1-Month Focused Sprint")
        st.caption("Target high-priority deficits first to build role-specific capability:")
        for step in roadmap_1m:
            st.markdown(f"- {step}")

    with rd_col2:
        st.markdown("#### 🚀 3-Month Progression Plan")
        st.caption("Undertake practical projects, portfolio building, and industry preparation:")
        for step in roadmap_3m:
            st.markdown(f"- {step}")


# =============================================================================
# MODULE 2: SURVEY ANALYTICS & INSIGHTS (INTERACTIVE DASHBOARD)
# =============================================================================
elif app_mode == "📊 Survey Analytics & Insights":
    st.title("📊 Youth Survey Analytics & Field Evidence")
    st.markdown(
        "Interactive dashboard exploring youth career aspirations, current skill profiles, and reported challenges. "
        "*Note: Metrics reflect our preliminary development cohort (N=38) and will refresh dynamically upon final survey closure.*"
    )
    st.markdown("---")

    if df_survey is not None:
        def count_multiselect(series):
            items = []
            for val in series.dropna():
                for item in re.split(r'[;,]\s*', str(val).strip()):
                    clean = item.strip().rstrip('.,;')
                    if clean and len(clean) > 1 and clean.lower() != "nan":
                        items.append(clean)
            if not items:
                return pd.DataFrame(columns=["Category", "Count"])
            s = pd.Series(items).value_counts()
            return pd.DataFrame({"Category": s.index, "Count": s.values})

        # Global Slicer Filter Bar
        with st.expander("🔍 Interactive Dashboard Filters (Slicers)", expanded=True):
            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
            with f_col1:
                career_list = ["All Careers"] + sorted(df_survey["career_field_interest"].dropna().unique().tolist())
                sel_career = st.selectbox("Career Track:", career_list)
            with f_col2:
                age_list = ["All Ages"] + sorted(df_survey["age_group"].dropna().unique().tolist())
                sel_age = st.selectbox("Age Group:", age_list)
            with f_col3:
                gender_list = ["All Genders"] + sorted(df_survey["gender"].dropna().unique().tolist())
                sel_gender = st.selectbox("Gender:", gender_list)
            with f_col4:
                edu_list = ["All Qualifications"] + sorted(df_survey["education_qualification"].dropna().unique().tolist())
                sel_edu = st.selectbox("Qualification:", edu_list)
            with f_col5:
                status_list = ["All Statuses"] + sorted(df_survey["current_status"].dropna().unique().tolist())
                sel_status = st.selectbox("Current Status:", status_list)

        # Apply Slicer Filters
        dff = df_survey.copy()
        if sel_career != "All Careers":
            dff = dff[dff["career_field_interest"] == sel_career]
        if sel_age != "All Ages":
            dff = dff[dff["age_group"] == sel_age]
        if sel_gender != "All Genders":
            dff = dff[dff["gender"] == sel_gender]
        if sel_edu != "All Qualifications":
            dff = dff[dff["education_qualification"] == sel_edu]
        if sel_status != "All Statuses":
            dff = dff[dff["current_status"] == sel_status]

        if dff.empty:
            st.warning("⚠️ No survey records match the selected filter combination. Please widen or reset your filters above.")
        else:
            # Executive Summary Cards
            k_col1, k_col2, k_col3, k_col4, k_col5 = st.columns(5)
            with k_col1:
                st.metric("Selected Cohort", f"{len(dff)} Youth", delta=f"{len(dff) - len(df_survey)}" if len(dff) != len(df_survey) else "Full Cohort")
            with k_col2:
                top_c = dff["career_field_interest"].mode()[0] if not dff["career_field_interest"].empty else "N/A"
                short_c = "IT / AI" if "Information Technology" in top_c else ("Civil Services" if "Government" in top_c else top_c.split('/')[0].strip())
                st.metric("Top Aspiration", short_c)
            with k_col3:
                avg_s = dff["current_skills_count"].mean() if "current_skills_count" in dff.columns else 0.0
                st.metric("Avg Skills Declared", f"{avg_s:.1f}")
            with k_col4:
                gap_p = (dff["has_skill_gap"].mean()) * 100 if "has_skill_gap" in dff.columns else 0.0
                st.metric("Skill Gap %", f"{gap_p:.1f}%")
            with k_col5:
                supp_df = count_multiselect(dff["support_required"])
                top_supp = supp_df.iloc[0]["Category"] if not supp_df.empty else "N/A"
                st.metric("Top Support Need", top_supp)

            st.markdown("<br>", unsafe_allow_html=True)

            # 4 Multi-Tab Dashboard Views
            tab1, tab2, tab3, tab4 = st.tabs([
                "🎯 Career Aspirations",
                "💡 Skills & Competency Gaps",
                "🚧 Challenges & Support",
                "🤖 Readiness & Youth Personas"
            ])

            # --- TAB 1: CAREER ASPIRATIONS ---
            with tab1:
                st.subheader("Career Ambitions & Decision Clarity")
                t1_col1, t1_col2 = st.columns([3, 2], gap="medium")
                with t1_col1:
                    st.markdown("#### Career Field Aspirations Distribution")
                    c_counts = dff["career_field_interest"].value_counts().reset_index()
                    c_counts.columns = ["Career Track", "Count"]
                    if not c_counts.empty:
                        st.bar_chart(c_counts.set_index("Career Track"), height=320)
                    else:
                        st.info("No data available for this selection.")
                with t1_col2:
                    st.markdown("#### Decision Clarity & Confidence")
                    dec_counts = dff["career_decided"].value_counts().reset_index()
                    dec_counts.columns = ["Status", "Count"]
                    st.dataframe(dec_counts, use_container_width=True, hide_index=True)

                    avg_conf = dff["career_confidence"].mean() if not dff["career_confidence"].empty else 0.0
                    st.metric("Mean Career Confidence", f"{avg_conf:.2f} / 5.0")

                t1_col3, t1_col4 = st.columns(2, gap="medium")
                with t1_col3:
                    st.markdown("#### Primary Career Choice Motivators")
                    factors_df = count_multiselect(dff["career_choice_factors"]).head(6)
                    if not factors_df.empty:
                        st.bar_chart(factors_df.set_index("Category"), height=260)
                    else:
                        st.info("No career motivators recorded.")
                with t1_col4:
                    st.markdown("#### Information-Seeking Frequency")
                    freq_counts = dff["career_info_frequency"].value_counts().reset_index()
                    freq_counts.columns = ["Frequency", "Count"]
                    st.dataframe(freq_counts, use_container_width=True, hide_index=True)

            # --- TAB 2: SKILLS & COMPETENCY GAPS ---
            with tab2:
                st.subheader("Competency Inventory vs Reported Gaps")
                t2_col1, t2_col2 = st.columns(2, gap="medium")
                with t2_col1:
                    st.markdown("#### Top Possessed Skills (Survey Declared)")
                    top_skills = count_multiselect(dff["current_skills"]).head(8)
                    if not top_skills.empty:
                        st.bar_chart(top_skills.set_index("Category"), height=300)
                    else:
                        st.info("No skills declared in this cohort.")
                with t2_col2:
                    st.markdown("#### Top Prioritized Areas for Improvement")
                    top_gaps = count_multiselect(dff["skills_to_improve"]).head(8)
                    if not top_gaps.empty:
                        st.bar_chart(top_gaps.set_index("Category"), height=300)
                    else:
                        st.info("No improvement areas recorded.")

                st.markdown("---")
                t2_col3, t2_col4 = st.columns(2, gap="medium")
                with t2_col3:
                    st.markdown("#### Self-Assessed General Skill Level (1–5)")
                    skill_dist = dff["overall_skill_level"].value_counts().sort_index().reset_index()
                    skill_dist.columns = ["Level", "Count"]
                    if not skill_dist.empty:
                        st.bar_chart(skill_dist.set_index("Level"), height=260)
                    else:
                        st.info("No skill levels recorded.")
                with t2_col4:
                    st.markdown("#### Skill Count vs Reported Challenges")
                    if len(dff) > 1:
                        trend_df = dff.groupby("current_skills_count")["challenges_count"].mean().reset_index()
                        trend_df.columns = ["Declared Skills", "Avg Challenges"]
                        st.line_chart(trend_df.set_index("Declared Skills"), height=260)
                        st.caption("📌 **Empirical Observation:** Youth possessing more technical skills actively report more operational hurdles, indicating heightened situational awareness of workplace requirements.")
                    else:
                        st.info("Insufficient data points to plot trend line.")

            # --- TAB 3: CHALLENGES & SUPPORT ---
            with tab3:
                st.subheader("Operational Hurdles & Required Interventions")
                t3_col1, t3_col2 = st.columns(2, gap="medium")
                with t3_col1:
                    st.markdown("#### Primary Career Hurdles Reported")
                    chal_df = count_multiselect(dff["skill_challenges"]).head(6)
                    if not chal_df.empty:
                        st.bar_chart(chal_df.set_index("Category"), height=300)
                    else:
                        st.info("No challenges recorded.")
                with t3_col2:
                    st.markdown("#### Institutional Support Types Requested")
                    supp_df = count_multiselect(dff["support_required"]).head(6)
                    if not supp_df.empty:
                        st.bar_chart(supp_df.set_index("Category"), height=300)
                    else:
                        st.info("No support requests recorded.")

                t3_col3, t3_col4 = st.columns(2, gap="medium")
                with t3_col3:
                    st.markdown("#### Institutional Guidance Usefulness Rating (1–5)")
                    g_avg = dff["guidance_usefulness_rating"].mean() if not dff["guidance_usefulness_rating"].empty else 0.0
                    st.metric("Mean Guidance Rating", f"{g_avg:.2f} / 5.0")
                    g_dist = dff["guidance_usefulness_rating"].round().value_counts().sort_index().reset_index()
                    g_dist.columns = ["Rating", "Count"]
                    st.dataframe(g_dist, use_container_width=True, hide_index=True)
                with t3_col4:
                    st.markdown("#### Formal Training / Internship Participation")
                    train_dist = dff["participated_training_or_internship"].value_counts().reset_index()
                    train_dist.columns = ["Participated", "Count"]
                    st.dataframe(train_dist, use_container_width=True, hide_index=True)
                    pct_trained = ((dff["participated_training_or_internship"] == "Yes").mean()) * 100 if len(dff) > 0 else 0.0
                    st.info(f"**{pct_trained:.1f}%** of youth in the filtered cohort have attended formal training or internships.")

            # --- TAB 4: READINESS & YOUTH PERSONAS ---
            with tab4:
                st.subheader("Readiness Scores & Exploratory Youth Personas")
                t4_col1, t4_col2 = st.columns(2, gap="medium")
                with t4_col1:
                    st.markdown("#### Survey Cohort Readiness Index")
                    r_mean = dff["readiness_score"].mean() if not dff["readiness_score"].empty else 0.0
                    r_med = dff["readiness_score"].median() if not dff["readiness_score"].empty else 0.0
                    st.metric("Cohort Mean Readiness", f"{r_mean:.1f}%", delta=f"Median: {r_med:.1f}%")

                    tier_table = dff["readiness_tier"].value_counts().reset_index()
                    tier_table.columns = ["Readiness Tier", "Count"]
                    st.dataframe(tier_table, use_container_width=True, hide_index=True)
                with t4_col2:
                    st.markdown("#### Average Readiness by Career Track")
                    track_r = dff.groupby("career_field_interest")["readiness_score"].mean().round(1).reset_index()
                    track_r.columns = ["Career Track", "Avg Readiness (%)"]
                    if not track_r.empty:
                        st.bar_chart(track_r.set_index("Career Track"), height=280)
                    else:
                        st.info("No track scores available.")

                st.markdown("---")
                st.markdown("#### 🤖 Exploratory ML Youth Personas (K-Means Clusters)")
                st.caption("Derived from exploratory cluster analysis to guide customized community interventions:")

                p_c1, p_c2, p_c3 = st.columns(3)
                with p_c1:
                    st.info(
                        "**Persona A (42.1%)**\n\n"
                        "*Actively Skilled but Barrier-Constrained*\n\n"
                        "- High confidence (4.5/5), core skills possessed.\n"
                        "- Faces guidance and practical project access barriers.\n\n"
                        "**Action:** Project incubation & industry mentorship."
                    )
                with p_c2:
                    st.success(
                        "**Persona B (31.6%)**\n\n"
                        "*High-Confidence Generalists*\n\n"
                        "- Moderate readiness (50.2%), broad skill inventory.\n"
                        "- Needs deep specialization in core technical tools.\n\n"
                        "**Action:** Advanced domain certifications & coding sprints."
                    )
                with p_c3:
                    st.warning(
                        "**Persona C (26.3%)**\n\n"
                        "*Early-Stage Explorers*\n\n"
                        "- Developing confidence (1.3/5), emerging skill base.\n"
                        "- Requires foundational career clarity and guidance.\n\n"
                        "**Action:** Foundational digital workshops & career counseling."
                    )
    else:
        st.warning("Survey dataset not found in data/ directory.")


# =============================================================================
# MODULE 3: CAREER COMPETENCY FRAMEWORK
# =============================================================================
elif app_mode == "🗺️ Career Competency Framework":
    st.title("🗺️ Role-Specific Career Competency Framework")
    st.markdown(
        "Explore the **69 standardized competency benchmarks** synthesized across 11 specific occupational roles. "
        "Each competency is weighted by industry importance to ensure transparent multi-criteria evaluation."
    )
    st.markdown("---")

    if df_role_matrix is not None:
        mf_col1, mf_col2 = st.columns([2, 1])
        with mf_col1:
            unique_roles = ["All Roles"] + sorted(df_role_matrix["target_role"].unique().tolist())
            role_filter = st.selectbox("Filter by Target Career Role:", unique_roles)
        with mf_col2:
            weight_filter = st.selectbox("Filter by Weight Tier:", ["All Tiers", "Tier 3: Core (Weight 3)", "Tier 2: Important (Weight 2)", "Tier 1: Foundational (Weight 1)"])

        filtered_matrix = df_role_matrix.copy()
        if role_filter != "All Roles":
            filtered_matrix = filtered_matrix[filtered_matrix["target_role"] == role_filter]
        if weight_filter == "Tier 3: Core (Weight 3)":
            filtered_matrix = filtered_matrix[filtered_matrix["weight"] == 3]
        elif weight_filter == "Tier 2: Important (Weight 2)":
            filtered_matrix = filtered_matrix[filtered_matrix["weight"] == 2]
        elif weight_filter == "Tier 1: Foundational (Weight 1)":
            filtered_matrix = filtered_matrix[filtered_matrix["weight"] == 1]

        st.dataframe(
            filtered_matrix,
            column_config={
                "career_track": st.column_config.TextColumn("Career Track", width="medium"),
                "target_role": st.column_config.TextColumn("Target Role", width="medium"),
                "competency_name": st.column_config.TextColumn("Competency Name", width="large"),
                "weight": st.column_config.NumberColumn("Weight", help="3=Core, 2=Important, 1=Foundational"),
                "category": st.column_config.TextColumn("Category"),
                "occupational_rationale": st.column_config.TextColumn("Occupational Rationale", width="large")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Role competency matrix not found in data/ directory.")


# =============================================================================
# MODULE 4: RESEARCH METHODOLOGY & FRAMEWORK
# =============================================================================
elif app_mode == "ℹ️ Research Methodology & Framework":
    st.title("ℹ️ Research Methodology & Theoretical Framework")
    st.markdown(
        "This project investigates youth career preparedness using an empirical survey and an explainable "
        "Multi-Criteria Decision Analysis (MCDA) scoring engine. Below is the documented academic methodology."
    )
    st.markdown("---")

    st.subheader("1. Problem Statement & Research Objectives")
    st.markdown(
        "Higher education graduates frequently encounter an employability gap arising from the divergence between academic curricula "
        "and evolving industry competency requirements. This study aims to:\n"
        "- Quantify career readiness across diverse disciplines using transparent, deterministic scoring.\n"
        "- Isolate prioritized skill gaps to deliver targeted, time-bounded learning milestones.\n"
        "- Explore youth behavioral archetypes through unsupervised machine learning."
    )

    st.subheader("2. Dual-Layer System Architecture")
    st.markdown(
        "- **Layer 1 (Research & Survey Analytics):** Preserves original 14 self-reported questionnaire skills across $N=38$ preliminary development respondents to ensure historical survey reproducibility.\n"
        "- **Layer 2 (Interactive Career Assessment):** Employs an evidence-based matrix of 11 distinct occupational roles (69 industry competencies) to deliver authentic, role-specific guidance."
    )

    st.subheader("3. Mathematical Formulation (Phase 5 Model)")
    st.markdown("For any targeted role requiring $N$ competencies with weights $W_i \\in \\{1, 2, 3\\}$:")
    st.latex(r"\text{Readiness Index (\%)} = \left( \frac{\sum_{i \in \text{Possessed}} W_i \times \mu(L)}{\sum_{i=1}^{N} W_i} \right) \times 100")

    st.markdown("Where $\\mu(L)$ represents the **Proficiency Multiplier** calibrated to self-assessed proficiency $L$:")
    st.markdown("- **$L \\ge 4$ (Proficient / Advanced):** $\\mu(L) = 1.0$ (100% weighted credit)")
    st.markdown("- **$L = 3$ (Competent / Intermediate):** $\\mu(L) = 0.8$ (80% weighted credit)")
    st.markdown("- **$L \\le 2$ (Developing / Novice):** $\\mu(L) = 0.5$ (50% weighted credit)")

    st.subheader("4. Rationale for Explainable Modeling")
    st.markdown(
        "- **Student Counseling Ethics:** Career guidance must be transparent. Black-box algorithms cannot provide students with clear, defensible milestone explanations.\n"
        "- **Small-Sample Validity:** In early-stage community research ($N=38$ development sample), complex models suffer from high variance and overfitting. Deterministic scoring guarantees consistent, reproducible outputs."
    )

    st.subheader("5. Privacy Preservation & Academic Scope")
    st.markdown(
        "- All survey records are anonymized (`RESP_001` - `RESP_038`); zero personal emails or phone numbers are stored.\n"
        "- The system evaluates competency alignment and does not claim to predict employment outcomes or replace certified professional counseling."
    )

# -----------------------------------------------------------------------------
# APPLICATION FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "🎓 **Community Engagement Project (CEP)** — Career Aspiration & Skill Gap Analysis for Youth | "
    "Designed for 24×7 Streamlit Community Cloud Public Deployment."
)
