# 🚀 GitHub Setup Guide

## 📋 Pre-Push Checklist

### ✅ **Files SAFE to Push** (Already in Repository)

#### **Code Files**
- ✅ `main.py` - FastAPI application
- ✅ `app/` directory - All Python modules
  - `orchestrator.py`
  - `database.py`
  - `config.py`
  - `agents/` - All agent files
  - `models/` - All model files
- ✅ `test_api.py` - Test scripts
- ✅ `requirements.txt` - Python dependencies
- ✅ `mcp_dataset.csv` - Sample data (1MB - acceptable)

#### **Configuration Templates**
- ✅ `.env.example` - Environment variable template (NO secrets)
- ✅ `.gitignore` - Git ignore rules

#### **Documentation**
- ✅ `README.md`
- ✅ `DOCUMENTATION_INDEX.md`
- ✅ `QUICK_START.md`
- ✅ `PROJECT_STRUCTURE.md`
- ✅ `PROJECT_MANIFEST.md`
- ✅ `SETUP_VERIFICATION.md`
- ✅ `START_HERE.md`
- ✅ `TROUBLESHOOTING.md`
- ✅ `WEEK1_SUMMARY.md`
- ✅ `ACL_PROTOCOL.md`

#### **Utility Scripts**
- ✅ `setup.bat` - Windows setup script
- ✅ `run.bat` - Windows run script

---

### ❌ **Files NEVER to Push** (Blocked by .gitignore)

#### **🔒 CRITICAL - Security & Credentials**
- ❌ `.env` - **Contains actual credentials/secrets**
- ❌ `*.pem`, `*.key`, `*.cert` - Security certificates
- ❌ `secrets/`, `credentials/` - Any credential directories

#### **💾 Database Files**
- ❌ `mcp_database.db` - Your local database
- ❌ `*.sqlite`, `*.sqlite3` - Any SQLite databases

#### **🐍 Python Runtime**
- ❌ `venv/`, `env/`, `.venv/` - Virtual environments (large!)
- ❌ `__pycache__/` - Compiled Python files
- ❌ `*.pyc`, `*.pyo`, `*.pyd` - Bytecode

#### **🛠️ IDE & Editor**
- ❌ `.vscode/`, `.idea/` - IDE configurations
- ❌ `*.swp`, `*.swo` - Vim swap files

#### **📝 Logs & Temporary**
- ❌ `*.log` - Log files
- ❌ `logs/` - Log directories
- ❌ `*.tmp`, `*.bak` - Temporary/backup files

---

## 🔍 Verify Before Push

### **Step 1: Check Git Status**
```bash
git status
```

**What to Look For:**
- Should see code files, docs, `.env.example`
- Should **NOT** see `.env`, `venv/`, `*.db`, `__pycache__/`

