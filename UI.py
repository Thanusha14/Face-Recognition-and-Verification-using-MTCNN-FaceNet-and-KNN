import streamlit as st
import pandas as pd
import ast
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Suspicious Voter Monitoring",
    layout="wide"
)

st.title("🔎 Suspicious Voter Monitoring System")
st.markdown("---")

# -------------------------
# Upload Section
# -------------------------
st.subheader("📁 Upload Suspicious Votes File")
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    
    # -------------------------
    # Load dataset
    # -------------------------
    df = pd.read_csv(uploaded_file)

    # Convert embeddings back to lists if stored as strings
    if 'facenet_embedding' in df.columns:
        df['facenet_embedding'] = df['facenet_embedding'].apply(
            lambda x: ast.literal_eval(x) if pd.notnull(x) and isinstance(x, str) else x
        )

    st.write("")  # Vertical spacing

    # -------------------------
    # Detect suspicious voters by fraud type
    # -------------------------
    fraud_categories = {
        "Same Constituency Identity Theft": df[df['fraud_type'] == 'same_constituency_identity_theft']['voter_id'].unique().tolist(),
        "Cross-Constituency Voting": df[df['fraud_type'] == 'cross_constituency_voting']['voter_id'].unique().tolist(),
        "Double Voting": df[df['fraud_type'] == 'double_voting']['voter_id'].unique().tolist(),
        "All Suspicious Voters": df[df['is_suspicious'] == True]['voter_id'].unique().tolist()
    }

    # -------------------------
    # Summary Statistics
    # -------------------------
    st.subheader("📊 Overview Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Votes", len(df))
    with col2:
        st.metric("Legitimate Votes", len(df[df['fraud_type'] == 'legitimate']))
    with col3:
        st.metric("Suspicious Votes", len(df[df['is_suspicious'] == True]))
    with col4:
        st.metric("Unique Voters", df['voter_id'].nunique())
    with col5:
        fraud_rate = (len(df[df['is_suspicious'] == True]) / len(df) * 100)
        st.metric("Fraud Rate", f"{fraud_rate:.1f}%")

    st.markdown("---")

    # -------------------------
    # Layout: Split screen
    # -------------------------
    col_left, spacer, col_right = st.columns([2.5, 0.3, 2])

    with col_left:
        st.subheader("🚨 Suspicious Voter Categories")
        st.write("")

        # Filter out categories with no voters
        active_categories = {k: v for k, v in fraud_categories.items() if len(v) > 0}
        
        suspicious_type = st.selectbox(
            "Select a suspicious activity type",
            list(active_categories.keys())
        )

        if suspicious_type:
            voter_list = active_categories[suspicious_type]
            # st.write(f"**Total voters flagged for {suspicious_type}:** {len(voter_list)}")
            st.write("")

            selected_voter = st.selectbox("Select a voter ID", sorted(voter_list))

            if selected_voter:
                voter_data = df[df['voter_id'] == selected_voter]
                st.subheader(f"📋 Details for Voter ID: {selected_voter}")
                st.write("")

                # Prepare display dataframe
                display_df = voter_data[[
                    'image_path', 
                    'registered_constituency', 
                    'voting_constituency',
                    'claimed_voter_id',
                    'fraud_type',
                    'is_suspicious'
                ]].copy()

                # Add reason column
                display_df['fraud_reason'] = ""
                for idx, row in display_df.iterrows():
                    reasons = []
                    if row['fraud_type'] == 'same_constituency_identity_theft':
                        reasons.append(f"Identity theft: Claims to be {row['claimed_voter_id']}")
                    if row['fraud_type'] == 'cross_constituency_voting':
                        reasons.append(f"Voting in wrong constituency: Registered in {row['registered_constituency']}, voting in {row['voting_constituency']}")
                    if row['fraud_type'] == 'double_voting':
                        reasons.append("Multiple voting attempts detected")
                    display_df.at[idx, 'fraud_reason'] = "; ".join(reasons) if reasons else "Legitimate"

                # Display table
                st.dataframe(
                    display_df[['image_path', 'registered_constituency', 'voting_constituency', 
                               'claimed_voter_id', 'fraud_type', 'fraud_reason']].reset_index(drop=True),
                    use_container_width=True
                )

                # Display face images
                st.subheader("🖼️ Face Images")
                img_cols = st.columns(4)
                for i, img_path in enumerate(voter_data['image_path']):
                    with img_cols[i % 4]:
                        try:
                            st.image(img_path, width=150, caption=f"Image {i+1}")
                        except:
                            st.error(f"Cannot load image: {img_path}")

    with col_right:
        # -------------------------
        # Fraud Type Distribution
        # -------------------------
        st.subheader("📊 Fraud Type Distribution")
        fraud_counts = df['fraud_type'].value_counts().reset_index()
        fraud_counts.columns = ['Fraud Type', 'Count']
        
        fig1 = px.pie(
            fraud_counts,
            values='Count',
            names='Fraud Type',
            title="Distribution of Vote Types",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig1, use_container_width=True)

        # -------------------------
        # Constituency-wise Analysis
        # -------------------------
        st.subheader("🗺️ Constituency-wise Suspicious Votes")
        
        suspicious_df = df[df['is_suspicious'] == True]
        
        if len(suspicious_df) > 0:
            # Count by voting constituency
            summary = suspicious_df.groupby('voting_constituency').agg({
                'voter_id': 'nunique',
                'fraud_type': lambda x: x.value_counts().to_dict()
            }).reset_index()
            summary.columns = ['Constituency', 'Suspicious Voters', 'Fraud Breakdown']
            
            # Create simplified summary for plotting
            plot_summary = suspicious_df.groupby('voting_constituency')['voter_id'].nunique().reset_index()
            plot_summary.columns = ['Constituency', 'Suspicious Voters']
            
            fig2 = px.bar(
                plot_summary,
                x='Constituency',
                y='Suspicious Voters',
                color='Suspicious Voters',
                text='Suspicious Voters',
                title="Suspicious Voters by Constituency",
                color_continuous_scale='Reds'
            )
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)
            
            # Detailed breakdown table
            st.subheader("📋 Detailed Constituency Breakdown")
            detailed_summary = suspicious_df.groupby(['voting_constituency', 'fraud_type']).size().reset_index()
            detailed_summary.columns = ['Constituency', 'Fraud Type', 'Count']
            
            pivot_table = detailed_summary.pivot(
                index='Constituency',
                columns='Fraud Type',
                values='Count'
            ).fillna(0).astype(int)
            
            st.dataframe(pivot_table, use_container_width=True)
        else:
            st.info("No suspicious votes detected in the dataset.")

    st.markdown("---")

    # -------------------------
    # Additional Analytics Section
    # -------------------------
    st.subheader("🔍 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Identity Theft Cases", "Cross-Constituency Fraud", "Double Voting"])
    
    with tab1:
        identity_theft = df[df['fraud_type'] == 'same_constituency_identity_theft']
        if len(identity_theft) > 0:
            st.write(f"**Total Identity Theft Cases:** {len(identity_theft)}")
            theft_summary = identity_theft[['voter_id', 'claimed_voter_id', 'voting_constituency']].copy()
            theft_summary.columns = ['Actual Voter (from face)', 'Claimed Voter ID', 'Constituency']
            st.dataframe(theft_summary.reset_index(drop=True), use_container_width=True)
        else:
            st.info("No identity theft cases detected.")
    
    with tab2:
        cross_const = df[df['fraud_type'] == 'cross_constituency_voting']
        if len(cross_const) > 0:
            st.write(f"**Total Cross-Constituency Cases:** {len(cross_const)}")
            cross_summary = cross_const[['voter_id', 'registered_constituency', 'voting_constituency']].copy()
            st.dataframe(cross_summary.reset_index(drop=True), use_container_width=True)
        else:
            st.info("No cross-constituency voting detected.")
    
    with tab3:
        double_voters = df[df['fraud_type'] == 'double_voting']['voter_id'].unique()
        if len(double_voters) > 0:
            st.write(f"**Total Double Voting Cases:** {len(double_voters)}")
            double_summary = []
            for voter in double_voters:
                count = len(df[(df['voter_id'] == voter)])
                double_summary.append({
                    'Voter ID': voter,
                    'Number of Votes': count,
                    'Constituencies': ', '.join(df[df['voter_id'] == voter]['voting_constituency'].unique())
                })
            st.dataframe(pd.DataFrame(double_summary), use_container_width=True)
        else:
            st.info("No double voting detected.")

    st.markdown("---")
    st.caption("🔒 Voter Fraud Detection System | Powered by FaceNet & Streamlit")

else:
    st.info("👆 Please upload a CSV file to begin analysis")
    