# Job Seeker Agent - Setup Guide 🚀

This guide will help you get the Job Seeker Agent up and running quickly.

## Prerequisites ✅

- Python 3.11 or higher
- Git (optional)
- Text editor

## Step 1: Install Dependencies 📦

```bash
pip install -r requirements.txt
```

## Step 2: Configure Your Resume 📝

### Option A: Use the Template
1. Copy `data/resume_template.json` to `data/resume.json`
2. Edit `data/resume.json` with your information

### Option B: Customize the Existing Example
1. Edit `data/resume.json` directly (it contains a complete example)
2. Replace Alex Jordan's information with your own

### Required Fields:
- **name**: Your full name
- **title**: Your professional title
- **contact**: Email, phone, LinkedIn, etc.
- **summary**: 2-3 sentence professional summary
- **skills**: List of your technical and soft skills
- **experience**: Work history with achievements
- **education**: Educational background

### Optional Fields:
- **projects**: Personal/professional projects
- **certifications**: Professional certifications
- **awards**: Achievements and recognition

## Step 3: Validate Your Resume ✅

Run the validation script to ensure everything is correct:

```bash
python validate_resume.py
```

You should see: `🎉 YOUR RESUME IS READY FOR THE JOB SEEKER AGENT!`

## Step 4: Test Basic Functionality 🧪

```bash
python main.py
```

Choose option 3 to skip job search and test resume generation.

## Step 5: Set Up Optional Features (Recommended) ⭐

### OpenAI API (for job search)
1. Get API key from https://platform.openai.com/api-keys
2. Set environment variable:
   ```powershell
   $env:OPENAI_API_KEY='your-api-key-here'
   ```

### Ollama (for AI resume tailoring)
1. Install from https://ollama.ai
2. Start the service:
   ```bash
   ollama serve
   ```
3. Install a model:
   ```bash
   ollama pull llama2
   ```

### PDF Generation (for professional output)

**Option A: wkhtmltopdf (Recommended)**
1. Download from https://wkhtmltopdf.org/downloads.html
2. Install and add to PATH

**Option B: Use Chrome/Edge**
- Ensure Chrome or Edge browser is installed
- The app will detect and use it automatically

## Step 6: Run the Complete Application 🎯

```bash
python main.py
```

Now you can:
1. Search for relevant jobs using AI
2. Select jobs you're interested in
3. Generate tailored resumes for each job
4. Export to PDF format

## Quick Test Commands 🔧

```bash
# Validate your resume
python validate_resume.py

# Test resume rendering
python app/resume_loader.py

# Test OpenAI connection (needs API key)
python app/gpt_interface.py

# Test Ollama connection (needs Ollama running)
python app/resume_formatter.py

# Run the full application
python main.py
```

## File Structure 📁

```
jobseeker-agent/
├── data/
│   ├── resume.json          # ← Your resume data (edit this!)
│   ├── resume_template.json # Template for reference
│   └── output/              # Generated resumes appear here
├── static/
│   └── resume_template.html # HTML template (customizable)
├── app/                     # Application modules
├── main.py                  # Main application
├── validate_resume.py       # Resume validator
└── config.yaml             # Configuration (optional)
```

## Troubleshooting 🔧

### Resume not loading?
- Check `data/resume.json` exists and has valid JSON
- Run `python validate_resume.py` to check for issues

### OpenAI errors?
- Verify API key is set correctly
- Check you have sufficient API credits
- Try `gpt-3.5-turbo` model instead of `gpt-4`

### Ollama not connecting?
- Ensure Ollama is running: `ollama serve`
- Check the model is installed: `ollama list`
- Verify URL in config: `http://localhost:11434`

### PDF generation failing?
- Install wkhtmltopdf for best results
- Ensure Chrome or Edge is available
- HTML resumes will still be generated

## What Each Component Does 🧩

| Component | Purpose | Status |
|-----------|---------|--------|
| **Resume Loader** | Renders your resume data into beautiful HTML | ✅ Ready |
| **OpenAI Interface** | Finds relevant job opportunities | ⚠️ Needs API key |
| **Ollama Formatter** | Tailors resumes for specific jobs | ⚠️ Needs Ollama |
| **PDF Generator** | Converts HTML to professional PDFs | ⚠️ Needs external tool |
| **Main Application** | Orchestrates the entire workflow | ✅ Ready |

## Success Indicators 🎯

You'll know everything is working when:

1. ✅ `python validate_resume.py` shows all green checkmarks
2. ✅ `python main.py` loads your resume successfully
3. ✅ HTML resumes are generated in `data/output/`
4. ✅ (Optional) Job search returns relevant positions
5. ✅ (Optional) Tailored resumes are created for specific jobs
6. ✅ (Optional) PDF files are generated successfully

## Support 💬

If you encounter issues:
1. Run `python validate_resume.py` first
2. Check the troubleshooting section above
3. Verify all dependencies are installed
4. Check that external services (OpenAI, Ollama) are configured

**Happy job hunting! 🎯**

