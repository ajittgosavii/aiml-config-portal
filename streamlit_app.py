# config_portal.py
"""
AI/ML Observability Platform - Configuration Portal
Self-service interface for engineers to configure data pipelines
"""

import streamlit as st
import json
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import plugin system (would be from package in production)
try:
    from plugin_manager import (
        PluginRegistry, PluginManager, Pipeline,
        PluginType, PluginMetadata, ConfigField
    )
    # Register example plugins
    from plugins.http_input import HTTPInputPlugin
    from plugins.json_parser import JSONParserPlugin
    from plugins.webhook_output import WebhookOutputPlugin
    from plugins.slack_alert import SlackAlertPlugin
    
    # Initialize plugin registry
    if 'plugin_registry' not in st.session_state:
        registry = PluginRegistry()
        registry.register(HTTPInputPlugin)
        registry.register(JSONParserPlugin)
        registry.register(WebhookOutputPlugin)
        registry.register(SlackAlertPlugin)
        st.session_state.plugin_registry = registry
        st.session_state.plugin_manager = PluginManager(registry)
        st.session_state.pipelines = {}
    
    PLUGINS_AVAILABLE = True
except Exception as e:
    PLUGINS_AVAILABLE = False
    st.error(f"⚠️ Plugin system not available: {e}")

