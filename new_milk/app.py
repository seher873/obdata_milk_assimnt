import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
import os
from db import MilkDatabase, MilkEntry

# --- PDF GENERATION ---
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "Milk Dairy Report", border=False, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.set_text_color(169, 169, 169)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_entry_table(self, entries, columns):
        self.set_font("Arial", "B", 10)
        self.set_fill_color(224, 235, 255)
        for col in columns:
            self.cell(30, 8, col, border=1, align='C', fill=True)
        self.ln()

        self.set_font("Arial", "", 9)
        for entry in entries:
            for value in entry:
                self.cell(30, 8, str(value), border=1)
            self.ln()

def generate_pdf(entries, filename):
    pdf = PDF()
    pdf.add_page()
    columns = [
        "ID", "Customer", "Start", "End",
        "M-Mound", "M-Sair", "M-Rate",
        "E-Mound", "E-Sair", "E-Rate",
        "Rent", "Comm.", "Bandi", "Paid"
    ]
    pdf.add_entry_table(entries, columns)
    filepath = os.path.join(".", filename)
    pdf.output(filepath)
    return filepath

# --- INITIALIZE DB ---
db = MilkDatabase()

# --- UI LAYOUT ---
st.set_page_config(page_title="Milk Dairy App", layout="wide")
st.markdown("""
<h1 style='text-align: center; color: #4B0082;'>Milk Dairy Management System</h1>
<p style='text-align: center;'>Elegant - Efficient - Easy to Use</p>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🏠 Home",
    "🗖 Daily Entry",
    "📚 Weekly Report",
    "🗖 Daily Report",
    "🦾 Monthly Report",
    "👤 Customer Details"
])

# --- HOME ---
with tabs[0]:
    st.markdown("""
    ### 👋 Welcome to Malik Dairy
    Manage milk records, track customer accounts, and generate reports effortlessly.
    """)

# --- DAILY ENTRY ---
with tabs[1]:
    st.header("🗖 Add Daily Entry")
    with st.form("entry_form", clear_on_submit=True):
        customer_name = st.text_input("Customer Name")
        start_date = st.date_input("Start Date", datetime.today())
        end_date = st.date_input("End Date", datetime.today())

        col1, col2, col3 = st.columns(3)
        with col1:
            morning_mound = st.number_input("Morning Mound (kg)", min_value=0.0)
            evening_mound = st.number_input("Evening Mound (kg)", min_value=0.0)
        with col2:
            morning_sair = st.number_input("Morning Sair (liters)", min_value=0)
            evening_sair = st.number_input("Evening Sair (liters)", min_value=0)
        with col3:
            morning_rate = st.number_input("Morning Rate (per kg)", min_value=0.0)
            evening_rate = st.number_input("Evening Rate (per kg)", min_value=0.0)

        rent = st.number_input("Rent (₹)", min_value=0.0)
        commission = st.number_input("Commission (₹)", min_value=0.0)
        bandi = st.number_input("Bandi (₹)", min_value=0.0)
        paid_amount = st.number_input("Paid Amount (₹)", min_value=0.0)

        submitted = st.form_submit_button("➕ Add Entry")
        if submitted:
            try:
                current_date = start_date
                while current_date <= end_date:
                    entry = MilkEntry(
                        customer_name, str(current_date), str(current_date),
                        morning_mound, morning_sair, morning_rate,
                        evening_mound, evening_sair, evening_rate,
                        rent, commission, bandi, paid_amount
                    )
                    db.insert_entry(entry)
                    current_date += timedelta(days=1)
                st.success("✅ Entries added successfully from start to end date!")
            except Exception as e:
                st.error(f"❌ Failed to add entries: {e}")

# --- WEEKLY REPORT ---
with tabs[2]:
    st.header("📚 Weekly Report")
    start = st.date_input("Start Date", datetime.today() - timedelta(days=7), key="week_start")
    end = st.date_input("End Date", datetime.today(), key="week_end")

    if st.button("📊 Show Weekly Report"):
        try:
            entries = db.get_weekly_report(str(start), str(end))
            if entries:
                st.dataframe(entries)
                filename = generate_pdf(entries, "weekly_report.pdf")
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Download Report PDF", f, file_name=filename)
            else:
                st.warning("⚠️ No entries found for the selected week.")
        except Exception as e:
            st.error(f"❌ Error generating weekly report: {e}")

# --- DAILY REPORT ---
columns = [
    "id", "customer_name", "start_date", "end_date",
    "morning_mound", "morning_sair", "morning_rate",
    "evening_mound", "evening_sair", "evening_rate",
    "rent", "commission", "bandi", "paid_amount"
]

with tabs[3]:
    st.header("🗖 Daily Report")
    selected_date = st.date_input("Select Date", datetime.today(), key="daily_date")
    if st.button("📋 Show Daily Report"):
        try:
            entries = db.get_daily_report(str(selected_date))
            if entries:
                for entry in entries:
                    for idx, value in enumerate(entry):
                        st.markdown(f"**{columns[idx]}**: {value}")
                    st.markdown("---")
                filename = generate_pdf(entries, f"daily_report_{selected_date}.pdf")
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=filename)
            else:
                st.warning("⚠️ No entries found for this day.")
        except Exception as e:
            st.error(f"❌ Error generating daily report: {e}")

# --- MONTHLY REPORT ---
with tabs[4]:
    st.header("🦾 Monthly Report")
    selected_month = st.selectbox("Select Month", [f"{i:02d}" for i in range(1, 13)])

    if st.button("📊 Show Monthly Report"):
        try:
            entries = db.get_monthly_report(selected_month)
            if entries:
                st.dataframe(entries)
                filename = generate_pdf(entries, f"monthly_report_{selected_month}.pdf")
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=filename)
            else:
                st.warning("⚠️ No entries found for this month.")
        except Exception as e:
            st.error(f"❌ Error generating monthly report: {e}")

# --- CUSTOMER DETAILS ---
with tabs[5]:
    st.header("👤 Customer Profile & Entries")
    customer_name = st.text_input("🔍 Enter Customer Name")
    if st.button("📂 Show Entries"):
        try:
            entries = db.get_customer_entries(customer_name)
            if entries:
                st.success(f"📄 Found {len(entries)} entries for {customer_name}.")
                for i, entry in enumerate(entries):
                    with st.expander(f"📋 Entry #{i+1} | {entry[2]} ➔ {entry[3]}"):
                        st.markdown(f"**Customer Name:** {entry[1]}")
                        
                        # Convert liters to mounds for both morning and evening
                        morning_mound = entry[4] * 40  # Convert morning liters to mounds
                        evening_mound = entry[7] * 40  # Convert evening liters to mounds
                        
                        st.markdown(f"**Morning Mound:** {morning_mound} (mounds) ➔ {entry[5]} (liters)")
                        st.markdown(f"**Evening Mound:** {evening_mound} (mounds) ➔ {entry[8]} (liters)")
                        st.markdown(f"**Morning Rate:** {entry[6]} (PKR/kg)")
                        st.markdown(f"**Evening Rate:** {entry[9]} (PKR/kg)")
                        st.markdown(f"**Rent:** {entry[10]} (PKR) | **Commission:** {entry[11]} (PKR) | **Bandi:** {entry[12]} (PKR)")
                        st.markdown(f"**Paid Amount:** {entry[13]} (PKR)")
            else:
                st.warning("❌ No entries found for this customer.")
        except Exception as e:
            st.error(f"❌ Error retrieving customer entries: {e}")
