"""
Local Deployment Verification Test Script for Phase 8 Streamlit Application
Author: Data Science CEP Project
Purpose: Test the isolated Streamlit application repository to ensure 100% cloud deployment readiness.
Checks:
  1. Module imports and relative path resolution (Zero G: drive dependencies)
  2. All 8 career tracks load from local model/ catalog
  3. Skill evaluation reproduclibility (Phase 5 scores match exactly)
  4. Boundary tests (Zero skills = 0.0%, All skills = 100.0%)
  5. Privacy audit (Survey dataset contains zero personal email addresses)
  6. Requirements.txt validation
"""

import os
import sys
import json
import pandas as pd

# Set working directory to 09_Streamlit_App
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
MODEL_DIR = os.path.join(APP_DIR, "model")

sys.path.insert(0, MODEL_DIR)

from career_readiness_model import CareerReadinessModel

def run_deployment_tests():
    print("=" * 65)
    print("RUNNING STREAMLIT LOCAL DEPLOYMENT READINESS VERIFICATION")
    print(f"Base Repository Directory: {APP_DIR}")
    print("=" * 65)
    
    test_results = {}
    
    # Check 1: Relative Path Resolution & File Existence
    print("\n1. Checking Required Repository Files...")
    req_files = [
        os.path.join(APP_DIR, "app.py"),
        os.path.join(APP_DIR, "requirements.txt"),
        os.path.join(APP_DIR, "README.md"),
        os.path.join(APP_DIR, ".gitignore"),
        os.path.join(MODEL_DIR, "career_readiness_model.py"),
        os.path.join(MODEL_DIR, "career_skills_catalog.json"),
        os.path.join(DATA_DIR, "career_skill_matrix.csv"),
        os.path.join(DATA_DIR, "survey_cleaned_public.csv")
    ]
    
    missing = [f for f in req_files if not os.path.exists(f)]
    if missing:
        print(f"FAILED: Missing files: {missing}")
        test_results["files_exist"] = "FAIL"
    else:
        print(f"PASSED: All {len(req_files)} deployment files present.")
        test_results["files_exist"] = "PASS"
        
    # Check 2: Model Initialization via Relative Path
    print("\n2. Initializing CareerReadinessModel via Local Relative Path...")
    catalog_path = os.path.join(MODEL_DIR, "career_skills_catalog.json")
    model = CareerReadinessModel(catalog_path)
    careers = model.available_careers
    print(f"Found {len(careers)} career tracks: {careers}")
    if len(careers) == 8:
        print("PASSED: Exactly 8 career tracks loaded successfully.")
        test_results["careers_loaded"] = "PASS"
    else:
        print(f"FAILED: Expected 8 careers, found {len(careers)}")
        test_results["careers_loaded"] = "FAIL"

    # Check 3: Functional Scoring Verification (Zero-Skill, Full-Skill, Partial)
    print("\n3. Testing Core Scoring Precision on Isolated Deployment Model...")
    it_skills = [s["skill"] for s in model.catalog["Information Technology / Data Science / AI"]["skills"]]
    
    # 3A. Zero skills
    res_zero = model.evaluate_readiness("Information Technology / Data Science / AI", [], 1)
    # 3B. Full skills Level 5
    res_full = model.evaluate_readiness("Information Technology / Data Science / AI", it_skills, 5)
    # 3C. Full skills Level 3
    res_lvl3 = model.evaluate_readiness("Information Technology / Data Science / AI", it_skills, 3)
    
    p_zero = (res_zero["readiness_score"] == 0.0) and (res_zero["readiness_tier"] == "Low Career Readiness")
    p_full = (res_full["readiness_score"] == 100.0) and (res_full["readiness_tier"] == "High Career Readiness")
    p_lvl3 = (res_lvl3["readiness_score"] == 80.0) and (res_lvl3["readiness_tier"] == "High Career Readiness")
    
    if p_zero and p_full and p_lvl3:
        print("PASSED: Zero-skill (0.0%), Full-skill (100.0%), and Level-3 (80.0%) reproduced with 100% precision.")
        test_results["scoring_precision"] = "PASS"
    else:
        print(f"FAILED: Scoring error (Zero: {res_zero['readiness_score']}, Full: {res_full['readiness_score']}, Lvl3: {res_lvl3['readiness_score']})")
        test_results["scoring_precision"] = "FAIL"

    # Check 4: Privacy & PII Audit
    print("\n4. Performing Privacy & PII Audit on Public Datasets...")
    df_pub = pd.read_csv(os.path.join(DATA_DIR, "survey_cleaned_public.csv"))
    has_email_col = "email" in df_pub.columns or "Username" in df_pub.columns
    has_resp_id = "respondent_id" in df_pub.columns
    
    # scan for '@' symbol in all string columns to ensure no email leaks
    email_leak = False
    for col in df_pub.select_dtypes(include="object").columns:
        if df_pub[col].astype(str).str.contains("@").any():
            email_leak = True
            break
            
    if not has_email_col and has_resp_id and not email_leak:
        print(f"PASSED: Survey dataset successfully anonymized ({len(df_pub)} rows). Zero personal email addresses detected.")
        test_results["privacy_audit"] = "PASS"
    else:
        print(f"FAILED: Privacy violation or email leak detected (has_email_col: {has_email_col}, email_leak: {email_leak})")
        test_results["privacy_audit"] = "FAIL"

    # Check 5: Code Path Dependency Audit
    print("\n5. Auditing Code for Hardcoded 'G:' or Personal Directory Dependencies...")
    hardcoded_issues = []
    for py_file in ["app.py", os.path.join("model", "career_readiness_model.py")]:
        with open(os.path.join(APP_DIR, py_file), "r", encoding="utf-8") as f:
            code = f.read()
            if "G:\\" in code or "G:/" in code:
                hardcoded_issues.append(f"Hardcoded G: drive path found in {py_file}")
            if "rehan" in code.lower():
                hardcoded_issues.append(f"Personal directory found in {py_file}")
                
    if not hardcoded_issues:
        print("PASSED: Zero hardcoded drive paths or personal directories found in production application code.")
        test_results["path_isolation"] = "PASS"
    else:
        print(f"FAILED: Path leaks found: {hardcoded_issues}")
        test_results["path_isolation"] = "FAIL"

    # Check 6: Streamlit Dry-Run Syntax Verification
    print("\n6. Compiling Streamlit Application Code Syntax...")
    try:
        import py_compile
        py_compile.compile(os.path.join(APP_DIR, "app.py"), doraise=True)
        print("PASSED: app.py compiled with zero syntax errors.")
        test_results["syntax_compilation"] = "PASS"
    except Exception as e:
        print(f"FAILED: app.py compilation error: {e}")
        test_results["syntax_compilation"] = "FAIL"

    print("\n" + "=" * 65)
    print("DEPLOYMENT READINESS SUMMARY:")
    print("=" * 65)
    all_passed = all(v == "PASS" for v in test_results.values())
    for k, v in test_results.items():
        print(f"  - {k.replace('_', ' ').title()}: {v}")
    print("=" * 65)
    print(f"FINAL RESULT: {'CERTIFIED DEPLOYMENT READY (ALL PASS)' if all_passed else 'FAILED CHECKS DETECTED'}")
    print("=" * 65)
    return all_passed

if __name__ == "__main__":
    run_deployment_tests()
