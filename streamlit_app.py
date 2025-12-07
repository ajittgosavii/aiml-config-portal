# streamlit_app.py
"""
AI/ML Observability Platform - Configuration Portal
Corporate Professional Edition
"""

import streamlit as st
import json
from typing import Dict, List, Any
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI/ML Observability - Config Portal",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize ALL session state variables at the very start
if 'workspaces' not in st.session_state:
    st.session_state.workspaces = []
if 'current_workspace' not in st.session_state:
    st.session_state.current_workspace = None
if 'pipelines' not in st.session_state:
    st.session_state.pipelines = []
if 'plugin_configs' not in st.session_state:
    st.session_state.plugin_configs = []
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1
if 'wizard_data' not in st.session_state:
    st.session_state.wizard_data = {}

# IMPORTANT: Set your actual dashboard URL here
DASHBOARD_URL = "https://aimldashboards.streamlit.app/"  # UPDATE THIS!

# Mock plugin data
MOCK_PLUGINS = {
    'input': [
        {
            'name': 'HTTP Endpoint',
            'description': 'Receive logs via HTTP POST',
            'category': 'input',
            'pricing': 'Free',
            'icon': '🌐'
        },
        {
            'name': 'AWS CloudWatch',
            'description': 'Ingest from CloudWatch Logs',
            'category': 'input',
            'pricing': 'Pro',
            'icon': '☁️'
        },
        {
            'name': 'Kubernetes',
            'description': 'Collect from K8s clusters',
            'category': 'input',
            'pricing': 'Pro',
            'icon': '⎈'
        },
        {
            'name': 'Syslog',
            'description': 'Standard syslog protocol',
            'category': 'input',
            'pricing': 'Free',
            'icon': '📋'
        }
    ],
    'processing': [
        {
            'name': 'JSON Parser',
            'description': 'Parse and flatten JSON logs',
            'category': 'processing',
            'pricing': 'Free',
            'icon': '📝'
        },
        {
            'name': 'Regex Parser',
            'description': 'Extract fields using regex',
            'category': 'processing',
            'pricing': 'Free',
            'icon': '🔍'
        },
        {
            'name': 'PII Masking',
            'description': 'Mask sensitive data',
            'category': 'processing',
            'pricing': 'Pro',
            'icon': '🔒'
        },
        {
            'name': 'Geo-IP Lookup',
            'description': 'Enrich with location data',
            'category': 'processing',
            'pricing': 'Pro',
            'icon': '🌍'
        }
    ],
    'output': [
        {
            'name': 'Webhook',
            'description': 'Send to HTTP endpoint',
            'category': 'output',
            'pricing': 'Free',
            'icon': '🔗'
        },
        {
            'name': 'Splunk HEC',
            'description': 'Send to Splunk via HEC',
            'category': 'output',
            'pricing': 'Pro',
            'icon': '📊'
        },
        {
            'name': 'S3 Bucket',
            'description': 'Store in AWS S3',
            'category': 'output',
            'pricing': 'Pro',
            'icon': '🗄️'
        },
        {
            'name': 'Elasticsearch',
            'description': 'Index in Elasticsearch',
            'category': 'output',
            'pricing': 'Pro',
            'icon': '🔎'
        }
    ],
    'alert': [
        {
            'name': 'Slack',
            'description': 'Send alerts to Slack',
            'category': 'alert',
            'pricing': 'Free',
            'icon': '💬'
        },
        {
            'name': 'PagerDuty',
            'description': 'Create PagerDuty incidents',
            'category': 'alert',
            'pricing': 'Pro',
            'icon': '🚨'
        },
        {
            'name': 'Email',
            'description': 'Send email notifications',
            'category': 'alert',
            'pricing': 'Free',
            'icon': '📧'
        },
        {
            'name': 'Microsoft Teams',
            'description': 'Post to Teams channels',
            'category': 'alert',
            'pricing': 'Pro',
            'icon': '👥'
        }
    ]
}

