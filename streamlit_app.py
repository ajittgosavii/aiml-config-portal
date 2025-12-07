# streamlit_app.py
"""
AI/ML Observability Platform - Configuration Portal
Self-service interface for engineers to configure data pipelines
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

# Mock plugin data (no imports needed!)
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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .plugin-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .plugin-card-free {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .plugin-card-pro {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .wizard-step {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .wizard-step-active {
        background: #e7f3ff;
        border-left-color: #0066cc;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("⚙️ Configuration Portal")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🎯 Quick Setup Wizard", "🔌 Plugin Marketplace", "📊 Pipeline Builder", "⚙️ Settings", "📚 Documentation"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard")
st.sidebar.markdown("[📈 Open Monitoring Dashboard](#)")

# Main content based on page selection
if page == "🏠 Home":
    st.markdown('<div class="main-header">🚀 AI/ML Observability Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Self-Service Configuration Portal</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the AI/ML Observability Configuration Portal! This self-service platform allows you to:
    
    - 🎯 **Configure data pipelines** in minutes without coding
    - 🔌 **Choose from 50+ plugins** for inputs, processing, outputs, and alerts
    - 📊 **Monitor your systems** with real-time dashboards
    - 🚀 **Deploy instantly** with zero DevOps required
    
    **Get started in 30 minutes** - No infrastructure setup needed!
    """)
    
    # Stats overview
    st.markdown("### 📊 Platform Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="plugin-card">', unsafe_allow_html=True)
        st.markdown("### 🔌 Plugins")
        total_plugins = sum(len(plugins) for plugins in MOCK_PLUGINS.values())
        st.markdown(f"### {total_plugins}")
        st.markdown("Available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="plugin-card plugin-card-free">', unsafe_allow_html=True)
        st.markdown("### ⚡ Pipelines")
        st.markdown(f"### {len(st.session_state.pipelines)}")
        st.markdown("Configured")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="plugin-card plugin-card-pro">', unsafe_allow_html=True)
        st.markdown("### 👥 Workspaces")
        st.markdown(f"### {len(st.session_state.workspaces) if len(st.session_state.workspaces) > 0 else 'Demo'}")
        st.markdown("Active")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🎯 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Start Quick Setup", type="primary", use_container_width=True):
            st.info("Navigate to '🎯 Quick Setup Wizard' in the sidebar!")
    
    with col2:
        if st.button("🔌 Browse Plugins", use_container_width=True):
            st.info("Navigate to '🔌 Plugin Marketplace' in the sidebar!")
    
    with col3:
        if st.button("📚 View Docs", use_container_width=True):
            st.info("Navigate to '📚 Documentation' in the sidebar!")
    
    st.markdown("---")
    
    # Features
    st.markdown("### ✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🚀 Self-Service Configuration**
        - Visual pipeline builder
        - No coding required
        - Test before deploying
        - Instant activation
        
        **🔌 Plugin Marketplace**
        - 50+ ready-to-use plugins
        - Input, processing, output, alerts
        - Free and premium options
        - One-click installation
        """)
    
    with col2:
        st.markdown("""
        **📊 Real-Time Monitoring**
        - Live dashboards
        - Performance metrics
        - Error tracking
        - Usage analytics
        
        **🔒 Enterprise Security**
        - Multi-tenant isolation
        - SSO integration
        - RBAC controls
        - Audit logging
        """)

elif page == "🎯 Quick Setup Wizard":
    st.markdown('<div class="main-header">🎯 Quick Setup Wizard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure your first pipeline in 6 easy steps</div>', unsafe_allow_html=True)
    
    # Progress indicator
    steps = ["Workspace", "Input", "Processing", "Output", "Alerts", "Review"]
    cols = st.columns(6)
    for idx, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if idx + 1 < st.session_state.wizard_step:
                st.success(f"✅ {step}")
            elif idx + 1 == st.session_state.wizard_step:
                st.info(f"▶️ {step}")
            else:
                st.text(f"⭕ {step}")
    
    st.markdown("---")
    
    # Step content
    if st.session_state.wizard_step == 1:
        st.markdown("### Step 1: Create Workspace")
        
        workspace_name = st.text_input("Workspace Name", placeholder="e.g., Production ML Monitoring")
        workspace_desc = st.text_area("Description", placeholder="e.g., Monitor production ML models and data pipelines")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Next Step ➡️", type="primary"):
                if workspace_name:
                    st.session_state.wizard_data['workspace_name'] = workspace_name
                    st.session_state.wizard_data['workspace_desc'] = workspace_desc
                    st.session_state.wizard_step = 2
                    st.rerun()
                else:
                    st.error("Please enter a workspace name")
    
    elif st.session_state.wizard_step == 2:
        st.markdown("### Step 2: Select Input Sources")
        st.markdown("Choose how you want to ingest logs and data:")
        
        selected_inputs = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['input']):
            with cols[idx % 2]:
                if st.checkbox(f"{plugin['icon']} {plugin['name']}", key=f"input_{idx}"):
                    selected_inputs.append(plugin['name'])
                st.caption(plugin['description'])
                st.caption(f"💰 {plugin['pricing']}")
        
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
                    st.error("Please select at least one input source")
    
    elif st.session_state.wizard_step == 3:
        st.markdown("### Step 3: Configure Processing")
        st.markdown("Choose how to process and enrich your data:")
        
        selected_processing = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['processing']):
            with cols[idx % 2]:
                if st.checkbox(f"{plugin['icon']} {plugin['name']}", key=f"proc_{idx}"):
                    selected_processing.append(plugin['name'])
                st.caption(plugin['description'])
                st.caption(f"💰 {plugin['pricing']}")
        
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
        st.markdown("Choose where to send your processed data:")
        
        selected_outputs = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['output']):
            with cols[idx % 2]:
                if st.checkbox(f"{plugin['icon']} {plugin['name']}", key=f"output_{idx}"):
                    selected_outputs.append(plugin['name'])
                st.caption(plugin['description'])
                st.caption(f"💰 {plugin['pricing']}")
        
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
                    st.error("Please select at least one output destination")
    
    elif st.session_state.wizard_step == 5:
        st.markdown("### Step 5: Configure Alerts (Optional)")
        st.markdown("Set up notifications for important events:")
        
        selected_alerts = []
        cols = st.columns(2)
        for idx, plugin in enumerate(MOCK_PLUGINS['alert']):
            with cols[idx % 2]:
                if st.checkbox(f"{plugin['icon']} {plugin['name']}", key=f"alert_{idx}"):
                    selected_alerts.append(plugin['name'])
                st.caption(plugin['description'])
                st.caption(f"💰 {plugin['pricing']}")
        
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
        st.markdown("Review your configuration and deploy:")
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("#### ✅ Configuration Summary")
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.wizard_step = 5
                st.rerun()
        with col2:
            if st.button("🚀 Deploy Now", type="primary"):
                # Save pipeline
                new_pipeline = {
                    'name': st.session_state.wizard_data.get('workspace_name'),
                    'created_at': datetime.now().isoformat(),
                    'config': st.session_state.wizard_data
                }
                st.session_state.pipelines.append(new_pipeline)
                
                st.success("🎉 Pipeline deployed successfully!")
                st.balloons()
                
                # Reset wizard
                st.session_state.wizard_step = 1
                st.session_state.wizard_data = {}
                
                st.info("Your pipeline is now active! Check the Pipeline Builder to manage it.")

elif page == "🔌 Plugin Marketplace":
    st.markdown('<div class="main-header">🔌 Plugin Marketplace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Browse and install plugins to extend your platform</div>', unsafe_allow_html=True)
    
    # Category tabs
    category = st.radio(
        "Category",
        ["All", "Input Sources", "Processing", "Outputs", "Alerts"],
        horizontal=True
    )
    
    # Filter plugins
    if category == "All":
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
    
    # Display plugins in grid
    cols = st.columns(3)
    for idx, plugin in enumerate(plugins_to_show):
        with cols[idx % 3]:
            pricing_class = "plugin-card" if plugin['pricing'] == 'Free' else "plugin-card-pro"
            st.markdown(f'<div class="{pricing_class}">', unsafe_allow_html=True)
            st.markdown(f"## {plugin['icon']} {plugin['name']}")
            st.markdown(plugin['description'])
            st.markdown(f"**Category:** {plugin['category'].title()}")
            st.markdown(f"**Pricing:** {plugin['pricing']}")
            
            if st.button("Install", key=f"install_{idx}"):
                st.success(f"Installed {plugin['name']}!")
            
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "📊 Pipeline Builder":
    st.markdown('<div class="main-header">📊 Pipeline Builder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage and monitor your data pipelines</div>', unsafe_allow_html=True)
    
    if len(st.session_state.pipelines) == 0:
        st.info("No pipelines configured yet. Use the Quick Setup Wizard to create your first pipeline!")
        
        if st.button("🎯 Go to Quick Setup Wizard", type="primary"):
            st.info("Navigate to '🎯 Quick Setup Wizard' in the sidebar!")
    else:
        st.markdown(f"### Active Pipelines ({len(st.session_state.pipelines)})")
        
        for idx, pipeline in enumerate(st.session_state.pipelines):
            with st.expander(f"📊 {pipeline['name']}", expanded=idx == 0):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Created:** {pipeline['created_at']}")
                    st.markdown(f"**Status:** 🟢 Active")
                    
                    config = pipeline['config']
                    st.markdown(f"**Inputs:** {', '.join(config.get('inputs', []))}")
                    if config.get('processing'):
                        st.markdown(f"**Processing:** {', '.join(config.get('processing', []))}")
                    st.markdown(f"**Outputs:** {', '.join(config.get('outputs', []))}")
                    if config.get('alerts'):
                        st.markdown(f"**Alerts:** {', '.join(config.get('alerts', []))}")
                
                with col2:
                    if st.button("⚙️ Configure", key=f"config_{idx}"):
                        st.info("Configuration panel would open here")
                    
                    if st.button("📊 Metrics", key=f"metrics_{idx}"):
                        st.info("Metrics dashboard would open here")
                    
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        st.session_state.pipelines.pop(idx)
                        st.rerun()

elif page == "⚙️ Settings":
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure your account and preferences</div>', unsafe_allow_html=True)
    
    st.markdown("### Account Settings")
    st.text_input("Organization Name", value="Demo Organization")
    st.text_input("Email", value="demo@example.com")
    
    st.markdown("---")
    st.markdown("### Workspace Settings")
    st.selectbox("Default Region", ["US East", "US West", "EU", "Asia Pacific"])
    st.selectbox("Data Retention", ["7 days", "30 days", "90 days", "1 year"])
    
    st.markdown("---")
    st.markdown("### Notifications")
    st.checkbox("Email notifications", value=True)
    st.checkbox("Slack notifications")
    st.checkbox("PagerDuty integration")
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

else:  # Documentation
    st.markdown('<div class="main-header">📚 Documentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Learn how to use the platform</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Getting Started
    
    ### Quick Setup Wizard
    The fastest way to get started! The wizard guides you through:
    1. Creating a workspace
    2. Selecting input sources
    3. Configuring processing
    4. Setting up outputs
    5. Configuring alerts (optional)
    6. Deploying your pipeline
    
    **Time to complete: 5-10 minutes**
    
    ### Plugin Marketplace
    Browse 50+ plugins across four categories:
    - **Input Sources**: Ingest data from various sources (CloudWatch, K8s, HTTP, Syslog, etc.)
    - **Processing**: Transform and enrich your data (parsing, filtering, masking, etc.)
    - **Outputs**: Send data to destinations (Splunk, S3, Elasticsearch, etc.)
    - **Alerts**: Get notified (Slack, PagerDuty, Email, Teams, etc.)
    
    ### Pipeline Builder
    Manage your active pipelines:
    - View pipeline status
    - Configure settings
    - Monitor metrics
    - Start/stop pipelines
    - Delete pipelines
    
    ## Key Concepts
    
    ### Workspaces
    Isolated environments for organizing your pipelines. Each workspace has:
    - Separate configuration
    - Independent data storage
    - Custom access controls
    
    ### Pipelines
    Data flows from input → processing → output, with optional alerts.
    
    ### Plugins
    Modular components that extend platform functionality.
    
    ## Pricing
    
    ### Starter (FREE)
    - 10 GB/day ingestion
    - 7 days retention
    - 5 users
    - 5 concurrent plugins
    - Community support
    
    ### Professional ($499/month)
    - 100 GB/day ingestion
    - 30 days retention
    - 25 users
    - 20 concurrent plugins
    - Business hours support
    - SSO integration
    
    ### Enterprise (Custom)
    - Unlimited ingestion
    - Custom retention
    - Unlimited users
    - Unlimited plugins
    - 24/7 support
    - Dedicated CSM
    - 99.9% SLA
    
    ## Support
    
    - **Community Forum**: https://discuss.yourplatform.com
    - **Email**: support@yourplatform.com
    - **Documentation**: https://docs.yourplatform.com
    - **Status Page**: https://status.yourplatform.com
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>AI/ML Observability Platform v1.0 | <a href='#'>Terms</a> | <a href='#'>Privacy</a> | <a href='#'>Support</a></p>
    <p>© 2024 Your Company. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)