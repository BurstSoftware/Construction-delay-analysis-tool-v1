import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Streamlit page configuration
st.set_page_config(page_title="Construction Delay Analysis Tool", layout="wide")

# Title and description
st.title("Construction Delay Analysis Tool")
st.markdown("""
Analyze project delays to identify causes, impacts, and mitigation strategies.
Track delays, visualize timelines and cause-effect relationships, and export reports for claims.
""")

# Initialize session state for storing delay data
if 'delays' not in st.session_state:
    st.session_state.delays = pd.DataFrame(columns=[
        'Task', 'Category', 'Start_Date', 'End_Date', 'Delay_Days', 'Cost_Impact', 'Description'
    ])

# Sidebar for navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Input Delays", "Analyze Impacts", "Visualizations", "Mitigation & Reports"])

# Function to calculate cost impact (placeholder for integration with Cost Estimators)
def calculate_cost_impact(category, delay_days):
    # Hypothetical cost estimator logic (replace with actual Cost Estimators integration)
    cost_per_day = {
        'Weather': 5000,
        'Labor': 8000,
        'Materials': 6000,
        'Equipment': 7000,
        'Other': 4000
    }
    return cost_per_day.get(category, 4000) * delay_days

# Page 1: Input Delays
if page == "Input Delays":
    st.header("Input Delay Details")
    with st.form(key="delay_form"):
        task = st.text_input("Task Name")
        category = st.selectbox("Delay Category", ['Weather', 'Labor', 'Materials', 'Equipment', 'Other'])
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        description = st.text_area("Description (Optional)")
        submit = st.form_submit_button("Add Delay")

        if submit:
            delay_days = (end_date - start_date).days
            if delay_days < 0:
                st.error("End Date must be after Start Date!")
            else:
                cost_impact = calculate_cost_impact(category, delay_days)
                new_delay = pd.DataFrame([{
                    'Task': task,
                    'Category': category,
                    'Start_Date': start_date,
                    'End_Date': end_date,
                    'Delay_Days': delay_days,
                    'Cost_Impact': cost_impact,
                    'Description': description
                }])
                st.session_state.delays = pd.concat([st.session_state.delays, new_delay], ignore_index=True)
                st.success("Delay added successfully!")

    # Display current delays
    if not st.session_state.delays.empty:
        st.subheader("Current Delays")
        st.dataframe(st.session_state.delays)

# Page 2: Analyze Impacts
elif page == "Analyze Impacts":
    st.header("Delay Impact Analysis")
    if st.session_state.delays.empty:
        st.warning("No delays recorded. Please add delays in the 'Input Delays' section.")
    else:
        total_delays = st.session_state.delays['Delay_Days'].sum()
        total_cost = st.session_state.delays['Cost_Impact'].sum()
        st.metric("Total Delay Days", total_delays)
        st.metric("Total Cost Impact", f"${total_cost:,.2f}")

        # Breakdown by category
        st.subheader("Delay Breakdown by Category")
        category_summary = st.session_state.delays.groupby('Category').agg({
            'Delay_Days': 'sum',
            'Cost_Impact': 'sum'
        }).reset_index()
        st.dataframe(category_summary)

        # Plotly bar chart for delays by category
        fig = px.bar(category_summary, x='Category', y='Delay_Days', title="Delays by Category")
        st.plotly_chart(fig)

# Page 3: Visualizations
elif page == "Visualizations":
    st.header("Delay Visualizations")
    if st.session_state.delays.empty:
        st.warning("No delays recorded. Please add delays in the 'Input Delays' section.")
    else:
        # Gantt Chart for Delay Timeline
        st.subheader("Delay Timeline (Gantt Chart)")
        gantt_data = [
            dict(Task=row['Task'], Start=row['Start_Date'], Finish=row['End_Date'], Category=row['Category'])
            for _, row in st.session_state.delays.iterrows()
        ]
        fig_gantt = ff.create_gantt(gantt_data, index_col='Category', show_colorbar=True, title="Delay Timeline")
        st.plotly_chart(fig_gantt)

        # Sankey Diagram for Cause-Effect
        st.subheader("Cause-Effect Diagram (Sankey)")
        categories = st.session_state.delays['Category'].unique().tolist()
        tasks = st.session_state.delays['Task'].unique().tolist()
        labels = categories + tasks
        source = []
        target = []
        value = []
        for _, row in st.session_state.delays.iterrows():
            source.append(categories.index(row['Category']))
            target.append(len(categories) + tasks.index(row['Task']))
            value.append(row['Delay_Days'])
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(label=labels),
            link=dict(source=source, target=target, value=value)
        )])
        fig_sankey.update_layout(title_text="Cause-Effect of Delays")
        st.plotly_chart(fig_sankey)

# Page 4: Mitigation & Reports
elif page == "Mitigation & Reports":
    st.header("Mitigation Strategies & Reports")
    if st.session_state.delays.empty:
        st.warning("No delays recorded. Please add delays in the 'Input Delays' section.")
    else:
        # Mitigation Recommendations
        st.subheader("Mitigation Recommendations")
        for category in st.session_state.delays['Category'].unique():
            st.write(f"**{category} Delays**")
            if category == 'Weather':
                st.write("- Schedule buffer days for weather uncertainties.")
                st.write("- Use weather-resistant materials.")
            elif category == 'Labor':
                st.write("- Offer overtime or hire additional workers.")
                st.write("- Improve worker training programs.")
            elif category == 'Materials':
                st.write("- Switch to alternative suppliers.")
                st.write("- Maintain buffer stock of critical materials.")
            elif category == 'Equipment':
                st.write("- Lease additional equipment.")
                st.write("- Schedule regular maintenance.")
            else:
                st.write("- Conduct root cause analysis.")
                st.write("- Engage with stakeholders for solutions.")

        # Export Report
        st.subheader("Export Delay Report")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            st.session_state.delays.to_excel(writer, sheet_name='Delays', index=False)
            category_summary = st.session_state.delays.groupby('Category').agg({
                'Delay_Days': 'sum',
                'Cost_Impact': 'sum'
            }).reset_index()
            category_summary.to_excel(writer, sheet_name='Summary', index=False)
        st.download_button(
            label="Download Delay Report (Excel)",
            data=buffer,
            file_name="delay_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | Integrated with Cost Estimators | Inspired by Primavera & Procore")
