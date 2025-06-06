#!/usr/bin/env python3
"""
Resume Validation Script

This script validates that your resume.json is properly formatted 
and contains all the necessary fields for the Job Seeker Agent.
"""

import json
import sys
from typing import Dict, Any, List

def validate_resume_structure(resume_data: Dict[str, Any]) -> List[str]:
    """
    Validate the resume structure and return any issues found
    
    Args:
        resume_data: The loaded resume data
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Required top-level fields
    required_fields = ['name', 'title', 'contact', 'summary', 'skills', 'experience', 'education']
    
    for field in required_fields:
        if field not in resume_data:
            errors.append(f"Missing required field: {field}")
        elif not resume_data[field]:
            errors.append(f"Empty required field: {field}")
    
    # Validate contact information
    if 'contact' in resume_data and isinstance(resume_data['contact'], dict):
        contact_fields = ['email', 'phone']
        for field in contact_fields:
            if field not in resume_data['contact'] or not resume_data['contact'][field]:
                errors.append(f"Missing or empty contact field: {field}")
    
    # Validate skills (should be a list)
    if 'skills' in resume_data:
        if not isinstance(resume_data['skills'], list):
            errors.append("Skills should be a list of strings")
        elif len(resume_data['skills']) == 0:
            errors.append("Skills list is empty")
    
    # Validate experience (should be a list of objects)
    if 'experience' in resume_data:
        if not isinstance(resume_data['experience'], list):
            errors.append("Experience should be a list of job objects")
        elif len(resume_data['experience']) == 0:
            errors.append("Experience list is empty")
        else:
            for i, exp in enumerate(resume_data['experience']):
                if not isinstance(exp, dict):
                    errors.append(f"Experience item {i+1} should be an object")
                    continue
                
                exp_required = ['title', 'company', 'start_date', 'description']
                for field in exp_required:
                    if field not in exp or not exp[field]:
                        errors.append(f"Experience item {i+1} missing: {field}")
    
    # Validate education (should be a list of objects)
    if 'education' in resume_data:
        if not isinstance(resume_data['education'], list):
            errors.append("Education should be a list of education objects")
        elif len(resume_data['education']) == 0:
            errors.append("Education list is empty")
        else:
            for i, edu in enumerate(resume_data['education']):
                if not isinstance(edu, dict):
                    errors.append(f"Education item {i+1} should be an object")
                    continue
                
                edu_required = ['school', 'degree']
                for field in edu_required:
                    if field not in edu or not edu[field]:
                        errors.append(f"Education item {i+1} missing: {field}")
    
    return errors

def print_resume_summary(resume_data: Dict[str, Any]) -> None:
    """
    Print a summary of the resume data
    """
    print("\n" + "="*60)
    print("RESUME SUMMARY")
    print("="*60)
    
    print(f"Name: {resume_data.get('name', 'N/A')}")
    print(f"Title: {resume_data.get('title', 'N/A')}")
    print(f"Email: {resume_data.get('contact', {}).get('email', 'N/A')}")
    print(f"Skills Count: {len(resume_data.get('skills', []))}")
    print(f"Experience Entries: {len(resume_data.get('experience', []))}")
    print(f"Education Entries: {len(resume_data.get('education', []))}")
    print(f"Projects: {len(resume_data.get('projects', []))}")
    print(f"Certifications: {len(resume_data.get('certifications', []))}")
    print(f"Awards: {len(resume_data.get('awards', []))}")
    
    # Show skills
    skills = resume_data.get('skills', [])
    if skills:
        print(f"\nTop Skills: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
    
    # Show recent experience
    experience = resume_data.get('experience', [])
    if experience:
        recent = experience[0]
        print(f"Current/Recent Role: {recent.get('title', 'N/A')} at {recent.get('company', 'N/A')}")

def main():
    """
    Main validation function
    """
    resume_path = "data/resume.json"
    
    print("Job Seeker Agent - Resume Validator")
    print("====================================\n")
    
    try:
        # Load the resume
        print(f"Loading resume from: {resume_path}")
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        
        print("✅ Resume JSON loaded successfully")
        
        # Validate structure
        print("\nValidating resume structure...")
        errors = validate_resume_structure(resume_data)
        
        if errors:
            print("\n❌ VALIDATION ERRORS FOUND:")
            for error in errors:
                print(f"  • {error}")
            print("\nPlease fix these issues before using the Job Seeker Agent.")
            sys.exit(1)
        else:
            print("✅ Resume structure is valid!")
        
        # Print summary
        print_resume_summary(resume_data)
        
        # Final check
        print("\n" + "="*60)
        print("READINESS CHECK")
        print("="*60)
        
        checks = [
            ("Resume data loaded", True),
            ("Required fields present", len(errors) == 0),
            ("Contact information", bool(resume_data.get('contact', {}).get('email'))),
            ("Professional summary", bool(resume_data.get('summary'))),
            ("Skills listed", len(resume_data.get('skills', [])) > 0),
            ("Work experience", len(resume_data.get('experience', [])) > 0),
            ("Education background", len(resume_data.get('education', [])) > 0),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False
        
        print("\n" + "="*60)
        if all_passed:
            print("🎉 YOUR RESUME IS READY FOR THE JOB SEEKER AGENT!")
            print("\nNext steps:")
            print("1. Run: python main.py")
            print("2. Set up OpenAI API key for job search (optional)")
            print("3. Install Ollama for AI resume tailoring (optional)")
        else:
            print("⚠️  Some issues found. Please review and fix them.")
        print("="*60)
        
    except FileNotFoundError:
        print(f"❌ Resume file not found: {resume_path}")
        print("\nPlease create your resume.json file in the data/ directory.")
        print("You can use data/resume_template.json as a starting point.")
        sys.exit(1)
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in resume file: {e}")
        print("\nPlease check your JSON syntax and try again.")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

