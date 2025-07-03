import json
import os
from jinja2 import Template
from typing import Dict, Any

class ResumeRenderer:
    def __init__(self, template_path: str = "static/resume_template.html"):
        """
        Initialize the resume renderer
        
        Args:
            template_path (str): Path to HTML template file
        """
        self.template_path = template_path
    
    def load_resume_data(self, resume_path: str = "data/resume.json") -> Dict[str, Any]:
        """
        Load resume data from JSON file
        
        Args:
            resume_path (str): Path to resume JSON file
            
        Returns:
            Dict[str, Any]: Resume data
        """
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Resume file not found: {resume_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing resume JSON: {e}")
            return {}
    
    def render_resume_html(self, resume_data: Dict[str, Any]) -> str:
        """
        Render resume data into HTML using the template
        
        Args:
            resume_data (dict): Resume data
            
        Returns:
            str: Rendered HTML content
        """
        try:
            # Read the HTML template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Create Jinja2 template
            template = Template(template_content)
            
            # Render with resume data
            rendered_html = template.render(**resume_data)
            
            return rendered_html
            
        except FileNotFoundError:
            print(f"Template file not found: {self.template_path}")
            return ""
        except Exception as e:
            print(f"Error rendering template: {e}")
            return ""
    
    def save_rendered_html(self, html_content: str, output_path: str) -> bool:
        """
        Save rendered HTML to file
        
        Args:
            html_content (str): Rendered HTML content
            output_path (str): Path to save the HTML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving HTML: {e}")
            return False
    
    def render_and_save(self, resume_data: Dict[str, Any], output_path: str) -> bool:
        """
        Render resume and save to HTML file
        
        Args:
            resume_data (dict): Resume data
            output_path (str): Path to save the HTML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        html_content = self.render_resume_html(resume_data)
        if html_content:
            return self.save_rendered_html(html_content, output_path)
        return False

def test_resume_renderer():
    """
    Test the resume renderer
    """
    renderer = ResumeRenderer()
    
    # Load resume data
    resume_data = renderer.load_resume_data()
    
    if not resume_data:
        print("Using sample data for testing")
        resume_data = {
            "name": "John Doe",
            "title": "Software Developer",
            "summary": "Experienced software developer with expertise in Python and web development.",
            "skills": ["Python", "JavaScript", "React", "Django", "SQL", "AWS"],
            "contact": {
                "location": "123 Main St, City, State",
                "phone": "(555) 123-4567",
                "email": "john.doe@email.com",
                "linkedin": "linkedin.com/in/johndoe",
                "github": "github.com/johndoe",
                "website": "johndoe.com"
            },
            "experience": [
                {
                    "title": "Software Developer",
                    "company": "Tech Solutions Inc.",
                    "location": "San Francisco, CA",
                    "start_date": "January 2021",
                    "end_date": "Present",
                    "description": [
                        "Developed and maintained web applications using Python and Django",
                        "Collaborated with cross-functional teams to deliver high-quality software",
                        "Implemented RESTful APIs and integrated third-party services"
                    ]
                }
            ],
            "education": [
                {
                    "school": "University of Technology",
                    "degree": "Bachelor of Science in Computer Science",
                    "year": "2020"
                }
            ],
            "certifications": ["AWS Certified Developer"],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built a full-stack e-commerce platform using Django and React",
                    "technologies": ["Django", "React", "PostgreSQL"]
                }
            ],
            "awards": ["Employee of the Month - March 2023"]
        }
    
    print("Testing resume rendering...")
    
    # Test rendering
    html_content = renderer.render_resume_html(resume_data)
    
    if html_content:
        print("✓ Resume rendered successfully")
        
        # Save to file
        output_path = "data/output/rendered_resume.html"
        success = renderer.save_rendered_html(html_content, output_path)
        
        if success:
            print(f"✓ HTML saved to: {output_path}")
        else:
            print("✗ Failed to save HTML")
    else:
        print("✗ Failed to render resume")

if __name__ == "__main__":
    test_resume_renderer()

