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

# Custom CSS for styling
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }
    .emergency-header {
        background-color: #DC143C;
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        margin: 10px 0;
    }
    .pharmacy-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .in-stock {
        color: #2E7D32;
        font-weight: bold;
    }
    .urgent-warning {
        background-color: #FFF3E0;
        border-left: 4px solid #FF6F00;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data functions
@st.cache_data
def load_medicines():
    return pd.read_csv('data/emergency_medicines.csv')

@st.cache_data
def load_pharmacies():
    return pd.read_csv('data/emergency_pharmacies.csv')

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

def voice_input_component():
    """Voice input component"""
    with open('voice_input.html', 'r') as f:
        html_content = f.read()
    
    voice_text = components.html(
        html_content,
        height=200,
    )
    
    return voice_text

# ----------------- Chronic-care helpers -----------------

CHRONIC_MEDS = [
    "Insulin Rapid-Acting",
    "Salbutamol Inhaler",
]

CHRONIC_COSTS = {
    "Insulin Rapid-Acting": 90000,
    "Salbutamol Inhaler": 15000,
}

# Approximate Kigali locations for distance estimates
# (purely for demo – in production we'd use the phone's GPS)
LOCATION_OPTIONS = {
    "CMU Africa campus (Kigali PEZ)": (-1.9354, 30.1586),
    "Kigali City Center (UTC area)": (-1.9441, 30.0619),
    "Kimironko (Market area)": (-1.9391, 30.1123),
    "Nyamirambo": (-1.9530, 30.0440),
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
if 'user_location_label' not in st.session_state:
    # Default to CMU Africa for the demo
    st.session_state.user_location_label = "CMU Africa campus(kigali PEZ)"

# Load data
medicines_df = load_medicines()
pharmacies_df = load_pharmacies()

# ============= HOME SCREEN =============
if st.session_state.mode == 'home':
    st.title("🚨 FindMyMed Lifeline")
    st.caption("Emergency Medicine Access + Chronic Care Management")
    st.markdown("---")
    
    # Emergency section
    st.markdown('<div class="emergency-header"><h1>⚡ EMERGENCY</h1><p>For immediate, life-threatening situations</p></div>', unsafe_allow_html=True)
    
    if st.button("🚨 I NEED HELP NOW", type="primary", use_container_width=True):
        st.session_state.mode = 'emergency'
        st.rerun()
    
    st.markdown("---")
    
    # Chronic care section
    st.markdown("### 📦 My Meds & Refills")
    st.caption("For people with chronic conditions (diabetes, asthma, allergies) who need regular medication")
    
    if st.button("📦 View My Meds & Plan Refills", use_container_width=True):
        st.session_state.mode = 'chronic'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔍 Search for Medicine")
    
    st.write("**Quick Access:**")
    cols = st.columns(2)
    quick_meds = [
        ("💉 Insulin", "Insulin Rapid-Acting"),
        ("🫁 Inhaler", "Salbutamol Inhaler"),
        ("💊 EpiPen", "EpiPen (Epinephrine Auto-Injector)"),
        ("❤️ Aspirin", "Aspirin 300mg")
    ]
    
    for idx, (label, med_name) in enumerate(quick_meds):
        col = cols[idx % 2]
        if col.button(label, use_container_width=True, key=f"quick_{idx}"):
            med_data = medicines_df[medicines_df['Medicine_Name'] == med_name].iloc[0]
            st.session_state.selected_medicine = med_data
            st.session_state.mode = 'results'
            st.rerun()
    
    st.write("**Or search by name:**")
    medicine_names = ["Select a medicine..."] + medicines_df['Medicine_Name'].tolist()
    selected = st.selectbox("", medicine_names, label_visibility="collapsed")
    
    if selected != "Select a medicine...":
        med_data = medicines_df[medicines_df['Medicine_Name'] == selected].iloc[0]
        st.session_state.selected_medicine = med_data
        st.session_state.mode = 'results'
        st.rerun()

    st.markdown("---")
    st.markdown("### 🏥 Partner Pharmacies")
    st.caption("Pharmacies can join our network and share emergency-stock updates instead of doing double data entry.")
    if st.button("🏥 I'm a pharmacy – Join the network", use_container_width=True):
        st.session_state.mode = 'pharmacy_partners'
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

# ============= PHARMACY PARTNER FORM =============
elif st.session_state.mode == 'pharmacy_partners':
    st.title("🏥 Partner Pharmacy Registration")
    st.caption("Join our network so patients and ambulances can find your emergency stock faster.")
    
    if st.button("← Back to Home"):
        st.session_state.mode = 'home'
        st.rerun()
    
    st.markdown("---")
    st.info(
        "In the MVP, pharmacy stock is loaded from CSV. This screen shows how, in reality, "
        "a pharmacy would register and share stock updates (or we would integrate directly "
        "with platforms like **Ishyiga** so they don't do double work)."
    )
    
    with st.form("pharmacy_partner_form"):
        name = st.text_input("Pharmacy name *", placeholder="e.g., Pharmacie du Peuple")
        address = st.text_input("Location / address *", placeholder="e.g., KN 4 Ave near UTC")
        phone = st.text_input("Phone number *", placeholder="+2507...")
        email = st.text_input("Email address", placeholder="contact@pharmacy.rw")
        hours = st.text_input("Operating hours", placeholder="Mon–Sat 8:00–20:00, Sun 9:00–17:00")
        
        st.markdown("**Which emergency medicines do you usually stock?**")
        emergency_meds = st.multiselect(
            "Select all that apply",
            medicines_df["Medicine_Name"].tolist(),
            default=[],
        )
        
        update_freq = st.selectbox(
            "How often can you update this information?",
            ["Daily", "Twice per week", "Weekly", "Other"],
        )
        notes = st.text_area(
            "Anything else we should know? (optional)",
            placeholder="e.g. We already use Ishyiga; API integration preferred.",
            height=80,
        )
        
        submitted = st.form_submit_button("Submit partnership request")
    
    if submitted:
        st.success("✅ Thank you! For the demo, this form does not send data anywhere.")
        st.info(
            "In a production system, this information would create a **pharmacy profile**, "
            "and stock updates would be pulled automatically from the pharmacy's existing "
            "system (Ishyiga / POS) or via a simple dashboard like this."
        )

# ============= EMERGENCY MANUAL SELECTION =============
elif st.session_state.mode == 'emergency_manual':
    st.markdown('<div class="emergency-header"><h2>🚨 Select Emergency Medicine</h2></div>', unsafe_allow_html=True)
    
    if st.button("← Back"):
        st.session_state.mode = 'emergency'
        st.session_state.last_symptoms = ""
        st.rerun()
    
    st.markdown("---")
    
    last_symptoms = st.session_state.get("last_symptoms", "").strip()
    if last_symptoms:
        st.warning("⚠️ We couldn't confidently match your symptoms to one of our emergency medicines.")
        st.info(
            f"**You described:** \"{last_symptoms}\"\n\n"
            "Our system couldn't find a safe, clear match. For your safety:\n"
            "- If this feels life-threatening, **call 912 immediately**\n"
            "- Otherwise, select the medicine you need below, or consult a pharmacist/doctor"
        )
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
        st.markdown('<div class="emergency-header" style="background-color: #1976D2;"><h2>📦 REFILL PLANNING</h2></div>', unsafe_allow_html=True)
    
    st.title(f"{'🚨' if is_emergency else '📦' if is_chronic else '🔍'} {med['Medicine_Name']}")
    
    if is_emergency:
        if med['Time_Window_Minutes'] <= 15:
            st.error(f"⏰ **CRITICAL: {med['Time_Window_Minutes']} minute window** - Get help immediately!")
        elif med['Time_Window_Minutes'] <= 60:
            st.warning(f"⚠️ **Time-sensitive: {med['Time_Window_Minutes']} minute window**")
    
    st.info(f"**Condition:** {med['Condition']}")
    st.caption(med['Description'])
    
    if st.button("← Back"):
        st.session_state.mode = 'chronic' if is_chronic else 'home'
        st.rerun()
    
    st.markdown("---")

    # Location selection for distance estimates
    st.subheader("📍 Where are you right now? (for distance estimates)")
    loc_keys = list(LOCATION_OPTIONS.keys())
    default_index = loc_keys.index(st.session_state.user_location_label) if st.session_state.user_location_label in loc_keys else 0
    selected_loc_label = st.selectbox(
        "Approximate your location in Kigali:",
        loc_keys,
        index=default_index,
    )
    st.session_state.user_location_label = selected_loc_label
    user_location = LOCATION_OPTIONS[selected_loc_label]
    st.caption(
        "Distances below are estimated from the area you selected (e.g. CMU Africa, Kimironko, Nyamirambo). "
        "In a full product we'd use your phone's GPS to calculate exact distance in real time."
    )
    
    st.markdown("---")
    
    with st.spinner("🔍 Finding pharmacies..."):
        available_pharmacies = search_pharmacies(med['Medicine_Name'], pharmacies_df, user_location)
    
    if len(available_pharmacies) > 0:
        total_pharmacies = len(available_pharmacies)
        display_limit = 5
        displayed_pharmacies = available_pharmacies.head(display_limit)
        
        if total_pharmacies > display_limit:
            st.success(
                f"✅ **{total_pharmacies} pharmacies** in our network have this medicine. "
                f"Showing the **{display_limit} closest** first."
            )
        else:
            st.success(f"✅ **{total_pharmacies} pharmacies** in our network have this medicine.")
        
        if 'distance_km' in available_pharmacies.columns:
            st.caption(f"📏 Sorted by distance from **{st.session_state.user_location_label}**.")
        
        for idx, (_, pharmacy) in enumerate(displayed_pharmacies.iterrows()):
            st.markdown(f"### {idx + 1}. {pharmacy['Pharmacy_Name']}")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"📍 {pharmacy['Address']}")
                st.write(f"📞 {pharmacy['Phone']}")
                if 'distance_km' in pharmacy:
                    st.write(f"🚶 **{pharmacy['distance_km']:.1f} km** away")
            
            with col2:
                st.markdown("<div class='in-stock'>✓ In Stock</div>", unsafe_allow_html=True)
                st.caption(f"Updated: {pharmacy['Last_Updated']}")
            
            col_call, col_map = st.columns(2)
            with col_call:
                st.markdown(f"[📞 Call Now](tel:{pharmacy['Phone']})")
            with col_map:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={pharmacy['Latitude']},{pharmacy['Longitude']}"
                st.markdown(f"[📍 Navigate]({maps_url})")
            
            st.markdown("---")
        
        if is_emergency:
            st.markdown("### 🚁 Alternative Options")
            st.info(
                "**SafeBoda / Zipline Delivery** (Planned Partnership)\n\n"
                "• For urgent but non-immediate cases\n"
                "• 15-30 minute delivery\n\n"
                "*Integration planned in Phase 2*"
            )
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

            # Quick refill request (demo only)
            st.markdown("### 📝 Quick Refill Request (Demo)")
            st.caption("This flow is for the demo – it shows how a refill order would look once prescriptions are verified.")

            pharmacy_names = displayed_pharmacies["Pharmacy_Name"].tolist()
            if not pharmacy_names:
                pharmacy_names = available_pharmacies["Pharmacy_Name"].tolist()

            with st.form("refill_request_form"):
                chosen_pharmacy = st.selectbox(
                    "Choose pharmacy to fulfill your refill:",
                    pharmacy_names,
                )
                quantity = st.selectbox("How many packs do you need?", [1, 2, 3, 4], index=0)
                delivery_option = st.radio(
                    "Delivery option:",
                    ["Pick up at pharmacy", "Home delivery (SafeBoda / Zipline – Phase 2)"],
                )
                phone = st.text_input("Your phone number (for confirmation SMS)", placeholder="+2507...")
                extra_notes = st.text_area(
                    "Notes for pharmacist (e.g., existing prescription, insurance)", height=80
                )
                submit_refill = st.form_submit_button("Submit refill request (demo)")

            if submit_refill:
                st.success(
                    "✅ Refill request captured for demo purposes.\n\n"
                    f"- Medicine: **{med['Medicine_Name']}**\n"
                    f"- Pharmacy: **{chosen_pharmacy}**\n"
                    f"- Quantity: **{quantity}**\n"
                    f"- Delivery: **{delivery_option}**\n\n"
                    "In production, this would be sent securely to the pharmacy after your prescription is verified."
                )
    
    else:
        st.error(f"😟 We identified **{med['Medicine_Name']}** for **{med['Condition']}**, but no pharmacies in our network show it in stock.")
        
        last_symptoms = (st.session_state.get('last_symptoms') or '').strip()
        if last_symptoms:
            st.caption(f"_Based on your symptoms: \"{last_symptoms}\"_")
        
        if is_emergency:
            st.error("🚑 **Call Emergency Services: 912** or go to nearest hospital immediately.")
            st.info("💡 Show this screen to a pharmacist/doctor so they know what you need.")

# Footer
st.markdown("---")
st.caption("FindMyMed Lifeline • Emergency Medicine Access + Chronic Care Management • CMU Africa 2026")
