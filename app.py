import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import numpy as np
import time

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="AI Business Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== INITIALIZE ALL SESSION STATE ====================
def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'
    
    if 'client_name' not in st.session_state:
        st.session_state.client_name = ''
    
    if 'business_name' not in st.session_state:
        st.session_state.business_name = ''
    
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    
    if 'settings_loaded' not in st.session_state:
        st.session_state.settings_loaded = False
    
    if 'data_initialized' not in st.session_state:
        st.session_state.data_initialized = False

init_session_state()

# ==================== DEFAULT DATA FUNCTIONS ====================
def get_default_sales():
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    items = ['Coffee', 'Sandwich', 'Cake', 'Tea', 'Pasta']
    data = []
    np.random.seed(42)
    for date in dates:
        for item in items:
            base = {'Coffee': 50, 'Sandwich': 30, 'Cake': 20, 'Tea': 40, 'Pasta': 25}[item]
            qty = int(base + np.random.randint(-10, 15))
            price = {'Coffee': 150, 'Sandwich': 200, 'Cake': 180, 'Tea': 100, 'Pasta': 250}[item]
            data.append({'Date': date, 'Item': item, 'Quantity': max(1, qty), 'Revenue': max(1, qty) * price})
    return pd.DataFrame(data)

def get_default_inventory():
    return pd.DataFrame({
        'Item': ['Coffee Beans', 'Bread', 'Flour', 'Milk', 'Pasta', 'Vegetables', 'Cheese', 'Sugar'],
        'Current_Stock': [50, 100, 80, 60, 40, 70, 30, 90],
        'Min_Stock': [20, 40, 30, 25, 15, 30, 10, 40],
        'Max_Stock': [100, 200, 150, 120, 80, 150, 60, 180],
        'Unit_Cost': [500, 50, 40, 60, 80, 30, 150, 50],
        'Reorder_Point': [30, 60, 45, 35, 20, 45, 15, 60]
    })

def get_default_bookings():
    dates = pd.date_range(start=datetime.now(), periods=10, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Name': [f'Customer {i}' for i in range(1, 11)],
        'Phone': [f'98765432{i:02d}' for i in range(10)],
        'Guests': [2, 4, 3, 6, 2, 4, 5, 3, 2, 4],
        'Time': ['12:00', '13:00', '19:00', '20:00', '12:00', '13:00', '19:00', '20:00', '12:00', '13:00'],
        'Status': ['Confirmed'] * 10
    })

def get_default_chat():
    return []

# ==================== DATA MANAGEMENT ====================
def get_data_folder():
    if st.session_state.business_name:
        business = st.session_state.business_name.replace(' ', '_').lower()
        return f"data_{business}"
    return "data_default"

def ensure_folder():
    folder = get_data_folder()
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            pass
    return folder

def save_data(filename, data):
    try:
        folder = ensure_folder()
        filepath = os.path.join(folder, filename)
        if isinstance(data, pd.DataFrame):
            data_copy = data.copy()
            for col in data_copy.columns:
                if pd.api.types.is_datetime64_any_dtype(data_copy[col]):
                    data_copy[col] = data_copy[col].astype(str)
            data_copy.to_json(filepath, orient='records', indent=2)
        else:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        return False

def load_data(filename, default_func):
    try:
        folder = ensure_folder()
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                    return df
                elif isinstance(data, list):
                    return data
        return default_func()
    except:
        return default_func()

def save_settings():
    try:
        settings = {
            'client_name': st.session_state.client_name,
            'business_name': st.session_state.business_name,
            'theme': st.session_state.theme,
            'setup_complete': st.session_state.setup_complete
        }
        if not os.path.exists('settings'):
            os.makedirs('settings')
        with open('settings/config.json', 'w') as f:
            json.dump(settings, f)
    except:
        pass

def load_settings():
    try:
        if os.path.exists('settings/config.json'):
            with open('settings/config.json', 'r') as f:
                settings = json.load(f)
                st.session_state.client_name = settings.get('client_name', '')
                st.session_state.business_name = settings.get('business_name', '')
                st.session_state.theme = settings.get('theme', 'dark')
                st.session_state.setup_complete = settings.get('setup_complete', False)
                if st.session_state.setup_complete and st.session_state.business_name:
                    st.session_state.page = 'dashboard'
    except:
        pass

