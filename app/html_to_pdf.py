import os
import pdfkit
from pathlib import Path

def html_to_pdf(html_content, output_path):
    """
    Convert HTML content to PDF using pdfkit (wkhtmltopdf)
    
    Args:
        html_content (str): HTML content as string
        output_path (str): Path where PDF should be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Configure pdfkit options
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        # Create PDF from HTML string
        pdfkit.from_string(html_content, output_path, options=options)
        
        print(f"PDF successfully created: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def test_pdf_conversion():
    """
    Test PDF conversion with the existing HTML template
    """
    # Read the existing HTML template
    html_template_path = "static/resume_base.html"
    output_pdf_path = "data/output/test_resume.pdf"
    
    try:
        with open(html_template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert to PDF
        success = html_to_pdf(html_content, output_pdf_path)
        
        if success:
            print("PDF conversion test successful!")
            print(f"Test output created at: {output_pdf_path}")
        else:
            print("PDF conversion test failed!")
            
    except FileNotFoundError:
        print(f"HTML template not found: {html_template_path}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_pdf_conversion()

