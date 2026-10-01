"""
Career Readiness & Skill-Match Model
Author: Data Science CEP Project
Purpose: A deterministic, explainable, rule-based scoring engine that evaluates an individual's
         skill inventory and proficiency against benchmark competency requirements for career tracks.
Input: 
  - Career-Skill Matrix (05_Career_Skill_Mapping/Career_Skills/career_skills_catalog.json)
  - User Current Skills (List of strings)
  - User Skill Level (Integer 1 to 5)
Output:
  - Skill Match Score (Percentage 0-100%)
  - Strong Skills (List)
  - Skills to Strengthen (List)
  - Critical Skill Gaps (List with weights & priority)
  - 1-Month and 3-Month Actionable Roadmaps
"""

import json
import os
import pandas as pd
import numpy as np

class CareerReadinessModel:
    def __init__(self, catalog_path):
        if not os.path.exists(catalog_path):
            raise FileNotFoundError(f"Catalog file not found at: {catalog_path}")
        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
        self.available_careers = list(self.catalog.keys())
        
        # Skill-specific learning recommendations for roadmap generation
        self.skill_recommendations = {
            "Programming/Coding": {
                "1_month": "Master Python/JavaScript fundamentals (loops, functions, OOP, data structures) via LeetCode/HackerRank.",
                "3_month": "Build 2 full-stack/backend projects, learn Git/GitHub collaboration, and contribute to an open-source repo."
            },
            "Data Analysis / Data Scientist": {
                "1_month": "Practice data manipulation using Pandas, NumPy, and SQL queries; learn EDA visualization with Seaborn.",
                "3_month": "Execute 2 end-to-end data analysis projects on real datasets (Kaggle), build a Power BI/Streamlit dashboard."
            },
            "Artificial Intelligence / Machine Learning": {
                "1_month": "Learn core ML algorithms (Regression, Classification, K-Means) using Scikit-Learn; understand evaluation metrics.",
                "3_month": "Train and evaluate models on real-world datasets, practice feature engineering, and deploy a model pipeline."
            },
            "Computer/Digital Skills": {
                "1_month": "Familiarize with Linux terminal commands, Git version control, and cloud environment basics (Google Cloud/AWS).",
                "3_month": "Automate routine computer workflows with shell/Python scripts; configure virtual environments and containers."
            },
            "Microsoft Office/Excel": {
                "1_month": "Master advanced Excel functions (XLOOKUP, Pivot Tables, SUMIFS, conditional formatting).",
                "3_month": "Build dynamic financial/operational dashboard models and learn basic Power Query/VBA automation."
            },
            "Communication Skills": {
                "1_month": "Practice structured executive communication (Minto Pyramid Principle); write concise emails and technical summaries.",
                "3_month": "Join Toastmasters or participate in group discussions, presentations, and technical mock interviews."
            },
            "English Language Skills": {
                "1_month": "Daily professional reading (industry journals/news) and formal technical report drafting practice.",
                "3_month": "Enroll in business English communication modules; practice formal vocabulary and oral workplace fluency."
            },
            "Problem-Solving": {
                "1_month": "Practice root-cause analysis frameworks (5 Whys, Issue Trees) and solve 15 logic puzzles/case prompts.",
                "3_month": "Participate in hackathons, business case competitions, or system troubleshooting sprints."
            },
            "Critical Thinking": {
                "1_month": "Learn cognitive bias identification and question baseline assumptions in analytical problem sets.",
                "3_month": "Conduct structured comparative evaluations of technologies/strategies; publish reasoned case studies."
            },
            "Leadership": {
                "1_month": "Take initiative to lead a small project module, study team leadership frameworks and delegating principles.",
                "3_month": "Lead a student club/college team initiative or organize a community workshop from inception to execution."
            },
            "Teamwork": {
                "1_month": "Use agile collaboration tools (Trello/Jira/Slack) and practice constructive feedback in group tasks.",
                "3_month": "Complete a multi-person collaborative software/research sprint adhering to peer review protocols."
            },
            "Time Management": {
                "1_month": "Implement Pomodoro and Eisenhower Matrix techniques; track and eliminate daily productivity leaks.",
                "3_month": "Maintain strict sprint delivery timelines across multiple concurrent academic and skill projects."
            },
            "Creativity": {
                "1_month": "Practice brainstorming exercises (SCAMPER technique) to ideate novel solutions to ordinary pain points.",
                "3_month": "Design a unique product feature, creative campaign, or pedagogical tool demonstrating fresh approaches."
            },
            "Presentation/Public Speaking": {
                "1_month": "Design clean, high-impact slide decks; record yourself presenting a 5-minute technical topic weekly.",
                "3_month": "Deliver 3 live presentations to an audience (seminar, webinars, college symposium) with Q&A defense."
            }
        }

    def get_proficiency_multiplier(self, skill_level):
        """Map Likert rating (1-5) to credit multiplier."""
        try:
            level = float(skill_level)
        except (ValueError, TypeError):
            level = 3.0
            
        if level >= 4:
            return 1.0  # Proficient / Advanced: 100% of weight
        elif level == 3:
            return 0.8  # Intermediate: 80% of weight
        elif level >= 1:
            return 0.5  # Novice / Developing: 50% of weight
        else:
            return 0.0

    def evaluate_readiness(self, career_field, current_skills_list, skill_level=3):
        """
        Evaluate readiness score, strong skills, gaps, and roadmaps.
        """
        # Handle non-standard or unmapped career fallback
        if career_field not in self.catalog:
            # Fallback to closest or general baseline
            return {
                "status": "UNMAPPED_CAREER",
                "message": f"Career track '{career_field}' is not in the benchmark matrix.",
                "readiness_score": 0.0,
                "readiness_tier": "Not Evaluated",
                "strong_skills": [],
                "skills_to_strengthen": [],
                "skill_gaps": [],
                "roadmap_1_month": ["Consult academic advisor or review broader industry benchmarks for this specialty."],
                "roadmap_3_month": ["Explore foundational skills in communication, digital literacy, and problem-solving."]
            }
            
        benchmark = self.catalog[career_field]
        total_benchmark_points = benchmark["total_weighted_points"]
        required_skills = benchmark["skills"]
        
        # Clean current skills input
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
                # Skill possessed
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
                # Skill gap
                skill_gaps.append({
                    "skill": skill_name,
                    "weight": weight,
                    "category": cat,
                    "priority": "High Priority" if weight == 3 else ("Medium Priority" if weight == 2 else "Foundational"),
                    "rationale": rationale
                })
                
        # Calculate percentage readiness index
        readiness_pct = (earned_score / total_benchmark_points) * 100.0
        readiness_pct = round(min(100.0, max(0.0, readiness_pct)), 2)
        
        # Classify readiness tier
        if readiness_pct >= 80.0:
            tier = "High Career Readiness"
            summary_desc = "Strong alignment with entry-level industry expectations; ready for internship/job placement."
        elif readiness_pct >= 60.0:
            tier = "Moderate Career Readiness"
            summary_desc = "Solid fundamental competencies; targeted intervention required in remaining high-priority gaps."
        elif readiness_pct >= 40.0:
            tier = "Emerging Career Readiness"
            summary_desc = "Partial alignment; substantial dedicated skill-building necessary in core technical/domain competencies."
        else:
            tier = "Low Career Readiness"
            summary_desc = "Early exploratory stage; foundational learning and structured coaching strongly advised."
            
        # Generate 1-month and 3-month actionable roadmaps
        roadmap_1m = []
        roadmap_3m = []
        
        # Prioritize gaps with weight 3, then weight 2
        sorted_gaps = sorted(skill_gaps, key=lambda x: x["weight"], reverse=True)
        
        for gap in sorted_gaps:
            s_name = gap["skill"]
            if s_name in self.skill_recommendations:
                rec = self.skill_recommendations[s_name]
                roadmap_1m.append(f"**Focus on {s_name} (Priority: {gap['priority']}):** {rec['1_month']}")
                roadmap_3m.append(f"**Master {s_name}:** {rec['3_month']}")
                
        # If user has skills to strengthen, add them to the roadmap
        for s_strength in skills_to_strengthen:
            s_name = s_strength["skill"]
            if s_name in self.skill_recommendations:
                rec = self.skill_recommendations[s_name]
                roadmap_1m.append(f"**Strengthen {s_name} (Current Level: {skill_level}/5):** Advance from intermediate to professional execution.")
                roadmap_3m.append(f"**Solidify {s_name}:** {rec['3_month']}")
                
        # Fallback if roadmap is sparse
        if not roadmap_1m:
            roadmap_1m.append("Maintain existing strong competencies; undertake advanced domain certifications or real-world client freelance projects.")
        if not roadmap_3m:
            roadmap_3m.append("Prepare for industry interviews, build a comprehensive GitHub/Portfolio website, and seek professional mentorship.")
            
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
            "roadmap_1_month": roadmap_1m[:5],  # top 5 prioritized steps
            "roadmap_3_month": roadmap_3m[:5]
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