# Corporate Professional CSS
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #f5f7fa;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Metric Cards - Corporate Design */
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .metric-sublabel {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    
    /* Plugin Cards - Corporate Design */
    .plugin-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .plugin-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    .plugin-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .plugin-icon {
        font-size: 2rem;
        margin-right: 0.75rem;
    }
    
    .plugin-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
    }
    
    .plugin-description {
        color: #64748b;
        font-size: 0.9rem;
        margin: 0.5rem 0 1rem 0;
        line-height: 1.5;
    }
    
    .plugin-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.85rem;
    }
    
    .plugin-category {
        color: #3b82f6;
        font-weight: 600;
    }
    
    .plugin-pricing {
        color: #10b981;
        font-weight: 600;
    }
    
    .plugin-pricing-pro {
        color: #f59e0b;
        font-weight: 600;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-active {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-inactive {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Alert Boxes */
    .alert-success {
        background: #d1fae5;
        border: 1px solid #a7f3d0;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        color: #065f46;
        margin: 1rem 0;
    }
    
    .alert-info {
        background: #dbeafe;
        border: 1px solid #bfdbfe;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        color: #1e40af;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: #fef3c7;
        border: 1px solid #fde68a;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        color: #92400e;
        margin: 1rem 0;
    }
    
    /* Wizard Steps */
    .wizard-progress {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .wizard-step {
        text-align: center;
        padding: 0.75rem;
    }
    
    .wizard-step-number {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin: 0 auto 0.5rem;
    }
    
    .wizard-step-active .wizard-step-number {
        background: #3b82f6;
        color: white;
    }
    
    .wizard-step-complete .wizard-step-number {
        background: #10b981;
        color: white;
    }
    
    .wizard-step-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
    }
    
    .wizard-step-active .wizard-step-label {
        color: #3b82f6;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Feature Grid */
    .feature-item {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Buttons Enhancement */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }
    
    /* Sidebar Styling - Corporate Professional */
    [data-testid="stSidebar"] {
        background: #1e293b;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        color: #e2e8f0 !important;
    }
    
    /* Dashboard Link Styling */
    .dashboard-link {
        display: block;
        background: #3b82f6;
        color: white !important;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        text-align: center;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.2s ease;
        margin: 1rem 0;
    }
    
    .dashboard-link:hover {
        background: #2563eb;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(59,130,246,0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }
    
    .footer a {
        color: #3b82f6;
        text-decoration: none;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .metric-card {
            margin-bottom: 1rem;
        }
        
        .main-header {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation - Corporate Professional
st.sidebar.markdown("# ⚙️ Configuration Portal")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🎯 Quick Setup Wizard", "🔌 Plugin Marketplace", "📊 Pipeline Builder", "⚙️ Settings", "📚 Documentation"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Monitoring")

# WORKING DASHBOARD LINK
st.sidebar.markdown(f"""
<a href="{DASHBOARD_URL}" target="_blank" class="dashboard-link">
    📈 Open Dashboard →
</a>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Quick Stats")
st.sidebar.metric("Active Pipelines", len(st.session_state.pipelines))
st.sidebar.metric("Available Plugins", sum(len(plugins) for plugins in MOCK_PLUGINS.values()))

# Main content based on page selection
if page == "🏠 Home":
    st.markdown('<div class="main-header">AI/ML Observability Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enterprise-grade observability for AI/ML systems • Self-service configuration in minutes</div>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    <div class="alert-info">
        <strong>🎉 Welcome to the Configuration Portal!</strong><br>
        Set up comprehensive monitoring for your AI/ML infrastructure without writing a single line of code.
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics overview
    st.markdown('<div class="section-header">📊 Platform Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">🔌</div>
            <div class="metric-value">16</div>
            <div class="metric-label">Available Plugins</div>
            <div class="metric-sublabel">Across 4 categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{len(st.session_state.pipelines)}</div>
            <div class="metric-label">Active Pipelines</div>
            <div class="metric-sublabel">Configured & running</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">Demo</div>
            <div class="metric-label">Workspace</div>
            <div class="metric-sublabel">Development environment</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown('<div class="section-header">🎯 Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("🚀 Start Quick Setup", type="primary", use_container_width=True, help="Launch the setup wizard")
    
    with col2:
        st.button("🔌 Browse Plugins", use_container_width=True, help="Explore available plugins")
    
    with col3:
        st.button("📚 View Documentation", use_container_width=True, help="Read the docs")
    
    # Key features
    st.markdown('<div class="section-header">✨ Key Features</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-item">
            <div class="feature-title">🚀 Self-Service Configuration</div>
            <div class="feature-description">
                Configure data pipelines in minutes with our visual wizard. No coding required—test before deploying and activate instantly.
            </div>
        </div>
        
        <div class="feature-item">
            <div class="feature-title">🔌 Plugin Marketplace</div>
            <div class="feature-description">
                Choose from 50+ ready-to-use plugins for inputs, processing, outputs, and alerts. Mix and match to build your perfect pipeline.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-item">
            <div class="feature-title">📊 Real-Time Monitoring</div>
            <div class="feature-description">
                Live dashboards with performance metrics, error tracking, and usage analytics. Know exactly what's happening in your systems.
            </div>
        </div>
        
        <div class="feature-item">
            <div class="feature-title">🔒 Enterprise Security</div>
            <div class="feature-description">
                Multi-tenant workspace isolation, SSO integration, RBAC controls, and comprehensive audit logging for compliance.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started
    st.markdown('<div class="section-header">🎓 Getting Started</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-item">
        <strong>Step 1:</strong> Navigate to the <strong>Quick Setup Wizard</strong> in the sidebar<br>
        <strong>Step 2:</strong> Follow the 6-step process to configure your first pipeline<br>
        <strong>Step 3:</strong> Deploy and start monitoring in real-time<br><br>
        <strong>⏱️ Total time: 5-10 minutes</strong>
    </div>
    """, unsafe_allow_html=True)

elif page == "🎯 Quick Setup Wizard":
    st.markdown('<div class="main-header">Quick Setup Wizard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure your observability pipeline in 6 simple steps</div>', unsafe_allow_html=True)
    
    # Progress indicator
    st.markdown('<div class="wizard-progress">', unsafe_allow_html=True)
    steps = ["Workspace", "Input", "Processing", "Output", "Alerts", "Review"]
    cols = st.columns(6)
    for idx, (col, step) in enumerate(zip(cols, steps)):
        with col:
            step_class = ""
            if idx + 1 < st.session_state.wizard_step:
                step_class = "wizard-step-complete"
                icon = "✅"
            elif idx + 1 == st.session_state.wizard_step:
                step_class = "wizard-step-active"
                icon = "▶️"
            else:
                icon = f"{idx + 1}"
            
            st.markdown(f"""
            <div class="wizard-step {step_class}">
                <div class="wizard-step-number">{icon}</div>
                <div class="wizard-step-label">{step}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Step content (same as before)
    if st.session_state.wizard_step == 1:
        st.markdown("### Step 1: Create Workspace")
        st.markdown("Define your workspace for organizing pipelines and resources.")
        
        workspace_name = st.text_input("Workspace Name *", placeholder="e.g., Production ML Monitoring")
        workspace_desc = st.text_area("Description", placeholder="e.g., Monitor production ML models and data pipelines")
        
        st.markdown("---")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Next Step ➡️", type="primary"):
                if workspace_name:
                    st.session_state.wizard_data['workspace_name'] = workspace_name
                    st.session_state.wizard_data['workspace_desc'] = workspace_desc
                    st.session_state.wizard_step = 2
                    st.rerun()
                else:
                    st.error("⚠️ Please enter a workspace name")
    
    elif st.session_state.wizard_step == 2:
        st.markdown("### Step 2: Select Input Sources")
        st.markdown("Choose how you want to ingest logs and metrics into the platform.")
        
        selected_inputs = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['input']):
            with cols[idx % 2]:
                pricing_class = "plugin-pricing" if plugin['pricing'] == 'Free' else "plugin-pricing-pro"
                st.markdown(f"""
                <div class="plugin-card">
                    <div class="plugin-card-header">
                        <span class="plugin-icon">{plugin['icon']}</span>
                        <h3 class="plugin-name">{plugin['name']}</h3>
                    </div>
                    <p class="plugin-description">{plugin['description']}</p>
                    <div class="plugin-meta">
                        <span class="plugin-category">📁 {plugin['category'].title()}</span>
                        <span class="{pricing_class}">💰 {plugin['pricing']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.checkbox(f"Select {plugin['name']}", key=f"input_{idx}"):
                    selected_inputs.append(plugin['name'])
        
        st.markdown("---")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Next Step ➡️", type="primary"):
                if selected_inputs:
                    st.session_state.wizard_data['inputs'] = selected_inputs
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.error("⚠️ Please select at least one input source")
    
    elif st.session_state.wizard_step == 3:
        st.markdown("### Step 3: Configure Processing")
        st.markdown("Transform and enrich your data as it flows through the pipeline.")
        
        selected_processing = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['processing']):
            with cols[idx % 2]:
                pricing_class = "plugin-pricing" if plugin['pricing'] == 'Free' else "plugin-pricing-pro"
                st.markdown(f"""
                <div class="plugin-card">
                    <div class="plugin-card-header">
                        <span class="plugin-icon">{plugin['icon']}</span>
                        <h3 class="plugin-name">{plugin['name']}</h3>
                    </div>
                    <p class="plugin-description">{plugin['description']}</p>
                    <div class="plugin-meta">
                        <span class="plugin-category">📁 {plugin['category'].title()}</span>
                        <span class="{pricing_class}">💰 {plugin['pricing']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.checkbox(f"Select {plugin['name']}", key=f"proc_{idx}"):
                    selected_processing.append(plugin['name'])
        
        st.markdown("---")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Next Step ➡️", type="primary"):
                st.session_state.wizard_data['processing'] = selected_processing
                st.session_state.wizard_step = 4
                st.rerun()
    
    elif st.session_state.wizard_step == 4:
        st.markdown("### Step 4: Select Output Destinations")
        st.markdown("Define where your processed data should be sent.")
        
        selected_outputs = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['output']):
            with cols[idx % 2]:
                pricing_class = "plugin-pricing" if plugin['pricing'] == 'Free' else "plugin-pricing-pro"
                st.markdown(f"""
                <div class="plugin-card">
                    <div class="plugin-card-header">
                        <span class="plugin-icon">{plugin['icon']}</span>
                        <h3 class="plugin-name">{plugin['name']}</h3>
                    </div>
                    <p class="plugin-description">{plugin['description']}</p>
                    <div class="plugin-meta">
                        <span class="plugin-category">📁 {plugin['category'].title()}</span>
                        <span class="{pricing_class}">💰 {plugin['pricing']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.checkbox(f"Select {plugin['name']}", key=f"output_{idx}"):
                    selected_outputs.append(plugin['name'])
        
        st.markdown("---")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Next Step ➡️", type="primary"):
                if selected_outputs:
                    st.session_state.wizard_data['outputs'] = selected_outputs
                    st.session_state.wizard_step = 5
                    st.rerun()
                else:
                    st.error("⚠️ Please select at least one output destination")
    
    elif st.session_state.wizard_step == 5:
        st.markdown("### Step 5: Configure Alerts (Optional)")
        st.markdown("Set up notifications to stay informed about important events.")
        
        selected_alerts = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['alert']):
            with cols[idx % 2]:
                pricing_class = "plugin-pricing" if plugin['pricing'] == 'Free' else "plugin-pricing-pro"
                st.markdown(f"""
                <div class="plugin-card">
                    <div class="plugin-card-header">
                        <span class="plugin-icon">{plugin['icon']}</span>
                        <h3 class="plugin-name">{plugin['name']}</h3>
                    </div>
                    <p class="plugin-description">{plugin['description']}</p>
                    <div class="plugin-meta">
                        <span class="plugin-category">📁 {plugin['category'].title()}</span>
                        <span class="{pricing_class}">💰 {plugin['pricing']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.checkbox(f"Select {plugin['name']}", key=f"alert_{idx}"):
                    selected_alerts.append(plugin['name'])
        
        st.markdown("---")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.wizard_step = 4
                st.rerun()
        with col2:
            if st.button("Next Step ➡️", type="primary"):
                st.session_state.wizard_data['alerts'] = selected_alerts
                st.session_state.wizard_step = 6
                st.rerun()
    
    elif st.session_state.wizard_step == 6:
        st.markdown("### Step 6: Review & Deploy")
        st.markdown("Review your configuration and deploy your pipeline.")
        
        st.markdown("""
        <div class="alert-success">
            <h4>✅ Configuration Complete!</h4>
            <p>Your pipeline is ready to deploy. Review the summary below:</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Workspace:** {st.session_state.wizard_data.get('workspace_name', 'N/A')}")
        st.markdown(f"**Description:** {st.session_state.wizard_data.get('workspace_desc', 'N/A')}")
        
        st.markdown(f"**Input Sources ({len(st.session_state.wizard_data.get('inputs', []))}):**")
        for input_name in st.session_state.wizard_data.get('inputs', []):
            st.markdown(f"- {input_name}")
        
        if st.session_state.wizard_data.get('processing'):
            st.markdown(f"**Processing ({len(st.session_state.wizard_data.get('processing', []))}):**")
            for proc_name in st.session_state.wizard_data.get('processing', []):
                st.markdown(f"- {proc_name}")
        
        st.markdown(f"**Output Destinations ({len(st.session_state.wizard_data.get('outputs', []))}):**")
        for output_name in st.session_state.wizard_data.get('outputs', []):
            st.markdown(f"- {output_name}")
        
        if st.session_state.wizard_data.get('alerts'):
            st.markdown(f"**Alerts ({len(st.session_state.wizard_data.get('alerts', []))}):**")
            for alert_name in st.session_state.wizard_data.get('alerts', []):
                st.markdown(f"- {alert_name}")
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.wizard_step = 5
                st.rerun()
        with col2:
            if st.button("🚀 Deploy Pipeline", type="primary"):
                # Save pipeline
                new_pipeline = {
                    'name': st.session_state.wizard_data.get('workspace_name'),
                    'created_at': datetime.now().isoformat(),
                    'config': st.session_state.wizard_data,
                    'status': 'active'
                }
                st.session_state.pipelines.append(new_pipeline)
                
                st.markdown("""
                <div class="alert-success">
                    <h3>🎉 Pipeline Deployed Successfully!</h3>
                    <p>Your pipeline is now active and processing data.</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                
                # Reset wizard
                st.session_state.wizard_step = 1
                st.session_state.wizard_data = {}

elif page == "🔌 Plugin Marketplace":
    st.markdown('<div class="main-header">Plugin Marketplace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Explore and install plugins to extend your observability platform</div>', unsafe_allow_html=True)
    
    # Category filter
    category = st.radio(
        "Filter by Category",
        ["All Plugins", "Input Sources", "Processing", "Outputs", "Alerts"],
        horizontal=True
    )
    
    # Filter plugins
    if category == "All Plugins":
        plugins_to_show = []
        for cat_plugins in MOCK_PLUGINS.values():
            plugins_to_show.extend(cat_plugins)
    elif category == "Input Sources":
        plugins_to_show = MOCK_PLUGINS['input']
    elif category == "Processing":
        plugins_to_show = MOCK_PLUGINS['processing']
    elif category == "Outputs":
        plugins_to_show = MOCK_PLUGINS['output']
    else:  # Alerts
        plugins_to_show = MOCK_PLUGINS['alert']
    
    st.markdown(f"### {len(plugins_to_show)} Plugins Available")
    
    # Display plugins in grid
    cols = st.columns(3)
    for idx, plugin in enumerate(plugins_to_show):
        with cols[idx % 3]:
            pricing_class = "plugin-pricing" if plugin['pricing'] == 'Free' else "plugin-pricing-pro"
            st.markdown(f"""
            <div class="plugin-card">
                <div class="plugin-card-header">
                    <span class="plugin-icon">{plugin['icon']}</span>
                    <h3 class="plugin-name">{plugin['name']}</h3>
                </div>
                <p class="plugin-description">{plugin['description']}</p>
                <div class="plugin-meta">
                    <span class="plugin-category">📁 {plugin['category'].title()}</span>
                    <span class="{pricing_class}">💰 {plugin['pricing']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📥 Install", key=f"install_{idx}", use_container_width=True):
                    st.success(f"✅ Installed {plugin['name']}!")
            with col_b:
                if st.button("ℹ️ Details", key=f"details_{idx}", use_container_width=True):
                    st.info(f"Details for {plugin['name']}")

elif page == "📊 Pipeline Builder":
    st.markdown('<div class="main-header">Pipeline Builder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage and monitor your active data pipelines</div>', unsafe_allow_html=True)
    
    if len(st.session_state.pipelines) == 0:
        st.markdown("""
        <div class="alert-info">
            <h4>📝 No Pipelines Yet</h4>
            <p>Get started by creating your first pipeline using the Quick Setup Wizard.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 Launch Quick Setup Wizard", type="primary"):
            st.info("Navigate to '🎯 Quick Setup Wizard' in the sidebar to begin!")
    else:
        st.markdown(f'<div class="section-header">Active Pipelines ({len(st.session_state.pipelines)})</div>', unsafe_allow_html=True)
        
        for idx, pipeline in enumerate(st.session_state.pipelines):
            with st.expander(f"📊 {pipeline['name']}", expanded=idx == 0):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Created:** {pipeline['created_at']}")
                    st.markdown('<span class="status-badge status-active">🟢 Active</span>', unsafe_allow_html=True)
                    
                    config = pipeline['config']
                    st.markdown(f"\n**Inputs:** {', '.join(config.get('inputs', []))}")
                    if config.get('processing'):
                        st.markdown(f"**Processing:** {', '.join(config.get('processing', []))}")
                    st.markdown(f"**Outputs:** {', '.join(config.get('outputs', []))}")
                    if config.get('alerts'):
                        st.markdown(f"**Alerts:** {', '.join(config.get('alerts', []))}")
                
                with col2:
                    if st.button("⚙️ Configure", key=f"config_{idx}", use_container_width=True):
                        st.info("Configuration panel")
                    
                    if st.button("📊 Metrics", key=f"metrics_{idx}", use_container_width=True):
                        st.info("Metrics dashboard")
                    
                    if st.button("🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                        st.session_state.pipelines.pop(idx)
                        st.rerun()

elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure your account and workspace preferences</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Account Settings</div>', unsafe_allow_html=True)
    st.text_input("Organization Name", value="Demo Organization")
    st.text_input("Email Address", value="demo@example.com")
    
    st.markdown('<div class="section-header">Workspace Settings</div>', unsafe_allow_html=True)
    st.selectbox("Default Region", ["US East (N. Virginia)", "US West (Oregon)", "EU (Ireland)", "Asia Pacific (Tokyo)"])
    st.selectbox("Data Retention Period", ["7 days", "30 days", "90 days", "1 year", "Custom"])
    
    st.markdown('<div class="section-header">Notifications</div>', unsafe_allow_html=True)
    st.checkbox("📧 Email notifications", value=True)
    st.checkbox("💬 Slack notifications")
    st.checkbox("🚨 PagerDuty integration")
    
    st.markdown("---")
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")

else:  # Documentation
    st.markdown('<div class="main-header">Documentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Everything you need to know about the platform</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Getting Started</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Quick Setup Wizard
    The fastest way to configure your observability pipeline:
    
    1. **Create Workspace** - Define your organizational workspace
    2. **Select Inputs** - Choose your data sources
    3. **Configure Processing** - Transform and enrich data
    4. **Set Outputs** - Define destinations
    5. **Add Alerts** - Set up notifications (optional)
    6. **Deploy** - Activate your pipeline
    
    **⏱️ Time to complete: 5-10 minutes**
    """)
    
    st.markdown('<div class="section-header">Plugin Categories</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Input Sources (4 plugins)
    Ingest data from various sources:
    - **HTTP Endpoint**: Receive logs via HTTP POST
    - **AWS CloudWatch**: Stream from CloudWatch Logs
    - **Kubernetes**: Collect from K8s clusters
    - **Syslog**: Standard syslog protocol
    
    ### Processing (4 plugins)
    Transform and enrich your data:
    - **JSON Parser**: Parse and flatten JSON
    - **Regex Parser**: Extract fields with regex
    - **PII Masking**: Mask sensitive data
    - **Geo-IP Lookup**: Add location data
    
    ### Outputs (4 plugins)
    Send data to destinations:
    - **Webhook**: HTTP endpoints
    - **Splunk HEC**: Splunk integration
    - **S3 Bucket**: AWS S3 storage
    - **Elasticsearch**: Search and analytics
    
    ### Alerts (4 plugins)
    Get notified about events:
    - **Slack**: Team notifications
    - **PagerDuty**: Incident management
    - **Email**: Email alerts
    - **Microsoft Teams**: Team collaboration
    """)
    
    st.markdown('<div class="section-header">Pricing Tiers</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Starter (FREE)**
        - 10 GB/day ingestion
        - 7 days retention
        - 5 users
        - 5 concurrent plugins
        - Community support
        """)
    
    with col2:
        st.markdown("""
        **Professional ($499/mo)**
        - 100 GB/day ingestion
        - 30 days retention
        - 25 users
        - 20 concurrent plugins
        - Business support
        - SSO integration
        """)
    
    with col3:
        st.markdown("""
        **Enterprise (Custom)**
        - Unlimited ingestion
        - Custom retention
        - Unlimited users
        - Unlimited plugins
        - 24/7 premium support
        - 99.9% SLA
        """)

# Professional Footer
st.markdown("""
<div class="footer">
    <p><strong>AI/ML Observability Platform</strong> v1.0</p>
    <p>
        <a href="#">Terms of Service</a> • 
        <a href="#">Privacy Policy</a> • 
        <a href="#">Documentation</a> • 
        <a href="#">Support</a>
    </p>
    <p style="color: #94a3b8; font-size: 0.85rem;">© 2024 Your Company. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)