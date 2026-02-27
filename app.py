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
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE ====================
def init_state():
    defaults = {
        'page': 'welcome',
        'client_name': '',
        'business_name': '',
        'theme': 'dark',
        'setup_complete': False,
        'api_key': '',
        'chat_history': [],
        'products': None,
        'sales_data': None,
        'inventory': None,
        'bookings': None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# ==================== DEFAULT DATA ====================
def default_products():
    return pd.DataFrame({
        'Product': ['Coffee', 'Sandwich', 'Cake', 'Tea', 'Pasta'],
        'Category': ['Beverages', 'Food', 'Dessert', 'Beverages', 'Food'],
        'Price': [150, 200, 180, 100, 250],
        'Cost': [50, 80, 60, 30, 100]
    })

def default_sales():
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    items = ['Coffee', 'Sandwich', 'Cake', 'Tea', 'Pasta']
    data = []
    np.random.seed(42)
    for d in dates:
        for item in items:
            base = {'Coffee': 50, 'Sandwich': 30, 'Cake': 20, 'Tea': 40, 'Pasta': 25}[item]
            qty = max(1, int(base + np.random.randint(-10, 15)))
            price = {'Coffee': 150, 'Sandwich': 200, 'Cake': 180, 'Tea': 100, 'Pasta': 250}[item]
            data.append({'Date': d, 'Product': item, 'Quantity': qty, 'Revenue': qty * price})
    return pd.DataFrame(data)

def default_inventory():
    return pd.DataFrame({
        'Item': ['Coffee Beans', 'Bread', 'Flour', 'Milk', 'Pasta', 'Vegetables', 'Cheese', 'Sugar'],
        'Stock': [50, 100, 80, 60, 40, 70, 30, 90],
        'Min_Stock': [20, 40, 30, 25, 15, 30, 10, 40],
        'Max_Stock': [100, 200, 150, 120, 80, 150, 60, 180],
        'Cost': [500, 50, 40, 60, 80, 30, 150, 50],
        'Reorder_At': [30, 60, 45, 35, 20, 45, 15, 60]
    })

def default_bookings():
    return pd.DataFrame({
        'Date': pd.date_range(start=datetime.now(), periods=5, freq='D'),
        'Name': ['John', 'Mary', 'Alex', 'Sarah', 'Mike'],
        'Phone': ['1234567890', '2345678901', '3456789012', '4567890123', '5678901234'],
        'Guests': [2, 4, 3, 6, 2],
        'Time': ['12:00', '13:00', '19:00', '20:00', '18:00'],
        'Status': ['Confirmed'] * 5
    })

# ==================== INITIALIZE DATA ====================
def load_data():
    if st.session_state.products is None:
        st.session_state.products = default_products()
    if st.session_state.sales_data is None:
        st.session_state.sales_data = default_sales()
    if st.session_state.inventory is None:
        st.session_state.inventory = default_inventory()
    if st.session_state.bookings is None:
        st.session_state.bookings = default_bookings()

# ==================== SAVE/LOAD SETTINGS ====================
def save_settings():
    try:
        settings = {
            'client_name': st.session_state.client_name,
            'business_name': st.session_state.business_name,
            'theme': st.session_state.theme,
            'setup_complete': st.session_state.setup_complete,
            'api_key': st.session_state.api_key
        }
        os.makedirs('settings', exist_ok=True)
        with open('settings/config.json', 'w') as f:
            json.dump(settings, f)
    except:
        pass

def load_settings():
    try:
        if os.path.exists('settings/config.json'):
            with open('settings/config.json', 'r') as f:
                s = json.load(f)
                st.session_state.client_name = s.get('client_name', '')
                st.session_state.business_name = s.get('business_name', '')
                st.session_state.theme = s.get('theme', 'dark')
                st.session_state.setup_complete = s.get('setup_complete', False)
                st.session_state.api_key = s.get('api_key', '')
                if st.session_state.setup_complete:
                    st.session_state.page = 'dashboard'
    except:
        pass

# Load on startup
if 'loaded' not in st.session_state:
    load_settings()
    st.session_state.loaded = True

# ==================== THEME ====================
def get_colors():
    if st.session_state.theme == 'dark':
        return {
            'bg': '#0E1117', 'card': '#1E2130', 'text': '#FFFFFF',
            'accent1': '#FF6B6B', 'accent2': '#4ECDC4'
        }
    else:
        return {
            'bg': '#FFFFFF', 'card': '#F0F2F6', 'text': '#262730',
            'accent1': '#E63946', 'accent2': '#2A9D8F'
        }

c = get_colors()

# ==================== CSS ====================
st.markdown(f"""
<style>
    .stApp {{ background: {c['bg']}; }}
    #MainMenu, footer {{ visibility: hidden; }}
    
    .big-title {{
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        color: {c['accent1']};
        margin: 1rem 0;
    }}
    
    .sub-title {{
        text-align: center;
        color: {c['text']};
        opacity: 0.7;
        margin-bottom: 2rem;
    }}
    
    .section-header {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {c['text']};
        border-bottom: 2px solid {c['accent2']};
        padding-bottom: 0.5rem;
        margin: 1rem 0;
    }}
    
    .card {{
        background: {c['card']};
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
    }}
    
    .metric-box {{
        background: {c['card']};
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {c['text']};
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        color: {c['text']};
        opacity: 0.7;
    }}
    
    .chat-user {{
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 8px 0 8px 25%;
    }}
    
    .chat-bot {{
        background: {c['card']};
        color: {c['text']};
        padding: 10px 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 8px 25% 8px 0;
        border-left: 3px solid {c['accent2']};
    }}
    
    .api-bar {{
        background: {c['card']};
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid {c['accent2']};
        margin-bottom: 1rem;
    }}
    
    .datetime {{
        position: fixed;
        top: 70px;
        right: 20px;
        font-size: 0.7rem;
        color: {c['text']};
        background: {c['card']};
        padding: 8px 12px;
        border-radius: 8px;
        z-index: 999;
        text-align: right;
    }}
    
    .welcome-box {{
        text-align: center;
        padding: 3rem;
        max-width: 500px;
        margin: 0 auto;
        background: {c['card']};
        border-radius: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== AI FUNCTIONS ====================
def predict_demand(product, days=7):
    try:
        from sklearn.linear_model import LinearRegression
        
        df = st.session_state.sales_data
        if df is None:
            return None
        
        prod_data = df[df['Product'] == product]
        if len(prod_data) < 3:
            return None
        
        prod_data = prod_data.sort_values('Date')
        X = np.arange(len(prod_data)).reshape(-1, 1)
        y = prod_data['Quantity'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_X = np.arange(len(prod_data), len(prod_data) + days).reshape(-1, 1)
        pred = model.predict(future_X)
        
        dates = pd.date_range(start=prod_data['Date'].max() + timedelta(days=1), periods=days)
        
        return pd.DataFrame({
            'Date': dates,
            'Predicted': np.maximum(pred, 0).astype(int)
        })
    except:
        return None

def get_ai_response(message, api_key):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        business = st.session_state.business_name or "Business"
        products = ""
        if st.session_state.products is not None:
            products = ", ".join(st.session_state.products['Product'].tolist())
        
        system = f"""You are a helpful AI assistant for {business}.
Products available: {products}
Help with orders, bookings, and questions. Be friendly and professional."""
        
        msgs = [{"role": "system", "content": system}]
        
        # Add history
        for m in st.session_state.chat_history[-5:]:
            msgs.append({"role": m['role'], "content": m['content']})
        
        msgs.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=msgs,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ==================== PAGE: WELCOME ====================
def page_welcome():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="welcome-box">
            <div style="font-size: 4rem;">🤖</div>
            <h1 style="margin: 1rem 0;">AI Business Manager</h1>
            <p style="opacity: 0.7;">Smart Inventory • AI Predictions • 24/7 Chatbot</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        name = st.text_input("👤 Your Name", placeholder="Enter your name...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True, type="primary"):
            if name and name.strip():
                st.session_state.client_name = name.strip()
                st.session_state.page = 'business'
                st.rerun()
            else:
                st.error("Please enter your name")

# ==================== PAGE: BUSINESS ====================
def page_business():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="welcome-box">
            <div style="font-size: 4rem;">🏢</div>
            <h1>Hello, {st.session_state.client_name}!</h1>
            <p style="opacity: 0.7;">Let's set up your business</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        business = st.text_input("🏪 Business Name", placeholder="Enter business name...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("← Back", use_container_width=True):
                st.session_state.page = 'welcome'
                st.rerun()
        
        with col_b:
            if st.button("Continue →", use_container_width=True, type="primary"):
                if business and business.strip():
                    st.session_state.business_name = business.strip()
                    st.session_state.page = 'theme'
                    st.rerun()
                else:
                    st.error("Please enter business name")

# ==================== PAGE: THEME ====================
def page_theme():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="welcome-box">
            <div style="font-size: 4rem;">🎨</div>
            <h1>Choose Theme</h1>
            <p style="opacity: 0.7;">Select your preferred look</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_d, col_l = st.columns(2)
        
        with col_d:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #1a1a2e; border-radius: 15px;">
                <div style="font-size: 3rem;">🌙</div>
                <div style="color: white; font-weight: 600;">Dark</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Dark", use_container_width=True):
                st.session_state.theme = 'dark'
                st.session_state.setup_complete = True
                st.session_state.page = 'dashboard'
                load_data()
                save_settings()
                st.rerun()
        
        with col_l:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f0f2f6; border-radius: 15px;">
                <div style="font-size: 3rem;">☀️</div>
                <div style="color: #1a1a2e; font-weight: 600;">Light</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Light", use_container_width=True):
                st.session_state.theme = 'light'
                st.session_state.setup_complete = True
                st.session_state.page = 'dashboard'
                load_data()
                save_settings()
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("← Back", use_container_width=True):
            st.session_state.page = 'business'
            st.rerun()

# ==================== PAGE: DASHBOARD ====================
def page_dashboard():
    load_data()
    c = get_colors()
    now = datetime.now()
    
    # DateTime
    st.markdown(f"""
    <div class="datetime">
        {now.strftime("%A, %d %B %Y")}<br>
        {now.strftime("%I:%M %p").lower()}
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.markdown(f"## 🤖 {st.session_state.business_name}")
        st.markdown(f"Welcome, **{st.session_state.client_name}**")
        
        st.markdown("---")
        
        # Theme Toggle
        theme_btn = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
        if st.button(theme_btn, use_container_width=True):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            save_settings()
            st.rerun()
        
        st.markdown("---")
        
        # API KEY IN SIDEBAR
        st.markdown("### 🔑 API Key")
        sidebar_api = st.text_input(
            "OpenAI API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-...",
            key="sidebar_api"
        )
        
        if sidebar_api != st.session_state.api_key:
            st.session_state.api_key = sidebar_api
            save_settings()
        
        if st.session_state.api_key:
            st.success("✅ API Key set")
        else:
            st.warning("⚠️ Enter API Key")
        
        st.markdown("[Get API Key →](https://platform.openai.com/api-keys)")
        
        st.markdown("---")
        
        # Export
        st.markdown("### 📥 Export Data")
        
        if st.session_state.products is not None:
            st.download_button(
                "🏷️ Products",
                st.session_state.products.to_csv(index=False),
                "products.csv",
                use_container_width=True
            )
        
        if st.session_state.sales_data is not None:
            st.download_button(
                "📊 Sales",
                st.session_state.sales_data.to_csv(index=False),
                "sales.csv",
                use_container_width=True
            )
        
        if st.session_state.inventory is not None:
            st.download_button(
                "📦 Inventory",
                st.session_state.inventory.to_csv(index=False),
                "inventory.csv",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Reset
        if st.button("🚪 Change Business", use_container_width=True):
            for key in ['setup_complete', 'client_name', 'business_name', 'products', 
                       'sales_data', 'inventory', 'bookings', 'chat_history']:
                if key in st.session_state:
                    if key == 'setup_complete':
                        st.session_state[key] = False
                    elif key in ['client_name', 'business_name']:
                        st.session_state[key] = ''
                    elif key == 'chat_history':
                        st.session_state[key] = []
                    else:
                        st.session_state[key] = None
            st.session_state.page = 'welcome'
            save_settings()
            st.rerun()
    
    # ==================== MAIN HEADER ====================
    hour = now.hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
    
    st.markdown(f'<div class="big-title">🏪 {st.session_state.business_name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{greeting}, {st.session_state.client_name}! 👋</div>', unsafe_allow_html=True)
    
    # ==================== METRICS ====================
    total_sales = st.session_state.sales_data['Revenue'].sum() if st.session_state.sales_data is not None else 0
    product_count = len(st.session_state.products) if st.session_state.products is not None else 0
    booking_count = len(st.session_state.bookings) if st.session_state.bookings is not None else 0
    low_stock = 0
    if st.session_state.inventory is not None:
        low_stock = len(st.session_state.inventory[st.session_state.inventory['Stock'] <= st.session_state.inventory['Reorder_At']])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">₹{total_sales:,.0f}</div>
            <div class="metric-label">💰 Total Sales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{product_count}</div>
            <div class="metric-label">🏷️ Products</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{low_stock}</div>
            <div class="metric-label">⚠️ Low Stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{booking_count}</div>
            <div class="metric-label">📅 Bookings</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== TABS ====================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏷️ Products",
        "🔮 Predictions", 
        "📦 Inventory",
        "💬 AI Chat",
        "📅 Bookings"
    ])
    
    # ==================== TAB 1: PRODUCTS ====================
    with tab1:
        st.markdown('<div class="section-header">🏷️ Your Products</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Product List")
            st.info("👇 You can edit directly in the table below. Add/delete rows as needed.")
            
            if st.session_state.products is not None:
                edited = st.data_editor(
                    st.session_state.products,
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "Product": st.column_config.TextColumn("Product Name", required=True),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=["Food", "Beverages", "Dessert", "Snacks", "Other"],
                            required=True
                        ),
                        "Price": st.column_config.NumberColumn("Sell Price (₹)", min_value=0, format="₹%.0f"),
                        "Cost": st.column_config.NumberColumn("Cost (₹)", min_value=0, format="₹%.0f")
                    },
                    key="product_editor"
                )
                
                if st.button("💾 Save Products", type="primary", use_container_width=True):
                    st.session_state.products = edited
                    st.success("✅ Products saved!")
        
        with col2:
            st.markdown("### ➕ Quick Add")
            
            with st.form("add_product_form", clear_on_submit=True):
                new_name = st.text_input("Product Name *", placeholder="e.g., Burger")
                new_cat = st.selectbox("Category", ["Food", "Beverages", "Dessert", "Snacks", "Other"])
                new_price = st.number_input("Selling Price (₹)", min_value=0, value=100, step=10)
                new_cost = st.number_input("Cost Price (₹)", min_value=0, value=50, step=5)
                
                submitted = st.form_submit_button("➕ Add Product", use_container_width=True, type="primary")
                
                if submitted:
                    if new_name and new_name.strip():
                        new_row = pd.DataFrame({
                            'Product': [new_name.strip()],
                            'Category': [new_cat],
                            'Price': [new_price],
                            'Cost': [new_cost]
                        })
                        st.session_state.products = pd.concat([st.session_state.products, new_row], ignore_index=True)
                        st.success(f"✅ '{new_name}' added!")
                        st.rerun()
                    else:
                        st.error("Enter product name")
            
            st.markdown("---")
            
            # Add Sale
            st.markdown("### 📊 Record Sale")
            
            with st.form("add_sale_form", clear_on_submit=True):
                if st.session_state.products is not None and len(st.session_state.products) > 0:
                    sale_product = st.selectbox("Product", st.session_state.products['Product'].tolist())
                else:
                    sale_product = st.text_input("Product Name")
                
                sale_date = st.date_input("Date", datetime.now())
                sale_qty = st.number_input("Quantity", min_value=1, value=1)
                sale_rev = st.number_input("Revenue (₹)", min_value=0, value=150, step=50)
                
                if st.form_submit_button("➕ Add Sale", use_container_width=True):
                    if sale_product:
                        new_sale = pd.DataFrame({
                            'Date': [pd.Timestamp(sale_date)],
                            'Product': [sale_product],
                            'Quantity': [sale_qty],
                            'Revenue': [sale_rev]
                        })
                        st.session_state.sales_data = pd.concat([st.session_state.sales_data, new_sale], ignore_index=True)
                        st.success("✅ Sale recorded!")
                        st.rerun()
    
    # ==================== TAB 2: PREDICTIONS ====================
    with tab2:
        st.markdown('<div class="section-header">🔮 AI Demand Predictions</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.session_state.sales_data is not None and len(st.session_state.sales_data) > 0:
                products_list = st.session_state.sales_data['Product'].unique().tolist()
                
                if products_list:
                    selected = st.selectbox("Select Product to Forecast:", products_list)
                    days = st.slider("Forecast Days:", 3, 14, 7)
                    
                    if st.button("🔮 Generate Forecast", type="primary"):
                        pred = predict_demand(selected, days)
                        
                        if pred is not None:
                            st.success(f"📈 {days}-Day Forecast for {selected}")
                            
                            # Chart
                            hist = st.session_state.sales_data[
                                st.session_state.sales_data['Product'] == selected
                            ].groupby('Date')['Quantity'].sum().reset_index()
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=hist['Date'], y=hist['Quantity'],
                                mode='lines+markers', name='Historical',
                                line=dict(color=c['accent2'], width=2)
                            ))
                            fig.add_trace(go.Scatter(
                                x=pred['Date'], y=pred['Predicted'],
                                mode='lines+markers', name='Predicted',
                                line=dict(color=c['accent1'], width=2, dash='dash')
                            ))
                            fig.update_layout(
                                height=400,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color=c['text'])
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            avg = pred['Predicted'].mean()
                            st.info(f"📊 Average: **{avg:.0f}/day** | Stock needed: **{avg * days:.0f} units**")
                        else:
                            st.warning("Not enough data. Add more sales records.")
                else:
                    st.info("No products with sales data. Add sales first.")
            else:
                st.info("No sales data. Add sales in Products tab.")
        
        with col2:
            st.markdown("### 🚨 Low Stock Alerts")
            
            if st.session_state.inventory is not None:
                low = st.session_state.inventory[
                    st.session_state.inventory['Stock'] <= st.session_state.inventory['Reorder_At']
                ]
                
                if len(low) > 0:
                    for _, row in low.iterrows():
                        st.warning(f"⚠️ **{row['Item']}**: {row['Stock']} left (min: {row['Reorder_At']})")
                else:
                    st.success("✅ All items well stocked!")
    
    # ==================== TAB 3: INVENTORY ====================
    with tab3:
        st.markdown('<div class="section-header">📦 Inventory Management</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.session_state.inventory is not None:
                edited_inv = st.data_editor(
                    st.session_state.inventory,
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "Item": st.column_config.TextColumn("Item", required=True),
                        "Stock": st.column_config.NumberColumn("Current Stock", min_value=0),
                        "Min_Stock": st.column_config.NumberColumn("Min Stock", min_value=0),
                        "Max_Stock": st.column_config.NumberColumn("Max Stock", min_value=0),
                        "Cost": st.column_config.NumberColumn("Unit Cost", min_value=0, format="₹%.0f"),
                        "Reorder_At": st.column_config.NumberColumn("Reorder At", min_value=0)
                    }
                )
                
                if st.button("💾 Save Inventory", type="primary", use_container_width=True):
                    st.session_state.inventory = edited_inv
                    st.success("✅ Inventory saved!")
                
                # Chart
                st.markdown("---")
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Current', x=st.session_state.inventory['Item'],
                    y=st.session_state.inventory['Stock'], marker_color=c['accent2']
                ))
                fig.add_trace(go.Bar(
                    name='Min', x=st.session_state.inventory['Item'],
                    y=st.session_state.inventory['Min_Stock'], marker_color=c['accent1']
                ))
                fig.update_layout(
                    barmode='group', height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=c['text'])
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ➕ Add Item")
            
            with st.form("add_inv", clear_on_submit=True):
                inv_name = st.text_input("Item Name *")
                inv_stock = st.number_input("Current Stock", min_value=0, value=50)
                inv_min = st.number_input("Min Stock", min_value=0, value=20)
                inv_max = st.number_input("Max Stock", min_value=0, value=100)
                inv_cost = st.number_input("Unit Cost (₹)", min_value=0, value=50)
                inv_reorder = st.number_input("Reorder At", min_value=0, value=30)
                
                if st.form_submit_button("➕ Add", use_container_width=True, type="primary"):
                    if inv_name:
                        new_inv = pd.DataFrame({
                            'Item': [inv_name],
                            'Stock': [inv_stock],
                            'Min_Stock': [inv_min],
                            'Max_Stock': [inv_max],
                            'Cost': [inv_cost],
                            'Reorder_At': [inv_reorder]
                        })
                        st.session_state.inventory = pd.concat([st.session_state.inventory, new_inv], ignore_index=True)
                        st.success(f"✅ {inv_name} added!")
                        st.rerun()
    
    # ==================== TAB 4: AI CHAT ====================
    with tab4:
        st.markdown('<div class="section-header">💬 AI Virtual Assistant (24/7)</div>', unsafe_allow_html=True)
        
        # API KEY BAR IN CHAT TAB
        st.markdown('<div class="api-bar">', unsafe_allow_html=True)
        
        col_k1, col_k2, col_k3 = st.columns([4, 1, 1])
        
        with col_k1:
            chat_api = st.text_input(
                "🔑 API Key",
                value=st.session_state.api_key,
                type="password",
                placeholder="Enter your OpenAI API key here (sk-...)",
                label_visibility="collapsed",
                key="chat_api_input"
            )
        
        with col_k2:
            if st.button("💾 Save", use_container_width=True):
                st.session_state.api_key = chat_api
                save_settings()
                st.success("✅")
        
        with col_k3:
            st.link_button("Get Key", "https://platform.openai.com/api-keys", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Use the API key
        api_key = chat_api if chat_api else st.session_state.api_key
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API Key above to use the AI chatbot")
            
            st.markdown("""
            ### 🔑 How to get API Key:
            1. Go to [platform.openai.com](https://platform.openai.com/signup)
            2. Sign up or login
            3. Go to [API Keys](https://platform.openai.com/api-keys)
            4. Click **"Create new secret key"**
            5. Copy and paste above
            6. Add billing: [Billing](https://platform.openai.com/account/billing)
            """)
        
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Chat History
                chat_box = st.container(height=400)
                
                with chat_box:
                    if st.session_state.chat_history:
                        for msg in st.session_state.chat_history:
                            if msg['role'] == 'user':
                                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.info("👋 Start chatting! Ask about orders, bookings, menu, etc.")
                
                # Chat Input
                with st.form("chat_input", clear_on_submit=True):
                    col_m, col_s = st.columns([5, 1])
                    
                    with col_m:
                        user_msg = st.text_input(
                            "Message",
                            placeholder="Type your message here...",
                            label_visibility="collapsed"
                        )
                    
                    with col_s:
                        send = st.form_submit_button("Send", use_container_width=True, type="primary")
                    
                    if send and user_msg:
                        st.session_state.chat_history.append({'role': 'user', 'content': user_msg})
                        
                        with st.spinner("🤖 Thinking..."):
                            response = get_ai_response(user_msg, api_key)
                        
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                        st.rerun()
            
            with col2:
                st.markdown("### 🎯 Quick")
                
                quick = ["What's on the menu?", "Book a table", "Business hours?", "Special offers?", "Contact info?"]
                
                for q in quick:
                    if st.button(q, use_container_width=True, key=f"quick_{q}"):
                        st.session_state.chat_history.append({'role': 'user', 'content': q})
                        response = get_ai_response(q, api_key)
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                        st.rerun()
                
                st.markdown("---")
                
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
                
                st.metric("Messages", len(st.session_state.chat_history))
    
    # ==================== TAB 5: BOOKINGS ====================
    with tab5:
        st.markdown('<div class="section-header">📅 Bookings</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.session_state.bookings is not None:
                st.dataframe(st.session_state.bookings, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### ➕ New Booking")
            
            with st.form("booking_form", clear_on_submit=True):
                b_name = st.text_input("Name *")
                b_phone = st.text_input("Phone *")
                b_date = st.date_input("Date")
                b_time = st.selectbox("Time", [f"{h:02d}:00" for h in range(9, 22)])
                b_guests = st.number_input("Guests", 1, 50, 2)
                
                if st.form_submit_button("➕ Add Booking", use_container_width=True, type="primary"):
                    if b_name and b_phone:
                        new_b = pd.DataFrame({
                            'Date': [pd.Timestamp(b_date)],
                            'Name': [b_name],
                            'Phone': [b_phone],
                            'Guests': [b_guests],
                            'Time': [b_time],
                            'Status': ['Confirmed']
                        })
                        st.session_state.bookings = pd.concat([st.session_state.bookings, new_b], ignore_index=True)
                        st.success("✅ Booking added!")
                        st.rerun()
                    else:
                        st.error("Fill all fields")
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; opacity: 0.5;">
        <p>🤖 AI Business Manager • {st.session_state.business_name}</p>
        <p style="font-size: 0.8rem;">{now.strftime('%d %B %Y • %I:%M %p')}</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== ROUTER ====================
if st.session_state.page == 'welcome':
    page_welcome()
elif st.session_state.page == 'business':
    page_business()
elif st.session_state.page == 'theme':
    page_theme()
elif st.session_state.page == 'dashboard':
    page_dashboard()
else:
    page_welcome()
