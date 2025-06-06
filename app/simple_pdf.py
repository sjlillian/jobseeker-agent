import subprocess
import os
import tempfile
from pathlib import Path

def html_to_pdf_browser(html_content, output_path):
    """
    Convert HTML to PDF using browser automation (Chromium/Chrome)
    This is a fallback for when WeasyPrint or pdfkit are not available
    
    Args:
        html_content (str): HTML content as string
        output_path (str): Path where PDF should be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name
        
        # Try different browser commands
        browsers = [
            'chrome --headless --disable-gpu --print-to-pdf={} file:///{}'.format(output_path, temp_html_path.replace('\\', '/')),
            'chromium --headless --disable-gpu --print-to-pdf={} file:///{}'.format(output_path, temp_html_path.replace('\\', '/')),
            'google-chrome --headless --disable-gpu --print-to-pdf={} file:///{}'.format(output_path, temp_html_path.replace('\\', '/')),
        ]
        
        success = False
        for browser_cmd in browsers:
            try:
                subprocess.run(browser_cmd.split(), check=True, capture_output=True)
                success = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        # Clean up temp file
        os.unlink(temp_html_path)
        
        if success:
            print(f"PDF successfully created: {output_path}")
            return True
        else:
            print("No compatible browser found for PDF conversion")
            return False
            
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def test_simple_pdf():
    """
    Test simple PDF conversion with the existing HTML template
    """
    # Read the existing HTML template
    html_template_path = "static/resume_base.html"
    output_pdf_path = "data/output/test_resume_simple.pdf"
    
    try:
        with open(html_template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert to PDF
        success = html_to_pdf_browser(html_content, output_pdf_path)
        
        if success:
            print("Simple PDF conversion test successful!")
            print(f"Test PDF created at: {output_pdf_path}")
        else:
            print("Simple PDF conversion test failed!")
            
    except FileNotFoundError:
        print(f"HTML template not found: {html_template_path}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_simple_pdf()

