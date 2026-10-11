"""
Career Aspiration & Skill Gap Analysis for Youth — Streamlit Web Application
Author: Data Science Community Engagement Project (CEP)
Architecture: Stateless Cloud-Ready Web Application (Relative Paths Only)
Deployment: GitHub Repository -> Streamlit Community Cloud (24x7 Accessible)
"""

import os
import sys
import json
import re
import pandas as pd
import streamlit as st

# Configure relative project paths (Cloud-Safe, Zero Hardcoded Paths)
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
# CACHED RESOURCE LOADERS
# -----------------------------------------------------------------------------
@st.cache_resource
def load_readiness_model():
    catalog_path = os.path.join(MODEL_DIR, "career_skills_catalog.json")
    return CareerReadinessModel(catalog_path)

@st.cache_data
def load_survey_data():
    csv_path = os.path.join(DATA_DIR, "survey_cleaned_public.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

@st.cache_data
def load_matrix_data():
    csv_path = os.path.join(DATA_DIR, "career_skill_matrix.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

model = load_readiness_model()
df_survey = load_survey_data()
df_matrix = load_matrix_data()

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & OVERVIEW
# -----------------------------------------------------------------------------
st.sidebar.title("🎓 Career Navigator")
st.sidebar.markdown("**Community Engagement Project (CEP)**")
st.sidebar.markdown("*A scientific, explainable tool to bridge youth aspirations with industry skills.*")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Select Module:",
    [
        "🎯 Career Readiness Assessment",
        "📊 Survey Analytics & Insights",
        "🗺️ Career Competency Matrix",
        "ℹ️ Methodology & Viva Guide"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Deployment Mode:** Cloud Production\n\n"
    "**Algorithm:** Phase 5 Deterministic Multi-Criteria Model\n\n"
    "**Version:** v1.0.0 (Cloud-Ready)"
)

# -----------------------------------------------------------------------------
# MODULE 1: CAREER READINESS ASSESSMENT (CORE MODEL)
# -----------------------------------------------------------------------------
if app_mode == "🎯 Career Readiness Assessment":
    st.title("🎯 Career Readiness & Skill Gap Assessment")
    st.markdown(
        "Evaluate your current skill inventory against standardized industry competency frameworks. "
        "Get an instant, explainable **Career Readiness Score**, identify critical gaps, and receive tailored roadmaps."
    )
    st.markdown("---")

    col_input1, col_input2 = st.columns([1, 1], gap="medium")

    with col_input1:
        st.subheader("1. Target Career Aspiration")
        career_options = model.available_careers
        selected_career = st.selectbox(
            "Select your desired career track:",
            options=career_options,
            index=0,
            help="Choose the occupational track you aspire to enter."
        )

        # Retrieve benchmark skills for this career
        req_skills_info = model.catalog[selected_career]["skills"]
        req_skills_names = [s["skill"] for s in req_skills_info]
        total_career_points = model.catalog[selected_career]["total_weighted_points"]

        st.caption(f"📌 Benchmark requires **{len(req_skills_names)} competencies** totaling **{total_career_points} weighted points**.")

        st.subheader("2. Self-Assessed Proficiency Level")
        proficiency_level = st.select_slider(
            "Rate your overall proficiency in the skills you possess:",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: {
                1: "Level 1: Novice (50% credit)",
                2: "Level 2: Developing (50% credit)",
                3: "Level 3: Intermediate / Competent (80% credit)",
                4: "Level 4: Proficient (100% credit)",
                5: "Level 5: Advanced / Master (100% credit)"
            }[x],
            help="Reflects your depth of hands-on application and confidence."
        )

    with col_input2:
        st.subheader("3. Current Skill Inventory")
        st.write("Check all skills you currently possess:")

        # Quick action buttons for convenience
        quick_cols = st.columns(3)
        with quick_cols[0]:
            select_all = st.button("Select All Skills")
        with quick_cols[1]:
            clear_all = st.button("Clear All")
        with quick_cols[2]:
            select_core = st.button("Select Core Only")

        # Session state management for skill checkboxes
        if "selected_skills" not in st.session_state or clear_all:
            st.session_state.selected_skills = []
        if select_all:
            st.session_state.selected_skills = list(req_skills_names)
        if select_core:
            st.session_state.selected_skills = [s["skill"] for s in req_skills_info if s["weight"] == 3]

        # Skill selection multi-select or checkboxes
        chosen_skills = []
        for s_info in req_skills_info:
            s_name = s_info["skill"]
            w = s_info["weight"]
            cat = s_info["category"]
            badge = "🔥 Tier 3 (Core)" if w == 3 else ("⭐ Tier 2 (Important)" if w == 2 else "🔹 Tier 1 (Foundational)")
            
            is_checked = s_name in st.session_state.selected_skills
            chk = st.checkbox(
                f"{s_name} — {badge}",
                value=is_checked,
                key=f"skill_chk_{s_name}"
            )
            if chk:
                chosen_skills.append(s_name)

    st.markdown("---")
    eval_btn = st.button("🚀 Calculate My Career Readiness Score", type="primary", use_container_width=True)

    if eval_btn or chosen_skills or st.session_state.selected_skills:
        # Run Phase 5 Model
        results = model.evaluate_readiness(selected_career, chosen_skills, proficiency_level)

        score = results["readiness_score"]
        tier = results["readiness_tier"]
        tier_desc = results["tier_description"]
        strong_skills = results["strong_skills"]
        skills_to_strengthen = results["skills_to_strengthen"]
        skill_gaps = results["skill_gaps"]
        roadmap_1m = results["roadmap_1_month"]
        roadmap_3m = results["roadmap_3_month"]

        st.subheader("📊 Assessment Results & Diagnostic Breakdown")

        # Top summary metrics
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Readiness Index", f"{score:.1f}%", delta=f"{score - 29.8:+.1f}% vs Survey Avg")
        with m_col2:
            st.metric("Readiness Tier", tier)
        with m_col3:
            st.metric("Strong / Matched", f"{len(strong_skills) + len(skills_to_strengthen)} / {len(req_skills_names)}")
        with m_col4:
            st.metric("Critical Gaps", f"{len(skill_gaps)}")

        # Visual progress bar
        st.progress(score / 100.0)
        st.caption(f"**Interpretation:** {tier_desc}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Two-column diagnostic breakdown
        col_res1, col_res2 = st.columns(2, gap="large")

        with col_res1:
            st.success("### ✅ Possessed Competencies")
            if strong_skills:
                st.write("**Strong Skills (Full Credit Earned):**")
                for s in strong_skills:
                    st.markdown(f"- **{s['skill']}** (Weight: {s['weight']}, Earned: {s['points_earned']} / {s['max_points']} pts)")
            if skills_to_strengthen:
                st.write("**Skills to Strengthen (Partial Credit Earned):**")
                for s in skills_to_strengthen:
                    st.markdown(f"- **{s['skill']}** (Weight: {s['weight']}, Earned: {s['points_earned']} / {s['max_points']} pts at Level {proficiency_level})")
            if not strong_skills and not skills_to_strengthen:
                st.warning("No matching skills currently selected for this career track.")

        with col_res2:
            st.error("### ⚠️ Competency Gaps (Priority Order)")
            if skill_gaps:
                for gap in skill_gaps:
                    p_badge = "🔴 High Priority" if gap["weight"] == 3 else ("🟡 Medium Priority" if gap["weight"] == 2 else "🔵 Foundational")
                    with st.expander(f"{p_badge}: **{gap['skill']}** (Weight {gap['weight']})", expanded=(gap["weight"] == 3)):
                        st.write(f"**Competency Category:** {gap['category']}")
                        st.write(f"**Industry Rationale:** {gap['rationale']}")
            else:
                st.success("🎉 Outstanding! You currently cover 100% of benchmark competencies for this track.")

        st.markdown("---")
        st.subheader("🗺️ Your Actionable Career Improvement Roadmap")

        tab_1m, tab_3m = st.tabs(["⚡ 1-Month Focused Sprint", "🚀 3-Month Practical Progression"])

        with tab_1m:
            st.markdown("#### High-Priority Milestones (First 30 Days)")
            st.markdown("Focus immediately on closing Tier-3 core competency deficits and establishing daily study discipline:")
            for item in roadmap_1m:
                st.markdown(f"- {item}")

        with tab_3m:
            st.markdown("#### Portfolio & Practice Milestones (Next 90 Days)")
            st.markdown("Solidify intermediate skills, undertake hands-on capstone projects, and prepare for placement:")
            for item in roadmap_3m:
                st.markdown(f"- {item}")

# -----------------------------------------------------------------------------
# MODULE 2: SURVEY ANALYTICS & INSIGHTS (INTERACTIVE WEB DASHBOARD)
# -----------------------------------------------------------------------------
elif app_mode == "📊 Survey Analytics & Insights":
    st.title("📊 Youth Survey Analytics & Field Evidence")
    st.markdown(
        "Interactive analytics dashboard visualizing findings from our empirical Community Engagement Project (CEP) survey. "
        "*Note: Metrics reflect our preliminary development cohort (N=38) and will be refreshed upon survey closure.*"
    )
    st.markdown("---")

    if df_survey is not None:
        # Helper function to unnest and count multi-select semicolon/comma separated responses
        def count_multiselect(series):
            items = []
            for val in series.dropna():
                for item in re.split(r'[;,]\s*', str(val).strip()):
                    clean = item.strip().rstrip('.,;')
                    if clean and len(clean) > 1 and clean.lower() != "nan":
                        items.append(clean)
            s = pd.Series(items).value_counts()
            return pd.DataFrame({"Item": s.index, "Count": s.values})

        # --- GLOBAL SLICER FILTER BAR ---
        with st.expander("🔍 Interactive Dashboard Filters (Slicers)", expanded=True):
            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
            
            with f_col1:
                career_list = ["All Careers"] + sorted(df_survey["career_field_interest"].dropna().unique().tolist())
                sel_career = st.selectbox("Career Field:", career_list)
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

        # Apply slicer filters dynamically
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
            st.warning("⚠️ No respondents match the selected filter combination. Please adjust your filters above.")
        else:
            # --- EXECUTIVE KPI SUMMARY CARDS ---
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            with kpi1:
                st.metric(
                    "Selected Cohort",
                    f"{len(dff)} Youth",
                    delta=f"{len(dff) - len(df_survey)}" if len(dff) != len(df_survey) else "Full Cohort"
                )
            with kpi2:
                top_c = dff["career_field_interest"].mode()[0] if not dff["career_field_interest"].empty else "N/A"
                short_c = "IT / AI" if "Information Technology" in top_c else ("Civil Services" if "Government" in top_c else top_c.split('/')[0].strip())
                st.metric("Top Aspiration", short_c)
            with kpi3:
                avg_s = dff["current_skills_count"].mean()
                st.metric("Avg Skills Declared", f"{avg_s:.1f} skills")
            with kpi4:
                gap_p = (dff["has_skill_gap"].mean()) * 100
                st.metric("Skill Gap Awareness", f"{gap_p:.1f}%")
            with kpi5:
                supp_df = count_multiselect(dff["support_required"])
                top_supp = supp_df.iloc[0]["Item"] if not supp_df.empty else "N/A"
                st.metric("Top Support Need", top_supp)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- 4 MULTI-TAB DASHBOARD MODULES ---
            tab_asp, tab_skl, tab_chl, tab_per = st.tabs([
                "🎯 Career Aspirations",
                "💡 Skills & Competency Gaps",
                "🚧 Challenges & Support",
                "🤖 Readiness & Exploratory Personas"
            ])

            # --- TAB 1: CAREER ASPIRATIONS ---
            with tab_asp:
                st.subheader("Career Ambitions & Decision Trajectory")
                col_a1, col_a2 = st.columns([3, 2], gap="medium")
                with col_a1:
                    st.markdown("#### Primary Career Track Distribution")
                    career_counts = dff["career_field_interest"].value_counts().reset_index(names=["Career Track", "Respondents"])
                    st.bar_chart(career_counts.set_index("Career Track"), color="#1E88E5", height=320)
                with col_a2:
                    st.markdown("#### Career Decision Clarity")
                    decided_counts = dff["career_decided"].value_counts().reset_index(names=["Decision Status", "Respondents"])
                    st.dataframe(decided_counts, use_container_width=True, hide_index=True)
                    
                    avg_conf = dff["career_confidence"].mean()
                    st.metric("Mean Career Confidence", f"{avg_conf:.2f} / 5.0", help="1=Low, 5=High Confidence")

                col_a3, col_a4 = st.columns(2, gap="medium")
                with col_a3:
                    st.markdown("#### Key Factors Influencing Career Choices")
                    factors_df = count_multiselect(dff["career_choice_factors"]).head(6)
                    st.bar_chart(factors_df.set_index("Item"), color="#00CC88", height=280)
                with col_a4:
                    st.markdown("#### Information-Seeking Frequency")
                    freq_counts = dff["career_info_frequency"].value_counts().reset_index(names=["Frequency", "Respondents"])
                    st.dataframe(freq_counts, use_container_width=True, hide_index=True)

            # --- TAB 2: SKILLS & COMPETENCY GAPS ---
            with tab_skl:
                st.subheader("Competency Inventory vs Reported Gaps")
                col_s1, col_s2 = st.columns(2, gap="medium")
                with col_s1:
                    st.markdown("#### Top Possessed Skills (Self-Declared)")
                    skills_df = count_multiselect(dff["current_skills"]).head(8)
                    st.bar_chart(skills_df.set_index("Item"), color="#2ECC71", height=320)
                with col_s2:
                    st.markdown("#### Top Prioritized Skill Gaps (Areas to Improve)")
                    gaps_df = count_multiselect(dff["skills_to_improve"]).head(8)
                    st.bar_chart(gaps_df.set_index("Item"), color="#E74C3C", height=320)

                st.markdown("---")
                col_s3, col_s4 = st.columns([1, 1], gap="medium")
                with col_s3:
                    st.markdown("#### Overall Self-Assessed Skill Level (1–5)")
                    skill_lvl_counts = dff["overall_skill_level"].value_counts().sort_index().reset_index(names=["Skill Level (1-5)", "Respondents"])
                    st.bar_chart(skill_lvl_counts.set_index("Skill Level (1-5)"), color="#F39C12", height=280)
                with col_s4:
                    st.markdown("#### Empirical Pattern: Skill Count vs Challenges")
                    pattern_data = dff.groupby("current_skills_count")["challenges_count"].mean().reset_index(names=["Declared Skills", "Avg Challenges Reported"])
                    st.line_chart(pattern_data.set_index("Declared Skills"), color="#9B59B6", height=280)
                    st.caption("📌 **Observed Pattern:** Students reporting a higher number of technical skills actively identify more operational hurdles (reflecting heightened situational awareness of professional expectations).")

            # --- TAB 3: CHALLENGES & SUPPORT REQUIREMENTS ---
            with tab_chl:
                st.subheader("Operational Obstacles & Institutional Support Needs")
                col_c1, col_c2 = st.columns(2, gap="medium")
                with col_c1:
                    st.markdown("#### Primary Career Hurdles Reported")
                    chal_df = count_multiselect(dff["skill_challenges"]).head(6)
                    st.bar_chart(chal_df.set_index("Item"), color="#E67E22", height=300)
                with col_c2:
                    st.markdown("#### Institutional Support Types Requested")
                    supp_df_all = count_multiselect(dff["support_required"]).head(6)
                    st.bar_chart(supp_df_all.set_index("Item"), color="#3498DB", height=300)

                col_c3, col_c4 = st.columns(2, gap="medium")
                with col_c3:
                    st.markdown("#### Institutional Guidance Usefulness Rating (1–5)")
                    guide_avg = dff["guidance_usefulness_rating"].mean()
                    st.metric("Mean Guidance Satisfaction", f"{guide_avg:.2f} / 5.0", help="Self-assessed institutional guidance effectiveness")
                    guide_counts = dff["guidance_usefulness_rating"].round().value_counts().sort_index().reset_index(names=["Rating (1-5)", "Count"])
                    st.dataframe(guide_counts, use_container_width=True, hide_index=True)
                with col_c4:
                    st.markdown("#### Formal Training / Internship Participation")
                    train_counts = dff["participated_training_or_internship"].value_counts().reset_index(names=["Participated?", "Count"])
                    st.dataframe(train_counts, use_container_width=True, hide_index=True)
                    yes_pct = ((dff["participated_training_or_internship"] == "Yes").mean()) * 100
                    st.info(f"**{yes_pct:.1f}%** of youth in the selected cohort have completed formal training or internship programs.")

            # --- TAB 4: READINESS & EXPLORATORY PERSONAS ---
            with tab_per:
                st.subheader("Model Readiness Scores & Exploratory Youth Personas")
                col_p1, col_p2 = st.columns([1, 1], gap="medium")
                with col_p1:
                    st.markdown("#### Readiness Score Distribution (Phase 5 Model)")
                    mean_score = dff["readiness_score"].mean()
                    med_score = dff["readiness_score"].median()
                    st.metric("Mean Readiness Score", f"{mean_score:.1f}%", delta=f"Median: {med_score:.1f}%")
                    
                    tier_dist = dff["readiness_tier"].value_counts().reset_index(names=["Readiness Tier", "Count"])
                    st.dataframe(tier_dist, use_container_width=True, hide_index=True)

                with col_p2:
                    st.markdown("#### Mean Readiness by Career Track")
                    track_scores = dff.groupby("career_field_interest")["readiness_score"].mean().round(1).reset_index(names=["Career Track", "Avg Readiness (%)"])
                    st.bar_chart(track_scores.set_index("Career Track"), color="#16A085", height=280)

                st.markdown("---")
                st.markdown("#### 🤖 Exploratory ML Youth Personas (K-Means Clusters)")
                st.caption("Identified during exploratory modeling to inform targeted community interventions:")
                
                per_col1, per_col2, per_col3 = st.columns(3)
                with per_col1:
                    st.info(
                        "**Persona A (42.1%)**\n\n"
                        "*Actively Skilled but Barrier-Constrained*\n\n"
                        "- **Profile:** High confidence (4.5/5), possesses core skills, faces guidance and practical project hurdles.\n\n"
                        "- **Recommended Support:** Industry mentorship & project incubation."
                    )
                with per_col2:
                    st.success(
                        "**Persona B (31.6%)**\n\n"
                        "*High-Confidence Generalists*\n\n"
                        "- **Profile:** Moderate-high readiness (50.2%), broad skill coverage, needs specialized technical depth.\n\n"
                        "- **Recommended Support:** Advanced domain certifications & deep-dives."
                    )
                with per_col3:
                    st.warning(
                        "**Persona C (26.3%)**\n\n"
                        "*Early-Stage Explorers*\n\n"
                        "- **Profile:** Developing confidence (1.3/5), emerging skill awareness, requires foundational support.\n\n"
                        "- **Recommended Support:** Career clarity workshops & foundational digital bootcamps."
                    )
    else:
        st.warning("Survey dataset not found in data/ directory.")

# -----------------------------------------------------------------------------
# MODULE 3: CAREER COMPETENCY MATRIX
# -----------------------------------------------------------------------------
elif app_mode == "🗺️ Career Competency Matrix":
    st.title("🗺️ Career Competency & Skill Weighting Matrix")
    st.markdown("Browse the 48 standardized competency rules synthesized for career tracks based on standard occupational requirements.")
    st.markdown("---")

    if df_matrix is not None:
        c_filter = st.selectbox("Filter by Career Field:", ["All Career Tracks"] + sorted(df_matrix["career"].unique().tolist()))
        
        display_df = df_matrix if c_filter == "All Career Tracks" else df_matrix[df_matrix["career"] == c_filter]
        
        st.dataframe(
            display_df,
            column_config={
                "career": st.column_config.TextColumn("Career Track", width="medium"),
                "required_skill": st.column_config.TextColumn("Required Competency", width="medium"),
                "weight": st.column_config.NumberColumn("Weight", help="3=Core, 2=Important, 1=Foundational"),
                "category": st.column_config.TextColumn("Category"),
                "competency_rationale": st.column_config.TextColumn("Competency Rationale", width="large")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Matrix data not found in data/ directory.")

# -----------------------------------------------------------------------------
# MODULE 4: METHODOLOGY & VIVA GUIDE
# -----------------------------------------------------------------------------
elif app_mode == "ℹ️ Methodology & Viva Guide":
    st.title("ℹ️ Project Methodology & Academic Defense Guide")
    st.markdown(
        "This project adheres to rigorous Data Science principles: "
        "**Correctness $\\to$ Explainability $\\to$ Statistical Humility $\\to$ Working Implementation.**"
    )
    st.markdown("---")

    st.subheader("1. Mathematical Scoring Formula (Phase 5 Model)")
    st.markdown("For any selected career $C$ requiring competencies with weights $W_i \\in \\{1, 2, 3\\}$:")
    st.latex(r"\text{Readiness Index (\%)} = \left( \frac{\sum_{i \in \text{Possessed}} W_i \times \mu(L)}{\sum_{i=1}^{N} W_i} \right) \times 100")
    
    st.markdown("Where $\\mu(L)$ is the **Proficiency Multiplier** derived from self-assessed skill rating $L$:")
    st.markdown("- **$L \\ge 4$ (Proficient / Advanced):** $\\mu(L) = 1.0$ (100% credit)")
    st.markdown("- **$L = 3$ (Intermediate / Competent):** $\\mu(L) = 0.8$ (80% credit)")
    st.markdown("- **$L \\le 2$ (Novice / Developing):** $\\mu(L) = 0.5$ (50% credit)")

    st.subheader("2. Why Deterministic Modeling Over Black-Box Deep Learning?")
    st.markdown(
        "1. **Ethical Individual Counseling:** A student seeking career guidance needs transparent, explainable recommendations rather than an uninterpretable probability score from a neural network.\n"
        "2. **Small-Sample Science:** With $N=38$ preliminary responses, training complex deep learning models leads to immediate overfitting and spurious correlations. Deterministic multi-criteria decision models remain robust, reliable, and testable."
    )

    st.subheader("3. Model Validation & Monotonicity Certification (Phase 7)")
    st.markdown(
        "- **Boundary Invariance:** Proved that scores strictly stay within $[0.0\\%, 100.0\\%]$.\n"
        "- **Strict Monotonicity (224 automated checks passed):** Proved mathematically that acquiring skills or deepening proficiency never decreases a candidate's readiness score.\n"
        "- **Partition Completeness:** $\\text{Strong Skills} + \\text{Skills to Strengthen} + \\text{Skill Gaps} \\equiv \\text{Total Required Skills}$ across all survey records."
    )

    st.subheader("4. Project Limitations & Ethical Boundaries")
    st.markdown(
        "- The model evaluates **readiness alignment**, not a guarantee of future employment or career success.\n"
        "- Skills are self-reported and reflect perceived competency.\n"
        "- Recommendations are educational guidance, not formal professional career counseling."
    )

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "🎓 **Community Engagement Project (CEP)** — Career Aspiration & Skill Gap Analysis for Youth | "
    "Designed for 24×7 Streamlit Community Cloud Public Deployment."
)
