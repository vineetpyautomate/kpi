import streamlit as st
import pandas as pd

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Vision-Audit Pro",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PROFESSIONAL STYLING (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    h1 { color: #1e3a8a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_value=True)

# --- 3. SIDEBAR / UPLOAD CENTER ---
with st.sidebar:
    st.title("📂 Control Panel")
    st.markdown("---")
    master_file = st.file_uploader("1️⃣ Upload Master Dump", type=['xlsx'])
    system_file = st.file_uploader("2️⃣ Upload System Dump", type=['xlsx'])
    st.markdown("---")
    st.info("💡 **Tip:** System Dump sheets will be merged automatically.")

# --- 4. MAIN APP DISPLAY ---
st.title("📊 VISION-AUDIT PRO")
st.caption("Technical Management Dashboard | Telecommunications Audit Engine")

if not master_file or not system_file:
    # Beautiful Landing Page if no files are uploaded
    st.info("### 👋 Welcome, Technical Manager")
    st.write("Please upload your Excel files in the sidebar to begin the automated audit.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🎯 Precise")
        st.write("Binary Match/No-Match logic ensures zero ambiguity in results.")
    with col2:
        st.subheader("🔄 Automated")
        st.write("Automatically merges multiple system sheets into one master view.")
    with col3:
        st.subheader("📱 Responsive")
        st.write("Access your audit results from any device via this Render link.")

else:
    try:
        # --- 5. DATA PROCESSING ENGINE ---
        # Load Master
        df_master = pd.read_excel(master_file)
        
        # Load System (Merge all sheets)
        system_dict = pd.read_excel(system_file, sheet_name=None)
        df_system = pd.concat(system_dict.values(), ignore_index=True)

        # Cleaning: Remove hidden spaces from column names
        df_master.columns = df_master.columns.str.strip()
        df_system.columns = df_system.columns.str.strip()

        # --- 6. EXECUTIVE SUMMARY METRICS ---
        st.success("✅ Files successfully processed!")
        m1, m2, m3 = st.columns(3)
        m1.metric("Master Records", len(df_master))
        m2.metric("System Records", len(df_system))
        m3.metric("Status", "Ready for Audit")

        # --- 7. MAPPING & AUDIT SECTION ---
        st.markdown("---")
        st.subheader("⚙️ Audit Configuration")
        
        c1, c2 = st.columns(2)
        with c1:
            master_key = st.selectbox("Select ID Column (Master)", df_master.columns)
        with c2:
            system_key = st.selectbox("Select ID Column (System)", df_system.columns)

        if st.button("🚀 RUN PROFESSIONAL AUDIT"):
            # The "Clap-Worthy" Logic: Outer Join
            merged = pd.merge(
                df_master, 
                df_system, 
                left_on=master_key, 
                right_on=system_key, 
                how='outer', 
                indicator=True
            )

            # Categorize
            verified = merged[merged['_merge'] == 'both']
            missing_in_sys = merged[merged['_merge'] == 'left_only']
            ghost_entries = merged[merged['_merge'] == 'right_only']

            # Results Display
            st.subheader("📋 Audit Results")
            res1, res2, res3 = st.columns(3)
            res1.metric("Verified Matches", len(verified))
            res2.error(f"Missing in System: {len(missing_in_sys)}")
            res3.warning(f"Unrecognized (Ghost): {len(ghost_entries)}")

            tab1, tab2, tab3 = st.tabs(["✅ Verified", "❌ Missing in System", "⚠️ Ghost Entries"])
            
            with tab1:
                st.dataframe(verified, use_container_width=True)
            with tab2:
                st.dataframe(missing_in_sys, use_container_width=True)
            with tab3:
                st.dataframe(ghost_entries, use_container_width=True)

    except Exception as e:
        st.error(f"Critical Error: {e}")