# Page config
st.set_page_config(
    page_title="Configuration Portal - AI/ML Observability",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Modern dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #2d3748 100%);
    }
    
    /* Plugin cards */
    .plugin-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .plugin-card-free {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .plugin-card-enterprise {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Status badges */
    .status-healthy {
        background-color: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .status-warning {
        background-color: #f59e0b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* Configuration wizard */
    .wizard-step {
        background: #f3f4f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .wizard-step-active {
        background: #dbeafe;
        border-left: 4px solid #3b82f6;
    }
    
    .wizard-step-complete {
        background: #d1fae5;
        border-left: 4px solid #10b981;
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 6px;
    }
    
    /* Pipeline builder */
    .pipeline-node {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .pipeline-arrow {
        text-align: center;
        font-size: 1.5rem;
        color: #6b7280;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
    st.session_state.workspace_config = {}
    st.session_state.selected_inputs = []
    st.session_state.selected_processors = []
    st.session_state.selected_outputs = []
    st.session_state.configured_plugins = {}

# Header
st.markdown("# ⚙️ Configuration Portal")
st.markdown("### Configure your AI/ML observability pipeline in minutes")

# Sidebar navigation
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    
    page = st.radio(
        "Choose a page:",
        [
            "🏠 Dashboard",
            "🔌 Plugin Marketplace",
            "🎯 Quick Setup Wizard",
            "⚡ Pipeline Builder",
            "🔧 Plugin Configuration",
            "📊 Monitoring",
            "📚 Documentation"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Quick Stats")
    
    if PLUGINS_AVAILABLE:
        registry = st.session_state.plugin_registry
        manager = st.session_state.plugin_manager
        
        input_plugins = len(registry.list_plugins(PluginType.INPUT))
        processing_plugins = len(registry.list_plugins(PluginType.PROCESSING))
        output_plugins = len(registry.list_plugins(PluginType.OUTPUT))
        alert_plugins = len(registry.list_plugins(PluginType.ALERT))
        
        st.metric("Available Plugins", input_plugins + processing_plugins + output_plugins + alert_plugins)
        st.metric("Configured Instances", len(manager.list_instances()))
        st.metric("Active Pipelines", len(st.session_state.pipelines))

# Main content based on selected page
if page == "🏠 Dashboard":
    st.markdown("## Welcome to Your Configuration Portal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="plugin-card plugin-card-free">', unsafe_allow_html=True)
        st.markdown("### 🔌 Plugins")
        if PLUGINS_AVAILABLE:
            total_plugins = len(st.session_state.plugin_registry.list_plugins())
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
        st.markdown('<div class="plugin-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Data Flow")
        st.markdown("### 0 GB/day")
        st.markdown("Processing")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="plugin-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Health")
        st.markdown('<div class="status-healthy">All Systems Operational</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Start Guide
    st.markdown("## 🚀 Quick Start")
    
    with st.expander("⚡ Set up your first pipeline in 5 minutes", expanded=True):
        st.markdown("""
        1. **Choose Data Sources** - Select where your logs come from (CloudWatch, K8s, HTTP, etc.)
        2. **Configure Processing** - Add parsers, filters, enrichment
        3. **Set Destinations** - Choose where to send processed logs (Splunk, S3, etc.)
        4. **Configure Alerts** - Set up notifications for critical events
        5. **Deploy** - Activate your pipeline with one click
        
        [Start Quick Setup Wizard →](#)
        """)
    
    with st.expander("📖 Browse Plugin Marketplace"):
        st.markdown("""
        Explore 50+ ready-to-use plugins:
        - **Input Plugins**: AWS, Azure, GCP, Kubernetes, HTTP, Syslog
        - **Processing Plugins**: Parsers, filters, enrichment, PII masking
        - **Output Plugins**: Splunk, Elasticsearch, S3, Snowflake
        - **Alert Plugins**: Slack, PagerDuty, ServiceNow, Email
        
        [Browse Plugins →](#)
        """)
    
    # Recent Activity
    st.markdown("## 📝 Recent Activity")
    
    if not st.session_state.pipelines:
        st.info("👋 No pipelines configured yet. Use the Quick Setup Wizard to get started!")
    else:
        for pipeline_name in st.session_state.pipelines:
            st.markdown(f"✅ Pipeline '{pipeline_name}' deployed")

elif page == "🔌 Plugin Marketplace":
    st.markdown("## 🔌 Plugin Marketplace")
    st.markdown("Browse and install ready-to-use plugins for your observability platform")
    
    if not PLUGINS_AVAILABLE:
        st.error("Plugin system not initialized")
        st.stop()
    
    # Category filter
    category_filter = st.selectbox(
        "Filter by category:",
        ["All", "Input", "Processing", "Output", "Alert", "Analytics"]
    )
    
    # Get plugins
    registry = st.session_state.plugin_registry
    
    if category_filter == "All":
        plugins = registry.list_plugins()
    else:
        category_map = {
            "Input": PluginType.INPUT,
            "Processing": PluginType.PROCESSING,
            "Output": PluginType.OUTPUT,
            "Alert": PluginType.ALERT,
            "Analytics": PluginType.ANALYTICS
        }
        plugins = registry.list_plugins(category_map[category_filter])
    
    # Display plugins in grid
    cols_per_row = 2
    for i in range(0, len(plugins), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j in range(cols_per_row):
            if i + j < len(plugins):
                plugin = plugins[i + j]
                
                with cols[j]:
                    pricing_class = "plugin-card-free" if plugin['pricing'] == "free" else "plugin-card-enterprise"
                    st.markdown(f'<div class="plugin-card {pricing_class}">', unsafe_allow_html=True)
                    
                    st.markdown(f"### {plugin['name']}")
                    st.markdown(f"**Category**: {plugin['category']}")
                    st.markdown(f"**Version**: {plugin['version']}")
                    st.markdown(f"{plugin['description']}")
                    st.markdown(f"**Pricing**: {plugin['pricing'].upper()}")
                    st.markdown(f"**Tags**: {', '.join(plugin['tags'][:3])}")
                    
                    if st.button(f"Configure {plugin['name']}", key=f"config_{plugin['id']}"):
                        st.session_state.selected_plugin = plugin['id']
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

elif page == "🎯 Quick Setup Wizard":
    st.markdown("## 🎯 Quick Setup Wizard")
    st.markdown("Configure your complete observability pipeline step-by-step")
    
    if not PLUGINS_AVAILABLE:
        st.error("Plugin system not initialized")
        st.stop()
    
    # Progress tracker
    steps = [
        "Workspace",
        "Data Sources",
        "Processing",
        "Outputs",
        "Alerts",
        "Review"
    ]
    
    current_step = st.session_state.current_step
    
    # Progress bar
    progress_col1, progress_col2 = st.columns([3, 1])
    with progress_col1:
        st.progress((current_step + 1) / len(steps))
    with progress_col2:
        st.markdown(f"**Step {current_step + 1} of {len(steps)}**")
    
    # Step indicators
    step_cols = st.columns(len(steps))
    for i, step_name in enumerate(steps):
        with step_cols[i]:
            if i < current_step:
                st.markdown(f"✅ {step_name}")
            elif i == current_step:
                st.markdown(f"➡️ **{step_name}**")
            else:
                st.markdown(f"⭕ {step_name}")
    
    st.markdown("---")
    
    # Step content
    if current_step == 0:  # Workspace
        st.markdown("### 🏢 Workspace Configuration")
        
        workspace_name = st.text_input(
            "Workspace Name",
            value=st.session_state.workspace_config.get('name', ''),
            placeholder="My Company Observability"
        )
        
        workspace_tier = st.selectbox(
            "Tier",
            ["Starter (Free)", "Professional ($499/mo)", "Enterprise (Custom)"]
        )
        
        workspace_region = st.selectbox(
            "Region",
            ["US East (N. Virginia)", "EU West (Ireland)", "AP South (Mumbai)"]
        )
        
        if st.button("Next →", type="primary"):
            st.session_state.workspace_config = {
                'name': workspace_name,
                'tier': workspace_tier,
                'region': workspace_region
            }
            st.session_state.current_step = 1
            st.rerun()
    
    elif current_step == 1:  # Data Sources
        st.markdown("### 📥 Select Data Sources")
        
        registry = st.session_state.plugin_registry
        input_plugins = registry.list_plugins(PluginType.INPUT)
        
        st.markdown("Choose which data sources to connect:")
        
        selected = []
        for plugin in input_plugins:
            if st.checkbox(
                f"{plugin['name']} - {plugin['description'][:80]}...",
                key=f"input_{plugin['id']}"
            ):
                selected.append(plugin['id'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.current_step = 0
                st.rerun()
        with col2:
            if st.button("Next →", type="primary"):
                st.session_state.selected_inputs = selected
                st.session_state.current_step = 2
                st.rerun()
    
    elif current_step == 2:  # Processing
        st.markdown("### ⚙️ Configure Processing")
        
        registry = st.session_state.plugin_registry
        processing_plugins = registry.list_plugins(PluginType.PROCESSING)
        
        st.markdown("Add processing steps to transform and enrich your logs:")
        
        selected = []
        for plugin in processing_plugins:
            if st.checkbox(
                f"{plugin['name']} - {plugin['description'][:80]}...",
                key=f"proc_{plugin['id']}"
            ):
                selected.append(plugin['id'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.current_step = 1
                st.rerun()
        with col2:
            if st.button("Next →", type="primary"):
                st.session_state.selected_processors = selected
                st.session_state.current_step = 3
                st.rerun()
    
    elif current_step == 3:  # Outputs
        st.markdown("### 📤 Select Output Destinations")
        
        registry = st.session_state.plugin_registry
        output_plugins = registry.list_plugins(PluginType.OUTPUT)
        
        st.markdown("Choose where to send processed logs:")
        
        selected = []
        for plugin in output_plugins:
            if st.checkbox(
                f"{plugin['name']} - {plugin['description'][:80]}...",
                key=f"output_{plugin['id']}"
            ):
                selected.append(plugin['id'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.current_step = 2
                st.rerun()
        with col2:
            if st.button("Next →", type="primary"):
                st.session_state.selected_outputs = selected
                st.session_state.current_step = 4
                st.rerun()
    
    elif current_step == 4:  # Alerts
        st.markdown("### 🔔 Configure Alerts")
        
        registry = st.session_state.plugin_registry
        alert_plugins = registry.list_plugins(PluginType.ALERT)
        
        st.markdown("Set up alert notifications:")
        
        selected = []
        for plugin in alert_plugins:
            if st.checkbox(
                f"{plugin['name']} - {plugin['description'][:80]}...",
                key=f"alert_{plugin['id']}"
            ):
                selected.append(plugin['id'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.current_step = 3
                st.rerun()
        with col2:
            if st.button("Next →", type="primary"):
                st.session_state.selected_alerts = selected
                st.session_state.current_step = 5
                st.rerun()
    
    elif current_step == 5:  # Review
        st.markdown("### 📋 Review & Deploy")
        
        st.markdown("#### Workspace Configuration")
        st.json(st.session_state.workspace_config)
        
        st.markdown("#### Selected Components")
        st.markdown(f"**Inputs**: {len(st.session_state.selected_inputs)} plugins")
        st.markdown(f"**Processors**: {len(st.session_state.selected_processors)} plugins")
        st.markdown(f"**Outputs**: {len(st.session_state.selected_outputs)} plugins")
        st.markdown(f"**Alerts**: {len(st.session_state.get('selected_alerts', []))} plugins")
        
        st.markdown("#### Estimated Cost")
        tier = st.session_state.workspace_config.get('tier', '')
        if 'Starter' in tier:
            base_cost = 0
        elif 'Professional' in tier:
            base_cost = 499
        else:
            base_cost = 999
        
        st.markdown(f"**${base_cost}/month** (based on selected tier)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back"):
                st.session_state.current_step = 4
                st.rerun()
        with col2:
            if st.button("Save as Draft"):
                st.success("✅ Configuration saved!")
        with col3:
            if st.button("🚀 Deploy Now", type="primary"):
                st.success("✅ Pipeline deployed successfully!")
                st.balloons()
                # Reset wizard
                st.session_state.current_step = 0

elif page == "⚡ Pipeline Builder":
    st.markdown("## ⚡ Pipeline Builder")
    st.markdown("Visual pipeline configuration with drag-and-drop (simplified version)")
    
    if not PLUGINS_AVAILABLE:
        st.error("Plugin system not initialized")
        st.stop()
    
    # Pipeline name
    pipeline_name = st.text_input("Pipeline Name", placeholder="my-production-pipeline")
    
    if pipeline_name:
        # Display pipeline visually
        st.markdown("### Pipeline Flow")
        
        st.markdown('<div class="pipeline-arrow">⬇️</div>', unsafe_allow_html=True)
        
        # Inputs
        st.markdown('<div class="pipeline-node">', unsafe_allow_html=True)
        st.markdown("#### 📥 Input Sources")
        input_plugins = st.multiselect(
            "Select input plugins:",
            [p['name'] for p in st.session_state.plugin_registry.list_plugins(PluginType.INPUT)],
            key="pipeline_inputs"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="pipeline-arrow">⬇️</div>', unsafe_allow_html=True)
        
        # Processing
        st.markdown('<div class="pipeline-node">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Processing Steps")
        processing_plugins = st.multiselect(
            "Select processing plugins:",
            [p['name'] for p in st.session_state.plugin_registry.list_plugins(PluginType.PROCESSING)],
            key="pipeline_processing"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="pipeline-arrow">⬇️</div>', unsafe_allow_html=True)
        
        # Outputs
        st.markdown('<div class="pipeline-node">', unsafe_allow_html=True)
        st.markdown("#### 📤 Output Destinations")
        output_plugins = st.multiselect(
            "Select output plugins:",
            [p['name'] for p in st.session_state.plugin_registry.list_plugins(PluginType.OUTPUT)],
            key="pipeline_outputs"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Save pipeline
        if st.button("💾 Save Pipeline", type="primary"):
            st.session_state.pipelines[pipeline_name] = {
                'inputs': input_plugins,
                'processing': processing_plugins,
                'outputs': output_plugins
            }
            st.success(f"✅ Pipeline '{pipeline_name}' saved!")

elif page == "🔧 Plugin Configuration":
    st.markdown("## 🔧 Plugin Configuration")
    st.markdown("Configure individual plugin instances with detailed settings")
    
    if not PLUGINS_AVAILABLE:
        st.error("Plugin system not initialized")
        st.stop()
    
    # Select plugin to configure
    registry = st.session_state.plugin_registry
    all_plugins = registry.list_plugins()
    
    plugin_options = {f"{p['name']} ({p['category']})": p['id'] for p in all_plugins}
    
    selected_plugin_name = st.selectbox(
        "Select plugin to configure:",
        list(plugin_options.keys())
    )
    
    if selected_plugin_name:
        plugin_id = plugin_options[selected_plugin_name]
        plugin_class = registry.get_plugin(plugin_id)
        
        if plugin_class:
            instance = plugin_class()
            metadata = instance.metadata
            config_schema = instance.config_schema
            
            st.markdown(f"### {metadata.name}")
            st.markdown(f"**Version**: {metadata.version} | **Author**: {metadata.author}")
            st.markdown(metadata.description)
            st.markdown(f"**Documentation**: [{metadata.documentation_url}]({metadata.documentation_url})")
            
            st.markdown("---")
            st.markdown("#### Configuration")
            
            # Build config form
            config = {}
            for field in config_schema:
                if field.type == "string":
                    config[field.name] = st.text_input(
                        field.label,
                        value=field.default or "",
                        help=field.description,
                        placeholder=field.placeholder,
                        key=f"config_{field.name}"
                    )
                elif field.type == "number":
                    config[field.name] = st.number_input(
                        field.label,
                        value=field.default or 0,
                        help=field.description,
                        key=f"config_{field.name}"
                    )
                elif field.type == "boolean":
                    config[field.name] = st.checkbox(
                        field.label,
                        value=field.default or False,
                        help=field.description,
                        key=f"config_{field.name}"
                    )
                elif field.type == "select":
                    config[field.name] = st.selectbox(
                        field.label,
                        options=field.options or [],
                        index=field.options.index(field.default) if field.default and field.options else 0,
                        help=field.description,
                        key=f"config_{field.name}"
                    )
                elif field.type == "secret":
                    config[field.name] = st.text_input(
                        field.label,
                        value="",
                        type="password",
                        help=field.description,
                        placeholder=field.placeholder,
                        key=f"config_{field.name}"
                    )
            
            # Test configuration
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧪 Test Connection", type="secondary"):
                    is_valid, error = instance.validate_config(config)
                    if is_valid:
                        st.success("✅ Configuration is valid!")
                    else:
                        st.error(f"❌ {error}")
            
            with col2:
                if st.button("💾 Save Configuration", type="primary"):
                    is_valid, error = instance.validate_config(config)
                    if is_valid:
                        # Create plugin instance
                        instance_id = f"{plugin_id}_{len(st.session_state.configured_plugins)}"
                        manager = st.session_state.plugin_manager
                        success, msg = manager.create_instance(plugin_id, instance_id, config)
                        
                        if success:
                            st.success(f"✅ Plugin configured as '{instance_id}'")
                            st.session_state.configured_plugins[instance_id] = config
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.error(f"❌ {error}")

elif page == "📊 Monitoring":
    st.markdown("## 📊 Platform Monitoring")
    st.markdown("Monitor health and performance of your configured plugins")
    
    if not PLUGINS_AVAILABLE:
        st.error("Plugin system not initialized")
        st.stop()
    
    manager = st.session_state.plugin_manager
    instances = manager.list_instances()
    
    if not instances:
        st.info("No plugin instances configured yet. Use the Quick Setup Wizard or Pipeline Builder to get started.")
    else:
        for instance in instances:
            with st.expander(f"{instance['plugin_name']} - {instance['instance_id']}", expanded=True):
                health = manager.health_check(instance['instance_id'])
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Category**: {instance['plugin_category']}")
                    st.markdown(f"**Message**: {health.get('message', 'N/A')}")
                
                with col2:
                    status = health.get('status', 'unknown')
                    if status == 'healthy':
                        st.markdown('<div class="status-healthy">● HEALTHY</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="status-warning">⚠ WARNING</div>', unsafe_allow_html=True)
                
                if health.get('metrics'):
                    st.markdown("**Metrics**:")
                    st.json(health['metrics'])

elif page == "📚 Documentation":
    st.markdown("## 📚 Documentation")
    
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        ### Quick Start Guide
        
        1. **Create Workspace** - Set up your organization and select a tier
        2. **Configure Data Sources** - Connect your log sources (AWS, K8s, etc.)
        3. **Add Processing** - Transform and enrich your logs
        4. **Set Destinations** - Route logs to your preferred storage/analytics platform
        5. **Configure Alerts** - Set up notifications for critical events
        
        Use the **Quick Setup Wizard** for guided configuration.
        """)
    
    with st.expander("🔌 Plugin Development"):
        st.markdown("""
        ### Creating Custom Plugins
        
        1. **Inherit from Base Class**:
           - `InputPlugin` for data sources
           - `ProcessingPlugin` for transformations
           - `OutputPlugin` for destinations
           - `AlertPlugin` for notifications
        
        2. **Implement Required Methods**:
           ```python
           class MyPlugin(InputPlugin):
               @property
               def metadata(self):
                   return PluginMetadata(...)
               
               @property
               def config_schema(self):
                   return [ConfigField(...)]
               
               def collect(self):
                   # Your logic here
           ```
        
        3. **Register Your Plugin**:
           ```python
           registry.register(MyPlugin)
           ```
        
        See full documentation at [docs.aiml-obs.com/plugin-development](https://docs.aiml-obs.com)
        """)
    
    with st.expander("💡 Best Practices"):
        st.markdown("""
        ### Configuration Best Practices
        
        - **Start Simple**: Begin with one input, one output
        - **Test Incrementally**: Add processing steps one at a time
        - **Monitor Health**: Check plugin health regularly
        - **Use Batching**: Configure appropriate batch sizes for performance
        - **Secure Secrets**: Never store credentials in plaintext
        - **Plan Capacity**: Estimate data volume and set limits
        """)
    
    with st.expander("🔒 Security"):
        st.markdown("""
        ### Security Features
        
        - **Encryption**: All data encrypted at rest and in transit
        - **Authentication**: API keys with scoped permissions
        - **Audit Logging**: Complete audit trail of all changes
        - **RBAC**: Role-based access control (Admin, Engineer, Viewer)
        - **Secrets Management**: Secure credential storage
        - **Network Isolation**: VPC peering and private endpoints
        """)

# Footer
st.markdown("---")
st.markdown("### 💡 Need Help?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("📖 [Documentation](https://docs.aiml-obs.com)")
with col2:
    st.markdown("💬 [Community Forum](https://community.aiml-obs.com)")
with col3:
    st.markdown("🎫 [Support Tickets](https://support.aiml-obs.com)")
