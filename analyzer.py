# analyzer.py
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import textwrap
from reportlab.lib.pagesizes import letter


def plot_graph(df, x, y, chart_type="Line", avg=False):
    plt.figure(figsize=(10, 5))

    if chart_type == "Line":
        for vessel in df["VesselName"].unique():
            vessel_df = df[df["VesselName"] == vessel]
            plt.plot(vessel_df[x], vessel_df[y], label=vessel)

    elif chart_type == "Bar":
        if avg:
            grouped = df.groupby("VesselName")[y].mean().reset_index()
            plt.bar(grouped["VesselName"], grouped[y])
        else:
            grouped = df.groupby(x)[y].mean().reset_index()
            plt.bar(grouped[x], grouped[y])

    elif chart_type == "Scatter":
        plt.scatter(df[x], df[y], alpha=0.7)

    elif chart_type == "Pie":
        grouped = df.groupby(x)[y].sum().reset_index()
        plt.pie(grouped[y], labels=grouped[x], autopct="%1.1f%%")

    plt.title(f"{chart_type} Chart: {y} vs {x}")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.grid(True)
    plt.legend(loc="best")
    return plt


# analyzer.py
from fpdf import FPDF

def generate_pdf(response_text, filename="summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Vessel Performance Summary", ln=True, align='C')
    pdf.ln(10)

    # Body
    pdf.set_font("Arial", size=12)
    lines = response_text.split('\n')
    
    for line in lines:
        if line.strip() == "":
            pdf.ln(5)
        else:
            pdf.multi_cell(0, 10, line)

    pdf.output(filename)

import seaborn as sns
import streamlit as st
import pandas as pd

def generate_insightful_graphs(df):
    if 'RPM' in df.columns and 'Fuel Consumption' in df.columns:
        st.markdown("#### 🔍 Fuel vs RPM")
        plt.figure(figsize=(8,4))
        sns.scatterplot(data=df, x='RPM', y='Fuel Consumption')
        st.pyplot(plt)

    if 'Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Date']):
     st.markdown("#### 📈 Trends over Time")
    for col in df.select_dtypes(include='number').columns:
        plt.figure(figsize=(8,4))
        sns.lineplot(data=df, x='Date', y=col, label=col)
        plt.legend(loc="best")  # Now legend will have correct labels
        st.pyplot(plt)

