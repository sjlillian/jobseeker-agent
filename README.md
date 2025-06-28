# Job Seeker Agent 🚀

An intelligent job search and resume tailoring application that uses AI to help you find relevant job opportunities and create customized resumes for each position.

## Features ✨

- 🔍 **AI-Powered Job Search**: Uses OpenAI GPT to find relevant job opportunities based on your resume
- 📝 **Resume Tailoring**: Uses local Ollama to customize your resume for specific job postings
- 📄 **PDF Generation**: Converts tailored resumes to professional PDF format
- 🎨 **Beautiful Templates**: Clean, professional HTML/CSS resume templates
- 🔧 **Configurable**: Easy configuration through YAML files
- 💻 **Interactive CLI**: User-friendly command-line interface

## Quick Start 🚀

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Your Resume
```bash
# Edit with your information (comprehensive example included)
notepad data/resume.json

# Validate your resume
python validate_resume.py
```

### 3. Test the Application
```bash
python main.py
```

📄 **For detailed setup instructions, see [SETUP.md](SETUP.md)**

## Usage 🎯

### Interactive Mode
```bash
python main.py
```

The application will guide you through finding jobs and creating tailored resumes.

### Component Testing

```bash
# Test resume rendering
python app/resume_loader.py

# Test Ollama connection
python app/resume_formatter.py

# Test OpenAI integration
python app/gpt_interface.py
```

## Components Status 📊

| Component | Status | Notes |
|-----------|--------|---------|
| 📝 Resume Loading | ✅ Working | Loads from JSON, renders HTML |
| 🔍 Job Search | ⚠️ In the works | Requires API key |
| 🤖 Resume Tailoring (Ollama) | ✅ Ready | Requires Ollama setup |
| 📄 HTML Generation | ✅ Working | Beautiful Jinja2 templates |
| 🗂️ PDF Conversion | ⚠️ Depends | Requires external tools |

## Next Steps 🎯

1. **Fill out your resume**: Edit `data/resume.json`
2. **Get OpenAI API key**: For job searching functionality
3. **Install Ollama**: For AI-powered resume tailoring
4. **Setup PDF conversion**: Install wkhtmltopdf or ensure browser availability

**Happy job hunting! 🎯**