def initialize_data():
    """Initialize all data in session state"""
    if 'sales_data' not in st.session_state:
        st.session_state.sales_data = load_data('sales.json', get_default_sales)
    
    if 'inventory' not in st.session_state:
        st.session_state.inventory = load_data('inventory.json', get_default_inventory)
    
    if 'bookings' not in st.session_state:
        st.session_state.bookings = load_data('bookings.json', get_default_bookings)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = load_data('chat.json', get_default_chat)
        if st.session_state.chat_history is None:
            st.session_state.chat_history = []
    
    st.session_state.data_initialized = True

def auto_save_all():
    try:
        if 'sales_data' in st.session_state and st.session_state.sales_data is not None:
            save_data('sales.json', st.session_state.sales_data)
        if 'inventory' in st.session_state and st.session_state.inventory is not None:
            save_data('inventory.json', st.session_state.inventory)
        if 'bookings' in st.session_state and st.session_state.bookings is not None:
            save_data('bookings.json', st.session_state.bookings)
        if 'chat_history' in st.session_state and st.session_state.chat_history is not None:
            save_data('chat.json', st.session_state.chat_history)
        save_settings()
    except:
        pass

# Load settings on first run
if not st.session_state.settings_loaded:
    load_settings()
    st.session_state.settings_loaded = True

# Initialize data if on dashboard
if st.session_state.setup_complete or st.session_state.page == 'dashboard':
    initialize_data()

# ==================== THEME SETTINGS ====================
def get_theme_colors():
    if st.session_state.theme == 'dark':
        return {
            'bg': '#0a0a0f',
            'bg2': '#12121a',
            'card': '#1a1a2e',
            'card_hover': '#252540',
            'text': '#ffffff',
            'text_bright': '#ffffff',
            'text_dim': '#a0a0b0',
            'accent1': '#ff6b6b',
            'accent2': '#4ecdc4',
            'gradient1': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'shadow': '0 10px 40px rgba(0,0,0,0.5)',
            'glow': '0 0 30px rgba(78, 205, 196, 0.3)'
        }
    else:
        return {
            'bg': '#f8f9fa',
            'bg2': '#ffffff',
            'card': '#ffffff',
            'card_hover': '#f0f0f5',
            'text': '#1a1a2e',
            'text_bright': '#000000',
            'text_dim': '#6c757d',
            'accent1': '#e63946',
            'accent2': '#2a9d8f',
            'gradient1': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'shadow': '0 10px 40px rgba(0,0,0,0.1)',
            'glow': '0 0 30px rgba(42, 157, 143, 0.2)'
        }

colors = get_theme_colors()

