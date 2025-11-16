import pandas as pd
import streamlit as st
from datetime import datetime

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="CashTrack – Smart Campus Wallet",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------
# CUSTOM CSS (HIGH-TECH THEME + CHAT BUBBLES)
# -------------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #141628 0, #050711 45%, #000000 100%);
        color: #f5f5f7 !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050715 0%, #050711 40%, #050609 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    section[data-testid="stSidebar"] * {
        color: #f5f5f7 !important;
        font-size: 14px !important;
    }

    .glass-card {
        background: rgba(20,22,40,0.72);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(16px);
    }

    .glass-card-tight {
        background: rgba(20,22,40,0.85);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 16px;
        backdrop-filter: blur(14px);
    }

    .hero-title {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
    }

    .hero-subtitle {
        font-size: 15px;
        opacity: 0.78;
    }

    .hero-chip {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        display: inline-block;
        background: rgba(120,60,255,0.35);
        border: 1px solid rgba(200,200,255,0.35);
        padding: 4px 9px;
        border-radius: 999px;
        margin-bottom: 8px;
    }

    .cashtrack-brand {
        font-size: 42px;
        font-weight: 800;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
    }

    .metric-label {
        font-size: 11px;
        opacity: 0.6;
        text-transform: uppercase;
        letter-spacing: 0.11em;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
    }

    .profile-label {
        font-size: 14px;
        opacity: 0.75;
    }
    .profile-value {
        font-size: 17px;
        font-weight: 600;
        color: #ffffff;
    }

    .stDataFrame tr, .stDataFrame td, .stDataFrame th {
        font-size: 14px !important;
        color: #e5e7eb !important;
    }

    /* Chat-style advisor */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin-top: 8px;
    }
    .chat-bubble {
        max-width: 90%;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 14px;
        line-height: 1.4;
        margin-bottom: 6px;
    }
    .chat-bubble.user {
        align-self: flex-end;
        background: rgba(59,130,246,0.22);
        border: 1px solid rgba(191,219,254,0.6);
    }
    .chat-bubble.bot {
        align-self: flex-start;
        background: rgba(15,23,42,0.9);
        border: 1px solid rgba(148,163,184,0.45);
    }
    .chat-label {
        font-size: 11px;
        text-transform: uppercase;
        opacity: 0.7;
        letter-spacing: 0.13em;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

@st.cache_data
def load_data():
    users = pd.read_csv("data/users_sample.csv", index_col=False)
    tx = pd.read_csv("data/wallet_transactions_sample.csv", index_col=False)

    tx["date"] = pd.to_datetime(tx["date"])
    merged = tx.merge(users, on="user_id", how="left")

    return merged, users

df, users_df = load_data()

# -------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------

st.sidebar.markdown(
    """
    <div class='glass-card-tight'>
        <div class='hero-chip'>Smart Campus Wallet</div>
        <div style='font-size:13px;opacity:0.85;'>
            Rutgers Smart Campus Wallet with RU Money Coach – a friendly guide for student finances.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Student dropdown (names + IDs)
valid_users = sorted(users_df["user_id"].unique())
student_options = [None] + valid_users

def format_student(uid):
    if uid is None:
        return "All Students"
    record = users_df[users_df["user_id"] == uid]
    if record.empty:
        return str(uid)
    row = record.iloc[0]
    return f"{row['name']} ({uid})"

selected_id = st.sidebar.selectbox(
    "Select Student",
    options=student_options,
    format_func=format_student
)

# Date range
min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Category dropdown
category_options = ["All Categories"] + sorted(df["category"].unique())
selected_category = st.sidebar.selectbox("Category", category_options)

# Amount slider
min_amt = float(df["amount"].min())
max_amt = float(df["amount"].max())

amount_range = st.sidebar.slider(
    "Amount Range ($)",
    min_value=0.0,
    max_value=round(max_amt, 2),
    value=(0.0, round(max_amt, 2)),
)

# -------------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------------

filtered = df.copy()

if selected_id is not None:
    filtered = filtered[filtered["user_id"] == selected_id]

filtered = filtered[
    (filtered["date"].dt.date >= start_date) &
    (filtered["date"].dt.date <= end_date)
]

filtered = filtered[
    (filtered["amount"] >= amount_range[0]) &
    (filtered["amount"] <= amount_range[1])
]

if selected_category != "All Categories":
    filtered = filtered[filtered["category"] == selected_category]

# flag for students like Olivia with no transactions
no_tx_for_student = False
if filtered.empty:
    if selected_id is not None:
        no_tx_for_student = True
    else:
        st.warning("No data matches your filters.")
        st.stop()

# -------------------------------------------------------
# HERO SECTION
# -------------------------------------------------------

st.markdown(
    """
    <div class='glass-card'>
        <div class='cashtrack-brand'>💳 CashTrack</div>
        <div class='hero-chip'>Live Spending Telemetry</div>
        <div class='hero-subtitle'>
            Real-time insights into student spending across dining, books, transportation, entertainment, and more.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# STUDENT PROFILE
# -------------------------------------------------------

if selected_id is not None:
    profile = users_df[users_df["user_id"] == selected_id].iloc[0]
    st.markdown(
        f"""
        <div class='glass-card'>
            <h3>🧑‍🎓 {profile['name']} ({profile['user_id']})</h3>
            <p><span class='profile-label'>Major:</span> <span class='profile-value'>{profile['major']}</span></p>
            <p><span class='profile-label'>Class Year:</span> <span class='profile-value'>{profile['class_year']}</span></p>
            <p><span class='profile-label'>Residence:</span> <span class='profile-value'>{profile['residence_type']}</span></p>
            <p><span class='profile-label'>Interests:</span> <span class='profile-value'>{profile['interests']}</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------

if no_tx_for_student:
    total = 0.0
    tx_count = 0
    days = 0
    avg_day = 0.0
    avg_tx = 0.0
else:
    total = filtered["amount"].sum()
    tx_count = len(filtered)
    days = (filtered["date"].max() - filtered["date"].min()).days + 1
    avg_day = total / days if days > 0 else total
    avg_tx = filtered["amount"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='glass-card-tight'><div class='metric-label'>Total Spent</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>${total:.2f}</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card-tight'><div class='metric-label'>Transactions</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{tx_count}</div></div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='glass-card-tight'><div class='metric-label'>Avg Per Day</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>${avg_day:.2f}</div></div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='glass-card-tight'><div class='metric-label'>Avg Per Transaction</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>${avg_tx:.2f}</div></div>", unsafe_allow_html=True)

# -------------------------------------------------------
# TABS
# -------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "📈 Analytics", "💡 RU Money Coach", "📋 Transactions"]
)

# -------------------------------------------------------
# TAB 1: OVERVIEW
# -------------------------------------------------------

with tab1:
    colA, colB = st.columns([2, 1])

    with colA:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Category Breakdown")

        if no_tx_for_student:
            st.info("This student has no transactions in the selected range yet.")
        else:
            cat_summary = (
                filtered.groupby("category")["amount"]
                .sum()
                .sort_values(ascending=False)
            )

            # bar chart
            st.bar_chart(cat_summary)

            # table with clear dollar label
            cat_df = cat_summary.reset_index().rename(
                columns={"category": "Category", "amount": "Amount ($)"}
            )
            st.dataframe(cat_df, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Quick Insights")

        if no_tx_for_student:
            st.info("Once this student starts using the wallet, spending insights will appear here.")
        else:
            if not cat_summary.empty:
                top_cat = cat_summary.idxmax()
                st.markdown(f"- Highest spending category: **{top_cat}**.")

            if avg_tx > 20:
                st.markdown(
                    "- Average purchase size is relatively high — planning weekly budgets could help."
                )

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------
# TAB 2: ANALYTICS
# -------------------------------------------------------

with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Spending Over Time")

    if no_tx_for_student:
        st.info("No spending activity to chart yet for this student in the selected period.")
    else:
        daily = filtered.set_index("date")["amount"].resample("D").sum()
        st.line_chart(daily)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Weekday Pattern")

    if no_tx_for_student:
        st.info("Weekday trends will appear once there is spending data for this student.")
    else:
        weekday_df = filtered.copy()
        weekday_df["weekday"] = weekday_df["date"].dt.day_name()
        weekday_summary = weekday_df.groupby("weekday")["amount"].sum()
        st.bar_chart(weekday_summary)

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------
# TAB 3: RU MONEY COACH
# -------------------------------------------------------

with tab3:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("💡 RU Money Coach")

    # Build context for "student message"
    if selected_id is None:
        who = "your current campus-wide view at Rutgers"
        residence_type = "mixed"
        major = "Various majors"
        class_year = ""
    else:
        row = users_df[users_df["user_id"] == selected_id].iloc[0]
        major = row["major"]
        class_year = row["class_year"]
        residence_type = row["residence_type"]
        who = f"{row['name']} ({major}, Class of {class_year})"

    user_msg = (
        f"Show me insights for {who} between {start_date} and {end_date}, "
        f"with total spending of ${total:.2f} across {tx_count} transactions."
    )

    # Coach logic
    advice = []

    if no_tx_for_student and selected_id is not None:
        advice.append(
            "There are no transactions for this student in the selected range yet. "
            "This is actually a great time to set simple habits — like choosing a weekly budget "
            "for dining or entertainment before spending begins."
        )
    else:
        res_lower = str(residence_type).lower()
        if "commuter" in res_lower:
            advice.append(
                "As a commuter at Rutgers, transit and off-campus food are usually your biggest levers. "
                "Track how many days you buy food near campus versus packing lunch."
            )
        elif "dorm" in res_lower:
            advice.append(
                "Since you live in a dorm, late-night dining and delivery can quietly add up. "
                "Try one 'no-delivery' night per week."
            )

        if "Dining" in filtered["category"].values:
            dining_total = filtered[filtered["category"] == "Dining"]["amount"].sum()
            if total > 0 and dining_total / total > 0.4:
                advice.append(
                    "Dining is taking a big slice of your budget. Look for campus meal deals or use your meal plan first "
                    "before swiping your card off-campus."
                )

        if "Books" in filtered["category"].values:
            books_total = filtered[filtered["category"] == "Books"]["amount"].sum()
            if books_total > 0:
                advice.append(
                    "You're spending a noticeable amount on books. Check the Rutgers library, rentals, or used book swaps "
                    "before buying new."
                )

        if avg_tx > 25:
            advice.append(
                "Your average transaction size is on the higher side. Planning purchases ahead of time can help avoid "
                "end-of-month stress."
            )

        if days > 0 and tx_count / days > 3:
            advice.append(
                "You're making purchases very frequently. Try a weekly 'no-spend day' or batch errands together to reduce impulse swipes."
            )

    if not advice:
        advice.append(
            "Your spending pattern looks fairly balanced in this view. Keep checking in weekly so you stay ahead of your budget."
        )

    # Chat-style rendering with spacing
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='chat-bubble user'>
            <div class='chat-label'>Student</div>
            {user_msg}
        </div>
        """,
        unsafe_allow_html=True,
    )

    for tip in advice:
        st.markdown(
            f"""
            <div class='chat-bubble bot'>
                <div class='chat-label'>RU Money Coach</div>
                {tip}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------
# TAB 4: TRANSACTIONS (PRIVATE)
# -------------------------------------------------------

with tab4:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Transaction Log")

    if selected_id is None:
        st.warning(
            "🔒 Transaction details are private. Select an individual student to view their history."
        )
    elif no_tx_for_student:
        st.info("This student has no recorded transactions in the selected range yet.")
    else:
        tx_view = filtered.sort_values("date", ascending=False).copy()
        tx_view["date"] = tx_view["date"].dt.strftime("%Y-%m-%d")

        tx_view = tx_view.rename(
            columns={
                "date": "Date",
                "merchant": "Merchant",
                "category": "Category",
                "amount": "Amount ($)",
                "payment_method": "Payment Method",
                "location": "Location",
            }
        )

        st.dataframe(
            tx_view[
                ["Date", "Merchant", "Category", "Amount ($)", "Payment Method", "Location"]
            ],
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
