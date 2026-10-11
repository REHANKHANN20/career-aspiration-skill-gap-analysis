import os
import sys
import json
import pandas as pd

app_dir = r"G:\My Drive\CEP_Career_Aspiration_Skill_Gap\09_Streamlit_App"
sys.path.append(os.path.join(app_dir, "model"))
from career_readiness_model import CareerReadinessModel

model = CareerReadinessModel()

print("=" * 65)
print("COMPREHENSIVE REGRESSION & INTEGRITY VERIFICATION SUITE")
print("=" * 65)

# Test 1: All 11 Roles & Boundary Conditions
passed_tests = 0
for role in model.available_roles:
    r_info = model.interactive_roles[role]
    skills = [s["skill"] for s in r_info["skills"]]

    # Boundary 1: Empty skills -> 0.0%
    res_empty = model.evaluate_interactive_role(role, [], 1)
    assert res_empty["readiness_score"] == 0.0
    assert len(res_empty["skill_gaps"]) == len(skills)
    assert len(res_empty["roadmap_1_month"]) > 0
    assert len(res_empty["roadmap_3_month"]) > 0
    passed_tests += 1

    # Boundary 2: All skills Level 5 -> 100.0%
    res_full = model.evaluate_interactive_role(role, skills, 5)
    assert res_full["readiness_score"] == 100.0
    assert len(res_full["skill_gaps"]) == 0
    assert len(res_full["strong_skills"]) == len(skills)
    passed_tests += 1

    # Boundary 3: All skills Level 3 -> 80.0%
    res_l3 = model.evaluate_interactive_role(role, skills, 3)
    assert abs(res_l3["readiness_score"] - 80.0) < 1e-4
    passed_tests += 1

    # Boundary 4: Partial skills with exact calculation
    res_one = model.evaluate_interactive_role(role, [skills[0]], 4)
    expected_pts = r_info["skills"][0]["weight"] * 1.0
    expected_pct = round((expected_pts / r_info["total_weighted_points"]) * 100.0, 2)
    assert res_one["readiness_score"] == expected_pct
    passed_tests += 1

print(f"TEST 1 PASSED: All 11 roles verified across 4 boundaries ({passed_tests} tests).")

# Test 2: Unmapped role fallback
res_unmapped = model.evaluate_interactive_role("Unknown Specialist", ["A", "B"], 3)
assert res_unmapped["status"] == "UNMAPPED_ROLE"
assert res_unmapped["readiness_score"] == 0.0
print("TEST 2 PASSED: Unmapped role fallback returns status=UNMAPPED_ROLE.")

# Test 3: Historical survey reproducibility (Layer 1)
df_survey = pd.read_csv(os.path.join(app_dir, "data", "survey_cleaned_public.csv"))
assert len(df_survey) == 49
batch_res = model.batch_evaluate_dataframe(df_survey)
expected_mean = df_survey["readiness_score"].mean()
assert abs(batch_res["readiness_score"].mean() - expected_mean) < 1e-6
print(f"TEST 3 PASSED: Final survey cohort intact (49 rows), baseline readiness {expected_mean:.2f}% verified.")

# Test 4: Domain recommendations verification
res_bank = model.evaluate_interactive_role("Banking Operations & Commercial Banking", ["Spreadsheet Management (Excel / Sheets)"], 3)
roadmap_str = " ".join(res_bank["roadmap_1_month"] + res_bank["roadmap_3_month"]).lower()
assert "python" not in roadmap_str
assert "pandas" not in roadmap_str
assert "kyc" in roadmap_str or "accounting" in roadmap_str
print("TEST 4 PASSED: Banking roadmap contains zero tech bias (no Python/Pandas).")

# Test 5: Clinical healthcare recommendations verification
res_med = model.evaluate_interactive_role("Healthcare — Clinical & Patient Care", ["Human Anatomy & Physiology"], 3)
med_roadmap_str = " ".join(res_med["roadmap_1_month"] + res_med["roadmap_3_month"]).lower()
assert "history taking" in med_roadmap_str or "pharmacology" in med_roadmap_str or "bls" in med_roadmap_str
print("TEST 5 PASSED: Clinical healthcare accurately assesses clinical & medical skills.")

print("=" * 65)
print("ALL REGRESSION & DATA INTEGRITY TESTS PASSED SUCCESSFULLY!")
print("=" * 65)
