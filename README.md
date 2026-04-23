# BizRadar 🚀

## Overview
BizRadar is a personalized AI-powered business assistant that helps businesses stay informed and make smarter decisions.

Instead of manually tracking government regulations, schemes, and industry updates, BizRadar automates the process and delivers a **daily, tailored briefing** based on your business profile.

---

## 🧠 How It Works
1. You set up your business profile *(industry, business type, location)*  
2. The system fetches:
   - Government regulations  
   - Scheme announcements  
   - Industry news  
3. Data is filtered and personalized using AI  
4. You receive a **daily morning briefing** with only relevant updates  
5. You can ask business questions and get **context-aware answers** based on real-time data  

---

## ✨ Key Features
- Personalized daily business insights  
- Real-time data fetching (no outdated/static info)  
- Context-aware AI responses  
- Government schemes & regulation tracking  
- Industry-specific news filtering  
- Interactive analytics dashboard  

---

## 🛠 Tech Stack

### Core
- **Python**  
  Primary language used to build the entire application  

### AI & Intelligence
- **google-genai (Gemini API)**  
  Powers business insights, personalization, and Q&A  

### Frontend (UI)
- **Streamlit**  
  Interactive web interface built entirely in Python  

### Data Collection
- **requests**  
  Fetches real-time data from online sources  
- **feedparser**  
  Parses RSS feeds from government and news websites  

### Data Processing
- **pandas**  
  Handles data cleaning, filtering, and structuring  

### Visualization
- **plotly**  
  Creates interactive charts and analytics  

### Configuration
- **python-dotenv**  
  Securely manages API keys and environment variables  

---

## 🗂 Data Handling
BizRadar does not use a traditional database.

- Data is fetched in real-time from online sources  
- Processed dynamically using pandas  
- Insights are generated instantly using AI  

This ensures:
- Always up-to-date information  
- No stale stored data  
- Lightweight and fast execution  

---

## 🧩 System Flow
1. Fetch data from RSS feeds and online sources  
2. Parse and structure data using pandas  
3. Filter relevant updates based on business profile  
4. Generate insights using Gemini AI  
5. Display results via Streamlit UI  

---

## ⚙️ Installation

```bash
git clone https://github.com/chetan2390/BizRadar.git
cd BizRadar
pip install -r requirements.txt

- Create a .env file in the root directory and add:
  GEMINI_API_KEY=your_api_key_here

- Run the application using:
  streamlit run app.py


