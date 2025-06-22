import streamlit as st
import requests
import json
import websocket
import threading
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

# Page configuration
st.set_page_config(
    page_title="EMS Copilot Test Interface",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .response-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .error-box {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
    .stButton > button {
        width: 100%;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🚑 EMS Copilot Test Interface</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Configuration
    api_url = st.text_input(
        "API Base URL",
        value="http://localhost:8000",
        help="Base URL for your FastAPI server"
    )
    
    # Example queries
    st.header("💡 Example Queries")
    example_queries = {
        "Vitals": "Record heart rate 85 for patient John Smith",
        "GPS": "Get directions to nearest hospital",
        "Weather": "What's the weather like in New York?",
        "Database": "Show me all patients in the emergency room",
        "Triage": "Patient has chest pain and shortness of breath"
    }
    
    selected_example = st.selectbox("Choose an example:", list(example_queries.keys()))
    if st.button("Use Example"):
        st.session_state.query_text = example_queries[selected_example]

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📡 REST API Test")
    
    # Query input
    query = st.text_area(
        "Enter your query:",
        value=st.session_state.get('query_text', ''),
        height=100,
        placeholder="e.g., 'Record heart rate 85 for patient John Smith'"
    )
    
    # Send button
    if st.button("🚀 Send Query (REST API)", type="primary"):
        if query.strip():
            with st.spinner("Sending request..."):
                try:
                    response = requests.post(
                        f"{api_url}/query",
                        json={"query": query},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.markdown('<div class="response-box success-box">', unsafe_allow_html=True)
                        st.json(data)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Store successful query
                        if 'query_history' not in st.session_state:
                            st.session_state.query_history = []
                        st.session_state.query_history.append({
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'query': query,
                            'response': data,
                            'type': 'REST'
                        })
                    else:
                        st.markdown('<div class="response-box error-box">', unsafe_allow_html=True)
                        st.error(f"Error {response.status_code}: {response.text}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                except requests.exceptions.ConnectionError:
                    st.markdown('<div class="response-box error-box">', unsafe_allow_html=True)
                    st.error("❌ Connection failed. Make sure your FastAPI server is running on the specified URL.")
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown('<div class="response-box error-box">', unsafe_allow_html=True)
                    st.error(f"❌ Error: {str(e)}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a query.")

with col2:
    st.header("🔌 WebSocket Test")
    
    # WebSocket status
    if 'ws_connected' not in st.session_state:
        st.session_state.ws_connected = False
    
    # Connection controls
    ws_col1, ws_col2 = st.columns(2)
    
    with ws_col1:
        if not st.session_state.ws_connected:
            if st.button("🔗 Connect WebSocket"):
                try:
                    # Initialize WebSocket connection
                    ws_url = api_url.replace('http', 'ws') + '/ws/chat'
                    st.session_state.ws = websocket.WebSocketApp(
                        ws_url,
                        on_open=lambda ws: st.session_state.update({'ws_connected': True}),
                        on_message=lambda ws, msg: st.session_state.update({'ws_message': msg}),
                        on_error=lambda ws, msg: st.error(f"WebSocket error: {msg}"),
                        on_close=lambda ws, close_status_code, close_msg: st.session_state.update({'ws_connected': False})
                    )
                    
                    # Start WebSocket in a separate thread
                    ws_thread = threading.Thread(target=st.session_state.ws.run_forever)
                    ws_thread.daemon = True
                    ws_thread.start()
                    
                    st.success("✅ WebSocket connected!")
                    st.session_state.ws_connected = True
                    
                except Exception as e:
                    st.error(f"❌ Failed to connect: {str(e)}")
    
    with ws_col2:
        if st.session_state.ws_connected:
            if st.button("🔌 Disconnect"):
                if 'ws' in st.session_state:
                    st.session_state.ws.close()
                st.session_state.ws_connected = False
                st.rerun()
    
    # WebSocket status indicator
    if st.session_state.ws_connected:
        st.success("🟢 WebSocket Connected")
    else:
        st.error("🔴 WebSocket Disconnected")
    
    # WebSocket query input
    ws_query = st.text_area(
        "WebSocket Query:",
        height=100,
        placeholder="Enter query for WebSocket test..."
    )
    
    if st.button("📤 Send via WebSocket", disabled=not st.session_state.ws_connected):
        if ws_query.strip() and st.session_state.ws_connected:
            try:
                message = {"message": ws_query}
                st.session_state.ws.send(json.dumps(message))
                st.success("✅ Message sent via WebSocket!")
                
                # Wait for response
                with st.spinner("Waiting for response..."):
                    time.sleep(1)
                    if 'ws_message' in st.session_state:
                        data = json.loads(st.session_state.ws_message)
                        st.markdown('<div class="response-box success-box">', unsafe_allow_html=True)
                        st.json(data)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Store in history
                        if 'query_history' not in st.session_state:
                            st.session_state.query_history = []
                        st.session_state.query_history.append({
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'query': ws_query,
                            'response': data,
                            'type': 'WebSocket'
                        })
                        
                        # Clear the message
                        del st.session_state.ws_message
            except Exception as e:
                st.error(f"❌ Error sending message: {str(e)}")
        elif not st.session_state.ws_connected:
            st.warning("Please connect WebSocket first.")
        else:
            st.warning("Please enter a query.")

# Query History
st.header("📋 Query History")
if 'query_history' in st.session_state and st.session_state.query_history:
    for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):  # Show last 10
        with st.expander(f"{entry['timestamp']} - {entry['type']} - {entry['query'][:50]}..."):
            st.write(f"**Query:** {entry['query']}")
            st.write(f"**Type:** {entry['type']}")
            st.json(entry['response'])
else:
    st.info("No queries yet. Start testing to see your history here!")

# Server Status Check
st.header("🔍 Server Status")
if st.button("Check Server Status"):
    try:
        response = requests.get(f"{api_url}/docs", timeout=5)
        if response.status_code == 200:
            st.success("✅ Server is running!")
            st.info(f"📖 API Documentation: {api_url}/docs")
        else:
            st.warning(f"⚠️ Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server. Make sure it's running!")
    except Exception as e:
        st.error(f"❌ Error checking server: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🚑 EMS Copilot Test Interface | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
) 