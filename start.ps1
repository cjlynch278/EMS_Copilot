# EMS Copilot Startup Script
# Starts both backend API server and Streamlit frontend

Write-Host "🚀 Starting EMS Copilot (Backend + Frontend)..." -ForegroundColor Cyan
Write-Host "Backend will be at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will be at: http://localhost:8501" -ForegroundColor Cyan

# Start backend server in new window
Start-Process powershell -ArgumentList "-Command", "python run_server.py" -WindowStyle Normal

# Start Streamlit app in new window
Start-Process powershell -ArgumentList "-Command", "cd frontend; streamlit run streamlit_app.py" -WindowStyle Normal

Write-Host "✅ Both services started in separate windows!" -ForegroundColor Green 