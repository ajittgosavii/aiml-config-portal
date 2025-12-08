"""
Login UI Module - Ultra-Centered Professional Design
Provides login, registration, and password reset interfaces
"""

import streamlit as st
import auth
import time

def show_login_page():
    """Display ultra-centered professional login page"""
    
    # Initialize session state
    auth.init_session_state()
    
    # If already authenticated, show welcome message
    if auth.is_authenticated():
        show_authenticated_ui()
        return
    
    # Ultra-professional centered login page styling with aggressive centering
    st.markdown("""
    <style>
        /* FORCE hide sidebar on login page */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* FORCE center the main content with margin auto */
        .main .block-container {
            max-width: 480px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-top: 3rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        /* Remove default Streamlit padding */
        .main {
            padding-top: 0 !important;
        }
        
        /* Center everything inside */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Login container card */
        .login-container {
            background: white;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            margin: 0 auto;
        }
        
        /* Header styling */
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-header h1 {
            color: #1e40af;
            font-size: 1.875rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }
        
        .login-header p {
            color: #64748b;
            font-size: 0.938rem;
            margin-top: 0.5rem;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            justify-content: center;
            background: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.625rem 1.25rem;
            font-weight: 600;
            font-size: 0.875rem;
            border-radius: 8px;
            background: transparent;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #f1f5f9;
        }
        
        .stTabs [aria-selected="true"] {
            background: #eff6ff;
            color: #1e40af;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 1.5px solid #e2e8f0 !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.938rem !important;
            transition: all 0.2s !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            outline: none !important;
        }
        
        .stTextInput > label {
            font-weight: 600 !important;
            color: #334155 !important;
            font-size: 0.875rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 0.938rem !important;
            transition: all 0.2s !important;
            width: 100% !important;
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            border: none !important;
            color: white !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Checkbox styling */
        .stCheckbox {
            margin-top: 0.5rem !important;
        }
        
        .stCheckbox > label {
            font-size: 0.875rem !important;
            color: #64748b !important;
        }
        
        /* Footer styling */
        .login-footer {
            text-align: center;
            color: white;
            font-size: 0.813rem;
            margin-top: 2rem;
            line-height: 1.6;
        }
        
        .login-footer p {
            margin: 0.25rem 0;
            opacity: 0.9;
        }
        
        /* Form container */
        [data-testid="stForm"] {
            background: transparent;
            border: none;
            padding: 0;
        }
        
        /* Alert/Message styling */
        .stAlert {
            border-radius: 8px !important;
            padding: 0.875rem !important;
            margin: 1rem 0 !important;
        }
        
        /* Info box styling */
        .element-container div[data-testid="stMarkdownContainer"] p {
            line-height: 1.6;
        }
        
        /* Responsive design */
        @media (max-width: 640px) {
            .main .block-container {
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            
            .login-container {
                padding: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Login header
    st.markdown("""
    <div class="login-header">
        <h1>🔐 AI/ML Observability Platform</h1>
        <p>Please sign in to continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for Login / Register / Reset
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "🔄 Reset Password"])
    
    # Login Tab
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "Email Address",
                placeholder="you@company.com",
                key="login_email"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                submit = st.form_submit_button(
                    "🔓 Sign In",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                remember = st.checkbox("Remember", value=True)
            
            if submit:
                if not email or not password:
                    st.error("❌ Please enter both email and password")
                else:
                    with st.spinner("Authenticating..."):
                        user_info = auth.verify_user(email, password)
                        
                        if user_info:
                            if user_info['status'] == 'active':
                                auth.login_user(user_info)
                                st.success(f"✅ Welcome back, {user_info['display_name']}!")
                                
                                if user_info['is_admin']:
                                    st.info("🔑 Admin access granted")
                                
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Your account has been deactivated. Please contact support.")
                        else:
                            st.error("❌ Invalid email or password")
    
    # Register Tab
    with tab2:
        with st.form("register_form", clear_on_submit=False):
            st.info("⚠️ Self-registration is currently disabled. Please contact your administrator to create an account.")
            
            reg_email = st.text_input(
                "Email Address",
                placeholder="you@company.com",
                disabled=True,
                key="reg_email"
            )
            reg_name = st.text_input(
                "Full Name",
                placeholder="John Doe",
                disabled=True,
                key="reg_name"
            )
            reg_password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 6 characters",
                disabled=True,
                key="reg_password"
            )
            reg_password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                disabled=True,
                key="reg_password_confirm"
            )
            
            st.form_submit_button(
                "📝 Create Account",
                use_container_width=True,
                disabled=True
            )
    
    # Reset Password Tab
    with tab3:
        with st.form("reset_form", clear_on_submit=False):
            st.markdown("Enter your email address and we'll send you a password reset link.")
            
            reset_email = st.text_input(
                "Email Address",
                placeholder="you@company.com",
                key="reset_email"
            )
            
            submit_reset = st.form_submit_button(
                "📧 Send Reset Link",
                use_container_width=True,
                type="primary"
            )
            
            if submit_reset:
                if not reset_email:
                    st.error("❌ Please enter your email address")
                else:
                    with st.spinner("Sending reset link..."):
                        if auth.send_password_reset_email(reset_email):
                            st.success("✅ Password reset email sent! Check your inbox.")
                            st.info("💡 If you don't receive it, check your spam folder")
                        else:
                            st.error("❌ Failed to send reset email. Please try again.")
    
    # Footer
    st.markdown("""
    <div class="login-footer">
        <p>© 2024 AI/ML Observability Platform • Secure Authentication via Firebase</p>
        <p>Need help? Contact support@yourcompany.com</p>
    </div>
    """, unsafe_allow_html=True)


def show_authenticated_ui():
    """Show UI for authenticated users"""
    
    user = auth.get_current_user()
    
    # User info in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 User Profile")
        
        st.markdown(f"""
        **{user['display_name']}**  
        {user['email']}
        """)
        
        if auth.is_admin():
            st.markdown("""
            <div style='background: #dbeafe; padding: 0.5rem; border-radius: 4px; text-align: center;'>
                <strong style='color: #1e40af;'>🔑 ADMIN</strong>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout_user()
            st.rerun()


def require_auth(func):
    """Decorator to require authentication for a page"""
    def wrapper(*args, **kwargs):
        if not auth.is_authenticated():
            show_login_page()
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def require_admin(func):
    """Decorator to require admin privileges for a page"""
    def wrapper(*args, **kwargs):
        if not auth.is_authenticated():
            show_login_page()
            st.stop()
        
        if not auth.is_admin():
            st.error("❌ Access Denied: Admin privileges required")
            st.stop()
        
        return func(*args, **kwargs)
    return wrapper
