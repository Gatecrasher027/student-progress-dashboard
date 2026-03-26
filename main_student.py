import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

st.set_page_config(
    page_title="Student Progress Monitor",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Progress Monitoring System")
st.caption("K-Means Clustering · C Programming Course · 200 Students")
st.divider()

@st.cache_data
def load_data():
    if os.path.exists("student_progress.csv"):
        return pd.read_csv("student_progress.csv")

    np.random.seed(42)
    cluster_profiles = {
        0: {"label": "High Performer",  "quiz": (82, 8),  "assign": (88, 7),  "midterm": (85, 7),  "final": (87, 7),  "attendance": (92, 5)},
        1: {"label": "Average",         "quiz": (65, 8),  "assign": (68, 8),  "midterm": (63, 9),  "final": (66, 8),  "attendance": (78, 8)},
        2: {"label": "Struggling",      "quiz": (42, 10), "assign": (45, 10), "midterm": (40, 11), "final": (43, 10), "attendance": (60, 12)},
        3: {"label": "Inconsistent",    "quiz": (70, 18), "assign": (65, 17), "midterm": (68, 19), "final": (64, 18), "attendance": (72, 15)},
    }
    cluster_sizes = [60, 70, 40, 30]
    rows = []
    sid = 1
    for cid, size in enumerate(cluster_sizes):
        p = cluster_profiles[cid]
        for _ in range(size):
            quiz    = np.clip(np.random.normal(*p["quiz"]),        0, 100)
            assign  = np.clip(np.random.normal(*p["assign"]),      0, 100)
            mid     = np.clip(np.random.normal(*p["midterm"]),     0, 100)
            final   = np.clip(np.random.normal(*p["final"]),       0, 100)
            attend  = np.clip(np.random.normal(*p["attendance"]),  0, 100)
            total   = round(quiz*0.15 + assign*0.25 + mid*0.25 + final*0.30 + attend*0.05, 2)
            grade   = "A" if total>=80 else "B" if total>=70 else "C" if total>=60 else "D" if total>=50 else "F"
            rows.append({
                "Student_ID": f"STU{sid:03d}", "Cluster": cid,
                "Cluster_Label": p["label"],
                "Quiz_Score": round(quiz,2), "Assignment_Score": round(assign,2),
                "Midterm_Score": round(mid,2), "Final_Score": round(final,2),
                "Attendance_Pct": round(attend,2), "Total_Score": total, "Grade": grade,
            })
            sid += 1
    return pd.DataFrame(rows).sample(frac=1, random_state=1).reset_index(drop=True)


df = load_data()

CLUSTER_COLORS = {
    "High Performer": "#1D9E75",
    "Average":        "#3266ad",
    "Inconsistent":   "#BA7517",
    "Struggling":     "#E24B4A",
}
GRADE_COLORS = {
    "A": "#1D9E75", "B": "#3266ad",
    "C": "#BA7517", "D": "#EF9F27", "F": "#E24B4A",
}

st.sidebar.header("Filters")

clusters = st.sidebar.multiselect(
    "Cluster", options=df["Cluster_Label"].unique().tolist(),
    default=df["Cluster_Label"].unique().tolist()
)

grades = st.sidebar.multiselect(
    "Grade", options=["A", "B", "C", "D", "F"],
    default=["A", "B", "C", "D", "F"]
)

score_range = st.sidebar.slider(
    "Total score range", min_value=0, max_value=100,
    value=(0, 100), step=1
)

st.sidebar.divider()
st.sidebar.markdown("**Scoring weights**")
st.sidebar.markdown("Quiz 15% · Assignment 25%")
st.sidebar.markdown("Midterm 25% · Final 30% · Attendance 5%")

dff = df[
    (df["Cluster_Label"].isin(clusters)) &
    (df["Grade"].isin(grades)) &
    (df["Total_Score"] >= score_range[0]) &
    (df["Total_Score"] <= score_range[1])
]

if dff.empty:
    st.warning("No students match the selected filters.")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Students",       f"{len(dff)}")
c2.metric("Avg Total Score",      f"{dff['Total_Score'].mean():.1f}%")
c3.metric("Avg Attendance",       f"{dff['Attendance_Pct'].mean():.1f}%")
c4.metric("Pass Rate (≥50)",      f"{(dff['Total_Score'] >= 50).mean()*100:.1f}%")
c5.metric("At Risk (Grade F)",    f"{(dff['Grade'] == 'F').sum()} students",
          delta=f"{(dff['Grade']=='F').mean()*100:.1f}% of filtered",
          delta_color="inverse")

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Cluster distribution")
    cluster_counts = dff["Cluster_Label"].value_counts().reset_index()
    cluster_counts.columns = ["Cluster", "Count"]
    fig = px.pie(
        cluster_counts, names="Cluster", values="Count",
        color="Cluster", color_discrete_map=CLUSTER_COLORS,
        hole=0.55,
    )
    fig.update_traces(textinfo="label+percent", textfont_size=12)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Avg scores by cluster")
    score_cols = ["Quiz_Score", "Assignment_Score", "Midterm_Score", "Final_Score", "Attendance_Pct"]
    avg_scores = dff.groupby("Cluster_Label")[score_cols].mean().reset_index()
    avg_melted = avg_scores.melt(id_vars="Cluster_Label", var_name="Component", value_name="Avg Score")
    avg_melted["Component"] = avg_melted["Component"].str.replace("_Score","").str.replace("_Pct","").str.replace("_"," ")
    fig = px.bar(
        avg_melted, x="Avg Score", y="Component", color="Cluster_Label",
        color_discrete_map=CLUSTER_COLORS, barmode="group", orientation="h",
        labels={"Cluster_Label": "Cluster"},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="",
                      yaxis=dict(categoryorder="array",
                                 categoryarray=["Quiz","Assignment","Midterm","Final","Attendance Pct"]))
    st.plotly_chart(fig, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Attendance vs Total Score")
    fig = px.scatter(
        dff, x="Attendance_Pct", y="Total_Score",
        color="Cluster_Label", color_discrete_map=CLUSTER_COLORS,
        hover_data=["Student_ID", "Grade"],
        labels={"Attendance_Pct": "Attendance (%)", "Total_Score": "Total Score (%)",
                "Cluster_Label": "Cluster"},
        opacity=0.75,
    )
    fig.update_traces(marker=dict(size=7))
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.subheader("Grade breakdown by cluster")
    grade_dist = dff.groupby(["Cluster_Label", "Grade"]).size().reset_index(name="Count")
    fig = px.bar(
        grade_dist, x="Cluster_Label", y="Count", color="Grade",
        color_discrete_map=GRADE_COLORS, barmode="stack",
        labels={"Cluster_Label": "Cluster", "Count": "No. of students"},
        category_orders={"Grade": ["A", "B", "C", "D", "F"]},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="Grade")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Score distribution across components")
box_data = dff.melt(
    id_vars="Cluster_Label",
    value_vars=["Quiz_Score", "Assignment_Score", "Midterm_Score", "Final_Score"],
    var_name="Component", value_name="Score"
)
box_data["Component"] = box_data["Component"].str.replace("_Score", "")
fig = px.box(
    box_data, x="Component", y="Score", color="Cluster_Label",
    color_discrete_map=CLUSTER_COLORS,
    labels={"Component": "", "Score": "Score (%)", "Cluster_Label": "Cluster"},
    category_orders={"Component": ["Quiz", "Assignment", "Midterm", "Final"]},
)
fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="")
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Student detail")
st.caption(f"{len(dff)} students shown · sorted by Total Score")

display_df = (
    dff[["Student_ID", "Cluster_Label", "Quiz_Score", "Assignment_Score",
         "Midterm_Score", "Final_Score", "Attendance_Pct", "Total_Score", "Grade"]]
    .sort_values("Total_Score", ascending=False)
    .reset_index(drop=True)
)

st.dataframe(
    display_df.style.background_gradient(
        subset=["Total_Score"], cmap="RdYlGn", vmin=0, vmax=100
    ).background_gradient(
        subset=["Attendance_Pct"], cmap="RdYlGn", vmin=0, vmax=100
    ),
    use_container_width=True,
    hide_index=True,
)