### **Step 2: Verify .env is Ignored**
```bash
git check-ignore .env
```
**Expected Output:** `.env` (means it's properly ignored)

### **Step 3: Check What Will Be Pushed**
```bash
git ls-files
```
Review the list - should NOT contain any sensitive files.

---

## 📤 Pushing to GitHub

### **Option 1: First Time Push (New Repository)**

#### **1. Create GitHub Repository**
1. Go to https://github.com
2. Click "New Repository"
3. Name: `mcp-multi-agent-orchestration`
4. Description: "Multi-Agent Orchestration Framework for Master Customer Profile Management"
5. **Keep it Private** (recommended for team projects)
6. **DO NOT** initialize with README (you already have one)
7. Click "Create Repository"

#### **2. Initialize Git (if not done)**
```bash
cd c:\Users\MohammadKhizrHaidar\Downloads\MCP
git init
```

#### **3. Add All Files**
```bash
git add .
```

#### **4. Create First Commit**
```bash
git commit -m "Initial commit: Week 1 MVP - Multi-Agent Orchestration Framework

- Implemented FastAPI backend with orchestration engine
- Created Planner and Executor agents
- Established Agent Communication Protocol (ACL)
- Integrated 477 customer records from CSV
- Added comprehensive documentation
- Fixed async database session management"
```

#### **5. Add Remote Origin**
```bash
git remote add origin https://github.com/YOUR_USERNAME/mcp-multi-agent-orchestration.git
```

Replace `YOUR_USERNAME` with your GitHub username.

#### **6. Push to GitHub**
```bash
git branch -M main
git push -u origin main
```

---

### **Option 2: Already Initialized Git (Update Existing)**

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Update: Fixed database session management in background workflows"

# Push to remote
git push origin main
```

---

## 👥 Team Setup Instructions

### **For Team Members Cloning the Repository**

Create a file called `TEAM_SETUP.md` in your repo with these instructions:

#### **1. Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/mcp-multi-agent-orchestration.git
cd mcp-multi-agent-orchestration
```

#### **2. Create Virtual Environment**
```bash
python -m venv venv
```

#### **3. Activate Virtual Environment**
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### **4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**If SSL issues (corporate networks):**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt
```

#### **5. Configure Environment**
```bash
# Copy the template
copy .env.example .env

# Edit .env with your local settings (use notepad or VS Code)
notepad .env
```

#### **6. Run Application**
```bash
python main.py
```

Visit: http://localhost:8000/docs

---

## 🔐 Security Best Practices

### **1. Never Commit Secrets**
- ❌ API keys
- ❌ Database passwords
- ❌ Private certificates
- ❌ AWS/Cloud credentials

### **2. Use .env.example**
```bash
# .env.example (SAFE - template only)
DATABASE_URL=sqlite+aiosqlite:///./mcp_database.db
DEBUG=True
SECRET_KEY=your-secret-key-here

# .env (DANGEROUS - actual values)
DATABASE_URL=postgresql://real_user:real_password@production.com/db
DEBUG=False
SECRET_KEY=a3k9f2h8d7g6s5d4f3g2h1j0
```

### **3. Rotate Exposed Secrets**
If you accidentally push `.env`:
1. Immediately delete from GitHub
2. Rotate all exposed credentials
3. Force push cleaned history (advanced)

### **4. Use GitHub Secrets**
For CI/CD pipelines, use GitHub Actions secrets instead of committing credentials.

---

## 📊 Repository Structure on GitHub

```
mcp-multi-agent-orchestration/
├── .gitignore                    ✅ Pushed
├── .env.example                  ✅ Pushed (template)
├── .env                          ❌ IGNORED
├── README.md                     ✅ Pushed
├── requirements.txt              ✅ Pushed
├── main.py                       ✅ Pushed
├── app/
│   ├── __init__.py              ✅ Pushed
│   ├── config.py                ✅ Pushed
│   ├── database.py              ✅ Pushed
│   ├── orchestrator.py          ✅ Pushed
│   ├── agents/                  ✅ Pushed (all files)
│   └── models/                  ✅ Pushed (all files)
├── mcp_dataset.csv              ✅ Pushed
├── venv/                        ❌ IGNORED
├── __pycache__/                 ❌ IGNORED
├── mcp_database.db              ❌ IGNORED
└── *.log                        ❌ IGNORED
```

---

## 🚨 Emergency: If You Pushed Secrets

### **Option 1: Delete from History (Nuclear Option)**
```bash
# Remove file from all history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

### **Option 2: Use BFG Repo-Cleaner**
```bash
# Download BFG from https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files .env
git push origin --force --all
```

### **Option 3: Make Repository Private**
If exposed, immediately:
1. Go to GitHub repository → Settings
2. Scroll to "Danger Zone"
3. Click "Change visibility" → "Make private"
4. Rotate all exposed credentials

---

## 📝 Recommended Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### **Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance

### **Examples:**
```bash
git commit -m "feat: Add customer query workflow endpoint"

git commit -m "fix: Resolve database session management in background tasks

- Created isolated session for async workflows
- Prevents IllegalStateChangeError on session cleanup
- Maintains proper session lifecycle in background tasks"

git commit -m "docs: Update API documentation with workflow examples"
```

---

## 🎯 Next Steps After Push

### **1. Protect Main Branch**
GitHub Settings → Branches → Add Rule:
- Require pull request reviews
- Require status checks to pass
- Prevent force pushes

### **2. Add Collaborators**
Settings → Manage Access → Invite Teams or People

### **3. Set Up CI/CD** (Week 2+)
Create `.github/workflows/tests.yml`:
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest test_api.py
```

### **4. Create Development Branch**
```bash
git checkout -b development
git push -u origin development
```

Team works on `development`, merges to `main` when stable.

---

## ✅ Final Checklist

Before you push, verify:

- [ ] `.gitignore` is properly configured
- [ ] `.env` is NOT being tracked (`git status` doesn't show it)
- [ ] `venv/` is NOT being tracked
- [ ] `mcp_database.db` is NOT being tracked
- [ ] `.env.example` exists with template values
- [ ] `README.md` has setup instructions
- [ ] All sensitive data removed from code
- [ ] Requirements.txt is up to date
- [ ] Documentation is current

---

## 🆘 Questions?

**Check if file will be ignored:**
```bash
git check-ignore -v <filename>
```

**See what's tracked:**
```bash
git ls-files
```

**Remove accidentally tracked file:**
```bash
git rm --cached <filename>
git commit -m "chore: Remove accidentally tracked file"
```

---

## 📚 Additional Resources

- [GitHub Docs - Ignoring Files](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files)
- [Git Best Practices](https://www.git-scm.com/book/en/v2)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Last Updated:** 2025-10-22  
**Version:** 1.0.0