# ==================== CSS ====================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {{ font-family: 'Poppins', sans-serif; }}
    
    .stApp {{ background: {colors['bg']}; color: {colors['text']}; }}
    
    #MainMenu, footer, header {{visibility: hidden;}}
    
    .welcome-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
        animation: fadeIn 1s ease-out;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    .welcome-icon {{
        font-size: 4rem;
        animation: pulse 2s ease-in-out infinite;
        margin-bottom: 1rem;
    }}
    
    .welcome-title {{
        font-size: 3rem;
        font-weight: 800;
        background: {colors['gradient1']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}
    
    .welcome-subtitle {{
        font-size: 1.2rem;
        color: {colors['text_dim']};
        margin-bottom: 2rem;
    }}
    
    .input-container {{
        background: {colors['card']};
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: {colors['shadow']};
        max-width: 450px;
        width: 100%;
        border: 1px solid {colors['card_hover']};
    }}
    
    .input-label {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {colors['text_bright']};
        margin-bottom: 0.5rem;
    }}
    
    .step-indicator {{
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    
    .step {{
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }}
    
    .step-active {{
        background: {colors['gradient1']};
        color: white;
    }}
    
    .step-inactive {{
        background: {colors['card_hover']};
        color: {colors['text_dim']};
    }}
    
    .step-complete {{
        background: {colors['accent2']};
        color: white;
    }}
    
    .main-header {{
        text-align: center;
        padding: 1.5rem 0;
    }}
    
    .business-name {{
        font-size: 2.5rem;
        font-weight: 800;
        background: {colors['gradient1']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .greeting {{
        font-size: 1.1rem;
        color: {colors['text_dim']};
    }}
    
    .datetime-display {{
        position: fixed;
        top: 15px;
        right: 20px;
        font-size: 0.7rem;
        color: {colors['text_bright']};
        background: {colors['card']};
        padding: 8px 12px;
        border-radius: 8px;
        z-index: 999;
        box-shadow: {colors['shadow']};
        text-align: right;
    }}
    
    .metric-card {{
        background: {colors['card']};
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid {colors['card_hover']};
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {colors['text_bright']};
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        color: {colors['text_dim']};
    }}
    
    .section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {colors['text_bright']};
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {colors['accent2']};
    }}
    
    .chat-user {{
        background: {colors['gradient1']};
        color: white;
        padding: 10px 15px;
        border-radius: 12px 12px 4px 12px;
        margin: 8px 0;
        margin-left: 25%;
    }}
    
    .chat-bot {{
        background: {colors['card_hover']};
        color: {colors['text_bright']};
        padding: 10px 15px;
        border-radius: 12px 12px 12px 4px;
        margin: 8px 0;
        margin-right: 25%;
        border-left: 3px solid {colors['accent2']};
    }}
    
    .alert-high {{
        background: rgba(255, 107, 107, 0.1);
        border-left: 4px solid #ff6b6b;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }}
    
    .alert-medium {{
        background: rgba(255, 230, 109, 0.1);
        border-left: 4px solid #ffe66d;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }}
    
    .stTextInput input {{
        background: {colors['bg2']} !important;
        color: {colors['text_bright']} !important;
        border: 2px solid {colors['card_hover']} !important;
        border-radius: 8px !important;
    }}
    
    .stTextInput input:focus {{
        border-color: {colors['accent2']} !important;
    }}
    
    .stButton > button {{
        background: {colors['gradient1']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 5px;
        background: {colors['bg2']};
        padding: 8px;
        border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {colors['card']};
        border-radius: 8px;
        padding: 8px 15px;
        color: {colors['text_bright']};
    }}
    
    [data-testid="stSidebar"] {{
        background: {colors['bg2']};
    }}
    
    [data-testid="stSidebar"] * {{
        color: {colors['text_bright']} !important;
    }}
    
    [data-testid="stMetricValue"] {{
        color: {colors['text_bright']} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {colors['text_dim']} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== AI FUNCTIONS ====================
def predict_demand(item_name, days_ahead=7):
    try:
        from sklearn.linear_model import LinearRegression
        
        if 'sales_data' not in st.session_state or st.session_state.sales_data is None:
            return None
        
        item_data = st.session_state.sales_data[st.session_state.sales_data['Item'] == item_name]
        
        if len(item_data) < 5:
            return None
        
        item_data = item_data.sort_values('Date')
        X = np.array(range(len(item_data))).reshape(-1, 1)
        y = item_data['Quantity'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_X = np.array(range(len(item_data), len(item_data) + days_ahead)).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        future_dates = pd.date_range(
            start=item_data['Date'].max() + timedelta(days=1),
            periods=days_ahead,
            freq='D'
        )
        
        return pd.DataFrame({
            'Date': future_dates,
            'Predicted_Quantity': np.maximum(predictions, 0).astype(int)
        })
    except:
        return None

def get_reorder_suggestions():
    try:
        if 'inventory' not in st.session_state or st.session_state.inventory is None:
            return None
        
        suggestions = []
        for _, row in st.session_state.inventory.iterrows():
            if row['Current_Stock'] <= row['Reorder_Point']:
                order_qty = row['Max_Stock'] - row['Current_Stock']
                suggestions.append({
                    'Item': row['Item'],
                    'Current': row['Current_Stock'],
                    'Reorder_Point': row['Reorder_Point'],
                    'Suggested_Order': order_qty,
                    'Cost': order_qty * row['Unit_Cost'],
                    'Priority': 'HIGH' if row['Current_Stock'] < row['Min_Stock'] else 'MEDIUM'
                })
        return pd.DataFrame(suggestions) if suggestions else None
    except:
        return None

def chatbot_response(user_message, api_key):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        business = st.session_state.business_name or "Business"
        
        context = f"""
You are a helpful AI assistant for {business}. You help with:
- Ordering and product information
- Reservations and bookings
- Business inquiries and FAQs
- Customer support

Be friendly, professional, and helpful. Use the business name "{business}" when appropriate.
"""
        
        messages = [{"role": "system", "content": context}]
        
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            for msg in st.session_state.chat_history[-5:]:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append({"role": msg['role'], "content": msg['content']})
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error. Please check your API key. Error: {str(e)}"

# ==================== PAGE: WELCOME ====================
def show_welcome_page():
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🤖</div>
        <h1 class="welcome-title">AI Business Manager</h1>
        <p class="welcome-subtitle">Intelligent Predictive Ordering • Smart Inventory • 24/7 Virtual Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="input-container">
            <div class="step-indicator">
                <div class="step step-active">1</div>
                <div class="step step-inactive">2</div>
                <div class="step step-inactive">3</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p class='input-label'>👤 What's your name?</p>", unsafe_allow_html=True)
        
        client_name = st.text_input("Your Name", placeholder="Enter your name...", key="input_client", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True, type="primary"):
            if client_name and client_name.strip():
                st.session_state.client_name = client_name.strip()
                st.session_state.page = 'business_name'
                st.rerun()
            else:
                st.error("Please enter your name")

# ==================== PAGE: BUSINESS NAME ====================
def show_business_name_page():
    st.markdown(f"""
    <div class="welcome-container">
        <div class="welcome-icon">🏢</div>
        <h1 class="welcome-title">Hello, {st.session_state.client_name}!</h1>
        <p class="welcome-subtitle">Let's set up your business</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="input-container">
            <div class="step-indicator">
                <div class="step step-complete">✓</div>
                <div class="step step-active">2</div>
                <div class="step step-inactive">3</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p class='input-label'>🏪 What's your business name?</p>", unsafe_allow_html=True)
        
        business_name = st.text_input("Business Name", placeholder="Enter business name...", key="input_business", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("← Back", use_container_width=True):
                st.session_state.page = 'welcome'
                st.rerun()
        with col_b:
            if st.button("Continue →", use_container_width=True, type="primary"):
                if business_name and business_name.strip():
                    st.session_state.business_name = business_name.strip()
                    st.session_state.page = 'theme_select'
                    st.rerun()
                else:
                    st.error("Please enter your business name")

# ==================== PAGE: THEME SELECTION ====================
def show_theme_page():
    st.markdown(f"""
    <div class="welcome-container">
        <div class="welcome-icon">🎨</div>
        <h1 class="welcome-title">Almost Done!</h1>
        <p class="welcome-subtitle">Choose your preferred theme</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="input-container">
            <div class="step-indicator">
                <div class="step step-complete">✓</div>
                <div class="step step-complete">✓</div>
                <div class="step step-active">3</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_dark, col_light = st.columns(2)
        
        with col_dark:
            st.markdown("""
            <div style="text-align: center; padding: 1.5rem; background: #1a1a2e; border-radius: 12px;">
                <div style="font-size: 2.5rem;">🌙</div>
                <div style="color: white; font-weight: 600; margin-top: 0.5rem;">Dark Mode</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Dark", use_container_width=True, key="dark"):
                st.session_state.theme = 'dark'
                st.session_state.setup_complete = True
                st.session_state.page = 'loading'
                save_settings()
                st.rerun()
        
        with col_light:
            st.markdown("""
            <div style="text-align: center; padding: 1.5rem; background: #f8f9fa; border-radius: 12px;">
                <div style="font-size: 2.5rem;">☀️</div>
                <div style="color: #1a1a2e; font-weight: 600; margin-top: 0.5rem;">Light Mode</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Light", use_container_width=True, key="light"):
                st.session_state.theme = 'light'
                st.session_state.setup_complete = True
                st.session_state.page = 'loading'
                save_settings()
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("← Back", use_container_width=True):
            st.session_state.page = 'business_name'
            st.rerun()

# ==================== PAGE: LOADING ====================
def show_loading_page():
    st.markdown(f"""
    <div class="welcome-container">
        <div class="welcome-icon">⚡</div>
        <h1 class="welcome-title">Setting Up {st.session_state.business_name}</h1>
        <p class="welcome-subtitle">Preparing your AI-powered dashboard...</p>
    </div>
    """, unsafe_allow_html=True)
    
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress.progress(i + 1)
    
    # Initialize all data
    initialize_data()
    
    st.session_state.page = 'dashboard'
    st.rerun()

# ==================== PAGE: DASHBOARD ====================
def show_dashboard():
    # Ensure data is initialized
    initialize_data()
    
    now = datetime.now()
    colors = get_theme_colors()
    
    # DateTime Display
    st.markdown(f"""
    <div class="datetime-display">
        {now.strftime("%A, %d %B %Y")}<br>
        {now.strftime("%I:%M:%S %p").lower()}
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2.5rem;">🤖</div>
            <h3 style="margin: 0.5rem 0;">{st.session_state.business_name}</h3>
            <p style="opacity: 0.7; font-size: 0.9rem;">Welcome, {st.session_state.client_name}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Theme Toggle
        theme_icon = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
        if st.button(theme_icon, use_container_width=True):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            save_settings()
            st.rerun()
        
        st.markdown("---")
        
        # API Key
        st.markdown("### 🔑 API Key")
        api_key = st.text_input("OpenAI Key", type="password", placeholder="sk-...", label_visibility="collapsed")
        
        st.markdown("---")
        
        # Data Management
        st.markdown("### 💾 Data")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", use_container_width=True):
                auto_save_all()
                st.success("Saved!")
        with col2:
            if st.button("🔄 Reload", use_container_width=True):
                st.session_state.sales_data = load_data('sales.json', get_default_sales)
                st.session_state.inventory = load_data('inventory.json', get_default_inventory)
                st.session_state.bookings = load_data('bookings.json', get_default_bookings)
                st.session_state.chat_history = load_data('chat.json', get_default_chat)
                st.rerun()
        
        st.markdown("---")
        
        # Export
        if 'sales_data' in st.session_state and st.session_state.sales_data is not None:
            sales_json = st.session_state.sales_data.to_json(orient='records', date_format='iso')
            st.download_button("📊 Export Sales", sales_json, "sales.json", use_container_width=True)
        
        if 'inventory' in st.session_state and st.session_state.inventory is not None:
            inv_json = st.session_state.inventory.to_json(orient='records')
            st.download_button("📦 Export Inventory", inv_json, "inventory.json", use_container_width=True)
        
        st.markdown("---")
        
        # Change Business
        if st.button("🚪 Change Business", use_container_width=True):
            st.session_state.setup_complete = False
            st.session_state.page = 'welcome'
            st.session_state.client_name = ''
            st.session_state.business_name = ''
            st.session_state.data_initialized = False
            for key in ['sales_data', 'inventory', 'bookings', 'chat_history']:
                if key in st.session_state:
                    del st.session_state[key]
            save_settings()
            st.rerun()
        
        st.markdown("---")
        st.info(f"📁 {get_data_folder()}/")
    
    # Main Header
    hour = now.hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
    
    st.markdown(f"""
    <div class="main-header">
        <div class="business-name">🏪 {st.session_state.business_name}</div>
        <div class="greeting">{greeting}, {st.session_state.client_name}! 👋</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    total_sales = 0
    low_stock = 0
    booking_count = 0
    chat_count = 0
    
    if 'sales_data' in st.session_state and st.session_state.sales_data is not None:
        total_sales = st.session_state.sales_data['Revenue'].sum()
    
    if 'inventory' in st.session_state and st.session_state.inventory is not None:
        low_stock = len(st.session_state.inventory[
            st.session_state.inventory['Current_Stock'] <= st.session_state.inventory['Reorder_Point']
        ])
    
    if 'bookings' in st.session_state and st.session_state.bookings is not None:
        booking_count = len(st.session_state.bookings)
    
    if 'chat_history' in st.session_state and st.session_state.chat_history is not None:
        chat_count = len(st.session_state.chat_history)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">₹{total_sales:,.0f}</div><div class="metric-label">💰 Total Sales</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{low_stock}</div><div class="metric-label">⚠️ Low Stock</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{booking_count}</div><div class="metric-label">📅 Bookings</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><div class="metric-value">{chat_count}</div><div class="metric-label">💬 Chats</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔮 Predictions", "📦 Inventory", "💬 AI Chat", "📊 Analytics", "📅 Bookings"])
    
    # TAB 1: PREDICTIONS
    with tab1:
        st.markdown('<div class="section-title">🔮 AI Demand Forecasting</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if 'sales_data' in st.session_state and st.session_state.sales_data is not None:
                items = st.session_state.sales_data['Item'].unique().tolist()
                selected_item = st.selectbox("Select Item:", items)
                days = st.slider("Forecast Days:", 3, 14, 7)
                
                if st.button("🔮 Generate Forecast", type="primary"):
                    prediction = predict_demand(selected_item, days)
                    
                    if prediction is not None:
                        st.success(f"📈 Forecast for {selected_item}")
                        
                        historical = st.session_state.sales_data[
                            st.session_state.sales_data['Item'] == selected_item
                        ].groupby('Date')['Quantity'].sum().reset_index()
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=historical['Date'], y=historical['Quantity'],
                                                mode='lines+markers', name='Historical',
                                                line=dict(color=colors['accent2'], width=2)))
                        fig.add_trace(go.Scatter(x=prediction['Date'], y=prediction['Predicted_Quantity'],
                                                mode='lines+markers', name='Predicted',
                                                line=dict(color=colors['accent1'], width=2, dash='dash')))
                        fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)',
                                         plot_bgcolor='rgba(0,0,0,0)', font=dict(color=colors['text']))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        avg = prediction['Predicted_Quantity'].mean()
                        st.info(f"📊 Average demand: **{avg:.0f} units/day** | Recommended stock: **{avg * 1.5:.0f} units**")
                    else:
                        st.warning("Not enough data for prediction")
            else:
                st.info("No sales data available")
        
        with col2:
            st.markdown("### 🚨 Reorder Alerts")
            reorder = get_reorder_suggestions()
            
            if reorder is not None and len(reorder) > 0:
                for _, item in reorder.iterrows():
                    alert_class = "alert-high" if item['Priority'] == 'HIGH' else "alert-medium"
                    icon = "🔴" if item['Priority'] == 'HIGH' else "🟡"
                    st.markdown(f"""<div class="{alert_class}"><strong>{icon} {item['Item']}</strong><br>Stock: {item['Current']} | Order: {item['Suggested_Order']}</div>""", unsafe_allow_html=True)
            else:
                st.success("✅ All items stocked!")
    
    # TAB 2: INVENTORY
    with tab2:
        st.markdown('<div class="section-title">📦 Inventory Management</div>', unsafe_allow_html=True)
        
        if 'inventory' in st.session_state and st.session_state.inventory is not None:
            edited_inv = st.data_editor(st.session_state.inventory, use_container_width=True, num_rows="dynamic")
            
            if st.button("💾 Update Inventory"):
                st.session_state.inventory = edited_inv
                auto_save_all()
                st.success("✅ Updated!")
                st.rerun()
            
            st.markdown("---")
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Current', x=st.session_state.inventory['Item'],
                                y=st.session_state.inventory['Current_Stock'], marker_color=colors['accent2']))
            fig.add_trace(go.Bar(name='Min', x=st.session_state.inventory['Item'],
                                y=st.session_state.inventory['Min_Stock'], marker_color=colors['accent1']))
            fig.update_layout(barmode='group', height=350, paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)', font=dict(color=colors['text']))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No inventory data")
    
    # TAB 3: AI CHAT
    with tab3:
        st.markdown('<div class="section-title">💬 AI Virtual Assistant (24/7)</div>', unsafe_allow_html=True)
        
        if not api_key:
            st.warning("⚠️ Enter OpenAI API Key in sidebar")
            st.info("Get key: https://platform.openai.com/api-keys")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if 'chat_history' in st.session_state and st.session_state.chat_history:
                    for msg in st.session_state.chat_history:
                        if isinstance(msg, dict):
                            if msg.get('role') == 'user':
                                st.markdown(f'<div class="chat-user"><strong>You:</strong> {msg.get("content", "")}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="chat-bot"><strong>🤖 AI:</strong> {msg.get("content", "")}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                with st.form("chat_form", clear_on_submit=True):
                    col_a, col_b = st.columns([5, 1])
                    with col_a:
                        msg = st.text_input("Message", placeholder="Type your message...", label_visibility="collapsed")
                    with col_b:
                        send = st.form_submit_button("Send")
                    
                    if send and msg:
                        if 'chat_history' not in st.session_state:
                            st.session_state.chat_history = []
                        
                        st.session_state.chat_history.append({'role': 'user', 'content': msg})
                        
                        with st.spinner("AI thinking..."):
                            response = chatbot_response(msg, api_key)
                        
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                        auto_save_all()
                        st.rerun()
            
            with col2:
                st.markdown("### Quick")
                questions = ["Menu?", "Book table", "Hours?"]
                for q in questions:
                    if st.button(q, use_container_width=True, key=f"q_{q}"):
                        if 'chat_history' not in st.session_state:
                            st.session_state.chat_history = []
                        st.session_state.chat_history.append({'role': 'user', 'content': q})
                        response = chatbot_response(q, api_key)
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                        auto_save_all()
                        st.rerun()
                
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.chat_history = []
                    auto_save_all()
                    st.rerun()
    
    # TAB 4: ANALYTICS
    with tab4:
        st.markdown('<div class="section-title">📊 Analytics</div>', unsafe_allow_html=True)
        
        if 'sales_data' in st.session_state and st.session_state.sales_data is not None:
            daily = st.session_state.sales_data.groupby('Date')['Revenue'].sum().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily['Date'], y=daily['Revenue'], mode='lines+markers',
                                    fill='tozeroy', line=dict(color=colors['accent2'], width=2)))
            fig.update_layout(title="Revenue Trend", height=300, paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)', font=dict(color=colors['text']))
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                item_rev = st.session_state.sales_data.groupby('Item')['Revenue'].sum().sort_values(ascending=False)
                fig = px.bar(item_rev, title="Revenue by Item", color_discrete_sequence=[colors['accent1']])
                fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=colors['text']))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                item_qty = st.session_state.sales_data.groupby('Item')['Quantity'].sum().sort_values(ascending=False)
                fig = px.bar(item_qty, title="Quantity by Item", color_discrete_sequence=[colors['accent2']])
                fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font=dict(color=colors['text']))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data")
    
    # TAB 5: BOOKINGS
    with tab5:
        st.markdown('<div class="section-title">📅 Bookings</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if 'bookings' in st.session_state and st.session_state.bookings is not None:
                st.dataframe(st.session_state.bookings, use_container_width=True, hide_index=True)
            else:
                st.info("No bookings")
        
        with col2:
            st.markdown("### ➕ New Booking")
            with st.form("booking", clear_on_submit=True):
                name = st.text_input("Name")
                phone = st.text_input("Phone")
                date = st.date_input("Date")
                time_slot = st.selectbox("Time", [f"{h:02d}:00" for h in range(9, 22)])
                guests = st.number_input("Guests", 1, 20, 2)
                
                if st.form_submit_button("Add", use_container_width=True):
                    if name and phone:
                        new = pd.DataFrame({
                            'Date': [pd.Timestamp(date)],
                            'Name': [name],
                            'Phone': [phone],
                            'Guests': [guests],
                            'Time': [time_slot],
                            'Status': ['Confirmed']
                        })
                        if 'bookings' not in st.session_state or st.session_state.bookings is None:
                            st.session_state.bookings = new
                        else:
                            st.session_state.bookings = pd.concat([st.session_state.bookings, new], ignore_index=True)
                        auto_save_all()
                        st.success("✅ Added!")
                        st.rerun()
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem; opacity: 0.5; margin-top: 1rem;">
        <p>🤖 AI Business Manager • {st.session_state.business_name}</p>
        <p style="font-size: 0.8rem;">{now.strftime('%d %B %Y • %I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN ROUTER ====================
if st.session_state.page == 'welcome':
    show_welcome_page()
elif st.session_state.page == 'business_name':
    show_business_name_page()
elif st.session_state.page == 'theme_select':
    show_theme_page()
elif st.session_state.page == 'loading':
    show_loading_page()
elif st.session_state.page == 'dashboard':
    show_dashboard()
else:
    show_welcome_page()
