import streamlit as st
import pandas as pd
from datetime import datetime
from geopy.distance import geodesic
import streamlit.components.v1 as components

# Try to import AI triage
try:
    from utils.ai_triage import claude_triage
    USE_AI = True
except ImportError:
    USE_AI = False
    print("Warning: Could not import ai_triage, using simple keyword matching")

# Page config
st.set_page_config(
    page_title="FindMyMed Emergency",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern, beautiful styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main {
        padding: 2rem 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Button Improvements */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Emergency Header with Gradient */
    .emergency-header {
        background: linear-gradient(135deg, #DC143C 0%, #FF1744 100%);
        color: white;
        padding: 2rem;
        text-align: center;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 24px rgba(220, 20, 60, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .emergency-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .emergency-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Pharmacy Card - Modern Design */
    .pharmacy-card {
        border: none;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .pharmacy-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    /* Stock Status Badges */
    .in-stock {
        color: #2E7D32;
        font-weight: 700;
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .stock-out {
        color: #C62828;
        font-weight: 700;
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    /* Urgent Warning */
    .urgent-warning {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-left: 5px solid #FF6F00;
        padding: 1.25rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(255, 111, 0, 0.2);
    }
    
    /* Pharmacy Header */
    .pharmacy-header {
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(25, 118, 210, 0.3);
    }
    
    .pharmacy-header h2 {
        margin: 0;
        font-weight: 700;
        font-size: 1.75rem;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .feature-card:hover {
        border-color: #1976D2;
        box-shadow: 0 4px 16px rgba(25, 118, 210, 0.15);
    }
    
    /* Section Headers */
    h1, h2, h3 {
        font-weight: 700;
        color: #1a1a1a;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1976D2;
        box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
    }
    
    /* Selectbox */
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
    }
    
    /* Toggle Switch */
    .stToggle {
        margin: 0.5rem 0;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stError {
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Info Boxes */
    .stInfo {
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid #1976D2;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e0e0e0;
    }
    
    /* Quick Access Buttons */
    .quick-access-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .quick-access-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-color: #1976D2;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #1976D2;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

# Load data functions
@st.cache_data
def load_medicines():
    import os
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'emergency_medicines.csv')
    return pd.read_csv(csv_path)

@st.cache_data
def load_pharmacies():
    import os
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'emergency_pharmacies.csv')
    return pd.read_csv(csv_path)

def calculate_distance(user_lat, user_lon, pharm_lat, pharm_lon):
    """Calculate distance between user and pharmacy in km"""
    return geodesic((user_lat, user_lon), (pharm_lat, pharm_lon)).km

def get_medicine_column_name(medicine_name):
    """Convert medicine name to CSV column name"""
    base_name = medicine_name.split('(')[0].strip()
    column_name = base_name.replace(' ', '_').replace('-', '_')
    return column_name

def search_pharmacies(medicine_name, pharmacies_df, user_location=None):
    """Search pharmacies that have the medicine in stock"""
    column_name = get_medicine_column_name(medicine_name)
    matching_cols = [col for col in pharmacies_df.columns if column_name.lower() in col.lower()]
    
    if not matching_cols:
        return pd.DataFrame()
    
    actual_column = matching_cols[0]
    available = pharmacies_df[pharmacies_df[actual_column] == 'Yes'].copy()
    
    if user_location and len(user_location) == 2:
        available['distance_km'] = available.apply(
            lambda row: calculate_distance(
                user_location[0], user_location[1],
                row['Latitude'], row['Longitude']
            ), axis=1
        )
        available = available.sort_values('distance_km')
    
    return available

def simple_triage(symptoms, medicines_df):
    """Simple keyword-based symptom to medicine matching"""
    symptoms_lower = symptoms.lower()
    
    for _, med in medicines_df.iterrows():
        keywords = med['Keywords'].lower().split(',')
        matches = sum(1 for keyword in keywords if keyword.strip() in symptoms_lower)
        if matches >= 2:
            return med
    
    return None

def analyze_symptoms(symptoms, medicines_df):
    """Analyze symptoms using AI or keyword matching"""
    if USE_AI:
        return claude_triage(symptoms, medicines_df)
    else:
        return simple_triage(symptoms, medicines_df)

def authenticate_pharmacy(pharmacy_name, phone):
    """Authenticate pharmacy by name and phone number"""
    pharmacies_df = load_pharmacies()
    
    # Normalize inputs - strip whitespace
    pharmacy_name = pharmacy_name.strip() if pharmacy_name else ""
    phone = phone.strip() if phone else ""
    
    # Ensure Phone column is string type
    pharmacies_df['Phone'] = pharmacies_df['Phone'].astype(str)
    
    # Try exact match first
    match = pharmacies_df[
        (pharmacies_df['Pharmacy_Name'].str.strip().str.lower() == pharmacy_name.lower()) &
        (pharmacies_df['Phone'].str.strip() == phone)
    ]
    
    # If no exact match, try partial name matching (more flexible)
    if match.empty:
        match = pharmacies_df[
            (pharmacies_df['Pharmacy_Name'].str.strip().str.lower().str.contains(pharmacy_name.lower(), na=False)) &
            (pharmacies_df['Phone'].str.strip() == phone)
        ]
    
    if not match.empty:
        return match.iloc[0]
    return None

def update_pharmacy_stock(pharmacy_name, medicine_column, stock_status):
    """Update pharmacy stock status in CSV"""
    try:
        import os
        # Load fresh data (bypass cache for updates)
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'emergency_pharmacies.csv')
        pharmacies_df = pd.read_csv(csv_path)
        idx = pharmacies_df[pharmacies_df['Pharmacy_Name'] == pharmacy_name].index
        
        if len(idx) == 0:
            return False
        
        pharmacies_df.loc[idx[0], medicine_column] = 'Yes' if stock_status else 'No'
        pharmacies_df.loc[idx[0], 'Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        pharmacies_df.to_csv(csv_path, index=False)
        
        # Clear the cache so next load gets fresh data
        load_pharmacies.clear()
        return True
    except Exception as e:
        st.error(f"Error updating stock: {e}")
        return False

def voice_input_component():
    """Voice input component"""
    try:
        import os
        html_path = os.path.join(os.path.dirname(__file__), 'voice_input.html')
        with open(html_path, 'r') as f:
            html_content = f.read()
        
        voice_text = components.html(
            html_content,
            height=200,
        )
        
        return voice_text
    except Exception as e:
        st.warning(f"Voice input not available: {e}")
        return None

# ----------------- Chronic-care helpers -----------------

# For the demo, we focus on these chronic / long-term meds
CHRONIC_MEDS = [
    "Insulin Rapid-Acting",
    "Salbutamol Inhaler",
]

# Rough demo costs in RWF (purely illustrative for the pitch)
CHRONIC_COSTS = {
    "Insulin Rapid-Acting": 90000,
    "Salbutamol Inhaler": 15000,
}

# ----------------- Session state -----------------

if 'mode' not in st.session_state:
    st.session_state.mode = 'home'
if 'selected_medicine' not in st.session_state:
    st.session_state.selected_medicine = None
if 'voice_transcript' not in st.session_state:
    st.session_state.voice_transcript = ''
if 'last_symptoms' not in st.session_state:
    st.session_state.last_symptoms = ''
if 'pharmacy_authenticated' not in st.session_state:
    st.session_state.pharmacy_authenticated = False
if 'current_pharmacy' not in st.session_state:
    st.session_state.current_pharmacy = None

# Load data with error handling
try:
    medicines_df = load_medicines()
    pharmacies_df = load_pharmacies()
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# ============= HOME SCREEN =============
if st.session_state.mode == 'home':
    # Hero Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; background: linear-gradient(135deg, #DC143C 0%, #1976D2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🚨 FindMyMed Lifeline
            </h1>
            <p style="font-size: 1.2rem; color: #666; margin-top: 0;">Emergency Medicine Access + Chronic Care Management</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Emergency section with enhanced design
    st.markdown('<div class="emergency-header"><h1>⚡ EMERGENCY</h1><p>For immediate, life-threatening situations</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚨 I NEED HELP NOW", type="primary", use_container_width=True):
            st.session_state.mode = 'emergency'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Cards Section
    st.markdown("### 🎯 Quick Actions")
    feature_cols = st.columns(3)
    
    with feature_cols[0]:
        st.markdown("""
        <div class="feature-card">
            <h3 style="margin-top: 0;">📦 Chronic Care</h3>
            <p style="color: #666; margin-bottom: 1rem;">Manage your regular medications and plan refills</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📦 View My Meds", use_container_width=True, key="chronic_btn"):
            st.session_state.mode = 'chronic'
            st.rerun()
    
    with feature_cols[1]:
        st.markdown("""
        <div class="feature-card">
            <h3 style="margin-top: 0;">🔍 Search</h3>
            <p style="color: #666; margin-bottom: 1rem;">Find pharmacies with specific medicines in stock</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🔍 Search for Medicine")
        medicine_names = ["Select a medicine..."] + medicines_df['Medicine_Name'].tolist()
        selected = st.selectbox("", medicine_names, label_visibility="collapsed", key="home_search")
        
        if selected != "Select a medicine...":
            med_data = medicines_df[medicines_df['Medicine_Name'] == selected].iloc[0]
            st.session_state.selected_medicine = med_data
            st.session_state.mode = 'results'
            st.rerun()
    
    with feature_cols[2]:
        st.markdown("""
        <div class="feature-card">
            <h3 style="margin-top: 0;">🏥 Pharmacy</h3>
            <p style="color: #666; margin-bottom: 1rem;">Update stock status for your pharmacy</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏥 Pharmacy Login", use_container_width=True, key="pharmacy_btn"):
            st.session_state.mode = 'pharmacy_login'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Access Medicines
    st.markdown("### 💊 Quick Access Medicines")
    st.caption("Tap to find nearby pharmacies with these medicines")
    
    quick_meds = [
        ("💉", "Insulin", "Insulin Rapid-Acting", "#E3F2FD"),
        ("🫁", "Inhaler", "Salbutamol Inhaler", "#E8F5E9"),
        ("💊", "EpiPen", "EpiPen (Epinephrine Auto-Injector)", "#FFF3E0"),
        ("❤️", "Aspirin", "Aspirin 300mg", "#FCE4EC")
    ]
    
    cols = st.columns(4)
    for idx, (icon, label, med_name, color) in enumerate(quick_meds):
        with cols[idx]:
            st.markdown(f"""
            <div style="background: {color}; border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-weight: 600; color: #333;">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Find {label}", key=f"quick_{idx}", use_container_width=True):
                med_data = medicines_df[medicines_df['Medicine_Name'] == med_name].iloc[0]
                st.session_state.selected_medicine = med_data
                st.session_state.mode = 'results'
                st.rerun()

# ============= EMERGENCY MODE =============
elif st.session_state.mode == 'emergency':
    st.markdown('<div class="emergency-header"><h2>🚨 EMERGENCY MODE</h2></div>', unsafe_allow_html=True)
    
    st.warning("⚠️ **Disclaimer:** This tool provides routing assistance only. Always consult a healthcare provider. For life-threatening emergencies, call 912.")
    
    if st.button("← Back to Home"):
        st.session_state.mode = 'home'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎤 What's happening?")
    
    use_voice = st.checkbox("🎤 Use voice input", value=False)
    
    if use_voice:
        st.info("💡 Tap the microphone and describe your symptoms")
        voice_text = voice_input_component()
        
        if voice_text:
            st.session_state.voice_transcript = voice_text
        
        symptoms = st.text_area(
            "Or type your symptoms:",
            value=st.session_state.voice_transcript,
            placeholder="Voice input will appear here...",
            height=120,
            key="symptoms_with_voice"
        )
    else:
        st.info("💡 Describe your symptoms or what you're feeling")
        symptoms = st.text_area(
            "Type your symptoms:",
            placeholder="Examples:\n• 'Can't breathe, chest tight, wheezing'\n• 'Throat swelling, ate peanuts, hives'\n• 'Shaky, dizzy, diabetic, low sugar'",
            height=120,
            key="symptoms_text_only"
        )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        analyze_btn = st.button("🔍 Analyze & Find Help", type="primary", use_container_width=True)
    with col2:
        skip_btn = st.button("Skip", use_container_width=True)
    
    if analyze_btn:
        typed = (symptoms or "").strip()
        voice = (st.session_state.get("voice_transcript") or "").strip()
        final_symptoms = typed or voice
        
        st.session_state.last_symptoms = final_symptoms
        
        if not final_symptoms:
            st.warning("⚠️ Please describe your symptoms (by text or voice) before analyzing.")
        else:
            ai_label = "🤖 AI analyzing symptoms..." if USE_AI else "🔍 Analyzing symptoms..."
            with st.spinner(ai_label):
                matched_med = analyze_symptoms(final_symptoms, medicines_df)
            
            if matched_med is not None:
                detection_label = "✅ Detected:" if USE_AI else "✅ Detected:"
                st.success(f"{detection_label} **{matched_med['Condition']}**")
                st.session_state.selected_medicine = matched_med
                st.session_state.mode = 'emergency_results'
                st.rerun()
            else:
                # Store symptoms for display on manual screen
                st.session_state.last_symptoms = final_symptoms
                st.session_state.selected_medicine = None
                st.session_state.mode = 'emergency_manual'
                st.rerun()
    
    if skip_btn:
        st.session_state.mode = 'emergency_manual'
        st.rerun()

# ============= CHRONIC CARE MODE =============
elif st.session_state.mode == 'chronic':
    st.title("📦 My Meds & Refills")
    st.caption("Chronic medication management - never run out of life-saving medicines")
    
    if st.button("← Back to Home"):
        st.session_state.mode = 'home'
        st.rerun()
    
    st.markdown("---")
    st.info("💡 This feature helps people with diagnosed chronic conditions plan refills and manage costs.")
    
    st.write("**Select your medication:**")
    
    cols = st.columns(2)
    for idx, med_name in enumerate(CHRONIC_MEDS):
        match = medicines_df[medicines_df["Medicine_Name"] == med_name]
        if match.empty:
            continue
        med = match.iloc[0]
        col = cols[idx % 2]
        
        with col:
            st.markdown(f"#### {med['Medicine_Name']}")
            st.caption(f"**For:** {med['Condition']}")
            
            est_cost = CHRONIC_COSTS.get(med_name)
            if est_cost:
                st.write(f"💰 Typical 3-month supply: **{est_cost:,} RWF**")
            
            if st.button(f"Plan Refill →", key=f"refill_{idx}", use_container_width=True):
                st.session_state.selected_medicine = med
                st.session_state.mode = 'chronic_results'
                st.rerun()

# ============= EMERGENCY MANUAL SELECTION =============
elif st.session_state.mode == 'emergency_manual':
    st.markdown('<div class="emergency-header"><h2>🚨 Select Emergency Medicine</h2></div>', unsafe_allow_html=True)
    
    if st.button("← Back"):
        st.session_state.mode = 'emergency'
        st.session_state.last_symptoms = ""
        st.rerun()
    
    st.markdown("---")
    
    # Show explanation if we came here from failed analysis
    last_symptoms = st.session_state.get("last_symptoms", "").strip()
    if last_symptoms:
        st.warning("⚠️ We couldn't confidently match your symptoms to one of our emergency medicines.")
        st.info(
            f"**You described:** \"{last_symptoms}\"\n\n"
            "Our system couldn't find a safe, clear match. For your safety:\n"
            "- If this feels life-threatening, **call 912 immediately**\n"
            "- Otherwise, select the medicine you need below, or consult a pharmacist/doctor"
        )
        # Clear after showing
        st.session_state.last_symptoms = ""
    
    st.write("**Select the medicine you need:**")
    
    cols = st.columns(2)
    for idx, (_, med) in enumerate(medicines_df.iterrows()):
        col = cols[idx % 2]
        if col.button(med['Medicine_Name'], key=f"manual_{idx}", use_container_width=True):
            st.session_state.selected_medicine = med
            st.session_state.mode = 'emergency_results'
            st.rerun()

# ============= RESULTS SCREEN =============
elif st.session_state.mode in ['results', 'emergency_results', 'chronic_results']:
    is_emergency = (st.session_state.mode == 'emergency_results')
    is_chronic = (st.session_state.mode == 'chronic_results')
    med = st.session_state.get('selected_medicine')
    
    # Safety net: if somehow we got here without a medicine
    if med is None:
        st.warning("⚠️ We couldn't identify a specific medicine for your symptoms.")
        st.info(
            "Please go back and either:\n"
            "- Re-describe your symptoms more clearly\n"
            "- Select a medicine manually with help from a healthcare provider"
        )
        if st.button("← Back to Emergency Mode"):
            st.session_state.mode = 'emergency'
            st.rerun()
        st.stop()
    
    if is_emergency:
        st.markdown('<div class="emergency-header"><h2>⚡ EMERGENCY</h2></div>', unsafe_allow_html=True)
    elif is_chronic:
        st.markdown('<div class="pharmacy-header"><h2>📦 REFILL PLANNING</h2></div>', unsafe_allow_html=True)
    
    # Medicine header with gradient
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    ">
        <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">
            {'🚨' if is_emergency else '📦' if is_chronic else '🔍'} {med['Medicine_Name']}
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Time window warning
    if is_emergency:
        if med['Time_Window_Minutes'] <= 15:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #FF1744 0%, #DC143C 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(220, 20, 60, 0.3);
            ">
                <h3 style="margin: 0; color: white;">⏰ CRITICAL: {med['Time_Window_Minutes']} minute window</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Get help immediately!</p>
            </div>
            """, unsafe_allow_html=True)
        elif med['Time_Window_Minutes'] <= 60:
            st.markdown(f"""
            <div class="urgent-warning">
                <h3 style="margin: 0; color: #FF6F00;">⚠️ Time-sensitive: {med['Time_Window_Minutes']} minute window</h3>
            </div>
            """, unsafe_allow_html=True)
    
    # Medicine info card
    st.markdown(f"""
    <div class="feature-card">
        <h3 style="margin-top: 0; color: #1976D2;">📋 Medicine Information</h3>
        <p style="font-size: 1.1rem; margin: 0.5rem 0;"><strong>Condition:</strong> {med['Condition']}</p>
        <p style="color: #666; margin: 0.5rem 0;">{med['Description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back"):
        st.session_state.mode = 'chronic' if is_chronic else 'home'
        st.rerun()
    
    st.markdown("---")
    
    user_location = (-1.9536, 30.0606)
    
    with st.spinner("🔍 Finding pharmacies..."):
        available_pharmacies = search_pharmacies(med['Medicine_Name'], pharmacies_df, user_location)
    
    if len(available_pharmacies) > 0:
        st.success(f"✅ **{len(available_pharmacies)} pharmacies** in our network have this medicine")
        
        for idx, (_, pharmacy) in enumerate(available_pharmacies.head(5).iterrows()):
            # Enhanced pharmacy card
            distance_text = f"<div style='font-size: 1.1rem; color: #1976D2; font-weight: 600; margin: 0.5rem 0;'>🚶 {pharmacy['distance_km']:.1f} km away</div>" if 'distance_km' in pharmacy else ""
            
            st.markdown(f"""
            <div class="pharmacy-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0; color: #1a1a1a; font-size: 1.5rem;">{idx + 1}. {pharmacy['Pharmacy_Name']}</h3>
                        {distance_text}
                    </div>
                    <div class="in-stock">✓ In Stock</div>
                </div>
                <div style="color: #666; margin: 1rem 0;">
                    <p style="margin: 0.5rem 0;"><strong>📍</strong> {pharmacy['Address']}</p>
                    <p style="margin: 0.5rem 0;"><strong>📞</strong> {pharmacy['Phone']}</p>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #999;">Last updated: {pharmacy['Last_Updated']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col_call, col_map = st.columns(2)
            with col_call:
                st.markdown(f"""
                <a href="tel:{pharmacy['Phone']}" style="
                    display: block;
                    text-align: center;
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white;
                    padding: 0.75rem;
                    border-radius: 12px;
                    text-decoration: none;
                    font-weight: 600;
                    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
                    transition: all 0.3s ease;
                ">📞 Call Now</a>
                """, unsafe_allow_html=True)
            with col_map:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={pharmacy['Latitude']},{pharmacy['Longitude']}"
                st.markdown(f"""
                <a href="{maps_url}" target="_blank" style="
                    display: block;
                    text-align: center;
                    background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
                    color: white;
                    padding: 0.75rem;
                    border-radius: 12px;
                    text-decoration: none;
                    font-weight: 600;
                    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
                    transition: all 0.3s ease;
                ">📍 Navigate</a>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        if is_emergency:
            st.markdown("### 🚁 Alternative Options")
            st.info("**SafeBoda / Zipline Delivery** (Planned Partnership)\n\n• For urgent but non-immediate cases\n• 15-30 minute delivery\n\n*Integration planned in Phase 2*")
            st.error("🚑 **Life-threatening emergency? Call 912 immediately.**")
        
        if is_chronic:
            st.markdown("### 💳 Payment & Refill Options")
            st.caption("📋 **Prescription required** - bring to pharmacy or upload via app (Phase 2)")
            
            est_cost = CHRONIC_COSTS.get(med['Medicine_Name'])
            if est_cost:
                st.write(f"**3-month supply cost:** {est_cost:,} RWF")
                
                col_now, col_bnpl, col_sub = st.columns(3)
                with col_now:
                    st.markdown("**💵 Pay Now**")
                    st.caption("Full payment at pharmacy")
                    st.caption("(Cash, MoMo, Insurance)")
                
                with col_bnpl:
                    st.markdown("**💳 Pay Later**")
                    st.caption(f"3 × {est_cost//3:,} RWF/month")
                    st.caption("Small service fee")
                    st.caption("*(Concept - Phase 2)*")
                
                with col_sub:
                    st.markdown("**📅 Subscribe**")
                    st.caption("5,000 RWF/month")
                    st.caption("Auto-refill delivery")
                    st.caption("*(Concept - Phase 2)*")
            
            st.markdown("---")
            st.success("💡 **How it works:** Present prescription → Choose payment → Pharmacy dispenses → You stay stocked!")
    
    else:
        st.error(f"😟 We identified **{med['Medicine_Name']}** for **{med['Condition']}**, but no pharmacies in our network show it in stock.")
        
        last_symptoms = (st.session_state.get('last_symptoms') or '').strip()
        if last_symptoms:
            st.caption(f"_Based on your symptoms: \"{last_symptoms}\"_")
        
        if is_emergency:
            st.error("🚑 **Call Emergency Services: 912** or go to nearest hospital immediately.")
            st.info("💡 Show this screen to a pharmacist/doctor so they know what you need.")

# ============= PHARMACY LOGIN =============
elif st.session_state.mode == 'pharmacy_login':
    st.title("🏥 Pharmacy Portal")
    st.caption("Update your stock status to help patients find medicines")
    
    if st.button("← Back to Home"):
        st.session_state.mode = 'home'
        st.session_state.pharmacy_authenticated = False
        st.session_state.current_pharmacy = None
        st.rerun()
    
    st.markdown("---")
    
    if not st.session_state.pharmacy_authenticated:
        st.info("💡 Select your pharmacy from the list below, or enter manually")
        
        # Create dropdown with pharmacy options
        pharmacy_options = ["Select a pharmacy..."] + [
            f"{row['Pharmacy_Name']} ({row['Phone']})" 
            for _, row in pharmacies_df.iterrows()
        ]
        
        selected_option = st.selectbox("Select Pharmacy", pharmacy_options)
        
        if selected_option != "Select a pharmacy...":
            # Parse the selected option
            parts = selected_option.rsplit(" (", 1)
            if len(parts) == 2:
                auto_name = parts[0]
            else:
                auto_name = ""
        else:
            auto_name = ""
        
        st.markdown("**Or enter manually:**")
        col1, col2 = st.columns(2)
        with col1:
            pharmacy_name = st.text_input("Pharmacy Name", value=auto_name, placeholder="e.g., Pharmacie de la Paix - Kimironko")
        with col2:
            phone = st.text_input("Phone Number", placeholder="e.g., +250788123456")
        
        if st.button("🔐 Login", type="primary", use_container_width=True):
            if pharmacy_name and phone:
                pharmacy = authenticate_pharmacy(pharmacy_name, phone)
                if pharmacy is not None:
                    st.session_state.pharmacy_authenticated = True
                    st.session_state.current_pharmacy = pharmacy
                    st.session_state.mode = 'pharmacy_dashboard'
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Pharmacy not found. Please check your name and phone number.")
                    st.info("💡 **Tip:** Use the dropdown above to select your pharmacy automatically, or make sure the name and phone match exactly.")
            else:
                st.warning("⚠️ Please enter both pharmacy name and phone number.")
    else:
        st.session_state.mode = 'pharmacy_dashboard'
        st.rerun()

# ============= PHARMACY DASHBOARD =============
elif st.session_state.mode == 'pharmacy_dashboard':
    if not st.session_state.pharmacy_authenticated or st.session_state.current_pharmacy is None:
        st.error("❌ Please log in first")
        st.session_state.mode = 'pharmacy_login'
        st.rerun()
    
    pharmacy = st.session_state.current_pharmacy
    
    st.markdown(f'<div class="pharmacy-header"><h2>🏥 {pharmacy["Pharmacy_Name"]}</h2><p>Stock Management Dashboard</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"📍 {pharmacy['Address']}")
        st.write(f"📞 {pharmacy['Phone']}")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.pharmacy_authenticated = False
            st.session_state.current_pharmacy = None
            st.session_state.mode = 'home'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Info banner
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #1976D2;
    ">
        <p style="margin: 0; font-weight: 600; color: #1976D2;">💡 Toggle medicines in/out of stock. Changes are saved immediately.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📦 Update Stock Status")
    
    # Get all medicine columns (exclude non-medicine columns)
    medicine_columns = [col for col in pharmacies_df.columns 
                       if col not in ['Pharmacy_Name', 'Address', 'Phone', 'Latitude', 'Longitude', 'Last_Updated']]
    
    # Create a grid layout for medicines
    num_cols = 2
    cols = st.columns(num_cols)
    
    changes_made = False
    
    for idx, med_col in enumerate(medicine_columns):
        col = cols[idx % num_cols]
        
        # Get medicine name from column (convert back from column format)
        med_name = med_col.replace('_', ' ')
        
        # Find matching medicine in medicines_df
        med_info = None
        for _, med_row in medicines_df.iterrows():
            col_name = get_medicine_column_name(med_row['Medicine_Name'])
            if col_name.lower() in med_col.lower():
                med_info = med_row
                med_name = med_row['Medicine_Name']
                break
        
        current_status = pharmacy[med_col] == 'Yes'
        
        with col:
            # Enhanced medicine card
            bg_color = "#E8F5E9" if current_status else "#FFEBEE"
            border_color = "#4CAF50" if current_status else "#F44336"
            status_badge = '<span class="in-stock">✓ In Stock</span>' if current_status else '<span class="stock-out">✗ Out of Stock</span>'
            
            st.markdown(f"""
            <div class="feature-card" style="border-left: 4px solid {border_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; color: #1a1a1a;">{med_name}</h4>
                    {status_badge}
                </div>
                {f'<p style="color: #666; margin: 0.5rem 0; font-size: 0.9rem;"><em>For: {med_info["Condition"]}</em></p>' if med_info is not None else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Toggle button
            new_status = st.toggle(
                "Toggle Stock Status",
                value=current_status,
                key=f"stock_{med_col}_{pharmacy['Pharmacy_Name']}"
            )
            
            if new_status != current_status:
                if update_pharmacy_stock(pharmacy['Pharmacy_Name'], med_col, new_status):
                    # Update session state pharmacy data
                    pharmacy[med_col] = 'Yes' if new_status else 'No'
                    pharmacy['Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                    st.session_state.current_pharmacy = pharmacy
                    changes_made = True
                    st.success(f"✅ {med_name} updated to {'In Stock' if new_status else 'Out of Stock'}")
                else:
                    st.error(f"❌ Failed to update {med_name}")
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    if changes_made:
        # Reload pharmacies to get updated data
        pharmacies_df = load_pharmacies()
        updated_pharmacy = pharmacies_df[pharmacies_df['Pharmacy_Name'] == pharmacy['Pharmacy_Name']].iloc[0]
        st.session_state.current_pharmacy = updated_pharmacy
    
    st.markdown("---")
    st.markdown("### 📊 Quick Actions")
    
    col_bulk1, col_bulk2 = st.columns(2)
    with col_bulk1:
        if st.button("✅ Mark All In Stock", use_container_width=True):
            for med_col in medicine_columns:
                update_pharmacy_stock(pharmacy['Pharmacy_Name'], med_col, True)
            pharmacies_df = load_pharmacies()
            updated_pharmacy = pharmacies_df[pharmacies_df['Pharmacy_Name'] == pharmacy['Pharmacy_Name']].iloc[0]
            st.session_state.current_pharmacy = updated_pharmacy
            st.success("✅ All medicines marked as in stock")
            st.rerun()
    
    with col_bulk2:
        if st.button("❌ Mark All Out of Stock", use_container_width=True):
            for med_col in medicine_columns:
                update_pharmacy_stock(pharmacy['Pharmacy_Name'], med_col, False)
            pharmacies_df = load_pharmacies()
            updated_pharmacy = pharmacies_df[pharmacies_df['Pharmacy_Name'] == pharmacy['Pharmacy_Name']].iloc[0]
            st.session_state.current_pharmacy = updated_pharmacy
            st.success("✅ All medicines marked as out of stock")
            st.rerun()
    
    st.markdown("---")
    last_updated = pharmacy.get('Last_Updated', 'Unknown')
    st.caption(f"Last updated: {last_updated}")

# Footer
st.markdown("---")
st.caption("FindMyMed Lifeline • Emergency Medicine Access + Chronic Care Management • CMU Africa 2026")