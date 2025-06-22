# EMS Copilot Frontend

This directory contains frontend interfaces for testing and interacting with the EMS Copilot API.

## 🚀 Quick Start

### Option 1: Streamlit App (Recommended)
```bash
cd frontend
pip install -r streamlit_requirements.txt
streamlit run streamlit_app.py
```

### Option 2: HTML Interface
```bash
cd frontend
python -m http.server 8080
# Then open http://localhost:8080/test_frontend.html
```

## 📁 Files

- **`streamlit_app.py`** - Modern, interactive Streamlit interface for testing the API
- **`test_frontend.html`** - Simple HTML interface for basic testing
- **`streamlit_requirements.txt`** - Python dependencies for Streamlit app

## 🎯 Features

### Streamlit App
- ✅ REST API testing
- ✅ WebSocket testing  
- ✅ Query history
- ✅ Server status monitoring
- ✅ Example queries
- ✅ Real-time response display
- ✅ Professional UI

### HTML Interface
- ✅ Basic REST API testing
- ✅ WebSocket testing
- ✅ Simple, lightweight

## 🔧 Configuration

Make sure your FastAPI backend is running:
```bash
cd backend
uvicorn src.ems_copilot.infrastructure.api.main:app --reload
```

The frontend will connect to `http://localhost:8000` by default. 