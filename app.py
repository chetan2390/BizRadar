# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from fetcher import fetch_news, fetch_regulations, fetch_schemes
from analyzer import analyze_batch, answer_question
from config import BUSINESS_PROFILE

# PAGE SETUP
st.set_page_config(
    page_title="BizRadar",
    page_icon="📡",
    layout="wide"
)

# CUSTOM CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1117;
    }
    
    /* Cards */
    .biz-card {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* High priority card */
    .biz-card-high {
        background: #1e2130;
        border: 1px solid #ff4b4b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Opportunity card */
    .biz-card-opportunity {
        background: #1e2130;
        border: 1px solid #00c853;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 16px;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e2130;
    }
    
    /* Button */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Profile badge */
    .profile-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        color: white;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: #1e2130;
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "news_analyzed" not in st.session_state:
    st.session_state.news_analyzed = []
if "regulations_analyzed" not in st.session_state:
    st.session_state.regulations_analyzed = []
if "schemes_analyzed" not in st.session_state:
    st.session_state.schemes_analyzed = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0
if "profile_setup" not in st.session_state:
    st.session_state.profile_setup = False

# PROFILE SETUP SCREEN
# Shows on first launch instead of hardcoded config

if not st.session_state.profile_setup:
    
    st.title("📡 Welcome to BizRadar")
    st.subheader("Let's set up your business profile")
    st.write("Tell us about your business and we'll personalise everything for you.")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        biz_name = st.text_input("Business Name", placeholder="e.g. Sharma Textiles")
        industry = st.text_input("Industry", placeholder="e.g. Textiles and Manufacturing")
        business_type = st.selectbox("Business Type", [
            "MSME", "Startup", "Large Enterprise", 
            "Sole Proprietorship", "Partnership", "Private Limited"
        ])
    
    with col2:
        location = st.text_input("Location", placeholder="e.g. Gujarat, India")
        sectors = st.multiselect("Sectors", [
            "Manufacturing", "Export", "Import", "Retail",
            "GST Registered", "E-commerce", "Services",
            "Agriculture", "Healthcare", "Education",
            "Fintech", "Real Estate", "Logistics"
        ])
        interests = st.multiselect("Track These Topics", [
            "GST updates", "export regulations", "MSME schemes",
            "textile industry news", "manufacturing policy",
            "RBI notifications", "SEBI updates", "startup funding",
            "import duty changes", "labour law updates",
            "environmental regulations", "food safety regulations"
        ])
    
    st.divider()
    
    if st.button("🚀 Launch BizRadar", width='stretch'):
        if biz_name and industry and location:
            # Save profile to session state
            st.session_state.user_profile = {
                "name": biz_name,
                "industry": industry,
                "business_type": business_type,
                "location": location,
                "sectors": sectors if sectors else ["General"],
                "interests": interests if interests else ["business news India", "GST updates"]
            }
            st.session_state.profile_setup = True
            st.rerun()
        else:
            st.error("Please fill in Business Name, Industry, and Location at minimum.")
    
    st.stop()

# USE PROFILE FROM SESSION OR CONFIG
profile = st.session_state.get("user_profile", BUSINESS_PROFILE)

# SIDEBAR
with st.sidebar:
    st.markdown(f"""
    <div class="profile-badge">
        <h3 style="margin:0; color:white;">🏢 {profile['name']}</h3>
        <p style="margin:4px 0 0 0; color:#e0e0e0; font-size:14px;">{profile['industry']}</p>
        <p style="margin:2px 0 0 0; color:#e0e0e0; font-size:12px;">📍 {profile['location']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"**Type:** {profile['business_type']}")
    
    if profile.get('sectors'):
        st.caption(f"**Sectors:** {', '.join(profile['sectors'])}")
    
    st.divider()
    
    refresh = st.button("🔄 Refresh Data", width='stretch')
    
    if st.button("⚙️ Change Profile", width='stretch'):
        st.session_state.profile_setup = False
        st.session_state.data_loaded = False
        st.rerun()
    
    st.divider()
    
    if st.session_state.data_loaded:
        total = (len(st.session_state.news_analyzed) + 
                len(st.session_state.regulations_analyzed) + 
                len(st.session_state.schemes_analyzed))
        st.metric("Relevant Updates", total)
        
        high = len([i for i in 
                   st.session_state.regulations_analyzed + 
                   st.session_state.news_analyzed
                   if i.get("priority") == "HIGH"])
        if high > 0:
            st.error(f"🚨 {high} HIGH priority items")
    
    st.divider()
    st.caption("Powered by Gemini AI • BizRadar v1.0")

# HEADER
st.title("📡 BizRadar")
st.caption(f"Your personalised business intelligence assistant • {datetime.now().strftime('%A, %B %d, %Y')}")
st.divider()

# DATA LOADING
if not st.session_state.data_loaded or refresh:
    
    progress = st.progress(0, text="Starting up BizRadar...")
    
    progress.progress(10, text="Fetching industry news...")
    raw_news = fetch_news(profile)
    
    progress.progress(30, text="Fetching government regulations...")
    raw_regulations = fetch_regulations(profile)
    
    progress.progress(50, text="Fetching government schemes...")
    raw_schemes = fetch_schemes(profile)
    
    progress.progress(60, text="Analyzing news with AI...")
    st.session_state.news_analyzed = analyze_batch(raw_news,profile)
    
    progress.progress(75, text="Analyzing regulations with AI...")
    st.session_state.regulations_analyzed = analyze_batch(raw_regulations,profile)
    
    progress.progress(90, text="Analyzing opportunities with AI...")
    st.session_state.schemes_analyzed = analyze_batch(raw_schemes,profile)
    
    progress.progress(100, text="BizRadar is ready!")
    st.session_state.data_loaded = True
    
    import time
    time.sleep(0.5)
    progress.empty()
    
    st.success("✅ BizRadar is up to date!")
    import time
    time.sleep(1)
    st.rerun()

# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Daily Digest",
    "⚖️ Regulations", 
    "📰 Industry News",
    "📊 Analytics",
    "🤖 Ask BizRadar"
])


# TAB 1 — DAILY DIGEST

with tab1:
    st.subheader(f"Good {'morning' if datetime.now().hour < 12 else 'afternoon'}, {profile['name']}!")
    st.caption("Here's everything that matters to your business today.")
    st.divider()

    # METRICS 
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Regulations", len(st.session_state.regulations_analyzed))
    with col2:
        st.metric("News Items", len(st.session_state.news_analyzed))
    with col3:
        st.metric("Opportunities", len(st.session_state.schemes_analyzed))
    with col4:
        high = len([i for i in
                   st.session_state.regulations_analyzed +
                   st.session_state.news_analyzed
                   if i.get("priority") == "HIGH"])
        st.metric("High Priority", high)

    st.divider()

    # HIGH PRIORITY ALERTS
    high_priority = [
        item for item in
        st.session_state.regulations_analyzed +
        st.session_state.news_analyzed +
        st.session_state.schemes_analyzed
        if item.get("priority") == "HIGH"
    ]

    if high_priority:
        st.error(f"🚨 {len(high_priority)} HIGH PRIORITY item(s) require your attention")
        for item in high_priority:
            with st.expander(f"🔴 {item['title']}", expanded=True):
                st.write(f"**Summary:** {item['summary']}")
                st.write(f"**Impact:** {item['impact_reason']}")
                if item['action_required']:
                    st.warning(f"⚠️ **Action Required:** {item['action_steps']}")
                st.caption(f"Source: {item['source']}")
                if item.get('link'):
                    st.link_button("Read More →", item['link'])
        st.divider()

    # CARD HELPER FUNCTION
    # This function draws one card.
    # Only 4 things change per card: title, summary, reason, impact type.

    def draw_card(title, summary, reason, impact, source, published, link):

        # Pick colors based on impact type
        if impact == "opportunity":
            border = "#00c853"
            bg = "#1a2e1a"
            badge = "OPPORTUNITY"
            badge_bg = "#00c853"
            badge_color = "#000000"
            reason_color = "#00c853"
        elif impact == "threat":
            border = "#ff4b4b"
            bg = "#2e1a1a"
            badge = "THREAT"
            badge_bg = "#ff4b4b"
            badge_color = "#ffffff"
            reason_color = "#ff4b4b"
        else:
            border = "#ffd740"
            bg = "#2e2a1a"
            badge = "NEUTRAL"
            badge_bg = "#ffd740"
            badge_color = "#000000"
            reason_color = "#ffd740"

        # Draw the card — HTML structure never changes
        st.markdown(f"""
        <div style="border-left:4px solid {border}; background:{bg}; border-radius:0 12px 12px 0; padding:16px 20px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="background:{badge_bg}; color:{badge_color}; font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px;">{badge}</span>
                <span style="color:#888; font-size:12px;">{source} • {published[:16]}</span>
            </div>
            <h4 style="color:#ffffff; margin:0 0 8px 0; font-size:15px;">{title}</h4>
            <p style="color:#c0c0c0; margin:0 0 8px 0; font-size:13px; line-height:1.6;">{summary}</p>
            <p style="color:{reason_color}; margin:0; font-size:13px;">→ {reason}</p>
        </div>
        """, unsafe_allow_html=True)

        if link:
            st.link_button("Read More →", link)

    # OPPORTUNITIES
    opportunities = [
        item for item in
        st.session_state.news_analyzed +
        st.session_state.schemes_analyzed
        if item.get("impact") == "opportunity"
    ]

    if opportunities:
        st.markdown("### 🟢 Opportunities For You")
        st.caption("Updates the AI identified as growth opportunities for your business.")
        st.divider()

        for item in opportunities[:3]:
            draw_card(
                title=item['title'],
                summary=item['summary'],
                reason=item['impact_reason'],
                impact="opportunity",
                source=item['source'],
                published=item['published'],
                link=item.get('link', '')
            )

    # LATEST NEWS
    if st.session_state.news_analyzed:
        st.divider()
        st.markdown("### 📰 Latest Industry News")
        st.caption("Live news from your industry — analyzed for your business.")
        st.divider()

        for item in st.session_state.news_analyzed[:4]:
            draw_card(
                title=item['title'],
                summary=item['summary'],
                reason=item['impact_reason'],
                impact=item.get('impact', 'neutral'),
                source=item['source'],
                published=item['published'],
                link=item.get('link', '')
            )

    if not high_priority and not opportunities and not st.session_state.news_analyzed:
        st.info("No relevant updates found. Try refreshing or updating your profile interests.")


# TAB 2 — REGULATIONS

with tab2:
    
    st.subheader("⚖️ Regulatory Intelligence")
    st.write("Government circulars and policy updates — filtered and explained for your business.")
    st.divider()
    
    if not st.session_state.regulations_analyzed:
        st.info("No relevant regulatory updates found. Try refreshing data.")
    else:
        priority_filter = st.selectbox("Filter by Priority", ["All", "HIGH", "MEDIUM", "LOW"])
        
        filtered = st.session_state.regulations_analyzed
        if priority_filter != "All":
            filtered = [r for r in filtered if r.get("priority") == priority_filter]
        
        st.caption(f"Showing {len(filtered)} regulatory updates")
        st.divider()
        
        for item in filtered:
            icon = "🔴" if item['priority'] == "HIGH" else "🟡" if item['priority'] == "MEDIUM" else "🟢"
            
            with st.expander(f"{icon} {item['title']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write("**Summary:**")
                    st.write(item['summary'])
                    st.write("**What this means for your business:**")
                    st.write(item['impact_reason'])
                    if item['action_required']:
                        st.warning(f"⚠️ **Action Required:** {item['action_steps']}")
                    else:
                        st.success("✅ No immediate action required")
                
                with col2:
                    st.metric("Relevance", f"{item['relevance_score']}/10")
                    st.write(f"**Priority:** {icon} {item['priority']}")
                    st.write(f"**Impact:** {item['impact'].upper()}")
                    st.caption(f"**Source:** {item['source']}")
                    st.caption(f"**Date:** {item['published']}")
                
                if item.get('link'):
                    st.link_button("View Original →", item['link'])


# TAB 3 — INDUSTRY NEWS

with tab3:
    
    st.subheader("📰 Industry Intelligence")
    st.write("Live news from your industry — filtered and analyzed for your business.")
    st.divider()
    
    if not st.session_state.news_analyzed:
        st.info("No relevant news found. Try refreshing data.")
    else:
        impact_filter = st.selectbox("Filter by Impact", ["All", "opportunity", "threat", "neutral"])
        
        filtered_news = st.session_state.news_analyzed
        if impact_filter != "All":
            filtered_news = [n for n in filtered_news if n.get("impact") == impact_filter]
        
        st.caption(f"Showing {len(filtered_news)} news items")
        st.divider()
        
        cols = st.columns(2)
        for i, item in enumerate(filtered_news):
            with cols[i % 2]:
                impact_color = "🟢" if item['impact'] == "opportunity" else "🔴" if item['impact'] == "threat" else "🟡"
                st.markdown(f"#### {item['title']}")
                st.write(f"**Summary:** {item['summary']}")
                st.write(f"{impact_color} **{item['impact'].upper()}** — {item['impact_reason']}")
                if item['action_required']:
                    st.info(f"💡 {item['action_steps']}")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.caption(f"📌 {item['source']}")
                with col_b:
                    st.caption(f"🗓️ {item['published']}")
                if item.get('link'):
                    st.link_button("Read →", item['link'])
                st.divider()

# TAB 4 — ANALYTICS

with tab4:
    
    st.subheader("📊 Business Intelligence Analytics")
    st.caption("What the AI found — and what it means for your business today.")
    st.divider()
    
    all_items = (st.session_state.news_analyzed + 
                st.session_state.regulations_analyzed + 
                st.session_state.schemes_analyzed)
    
    if not all_items:
        st.info("Load data first to see analytics.")
    else:
        import plotly.express as px
        import plotly.graph_objects as go
        
        col1, col2 = st.columns([1, 1])
        
        # CHART 1 — IMPACT BREAKDOWN
        with col1:
            st.markdown("#### 🌐 What's Happening Around Your Business")
            st.caption("Are today's updates mostly opportunities or threats?")
            
            impact_counts = {}
            for item in all_items:
                impact = item.get("impact", "neutral").capitalize()
                impact_counts[impact] = impact_counts.get(impact, 0) + 1
            
            labels = list(impact_counts.keys())
            values = list(impact_counts.values())
            
            fig1 = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(
                    colors=["#00c853", "#ff4b4b", "#ffd740"],
                    line=dict(color="#0f1117", width=3)
                ),
                textinfo="label+percent",
                textfont=dict(size=14, color="white"),
                hovertemplate="<b>%{label}</b><br>%{value} items<br>%{percent}<extra></extra>"
            )])
            
            # Add centre text
            total = len(all_items)
            dominant = max(impact_counts, key=impact_counts.get)
            
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", family="Arial"),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=13)
                ),
                margin=dict(t=20, b=60, l=20, r=20),
                height=340,
                annotations=[dict(
                    text=f"<b>{total}</b><br>updates",
                    x=0.5, y=0.5,
                    font=dict(size=16, color="white"),
                    showarrow=False
                )]
            )
            
            st.plotly_chart(fig1, key="impact_chart")
            
            # Insight below chart
            if dominant == "Opportunity":
                st.success(f"🟢 Mostly opportunities today — good time to act")
            elif dominant == "Threat":
                st.error(f"🔴 More threats than usual — review high priority items")
            else:
                st.info(f"🟡 Neutral day — stay informed")
        
        # CHART 2 — TOP ITEMS TABLE
        with col2:
            st.markdown("#### 🎯 Top Items Ranked by AI")
            st.caption("Items the AI rated most relevant to your business.")
            
            top_items = sorted(
                all_items,
                key=lambda x: x.get("relevance_score", 0),
                reverse=True
            )[:8]
            
            # Build a clean visual table using plotly
            titles = [
                (item["title"][:45] + "...") if len(item["title"]) > 45 
                else item["title"] 
                for item in top_items
            ]
            scores = [item.get("relevance_score", 0) for item in top_items]
            impacts = [item.get("impact", "neutral").upper() for item in top_items]
            priorities = [item.get("priority", "LOW") for item in top_items]
            
            # Color code impact column
            impact_colors = [
                "#00c853" if i == "OPPORTUNITY" 
                else "#ff4b4b" if i == "THREAT" 
                else "#ffd740" 
                for i in impacts
            ]
            
            fig2 = go.Figure(data=[go.Table(
                columnwidth=[260, 60, 110, 80],
                header=dict(
                    values=["<b>Title</b>", "<b>Score</b>", "<b>Impact</b>", "<b>Priority</b>"],
                    fill_color="#2d3148",
                    font=dict(color="white", size=13),
                    align="left",
                    height=36
                ),
                cells=dict(
                    values=[titles, 
                            [f"{s}/10" for s in scores],
                            impacts,
                            priorities],
                    fill_color=[
                        ["#1e2130"] * len(top_items),
                        ["#1e2130"] * len(top_items),
                        impact_colors,
                        ["#3d1f1f" if p == "HIGH" 
                         else "#3d3d1f" if p == "MEDIUM" 
                         else "#1f3d1f" 
                         for p in priorities]
                    ],
                    font=dict(color="white", size=12),
                    align="left",
                    height=32
                )
            )])
            
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=0, r=0),
                height=340
            )
            
            st.plotly_chart(fig2, key="relevance_table")
        
        st.divider()
        
        # SUMMARY INSIGHT ROW
        st.markdown("#### 💡 Today's Intelligence Summary")
        
        col3, col4, col5 = st.columns(3)
        
        opportunities_count = sum(1 for i in all_items if i.get("impact") == "opportunity")
        threats_count = sum(1 for i in all_items if i.get("impact") == "threat")
        action_count = sum(1 for i in all_items if i.get("action_required") == True)
        avg_score = round(sum(i.get("relevance_score", 0) for i in all_items) / len(all_items), 1)
        
        with col3:
            st.metric(
                "Opportunities Found",
                opportunities_count,
                help="Updates classified as opportunities for your business"
            )
        with col4:
            st.metric(
                "Threats Detected",
                threats_count,
                help="Updates that could negatively impact your business"
            )
        with col5:
            st.metric(
                "Actions Required",
                action_count,
                help="Updates that require you to do something"
            )
        
        st.divider()
        st.caption(f"Average relevance score across all items: **{avg_score}/10** — higher means more relevant to your specific business profile.")

# TAB 5 — ASK BIZRADAR

with tab5:
    
    st.subheader("🤖 Ask BizRadar")
    st.write("Ask anything about your business — strategy, regulations, expansion, schemes, competitors.")
    st.divider()
    
    # Example questions
    st.write("**Quick questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 How do I expand my business?", width='stretch'):
            st.session_state.pending_question = "How do I expand my business?"
    with col2:
        if st.button("🏛️ What schemes apply to me?", width='stretch'):
            st.session_state.pending_question = "What government schemes and subsidies can my business apply for?"
    with col3:
        if st.button("🌍 How do I start exporting?", width='stretch'):
            st.session_state.pending_question = "What do I need to do to start exporting my products internationally?"
    
    st.divider()
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Handle pending question from buttons
    pending = st.session_state.get("pending_question", None)
    
    # Chat input — stays at bottom
    user_question = st.chat_input("Ask BizRadar anything about your business...")
    
    # Use pending question if no direct input
    if pending and not user_question:
        user_question = pending
        st.session_state.pending_question = None
    
    if user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Get answer
        with st.spinner("BizRadar is thinking..."):
            answer = answer_question(
                question=user_question,
                profile=profile,
                recent_news=st.session_state.news_analyzed,
                recent_regulations=st.session_state.regulations_analyzed
            )
        
        # Add answer to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })
        
        # Rerun to display new messages — stays on current tab
        st.rerun()