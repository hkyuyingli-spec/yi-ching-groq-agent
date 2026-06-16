import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from firebase_config import get_db
import datetime

st.set_page_config(page_title="Enigma Analytics Dashboard", layout="wide")

st.title("📊 Enigma Personalisation Analytics")

def get_analytics_data():
    db = get_db()
    if not db:
        # Mock data for demonstration if Firebase is not connected
        return pd.DataFrame([
            {"relevant": True, "clarity_stars": 3, "action_taken": "Yes", "timestamp": datetime.datetime.now() - datetime.timedelta(days=i), "hexagram_name": "The Creative"}
            for i in range(20)
        ] + [
            {"relevant": False, "clarity_stars": 1, "action_taken": "No", "timestamp": datetime.datetime.now() - datetime.timedelta(days=i), "hexagram_name": "Conflict"}
            for i in range(5)
        ])
    
    # Fetch from readings and feedback collections
    # This is a simplified fetch for the prototype
    readings_ref = db.collection("readings").stream()
    feedback_ref = db.collection("feedback").stream()
    
    readings_data = {doc.id: doc.to_dict() for doc in readings_ref}
    feedback_data = {doc.id: doc.to_dict() for doc in feedback_ref}
    
    combined = []
    for r_id, r_val in readings_data.items():
        fb = feedback_data.get(r_id, {})
        combined.append({
            "relevant": fb.get("relevant"),
            "clarity_stars": fb.get("clarity_stars"),
            "action_taken": fb.get("action_taken"),
            "timestamp": datetime.datetime.fromtimestamp(r_val.get("timestamp", 0)),
            "hexagram_name": r_val.get("hexagram_name")
        })
        
    return pd.DataFrame(combined)

df = get_analytics_data()

if df.empty:
    st.warning("No data available yet. Start some readings to see analytics!")
else:
    # KPI Cards
    total_readings = len(df)
    relevance_rate = (df['relevant'] == True).sum() / total_readings * 100 if total_readings > 0 else 0
    avg_clarity = df['clarity_stars'].mean()
    action_rate = (df['action_taken'] == "Yes").sum() / total_readings * 100 if total_readings > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Readings", total_readings)
    col2.metric("Relevance Rate", f"{relevance_rate:.1f}%")
    col3.metric("Avg Clarity", f"{avg_clarity:.1f} ⭐")
    col4.metric("Action Rate", f"{action_rate:.1f}%")

    st.divider()

    # Charts
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Weekly Clarity Trend")
        df['date'] = df['timestamp'].dt.date
        trend = df.groupby('date')['clarity_stars'].mean().reset_index()
        fig_trend = px.line(trend, x='date', y='clarity_stars', title="Avg Clarity Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.subheader("Clarity Distribution")
        fig_dist = px.histogram(df, x='clarity_stars', nbins=3, title="Clarity Star Distribution")
        st.plotly_chart(fig_dist, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Top 5 Helpful Hexagrams")
        helpful = df[df['relevant'] == True]['hexagram_name'].value_counts().head(5).reset_index()
        fig_helpful = px.bar(helpful, x='hexagram_name', y='count', title="Relevant Hexagrams")
        st.plotly_chart(fig_helpful, use_container_width=True)

    with c4:
        st.subheader("Action Distribution")
        action_counts = df['action_taken'].value_counts().reset_index()
        fig_action = px.pie(action_counts, names='action_taken', values='count', title="Did users take action?")
        st.plotly_chart(fig_action, use_container_width=True)
