# Student Progress Monitoring System

An interactive dashboard for monitoring and analysing student performance using K-Means Clustering.

## Project Overview

**Course:** C Programming  
**Algorithm:** K-Means Clustering  
**Dataset:** 200 students across 4 performance clusters  

## Clusters

| Cluster | Description |
|---|---|
| High Performer | Consistently high scores across all components |
| Average | Moderate performance, stable across assessments |
| Struggling | Low scores, poor attendance, needs intervention |
| Inconsistent | High variance — strong in some areas, weak in others |

## Scoring Weights

| Component | Weight |
|---|---|
| Quiz | 15% |
| Assignment | 25% |
| Midterm | 25% |
| Final Exam | 30% |
| Attendance | 5% |

## Dashboard Features

- Sidebar filters — cluster, grade, total score range
- 5 KPI cards — total students, avg score, avg attendance, pass rate, at-risk count
- Cluster distribution donut chart
- Average scores by cluster (grouped bar)
- Attendance vs Total Score scatter plot
- Grade breakdown stacked bar chart
- Score distribution box plot across all components
- Student detail table with colour-coded score gradients

## Tech Stack

Python · Streamlit · Plotly · Pandas · NumPy
