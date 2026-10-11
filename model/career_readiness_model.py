"""
Career Readiness & Competency Matching Model (Dual-Layer Architecture)
Community Engagement Project (CEP) — Youth Career Readiness Analyzer

Architecture:
- Layer 1 (Research & Survey Analytics): Preserves original 8 career tracks & 14 survey skills
  calibrated against the survey dataset (N=38 preliminary cohort).
- Layer 2 (Interactive Assessment & Career Guidance): Provides evidence-based, role-specific
  competency benchmarks (11 distinct career roles) with domain-specific skills and tailored roadmaps.
"""

import json
import os
import pandas as pd
import numpy as np


class CareerReadinessModel:
    def __init__(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        catalog_path = None
        interactive_matrix_path = None

        if len(args) >= 1:
            catalog_path = args[0]
        if len(args) >= 2:
            interactive_matrix_path = args[1]

        catalog_path = kwargs.get("catalog_path", catalog_path)
        interactive_matrix_path = kwargs.get("interactive_matrix_path", interactive_matrix_path)

        # Layer 1 catalog path (Survey & Research Historical Baseline)
        if catalog_path is None:
            catalog_path = os.path.join(base_dir, "career_skills_catalog.json")
        if not os.path.exists(catalog_path):
            raise FileNotFoundError(f"Layer 1 Catalog not found at: {catalog_path}")
        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
        self.available_careers = list(self.catalog.keys())

        # Layer 2 matrix path (Interactive Role-Specific Assessment)
        if interactive_matrix_path is None:
            interactive_matrix_path = os.path.join(base_dir, "interactive_role_competency_matrix.json")
        if os.path.exists(interactive_matrix_path):
            with open(interactive_matrix_path, "r", encoding="utf-8") as f:
                self.interactive_roles = json.load(f)
        else:
            self.interactive_roles = {}

        self.available_roles = list(self.interactive_roles.keys())

        # Comprehensive Role-Specific & General Learning Roadmaps (Layer 2)
        self.skill_recommendations = {
            # --- IT & Software Engineering ---
            "Data Structures & Algorithms (DSA)": {
                "1_month": "Solve 30 foundational array, string, and hash table problems on LeetCode/NeetCode 150.",
                "3_month": "Master recursion, trees, graphs, and dynamic programming; participate in bi-weekly coding contests."
            },
            "Programming Languages (Python, Java, C++, JavaScript)": {
                "1_month": "Build clean CLI applications, implement OOP design patterns, and practice code modularity.",
                "3_month": "Develop 2 production-ready backend/full-stack applications with unit tests and logging."
            },
            "Git Version Control & GitHub": {
                "1_month": "Learn Git CLI (branching, merging, rebasing, stash) and establish a disciplined commit habit.",
                "3_month": "Contribute to an open-source project via Pull Requests and configure GitHub Actions for CI/CD."
            },
            "Web / API Development (REST, Backend/Frontend)": {
                "1_month": "Build a CRUD REST API with FastAPI/Flask/Node.js, implement JWT auth, and test with Postman.",
                "3_month": "Deploy a complete client-server application with database persistence on a cloud provider."
            },
            "Database Management & SQL": {
                "1_month": "Master SQL queries (JOINs, GROUP BY, subqueries, indexing) and 3NF database normalization.",
                "3_month": "Design schema migrations, optimize slow queries with EXPLAIN ANALYZE, and connect ORMs."
            },
            "Debugging & System Troubleshooting": {
                "1_month": "Practice using interactive debuggers (PDB/VS Code), analyzing stack traces, and writing pytest suites.",
                "3_month": "Implement centralized logging, error monitoring (Sentry), and fault-tolerant retry patterns."
            },
            "Agile Teamwork & Communication": {
                "1_month": "Use Jira/Trello boards to break down feature epics into sprint user stories with clear acceptance criteria.",
                "3_month": "Conduct peer code reviews, lead daily standups, and present sprint demos to non-technical stakeholders."
            },

            # --- Data Science & AI ---
            "Python for Data Analysis (Pandas, NumPy)": {
                "1_month": "Master vector operations in NumPy, Pandas data cleaning, indexing, grouping, and handling missing values.",
                "3_month": "Perform end-to-end Exploratory Data Analysis (EDA) on 3 messy real-world datasets from Kaggle/data.gov."
            },
            "Applied Machine Learning (Scikit-Learn)": {
                "1_month": "Train and evaluate linear models, decision trees, and Random Forests; master cross-validation and confusion matrices.",
                "3_month": "Build an end-to-end predictive pipeline with feature scaling, encoding, hyperparameter tuning, and model artifact serialization."
            },
            "SQL & Relational Databases": {
                "1_month": "Master complex aggregations, window functions (ROW_NUMBER, LAG, LEAD), and CTEs on PostgreSQL/SQLite.",
                "3_month": "Build automated data transformation pipelines and integrate database queries into analytical notebooks."
            },
            "Statistical Inference & Probability": {
                "1_month": "Study probability distributions, Central Limit Theorem, hypothesis testing (t-tests, chi-square), and p-values.",
                "3_month": "Design and interpret A/B tests, confidence intervals, and multiple regression models for business metrics."
            },
            "Data Visualization (Seaborn, Power BI, Streamlit)": {
                "1_month": "Create publication-quality statistical charts using Seaborn and build a multi-page interactive Streamlit dashboard.",
                "3_month": "Publish an executive Power BI/Tableau dashboard incorporating DAX measures, dynamic slicers, and storytelling."
            },
            "Analytical Problem-Solving": {
                "1_month": "Deconstruct business pain points into MECE issue trees and define measurable key performance indicators (KPIs).",
                "3_month": "Deliver 2 complete business analytics case studies with root-cause identification and ROI recommendations."
            },
            "Technical Storytelling & Presentation": {
                "1_month": "Practice writing executive one-pagers that translate statistical outputs into practical business actions.",
                "3_month": "Present complex analytical findings to non-technical audiences using structured narrative frameworks (Situation-Complication-Resolution)."
            },

            # --- Banking Operations ---
            "Banking Operations & KYC/AML Guidelines": {
                "1_month": "Study RBI Master Directions on KYC, statutory account verification, AML flags, and banking ombudsman schemes.",
                "3_month": "Prepare for Indian Institute of Banking & Finance (IIBF) certifications (JAIIB principles or Banking Operations Diploma)."
            },
            "Spreadsheet Management (Excel / Sheets)": {
                "1_month": "Master XLOOKUP, Pivot Tables, conditional formatting, and SUMIFS for ledger balancing and variance tracking.",
                "3_month": "Automate daily bank reconciliation and operational MIS generation using Power Query."
            },
            "Financial Accounting Basics (Debit/Credit, Ledgers)": {
                "1_month": "Master double-entry bookkeeping, trial balance preparation, and debit/credit ledger posting conventions.",
                "3_month": "Reconcile multi-entity journal entries, prepare basic financial statements, and pass accounting mock assessments."
            },
            "Client Relationship & Customer Advisory": {
                "1_month": "Learn banking product features (CASA, fixed deposits, credit cards, retail loans) and structured client communication.",
                "3_month": "Roleplay client portfolio advisory scenarios, handling customer complaints, and cross-selling banking solutions ethically."
            },
            "Retail Credit & Loan Appraisal Basics": {
                "1_month": "Understand credit scoring (CIBIL), loan-to-value (LTV) ratios, debt-to-income (DTI) metrics, and borrower KYC.",
                "3_month": "Conduct credit appraisal of retail home/auto loan applications and prepare preliminary loan sanction notes."
            },
            "Ethical Compliance & Accuracy": {
                "1_month": "Review banking ethics guidelines, prevention of fraud protocols, and customer data confidentiality norms.",
                "3_month": "Complete audit compliance checklists for branch operations with zero discrepancy tolerances."
            },

            # --- Corporate Finance & Valuation ---
            "Financial Statement Analysis (P&L, Balance Sheet, Cash Flow)": {
                "1_month": "Read and deconstruct annual reports (10-K / Annual Filings) of 3 publicly listed Indian companies.",
                "3_month": "Compute DuPont analysis, operating cash cycles, and working capital dynamics across competitive peer sets."
            },
            "Advanced Financial Modeling in Excel": {
                "1_month": "Construct dynamically linked 3-statement financial models (Income Statement, Balance Sheet, Cash Flow) in Excel.",
                "3_month": "Incorporate debt schedules, working capital forecasts, depreciation waterfalls, and scenario toggles."
            },
            "Corporate Valuation (DCF, Relative Multiples)": {
                "1_month": "Learn Discounted Cash Flow (DCF) mechanics: Free Cash Flow to Firm (FCFF), WACC, and terminal value computation.",
                "3_month": "Conduct complete equity valuation case studies using DCF, EV/EBITDA, and P/E trading comparable multiples."
            },
            "Indian Corporate Taxation & GST Basics": {
                "1_month": "Understand corporate tax brackets, MAT provisions, and GST input tax credit (ITC) flow for businesses.",
                "3_month": "Model tax implications in financial statements and review corporate tax return filings (ITR-6 overview)."
            },
            "Quantitative Reasoning & Ratio Analysis": {
                "1_month": "Calculate and interpret solvency, liquidity, profitability, and asset turnover ratios across diverse industries.",
                "3_month": "Perform distress prediction modeling (Altman Z-Score) and synthesize financial health diagnoses."
            },
            "Executive Investment Reporting & Presentation": {
                "1_month": "Draft structured equity research notes summarizing company drivers, financial risks, and valuation conclusions.",
                "3_month": "Deliver a formal 10-minute pitch presentation of an investment recommendation to a mock investment committee."
            },

            # --- Healthcare: Clinical ---
            "Human Anatomy & Physiology": {
                "1_month": "Study major anatomical systems (cardiovascular, respiratory, nervous, musculoskeletal) and homeostasis.",
                "3_month": "Correlate anatomical structures with pathological disease states and clinical clinical examination landmarks."
            },
            "Clinical History Taking & Physical Examination": {
                "1_month": "Master structured medical history taking (SOCRATES pain framework, past history, systemic review).",
                "3_month": "Practice systematic clinical examination (vitals, chest auscultation, abdominal palpation) under clinical supervision."
            },
            "Basic Pharmacology & Medication Safety": {
                "1_month": "Study principal drug classifications, routes of administration, common antibiotics, and analgesics.",
                "3_month": "Review prescription safety protocols, calculate precise dosages, and identify critical drug-drug interactions."
            },
            "Infection Control & Bio-Safety Protocols": {
                "1_month": "Master aseptic technique, hand hygiene guidelines (WHO 5 Moments), and biomedical waste color-coding (BMW Rules).",
                "3_month": "Demonstrate full PPE donning/doffing, sterilization validation, and hospital-acquired infection (HAI) prevention."
            },
            "Basic Life Support (BLS) & Emergency Triage": {
                "1_month": "Enroll in an accredited Basic Life Support (BLS/CPR) certification course and understand AED operation.",
                "3_month": "Practice emergency triage categorization (START triage algorithm) in simulated mass casualty scenarios."
            },
            "Patient Empathy & Bedside Communication": {
                "1_month": "Study patient-centered communication models (SPIKES protocol for breaking difficult news, active listening).",
                "3_month": "Conduct compassionate simulated patient counseling sessions regarding diagnosis, consent, and treatment adherence."
            },
            "Medical Ethics & Patient Confidentiality": {
                "1_month": "Review the Hippocratic oath, statutory medical council codes of ethics, and patient autonomy principles.",
                "3_month": "Analyze clinical medico-legal case studies involving informed consent, emergency care, and patient record privacy."
            },

            # --- Healthcare: Administration ---
            "Healthcare Systems & Hospital Operations": {
                "1_month": "Understand hospital departmental workflows (OPD, IPD, OT, ICU, Diagnostics) and patient flow mechanics.",
                "3_month": "Analyze bed occupancy rates, average length of stay (ALOS), and hospital accreditation requirements (NABH/JCI)."
            },
            "Electronic Health Records (EHR) & Health IT": {
                "1_month": "Familiarize with Hospital Information Management Systems (HIMS) and ICD-10 medical diagnostic coding.",
                "3_month": "Configure digital clinical workflow templates and audit electronic patient records for documentation completeness."
            },
            "Healthcare Quality Assurance & Audit Compliance": {
                "1_month": "Study National Quality Assurance Standards (NQAS) and standard operating procedures (SOPs) for clinical safety.",
                "3_month": "Design and execute a hospital department quality audit, reporting incident trends and corrective actions."
            },
            "Medical Billing, Insurance & TPA Coordination": {
                "1_month": "Learn public and private health insurance mechanisms (Ayushman Bharat PMJAY, TPA pre-authorization, claim settlement).",
                "3_month": "Manage mock medical insurance claims, audit billing itemization against surgical packages, and handle query reconciliations."
            },
            "Interdepartmental Hospital Coordination": {
                "1_month": "Map inter-department communication pathways between pharmacy, nursing stations, diagnostics, and central billing.",
                "3_month": "Implement root-cause interventions to reduce patient wait times and optimize patient discharge turnover."
            },
            "Health Data Analytics & Operational Excel": {
                "1_month": "Track key hospital operational metrics using Excel pivot tables, analyzing patient census and departmental revenues.",
                "3_month": "Develop dynamic hospital operational dashboards visualizing bed utilization, pharmacy inventory turnover, and mortality ratios."
            },

            # --- Civil Services & Public Administration ---
            "Indian Polity & Constitutional Law": {
                "1_month": "Read standard constitutional treatises (M. Laxmikanth); master Fundamental Rights, DPSPs, and Preamble.",
                "3_month": "Analyze parliamentary procedures, federal center-state relations, judicial review cases, and constitutional amendments."
            },
            "Indian Economy, Development & Public Finance": {
                "1_month": "Study macroeconomic fundamentals: GDP components, inflation dynamics, monetary policy, and Union Budget overview.",
                "3_month": "Evaluate key central welfare schemes, agricultural economy, NITI Aayog policy papers, and fiscal federalism."
            },
            "Modern Indian History, Geography & Current Affairs": {
                "1_month": "Establish daily structured reading of national newspapers (The Hindu/Indian Express) and compile monthly policy summaries.",
                "3_month": "Synthesize timeline maps of modern Indian history and physical/human geography of India for General Studies."
            },
            "Ethics, Integrity & Administrative Aptitude": {
                "1_month": "Study ethical foundational principles (Nolan Committee principles, civil service values, administrative accountability).",
                "3_month": "Solve 30 UPSC General Studies Paper-IV ethics case studies demonstrating balanced administrative judgment."
            },
            "Formal Bureaucratic Drafting & Essay Writing": {
                "1_month": "Practice writing structured, evidence-backed essays on national socioeconomic and technological challenges.",
                "3_month": "Draft official administrative memos, public notices, and policy executive summaries with precise vocabulary."
            },
            "Analytical Aptitude & Logical Reasoning (CSAT)": {
                "1_month": "Practice CSAT reading comprehension passages and solve quantitative aptitude problems (percentages, ratios, data interpretation).",
                "3_month": "Complete 10 timed full-length CSAT mock papers with strict negative marking evaluation."
            },

            # --- Engineering & CAD ---
            "Core Engineering Principles (Mechanics / Thermodynamics / Circuits)": {
                "1_month": "Review fundamental physical laws, equilibrium equations, circuit theorems, or thermodynamic cycles.",
                "3_month": "Solve applied engineering engineering problems and design basic components using first-principles calculations."
            },
            "Computer-Aided Design (AutoCAD / SolidWorks / CATIA)": {
                "1_month": "Master 2D engineering drafting, orthographic projections, dimensioning standards, and layer management in AutoCAD.",
                "3_month": "Build complete 3D parametric part assemblies in SolidWorks with exploded views, BOM tables, and GD&T drawings."
            },
            "Engineering Mathematics & Analytical Calculation": {
                "1_month": "Brush up engineering mathematics: matrices, ordinary differential equations, vector calculus, and numerical methods.",
                "3_month": "Apply computational scripts (MATLAB/Python) to solve dynamic mechanical systems or circuit transient responses."
            },
            "Manufacturing Processes & Industrial Safety (OSHA)": {
                "1_month": "Study standard manufacturing methods (machining, casting, welding, CNC routing) and industrial safety norms.",
                "3_month": "Conduct a Design for Manufacturing (DFM) analysis and formulate an OSHA-compliant industrial workplace safety plan."
            },
            "Technical Report Writing & Engineering Documentation": {
                "1_month": "Learn engineering documentation formats: technical specifications, standard operating procedures, and design change orders.",
                "3_month": "Author a comprehensive 15-page engineering capstone project report with design calculations, CAD sheets, and cost estimates."
            },
            "Cross-Functional Engineering Teamwork": {
                "1_month": "Participate in collaborative design reviews, identifying manufacturing bottlenecks across mechanical and electrical teams.",
                "3_month": "Manage a multidisciplinary engineering project milestone schedule using Gantt charts and risk mitigation registers."
            },

            # --- Digital Marketing ---
            "Search Engine Optimization (SEO & Content Strategy)": {
                "1_month": "Conduct keyword research using Google Keyword Planner/Ubersuggest, audit on-page SEO factors, and optimize metadata.",
                "3_month": "Publish 3 long-form SEO-optimized articles, track Google Search Console indexation, and execute a backlink outreach campaign."
            },
            "Paid Performance Advertising (Meta Ads & Google Ads)": {
                "1_month": "Understand campaign objectives, custom audience targeting, pixel tracking, and quality score dynamics.",
                "3_month": "Create, launch, and optimize live test campaigns on Meta Ads Manager with A/B creative testing to maximize ROAS."
            },
            "Web Analytics & Conversion Tracking (Google Analytics 4)": {
                "1_month": "Set up Google Analytics 4 (GA4) with Google Tag Manager, creating custom event tags for button clicks and form submissions.",
                "3_month": "Build an e-commerce funnel drop-off report in GA4 and formulate data-backed UX recommendations to increase conversions."
            },
            "Copywriting & Content Creation": {
                "1_month": "Master copywriting frameworks (AIDA, PAS, Before-After-Bridge) for social media hooks, emails, and landing page headlines.",
                "3_month": "Write a complete 5-stage automated email drip sequence and high-converting sales landing page copy."
            },
            "Visual Design & Asset Creation (Canva / Figma Basics)": {
                "1_month": "Learn design hierarchy, typography contrast, brand palettes, and design clean social carousels on Canva/Figma.",
                "3_month": "Develop a cohesive multi-channel visual brand identity kit including logos, ad templates, and marketing banners."
            },
            "Social Media Community Management": {
                "1_month": "Analyze organic engagement strategies across LinkedIn/Instagram and build a 30-day content calendar.",
                "3_month": "Execute community growth experiments, monitor social sentiment, and manage customer DM inquiry response protocols."
            },

            # --- Education & Teaching ---
            "Subject Matter Mastery & Curriculum Delivery": {
                "1_month": "Deconstruct state/national curriculum standards for your discipline into weekly modular learning outcomes.",
                "3_month": "Author an engaging complete 8-week course curriculum unit complete with lesson plans, lecture notes, and study guides."
            },
            "Pedagogical Techniques & Classroom Management": {
                "1_month": "Study active learning methodologies (flipped classroom, inquiry-based learning, Bloom's Taxonomy).",
                "3_month": "Record and self-review 3 simulated 45-minute classroom lessons incorporating interactive student checks for understanding."
            },
            "Public Speaking & Verbal Articulation": {
                "1_month": "Practice vocal projection, pacing, avoiding filler words, and framing concepts with relatable real-world analogies.",
                "3_month": "Deliver live workshops/webinars to student audiences, effectively managing spontaneous questions and discussion."
            },
            "Student Assessment, Rubrics & Constructive Feedback": {
                "1_month": "Design formative diagnostic quizzes and design clear rubrics for project-based and essay evaluations.",
                "3_month": "Grade student mock submissions using differentiated feedback techniques that encourage student growth mindset."
            },
            "Educational Technology & LMS (Google Classroom, Zoom)": {
                "1_month": "Set up a structured Google Classroom/Canvas course module with assignments, grading rubrics, and video links.",
                "3_month": "Integrate interactive assessment tools (Kahoot, Mentimeter, Padlet) into digital instruction workflows."
            },
            "Student Mentorship & Empathy": {
                "1_month": "Study student developmental psychology and techniques for active listening during academic advising conversations.",
                "3_month": "Formulate a personalized academic recovery plan for struggling students addressing motivation, study habits, and anxiety."
            },

            # --- Scientific Research ---
            "Scientific Method & Experimental Design": {
                "1_month": "Formulate testable research questions, null/alternative hypotheses, and design controlled experimental variables.",
                "3_month": "Author a formal scientific research proposal outlining background, hypothesis, experimental design, and expected results."
            },
            "Statistical Analysis & Scientific Computing": {
                "1_month": "Master hypothesis testing (t-tests, ANOVA, Chi-square) and data visualization using Python (SciPy) or R.",
                "3_month": "Perform rigorous statistical analysis on an empirical dataset, computing effect sizes and confidence intervals."
            },
            "Laboratory Instrumentation & Protocol Compliance": {
                "1_month": "Review Good Laboratory Practice (GLP) standards, chemical/biological safety data sheets, and calibration procedures.",
                "3_month": "Document standardized operating procedures (SOP) for experimental setups with rigorous precision logging."
            },
            "Scholarly Literature Review & Citation Standards": {
                "1_month": "Conduct structured literature searches on PubMed/Google Scholar and manage references using Zotero/Mendeley.",
                "3_month": "Author a comprehensive 10-page literature review paper synthesizing recent advances and identifying research gaps."
            },
            "Manuscript Writing & Scientific Presentation": {
                "1_month": "Learn the IMRaD (Introduction, Methods, Results, Discussion) scientific paper structure and scientific figure guidelines.",
                "3_month": "Prepare and defend an academic poster presentation summarizing experimental methodology and quantitative findings."
            },
            "Research Ethics & Academic Integrity": {
                "1_month": "Review institutional research ethics codes, plagiarism standards (Turnitin policies), and data stewardship guidelines.",
                "3_month": "Complete certified research ethics training modules (e.g., CITI Program overview or national bioethics protocols)."
            }
        }

    def get_proficiency_multiplier(self, skill_level):
        """Map Likert rating (1-5) to deterministic credit multiplier."""
        try:
            level = float(skill_level)
        except (ValueError, TypeError):
            level = 3.0

        if level >= 4:
            return 1.0  # Proficient / Advanced: 100% of weight
        elif level == 3:
            return 0.8  # Intermediate / Competent: 80% of weight
        elif level >= 1:
            return 0.5  # Novice / Developing: 50% of weight
        else:
            return 0.0

    def evaluate_interactive_role(self, role_name, current_skills_list, skill_level=3):
        """
        Layer 2 Assessment Engine:
        Evaluates user against role-specific evidence-based competencies.
        """
        if role_name not in self.interactive_roles:
            return {
                "status": "UNMAPPED_ROLE",
                "message": f"Role '{role_name}' is not in the interactive competency framework.",
                "readiness_score": 0.0,
                "readiness_tier": "Not Evaluated",
                "strong_skills": [],
                "skills_to_strengthen": [],
                "skill_gaps": [],
                "roadmap_1_month": ["Consult academic advisor or review broader industry benchmarks for this specialty."],
                "roadmap_3_month": ["Explore foundational skills in communication, digital literacy, and problem-solving."]
            }

        benchmark = self.interactive_roles[role_name]
        total_benchmark_points = benchmark["total_weighted_points"]
        required_skills = benchmark["skills"]

        cleaned_user_skills = set([s.strip() for s in current_skills_list if s.strip()])

        earned_score = 0.0
        strong_skills = []
        skills_to_strengthen = []
        skill_gaps = []

        mult = self.get_proficiency_multiplier(skill_level)

        for req in required_skills:
            skill_name = req["skill"]
            weight = req["weight"]
            cat = req["category"]
            rationale = req["rationale"]

            if skill_name in cleaned_user_skills:
                item_score = weight * mult
                earned_score += item_score

                skill_info = {
                    "skill": skill_name,
                    "weight": weight,
                    "category": cat,
                    "points_earned": round(item_score, 2),
                    "max_points": weight
                }

                if mult == 1.0:
                    strong_skills.append(skill_info)
                else:
                    skills_to_strengthen.append(skill_info)
            else:
                skill_gaps.append({
                    "skill": skill_name,
                    "weight": weight,
                    "category": cat,
                    "priority": "High Priority" if weight == 3 else ("Medium Priority" if weight == 2 else "Foundational"),
                    "rationale": rationale
                })

        readiness_pct = (earned_score / total_benchmark_points) * 100.0
        readiness_pct = round(min(100.0, max(0.0, readiness_pct)), 2)

        if readiness_pct >= 80.0:
            tier = "High Career Readiness"
            summary_desc = "Strong alignment with entry-level industry expectations; ready for internship/job placement."
        elif readiness_pct >= 60.0:
            tier = "Moderate Career Readiness"
            summary_desc = "Solid fundamental competencies; targeted intervention required in remaining high-priority gaps."
        elif readiness_pct >= 40.0:
            tier = "Emerging Career Readiness"
            summary_desc = "Partial alignment; dedicated skill-building necessary in core technical/domain competencies."
        else:
            tier = "Low Career Readiness"
            summary_desc = "Early exploratory stage; foundational learning and structured coaching strongly advised."

        # Generate role-specific roadmaps
        roadmap_1m = []
        roadmap_3m = []

        sorted_gaps = sorted(skill_gaps, key=lambda x: x["weight"], reverse=True)

        for gap in sorted_gaps:
            s_name = gap["skill"]
            if s_name in self.skill_recommendations:
                rec = self.skill_recommendations[s_name]
                roadmap_1m.append(f"**Focus on {s_name} (Priority: {gap['priority']}):** {rec['1_month']}")
                roadmap_3m.append(f"**Master {s_name}:** {rec['3_month']}")
            else:
                roadmap_1m.append(f"**Develop {s_name} (Priority: {gap['priority']}):** Study fundamental textbooks and practical modules for this domain competency.")
                roadmap_3m.append(f"**Apply {s_name}:** Complete a practical project demonstrating proficiency in {s_name}.")

        for s_strength in skills_to_strengthen:
            s_name = s_strength["skill"]
            if s_name in self.skill_recommendations:
                rec = self.skill_recommendations[s_name]
                roadmap_1m.append(f"**Strengthen {s_name} (Current Level: {skill_level}/5):** Advance from intermediate to professional execution.")
                roadmap_3m.append(f"**Solidify {s_name}:** {rec['3_month']}")

        if not roadmap_1m:
            roadmap_1m.append("Maintain existing strong competencies; undertake advanced domain certifications or real-world client freelance projects.")
        if not roadmap_3m:
            roadmap_3m.append("Prepare for industry interviews, build a comprehensive portfolio, and seek professional mentorship.")

        return {
            "status": "SUCCESS",
            "role_name": role_name,
            "career_track": benchmark.get("career_track", role_name),
            "description": benchmark.get("description", ""),
            "readiness_score": readiness_pct,
            "readiness_tier": tier,
            "tier_description": summary_desc,
            "total_benchmark_points": total_benchmark_points,
            "earned_weighted_score": round(earned_score, 2),
            "strong_skills_count": len(strong_skills),
            "strong_skills": strong_skills,
            "skills_to_strengthen_count": len(skills_to_strengthen),
            "skills_to_strengthen": skills_to_strengthen,
            "skill_gaps_count": len(skill_gaps),
            "skill_gaps": skill_gaps,
            "roadmap_1_month": roadmap_1m[:5],
            "roadmap_3_month": roadmap_3m[:5]
        }

    # Backward compatibility for Layer 1 survey baseline batch evaluation
    def evaluate_readiness(self, career_field, current_skills_list, skill_level=3):
        """
        Layer 1 Survey Baseline Engine:
        Evaluates survey cohort respondents using the original 8-career survey matrix.
        """
        if career_field not in self.catalog:
            return {
                "status": "UNMAPPED_CAREER",
                "message": f"Career track '{career_field}' is not in the benchmark matrix.",
                "readiness_score": 0.0,
                "readiness_tier": "Not Evaluated",
                "strong_skills": [],
                "skills_to_strengthen": [],
                "skill_gaps": [],
                "roadmap_1_month": ["Review broader industry benchmarks for this specialty."],
                "roadmap_3_month": ["Explore foundational skills in communication, digital literacy, and problem-solving."]
            }

        benchmark = self.catalog[career_field]
        total_benchmark_points = benchmark["total_weighted_points"]
        required_skills = benchmark["skills"]

        cleaned_user_skills = set([s.strip() for s in current_skills_list if s.strip()])

        earned_score = 0.0
        strong_skills = []
        skills_to_strengthen = []
        skill_gaps = []

        mult = self.get_proficiency_multiplier(skill_level)

        for req in required_skills:
            skill_name = req["skill"]
            weight = req["weight"]
            cat = req["category"]
            rationale = req["rationale"]

            if skill_name in cleaned_user_skills:
                item_score = weight * mult
                earned_score += item_score

                skill_info = {
                    "skill": skill_name,
                    "weight": weight,
                    "category": cat,
                    "points_earned": round(item_score, 2),
                    "max_points": weight
                }

                if mult == 1.0:
                    strong_skills.append(skill_info)
                else:
                    skills_to_strengthen.append(skill_info)
            else:
                skill_gaps.append({
                    "skill": skill_name,
                    "weight": weight,
                    "category": cat,
                    "priority": "High Priority" if weight == 3 else ("Medium Priority" if weight == 2 else "Foundational"),
                    "rationale": rationale
                })

        readiness_pct = (earned_score / total_benchmark_points) * 100.0
        readiness_pct = round(min(100.0, max(0.0, readiness_pct)), 2)

        if readiness_pct >= 80.0:
            tier = "High Career Readiness"
            summary_desc = "Strong alignment with entry-level industry expectations."
        elif readiness_pct >= 60.0:
            tier = "Moderate Career Readiness"
            summary_desc = "Solid fundamental competencies; targeted intervention required."
        elif readiness_pct >= 40.0:
            tier = "Emerging Career Readiness"
            summary_desc = "Partial alignment; dedicated skill-building necessary."
        else:
            tier = "Low Career Readiness"
            summary_desc = "Early exploratory stage; foundational learning advised."

        return {
            "status": "SUCCESS",
            "career_field": career_field,
            "readiness_score": readiness_pct,
            "readiness_tier": tier,
            "tier_description": summary_desc,
            "total_benchmark_points": total_benchmark_points,
            "earned_weighted_score": round(earned_score, 2),
            "strong_skills_count": len(strong_skills),
            "strong_skills": strong_skills,
            "skills_to_strengthen_count": len(skills_to_strengthen),
            "skills_to_strengthen": skills_to_strengthen,
            "skill_gaps_count": len(skill_gaps),
            "skill_gaps": skill_gaps,
            "roadmap_1_month": [],
            "roadmap_3_month": []
        }

    def batch_evaluate_dataframe(self, df):
        """
        Evaluate readiness across all rows of a survey dataframe.
        """
        results = []
        for idx, row in df.iterrows():
            career = row.get("career_field_interest", "Not Specified")
            skills_str = str(row.get("current_skills", ""))
            skills_list = [s.strip() for s in skills_str.split(";") if s.strip()]
            level = row.get("overall_skill_level", 3)

            res = self.evaluate_readiness(career, skills_list, level)

            results.append({
                "email": row.get("email", f"resp_{idx}"),
                "career_field_interest": career,
                "overall_skill_level": level,
                "current_skills_declared": len(skills_list),
                "model_status": res["status"],
                "readiness_score": res["readiness_score"],
                "readiness_tier": res["readiness_tier"],
                "strong_skills_count": res.get("strong_skills_count", 0),
                "skills_to_strengthen_count": res.get("skills_to_strengthen_count", 0),
                "skill_gaps_count": res.get("skill_gaps_count", 0),
                "perceived_skill_gap": row.get("perceived_skill_gap", "Unknown")
            })

        return pd.DataFrame(results)
