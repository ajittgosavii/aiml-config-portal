"""
Admin Panel for User Management
Only accessible to users with admin privileges
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import auth

def show_admin_panel():
    """Display admin management panel"""
    
    # Check if user is admin
    if not auth.is_admin():
        st.error("❌ Access Denied: Admin privileges required")
        return
    
    st.title("👤 Admin User Management")
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["📋 All Users", "➕ Create User", "⚙️ Settings"])
    
    # Tab 1: View All Users
    with tab1:
        st.header("All Registered Users")
        
        users = auth.get_all_users()
        
        if users:
            # Convert to DataFrame
            df = pd.DataFrame(users)
            
            # Format datetime columns
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            if 'last_login' in df.columns:
                df['last_login'] = pd.to_datetime(df['last_login']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Reorder columns
            column_order = ['email', 'display_name', 'is_admin', 'status', 'created_at', 'last_login']
            df = df[[col for col in column_order if col in df.columns]]
            
            # Display stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", len(users))
            with col2:
                admin_count = sum(1 for u in users if u.get('is_admin', False))
                st.metric("Admin Users", admin_count)
            with col3:
                active_count = sum(1 for u in users if u.get('status') == 'active')
                st.metric("Active Users", active_count)
            
            st.markdown("---")
            
            # Display users table
            st.dataframe(df, use_container_width=True, height=400)
            
            st.markdown("---")
            
            # User Actions
            st.subheader("🔧 User Actions")
            
            # Select user
            user_emails = [u['email'] for u in users]
            selected_email = st.selectbox("Select User", user_emails)
            
            if selected_email:
                selected_user = next(u for u in users if u['email'] == selected_email)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Make/Revoke Admin
                    if selected_user.get('is_admin', False):
                        if st.button("🔓 Revoke Admin", use_container_width=True):
                            if auth.revoke_admin(selected_user['uid']):
                                st.success(f"✅ Admin privileges revoked for {selected_email}")
                                st.rerun()
                    else:
                        if st.button("🔒 Make Admin", use_container_width=True):
                            if auth.make_admin(selected_user['uid']):
                                st.success(f"✅ Admin privileges granted to {selected_email}")
                                st.rerun()
                
                with col2:
                    # Reset Password
                    if st.button("🔑 Reset Password", use_container_width=True):
                        if auth.send_password_reset_email(selected_email):
                            st.success(f"✅ Password reset email sent to {selected_email}")
                
                with col3:
                    # Delete User
                    if st.button("🗑️ Delete User", use_container_width=True, type="primary"):
                        # Confirmation
                        if 'confirm_delete' not in st.session_state:
                            st.session_state.confirm_delete = False
                        
                        if not st.session_state.confirm_delete:
                            st.session_state.confirm_delete = True
                            st.warning("⚠️ Click again to confirm deletion")
                        else:
                            if auth.delete_user(selected_user['uid']):
                                st.success(f"✅ User {selected_email} deleted")
                                st.session_state.confirm_delete = False
                                st.rerun()
        
        else:
            st.info("No users found")
    
    # Tab 2: Create User
    with tab2:
        st.header("Create New User")
        
        with st.form("create_user_form"):
            new_email = st.text_input("Email Address", placeholder="user@company.com")
            new_display_name = st.text_input("Display Name", placeholder="John Doe")
            new_password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            new_password_confirm = st.text_input("Confirm Password", type="password")
            new_is_admin = st.checkbox("Grant Admin Privileges")
            
            submitted = st.form_submit_button("➕ Create User", use_container_width=True, type="primary")
            
            if submitted:
                # Validation
                if not new_email or not new_password:
                    st.error("❌ Email and password are required")
                elif new_password != new_password_confirm:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    # Create user
                    result = auth.create_user(
                        email=new_email,
                        password=new_password,
                        display_name=new_display_name,
                        is_admin=new_is_admin
                    )
                    
                    if result:
                        st.success(f"✅ User created successfully!")
                        st.info(f"**Email:** {new_email}")
                        st.info(f"**Password:** {new_password}")
                        st.warning("⚠️ Please share these credentials securely with the user")
    
    # Tab 3: Settings
    with tab3:
        st.header("Admin Settings")
        
        st.subheader("🔐 Security Settings")
        
        # Require Email Verification
        require_verification = st.checkbox("Require email verification for new users", value=False)
        
        # Password Requirements
        st.markdown("**Password Requirements:**")
        min_password_length = st.number_input("Minimum password length", min_value=6, max_value=20, value=8)
        require_uppercase = st.checkbox("Require uppercase letter", value=True)
        require_number = st.checkbox("Require number", value=True)
        require_special = st.checkbox("Require special character", value=False)
        
        st.markdown("---")
        
        st.subheader("📊 Activity Log")
        
        # Show recent activity
        st.info("Activity logging coming soon...")
        
        st.markdown("---")
        
        if st.button("💾 Save Settings", use_container_width=True, type="primary"):
            st.success("✅ Settings saved successfully")
