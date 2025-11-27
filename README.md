# ChefByte 🍳 | SnackOps Project

### The Ultimate AI-Powered Culinary Agent for Modern Households

**Built with Google Agentic Development Kit (ADK) & Gemini 2.5 Flash**

> An intelligent, agentic meal planning companion that transforms your fridge contents and receipts into personalized, chef-curated meal plans using advanced multi-modal AI.

[![Made with Google ADK](https://img.shields.io/badge/Made%20with-Google%20ADK-4285F4?style=for-the-badge&logo=google)](https://github.com/google/adk)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.5-8E75B2?style=for-the-badge)](https://deepmind.google/technologies/gemini/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

---

## 🎯 Overview

**ChefByte** is the next evolution of the **SnackOps** project, reimagined as a fully agentic system. It moves beyond simple recipe search to true autonomous decision-making.

Powered by **Google's Agentic Development Kit (ADK)** and **Gemini 2.5 Flash**, ChefByte doesn't just follow scripts—it *thinks*. It analyzes your ingredients, understands your dietary needs, and autonomously selects the best tools to generate culinary masterpieces.

### What's New in v2.0?

🚀 **True Agentic Core** - Gemini autonomously decides which tools to use (Vision, Search, Variations) based on your request.  
🧾 **Receipt Scanning** - Scan grocery receipts to instantly digitize your inventory and track spending.  
🎨 **Modern React UI** - A stunning, responsive interface with glassmorphism design and smooth animations.  
🔄 **Smart History** - Remembers your past generations and keeps your inventory synced.  
⚡ **Performance Optimized** - Generates 3 recipe variations in seconds using parallel tool execution.

---

## Why ChefByte?

### The Problem
Modern households struggle with three daily questions:
1. "What's in my fridge?"
2. "What can I cook with this?"
3. "How do I make it healthy?"

Traditional recipe apps are static databases. They don't know your inventory, your dietary needs, or your cooking style.

### Our Solution
We built ChefByte to be an **active kitchen companion**, not a passive database. By leveraging **Agentic AI**, ChefByte understands context. It sees your ingredients, reads your receipts, and thinks like a chef to create personalized meal plans that reduce food waste and decision fatigue.

### Why You Should Use It
- **Reduce Food Waste**: Instantly find recipes for ingredients about to expire.
- **Save Money**: Digitizing receipts helps you track inventory and avoid overbuying.
- **Eat Healthier**: Automatic macro tracking ensures you meet your nutrition goals.
- **Save Time**: Stop scrolling through recipe blogs. Get 3 perfect options in seconds.

---

## Compatibility

![macOS](https://img.shields.io/badge/macOS-Supported-000000?style=for-the-badge&logo=apple&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-Supported-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Supported-FCC624?style=for-the-badge&logo=linux&logoColor=black)

ChefByte is designed to run locally on your machine for maximum privacy and performance.

| OS | Status | Notes |
| :--- | :--- | :--- |
| **macOS** | ✅ Verified | Native support (Apple Silicon & Intel) |
| **Windows** | ✅ Verified | Supports WSL2 and PowerShell |
| **Linux** | ✅ Verified | Ubuntu, Debian, Fedora, Arch |

**Requirements:**
- **RAM**: 4GB minimum (8GB recommended)
- **Python**: 3.12 or higher
- **Node.js**: v18 or higher
- **Internet**: Required for Gemini API access

---

## 📸 Interface Showcase

<div align="center">
  <img src="Chefbyte-ui/readme-pics/dashboard.png" alt="ChefByte Dashboard" width="100%" style="border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />
</div>

<div align="center" style="display: flex; gap: 20px; justify-content: center;">
  <img src="Chefbyte-ui/readme-pics/recipe-card.png" alt="Recipe Card" width="48%" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />
  <img src="Chefbyte-ui/readme-pics/recipt-card.png" alt="Receipt Scanner" width="48%" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />
</div>

<br/>

---

## Key Features

### 1. Agentic Intelligence
ChefByte isn't a chatbot. It's an agent.
- **Autonomous Tool Selection**: It decides when to use vision, when to search, and when to generate variations.
- **Strategic Reasoning**: It explains *why* it chose specific recipes based on your ingredients.
- **Fallback Mechanisms**: Robust error handling ensures you always get a result.

### 2. Multi-Modal Vision
- **Fridge Scanner**: Identify ingredients from a messy fridge photo.
- **Receipt Digitizer**: Extract items, prices, and store details from grocery receipts.
- **Auto-Detection**: The system automatically figures out if you uploaded a fridge photo or a receipt.

### 3. Smart Recipe Generation
Get 3 distinct variations for every request:
- **Standard**: A classic, well-balanced meal.
- **Creative Twist**: A fusion or innovative take on the ingredients.
- **Quick & Easy**: A simplified version for busy days.

### 4. Nutrition & Health
- **Macro Tracking**: Calories, Protein, Carbs, and Fats calculated for every recipe.
- **Dietary Filters**: Vegetarian, Vegan, Keto, Paleo, and more.
- **Portion Scaling**: Adjust servings and watch ingredient quantities update instantly.

### 5. Persistent Memory
- **Inventory Tracking**: Remembers what's in your kitchen.
- **Recipe History**: Access your past generations anytime.
- **User Preferences**: Remembers your diet and calorie goals.

---

## 🏗️ Architecture

ChefByte uses a decoupled architecture with a FastAPI backend and a React frontend.

### The Agentic Stack

```mermaid
graph TD
    User[User Interaction] --> UI[React Frontend]
    UI --> API[FastAPI Backend]
    API --> Agent[ChefByte ADK Agent]
    
    subgraph "Agent Brain (Gemini 2.5 Flash)"
        Agent --> Decision{Autonomous Decision}
        Decision -->|Need Ingredients?| Vision[Vision Tool]
        Decision -->|Need Recipes?| Variations[Recipe Variations Tool]
        Decision -->|Need Search?| Search[Search Tool]
    end
    
    Vision -->|Fridge/Receipt Data| Memory[Persistent Memory]
    Variations -->|Generated Recipes| UI
    Search -->|Database Matches| UI
```

### Core Components

- **ChefByteADKAgent**: The orchestrator that manages the conversation and tool execution.
- **Vision Tool**: Unified tool for processing both fridge photos and receipts.
- **Recipe Variations Tool**: Generates 3 distinct recipe types in a single optimized call.
- **Persistent Memory**: JSON-based storage for user context and history.

---

## 📂 Project Structure

The project is organized into two main components: a **FastAPI Backend** and a **React Frontend**.

```plaintext
SnackOps/
├── ChefByte/                 # 🐍 Backend (FastAPI + Agentic Core)
│   ├── adk_agent/            #    - Agent Logic & Tools
│   │   ├── tools/            #      - Vision, Search, Variations
│   │   └── chefbyte_agent.py #      - Main Agent Orchestrator
│   ├── data/                 #    - Recipe Databases & Memory
│   ├── api.py                #    - FastAPI Endpoints
│   └── start_backend.sh      #    - Startup Script
│
├── Chefbyte-ui/              # ⚛️ Frontend (React + Vite)
│   ├── src/
│   │   ├── components/       #    - Reusable UI Components
│   │   ├── services/         #    - API Integration
│   │   └── App.tsx           #    - Main Application
│   └── start_frontend.sh     #    - Startup Script
│
└── README.md                 # 📄 Documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google API Key (Gemini)

### 1. Clone & Setup
```bash
git clone https://github.com/DevxD98/SnackOps.git
cd SnackOps
```

### 2. Backend Setup
```bash
cd ChefByte
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### 3. Frontend Setup
```bash
cd ../Chefbyte-ui
npm install
```

### 4. Run the System
You can run both servers easily:

**Terminal 1 (Backend):**
```bash
cd ChefByte
./start_backend.sh
```

**Terminal 2 (Frontend):**
```bash
cd Chefbyte-ui
./start_frontend.sh
```

Open **http://localhost:3000** and start cooking! 👨‍🍳

---

## 🔧 Technologies

### Backend
- **Google ADK**: Agent framework
- **Gemini 2.5 Flash**: LLM & Vision
- **FastAPI**: High-performance API
- **Uvicorn**: ASGI Server

### Frontend
- **React 18**: UI Library
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Lucide React**: Icons
- **Framer Motion**: Animations

---

## Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/DevxD98">
        <img src="https://images.weserv.nl/?url=github.com/DevxD98.png&h=100&w=100&fit=cover&mask=circle&maxage=7d" width="100px;" alt="DevxD98"/>
        <br />
        <sub><b>DevxD98</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/itzAditya0">
        <img src="https://images.weserv.nl/?url=github.com/itzAditya0.png&h=100&w=100&fit=cover&mask=circle&maxage=7d" width="100px;" alt="itzAditya0"/>
        <br />
        <sub><b>itzAditya0</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/ojasvi0407">
        <img src="https://images.weserv.nl/?url=github.com/ojasvi0407.png&h=100&w=100&fit=cover&mask=circle&maxage=7d" width="100px;" alt="ojasvi0407"/>
        <br />
        <sub><b>ojasvi0407</b></sub>
      </a>
    </td>
  </tr>
</table>

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

<div align="center">
  <h3>Made for Modern Kitchens</h3>
  <p>ChefByte - Your AI Sous Chef</p>
</div>
