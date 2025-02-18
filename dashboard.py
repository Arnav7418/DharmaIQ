import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from prometheus_client.parser import text_string_to_metric_families

# Configure page settings
st.set_page_config(
    page_title="📊 DharmaIQ Metrics Dashboard",
    page_icon="📊",
    layout="wide"
)

def fetch_metrics():
    try:
        response = requests.get("http://localhost:8000/metrics")
        return response.text
    except requests.RequestException:
        st.error("⚠️ Failed to connect to metrics endpoint")
        return None

def parse_metrics(metrics_text):
    if not metrics_text:
        return {}
    
    data = {}
    try:
        for family in text_string_to_metric_families(metrics_text):
            for sample in family.samples:
                name = sample.name
                value = sample.value
                labels = tuple(sorted(sample.labels.items()))
                data.setdefault(name, []).append({
                    'value': value,
                    'labels': dict(labels),
                    'timestamp': datetime.now()
                })
    except Exception as e:
        st.error(f"🚨 Error parsing metrics: {str(e)}")
    return data

def main():
    st.title("📈 DharmaIQ Monitoring Dashboard")
    
    if 'time_series_data' not in st.session_state:
        st.session_state.time_series_data = []
    
    metrics_text = fetch_metrics()
    if metrics_text:
        metrics_data = parse_metrics(metrics_text)
        
        st.session_state.time_series_data.append({
            'timestamp': datetime.now(),
            'data': metrics_data
        })
        
        cutoff_time = datetime.now() - timedelta(minutes=30)
        st.session_state.time_series_data = [
            entry for entry in st.session_state.time_series_data 
            if entry['timestamp'] > cutoff_time
        ]

        # Organizing the layout with tabs
        tab1, tab2, tab3 = st.tabs(["📌 Requests & Responses", "❌ Errors & Connections", "📊 Historical Data"])
        
        with tab1:
            st.subheader("Request Distribution")
            request_data = [
                {'source': metric['labels'].get('source', 'unknown'), 'count': metric['value']}
                for metric in metrics_data.get('app_requests_total', [])
            ]
            
            if request_data:
                df_requests = pd.DataFrame(request_data)
                fig = px.pie(df_requests, values='count', names='source',
                             title='Requests by Source',
                             color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Response Times")
            response_data = [
                {'source': metric['labels'].get('source', 'unknown'), 'time': round(metric['value'], 3)}
                for metric in metrics_data.get('app_response_time_seconds_sum', [])
            ]
            
            if response_data:
                df_response = pd.DataFrame(response_data)
                fig = px.bar(df_response, x='source', y='time',
                             title='Average Response Time by Source (seconds)',
                             color='source',
                             color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("Error Tracking")
            error_data = [
                {'type': metric['labels'].get('type', 'unknown'), 'count': metric['value']}
                for metric in metrics_data.get('app_errors_total', [])
            ]
            
            if error_data:
                df_errors = pd.DataFrame(error_data)
                fig = px.bar(df_errors, x='type', y='count',
                             title='Errors by Type',
                             color='type',
                             color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Active WebSocket Connections")
            connections = next(
                (m['value'] for m in metrics_data.get('app_active_connections', []) if not m['labels']),
                0
            )
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=connections,
                title={'text': "Active WebSocket Connections"},
                gauge={'axis': {'range': [0, max(10, connections)]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 5], 'color': "lightgray"},
                           {'range': [5, 8], 'color': "gray"}
                       ]}))
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.subheader("Historical Metrics (Last 30 minutes)")
            historical_data = [
                {'timestamp': entry['timestamp'],
                 'source': metric['labels'].get('source', 'unknown'),
                 'value': metric['value']}
                for entry in st.session_state.time_series_data 
                for metric in entry['data'].get('app_requests_total', [])
            ]
            
            if historical_data:
                df_historical = pd.DataFrame(historical_data)
                fig = px.line(df_historical, x='timestamp', y='value', 
                              color='source', 
                              title='Request Counts Over Time',
                              color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)

        time.sleep(5)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
