# 🏛️ Council Agent

A sophisticated multi-agent decision-support system powered by **Google Gemini**. Get strategic, multifaceted perspectives on your most critical goals through a structured two-round deliberation process.

![Premium UI](https://img.shields.io/badge/UI-Glassmorphism-blueviolet)
![Engine](https://img.shields.io/badge/Engine-Gemini%202.5%20Flash-blue)

## ✨ Features

- **Multi-Agent Council**: Consult with a specialized panel. By default, it includes:
  - **The Realist**: Focuses on feasibility, logistics, and practical timelines.
  - **The Critic**: Challenges assumptions, identifies hidden risks, and plays devil's advocate.
  - **The Coach**: Protects your mental load, sustainability, and long-term wellbeing.
- **Dynamic Roles**: Customize your council! Define your own agents on the fly (e.g., "Skeptical Investor", "Stoic Philosopher").
- **Two-Round Deliberation**:
  - **Round 1**: Initial independent analysis from each agent.
  - **Round 2**: Cross-critique where agents review and refine each other's advice.
- **Final Moderation**: A central moderator synthesizes all perspectives into a 7-day action plan.
- **Premium Web Interface**: Responsive, modern Glassmorphism-styled UI for seamless interaction.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/du0ks/council-agent.git
cd council-agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set API Key
Export your Gemini API key to your environment:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Run the Application
Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
Once running, open your browser and navigate to:
**[http://localhost:8000](http://localhost:8000)**

## 🛠️ Technology Stack
- **Backend**: FastAPI (Python)
- **AI Engine**: Google Gemini API (`gemini-2.5-flash`)
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript
- **Markdown**: Marked.js for real-time rendering

## 📝 Usage Tips
- **Be Specific**: Provide as much context as possible in the context box for better results.
- **Customize Agents**: Don't stick to the defaults! Try adding a "Financial Optimizer" or a "Legal Auditor" for specialized goals.

---
*Created with ❤️ by du0ks*