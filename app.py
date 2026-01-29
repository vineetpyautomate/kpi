import streamlit as st
import pandas as pd
import io

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Vision-Audit Pro",
    page_icon="📡",
    layout="wide"
)

# --- 2. PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    /* Global Font scaling */
    html, body, [class*="css"] {
        font-size: 1.0rem; /* Standard base size */
        font-family: 'Inter', sans-serif;
    }
    
    /* Dynamic Headers */
    h1 { font-size: 2.5vw !important; color: #1e3a8a; min-size: 24px; }
    h2 { font-size: 1.8vw !important; color: #1e3a8a; min-size: 20px; }
    h3 { font-size: 1.4vw !important; color: #1e3a8a; min-size: 18px; }

    /* Dynamic Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.0vw !important; 
        color: #1e3a8a;
        min-width: 100px;
    }
    
    /* Tables and Sidebar */
    .stDataFrame { font-size: 0.9rem !important; }
    .stSidebar { background-color: #f1f5f9; }
    
    /* Metric container styling */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 1vw;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. TITLE & SIDEBAR ---
st.title("📊 Vineet-Audit PRO")
st.caption("Technical Management Dashboard | Exception-Based Audit Engine")

with st.sidebar:
    st.header("📁 Data Upload")
    master_file = st.file_uploader("Upload CIQ Excel", type=['xlsx'])
    system_file = st.file_uploader("Upload Site Dump (Multi-sheet)", type=['xlsx'])
    st.divider()
    st.info("Upload both files to activate the Audit Modules.")

# --- 4. MAIN LOGIC GATE ---
if master_file and system_file:
    try:
        # Load Data
        df_master = pd.read_excel(master_file)
        system_dict = pd.read_excel(system_file, sheet_name=None)
        df_system = pd.concat(system_dict.values(), ignore_index=True)
        
        st.success("✅ Files Linked Successfully")

        # ---------------------------------------------------------
        # MODULE 1: ROUTER cellid INTEGRITY
        # ---------------------------------------------------------
        st.markdown("---")
        st.header("🛰️ Module 1: Managed_Element Audit")
        
        if st.button("🚀 Run Managed_Element Check"):
            master_set = set(df_master['MANAGED_ELEMENT_ID'].astype(str).str.strip().str.upper().unique())
            dump_set = set(df_system['NodeID'].astype(str).str.strip().str.upper().unique())
            
            missing = master_set - dump_set
            unauthorized = dump_set - master_set

            if not missing and not unauthorized:
                st.success(f"### ✅ STATUS: OK (All {len(master_set)} Managed_Element Correct)")
            else:
                st.error(f"### 🚨 STATUS: DISCREPANCY FOUND")
                # (Same exception table logic as before...)
                exception_data = []
                for m_id in missing: exception_data.append({"cellid": m_id, "Result": "❌ MISSING IN DUMP"})
                for u_id in unauthorized: exception_data.append({"cellid": u_id, "Result": "🚩 UNAUTHORIZED"})
                st.dataframe(pd.DataFrame(exception_data), use_container_width=True)

        # ---------------------------------------------------------
        # MODULE 2: HOSTNAME/ALIAS COMPARISON (New Logic)
        # ---------------------------------------------------------
        st.markdown("---")
        st.header("🏷️ Module 2: Cell Name Audit")
        st.write("Comparing **CellName (CIQ)** vs **EUtranCellFDD (Site Dump)**.")

        if st.button("🚀 RUN CELL-NAME COMPARISON"):
            # A. Clean and Split Master Names
            # We use .split(';').str[0] to get only 'xxxx_xxxx_x'
            df_master['CLEAN_ALIAS'] = df_master['ALIAS_NAME'].astype(str).str.split(';').str[0].str.strip().str.upper()
            df_system['CLEAN_ROUTER_NAME'] = df_system['EUtranCellFDD'].astype(str).str.strip().str.upper()

            # B. Get Sets for Comparison
            master_names = set(df_master['CLEAN_ALIAS'].unique())
            dump_names = set(df_system['CLEAN_ROUTER_NAME'].unique())

            name_missing = master_names - dump_names
            name_unauthorized = dump_names - master_names

            # C. Results UI
            if not name_missing and not name_unauthorized:
                st.balloons()
                st.success(f"### ✅ CELL-NAME MATCH (Checked {len(master_names)} unique names)")
            else:
                st.warning("⚠️ Hostname Discrepancies Detected")
                
                col_a, col_b = st.columns(2)
                col_a.metric("Missing in Dump", len(name_missing))
                col_b.metric("Extra in Dump", len(name_unauthorized))

                # Create Table for Exceptions
                name_exceptions = []
                for n in name_missing: name_exceptions.append({"Name": n, "Category": "❌ Missing in System"})
                for u in name_unauthorized: name_exceptions.append({"Name": u, "Category": "🚩 Extra/Unauthorized Name"})
                
                df_name_ex = pd.DataFrame(name_exceptions)
                st.dataframe(df_name_ex, use_container_width=True)
        
        # ---------------------------------------------------------
        # MODULE 3: FULL NAME & CELL_ID INTEGRITY
        # ---------------------------------------------------------
        st.markdown("---")
        st.header("🔗 Module 3: CellName & Cell ID Audit")
        st.write("Comparing **CellName (CIQ)** vs **EUtranCellFDD (Site Dump)** and **CELL_ID** vs **cellid**.")

        if st.button("🚀 RUN FULL AUDIT"):
            # A. Prepare Master Data (Anchor = Name before ;)
            master_prep = df_master.copy()
            master_prep['Lookup_Name'] = master_prep['ALIAS_NAME'].astype(str).str.split(';').str[0].str.strip().str.upper()
            master_prep['MASTER_CELL_ID'] = master_prep['CELL_ID'].astype(str).str.strip().str.upper()
            
            # B. Prepare Dump Data
            dump_prep = df_system.copy()
            dump_prep['Dump_Name'] = dump_prep['EUtranCellFDD'].astype(str).str.strip().str.upper()
            dump_prep['DUMP_CELL_ID'] = dump_prep['cellid'].astype(str).str.strip().str.upper()

            # C. LEFT JOIN: Ensuring every Master record is checked
            
            comparison = pd.merge(
                master_prep[['Lookup_Name', 'MASTER_CELL_ID']].drop_duplicates(),
                dump_prep[['Dump_Name', 'DUMP_CELL_ID']].drop_duplicates(),
                left_on='Lookup_Name',
                right_on='Dump_Name',
                how='left'
            )

            # D. The "Red Flag" Logic
            def identify_discrepancy(row):
                if pd.isna(row['Dump_Name']):
                    return "🚩 NAME DISCREPANCY (Not in Dump)"
                if row['MASTER_CELL_ID'] != row['DUMP_CELL_ID']:
                    return "🛑 CELL_ID MISMATCH"
                return "✅ OK"

            comparison['Audit_Status'] = comparison.apply(identify_discrepancy, axis=1)
            
            # E. Filtering Exceptions
            exceptions = comparison[comparison['Audit_Status'] != "✅ OK"]

            # F. UI RESULTS
            if exceptions.empty:
                st.balloons()
                st.success(f"### ✅ CellName and CellID are correct")
                st.info(f"Checked {len(comparison)} unique CellName. All CellNames and Cell IDs are 100% accurate.")
            else:
                st.error(f"### 🚨 {len(exceptions)} DISCREPANCIES FOUND")
                
                # Metrics for quick overview
                m1, m2 = st.columns(2)
                name_err = len(exceptions[exceptions['Audit_Status'].str.contains("NAME")])
                cell_err = len(exceptions[exceptions['Audit_Status'].str.contains("CELL")])
                m1.metric("Name Discrepancies", name_err)
                m2.metric("Cell ID Mismatches", cell_err)

                # Format the report table
                report_df = exceptions[['Lookup_Name', 'MASTER_CELL_ID', 'DUMP_CELL_ID', 'Audit_Status']].rename(columns={
                    'Lookup_Name': 'CIQ CellName',
                    'MASTER_CELL_ID': 'Expected Cell ID',
                    'DUMP_CELL_ID': 'Actual Cell ID',
                    'Audit_Status': 'Error Type'
                })

                # Visual Highlighting
                def style_errors(val):
                    if "NAME DISCREPANCY" in val: return 'background-color: #fef3c7; color: #92400e;' # Yellow
                    if "CELL_ID MISMATCH" in val: return 'background-color: #fee2e2; color: #991b1b;' # Red
                    return ''

                st.subheader("📋 Exception Report")
                st.dataframe(
                    report_df.style.applymap(style_errors, subset=['Error Type']),
                    use_container_width=True
                )

                # G. EXCEL EXPORT
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    report_df.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 Download Detailed Exception Report",
                    data=buffer.getvalue(),
                    file_name="Master_System_Discrepancies.xlsx",
                    mime="application/vnd.ms-excel"
                )

        # --- MODULE 4: EARFCN AUDIT ---
        st.markdown("---")
        st.header("📶 Module 4: EARFCN Frequency Audit")
        st.write("Checking **EARFCNDL** vs **earfcndl** (Excluding NR Cells).")

        if st.button("🚀 RUN EARFCN AUDIT"):
            # A. Prepare Master Data (Filter out 'PR')
            # 1. Split ALIAS_NAME to get Hostname
            master_prep = df_master.copy()
            master_prep['Lookup_Name'] = master_prep['ALIAS_NAME'].astype(str).str.split(';').str[0].str.strip().str.upper()
            
            # 2. Apply "Except PR" filter
            master_filtered = master_prep[~master_prep['SERVICE_TYPE'].astype(str).str.contains('NR', case=False, na=False)]
            
            excluded_count = len(master_prep) - len(master_filtered)
            
            # 3. Clean EARFCN values
            master_filtered['M_EARFCN'] = master_filtered['EARFCNDL'].astype(str).str.strip()

            # B. Prepare Dump Data
            dump_prep = df_system.copy()
            dump_prep['Dump_Name'] = dump_prep['EUtranCellFDD'].astype(str).str.strip().str.upper()
            dump_prep['S_EARFCN'] = dump_prep['earfcndl'].astype(str).str.strip()

            # C. Join on Hostname
            
            earfcn_comparison = pd.merge(
                master_filtered[['Lookup_Name', 'M_EARFCN', 'SERVICE_TYPE']].drop_duplicates(),
                dump_prep[['Dump_Name', 'S_EARFCN']].drop_duplicates(),
                left_on='Lookup_Name',
                right_on='Dump_Name',
                how='inner'
            )

            # D. Comparison Logic
            earfcn_comparison['Audit_Status'] = earfcn_comparison.apply(
                lambda x: "✅ MATCH" if x['M_EARFCN'] == x['S_EARFCN'] else "🛑 FREQUENCY MISMATCH", 
                axis=1
            )

            # E. Results
            mismatches = earfcn_comparison[earfcn_comparison['Audit_Status'] == "🛑 FREQUENCY MISMATCH"]

            if mismatches.empty:
                st.balloons()
                st.success(f"### ✅ ALL FREQUENCIES OK")
                st.info(f"Verified {len(earfcn_comparison)} sites. All LTE (Except NR) frequencies are correct.")
            else:
                st.error(f"### 🚨 {len(mismatches)} FREQUENCY DISCREPANCIES FOUND")
                
                report_df = mismatches[['Lookup_Name', 'SERVICE_TYPE', 'M_EARFCN', 'S_EARFCN', 'Audit_Status']].rename(columns={
                    'Lookup_Name': 'Site Name',
                    'SERVICE_TYPE': 'Type',
                    'M_EARFCN': 'Expected (CIQ)',
                    'S_EARFCN': 'Actual (Site Dump)',
                    'Audit_Status': 'Status'
                })

                st.dataframe(
                    report_df.style.background_gradient(cmap='Oranges', subset=['Expected (CIQ)']),
                    use_container_width=True
                )

                # Export
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    report_df.to_excel(writer, index=False)
                st.download_button("📥 Download EARFCN Report", buffer.getvalue(), "EARFCN_Mismatches.xlsx")

        # ---------------------------------------------------------
        # MODULE 5: THE MAPPING VERIFICATION (ID against Name)
        # ---------------------------------------------------------
        st.markdown("---")
        st.header("🔗 Module 5: Managed_Element+CellName Audit")
        st.write("Verifying: Does the **NodeID** in the dump match the **MANAGED_ELEMENT_ID** in the CIQ for each Name?")

        if st.button("🚀 RUN MAPPING VERIFICATION"):
            
            # --- CLEANING HELPER ---
            def clean_val(series):
                return series.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.upper()

            # A. Prepare Master Anchor (Clean ALIAS_NAME vs ID)
            master_prep = df_master.copy()
            # Anchor: Unique Name (part before ;)
            master_prep['M_NAME'] = clean_val(master_prep['ALIAS_NAME'].astype(str).str.split(';').str[0])
            master_prep['M_ID'] = clean_val(master_prep['MANAGED_ELEMENT_ID'])
            
            # B. Prepare System Data (RouterName vs NodeID)
            dump_prep = df_system.copy()
            dump_prep['D_NAME'] = clean_val(dump_prep['EUtranCellFDD'])
            dump_prep['D_ID'] = clean_val(dump_prep['NodeID'])

            # C. VLOOKUP Logic (Anchor = Name)
            # We look at the name and check what ID is assigned to it in the system
            
            
            # Create a lookup: { "NAME": "ID" }
            system_id_lookup = dict(zip(dump_prep['D_NAME'], dump_prep['D_ID']))

            def verify_mapping(row):
                m_name = row['M_NAME']
                expected_id = row['M_ID']
                
                # Check if the name exists in the system dump
                if m_name not in system_id_lookup:
                    return "Not Match (Name missing in Dump)"
                
                # Check if the ID assigned to this name matches the Master
                actual_id = system_id_lookup.get(m_name)
                if expected_id == actual_id:
                    return "Matched"
                else:
                    return "Not Match (Wrong ID assigned)"

            master_prep['Audit_Status'] = master_prep.apply(verify_mapping, axis=1)
            master_prep['Actual_System_ID'] = master_prep['M_NAME'].map(system_id_lookup).fillna("N/A")

            # D. UI Results
            m_count = len(master_prep[master_prep['Audit_Status'] == "Matched"])
            nm_count = len(master_prep[master_prep['Audit_Status'].str.contains("Not Match")])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Names Audited", len(master_prep))
            c2.metric("Correct Mappings", m_count)
            c3.metric("Mapping Errors", nm_count, delta_color="inverse")

            # Result Table
            
            report_df = master_prep[['M_NAME', 'M_ID', 'Actual_System_ID', 'Audit_Status']].rename(columns={
                'M_NAME': 'CellName',
                'M_ID': 'Expected ID (CIQ)',
                'Actual_System_ID': 'Actual ID (Dump)',
                'Audit_Status': 'Status'
            })

            def highlight_status(val):
                color = '#dcfce7' if val == "Matched" else '#fee2e2'
                return f'background-color: {color}'

            st.dataframe(report_df.style.applymap(highlight_status, subset=['Status']), use_container_width=True)

            # E. Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                report_df.to_excel(writer, index=False)
            st.download_button("📥 Download Mapping Report", buffer.getvalue(), "Mapping_Audit.xlsx")

    except Exception as e:
        st.error(f"⚠️ Technical Error: {e}")
        st.info("Ensure your columns are named exactly: 'MANAGED_ELEMENT_ID', 'ALIAS_NAME', 'NodeID', 'EUtranCellFDD'")

    except Exception as e:
        st.error(f"⚠️ Critical Error: {e}")

else:
    st.info("👋 **Welcome Teams.** Upload files to begin the parameters check.")

