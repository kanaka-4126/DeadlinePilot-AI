"""
Streamlit application for DeadlinePilot AI.
Autonomous Productivity Assistant & Workload Scheduler.
"""

import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

from agent import DeadlinePilotAgent, DEFAULT_MODEL
from tools import SAMPLE_STUDENT_SCENARIO

# 1. Page Configuration
st.set_page_config(
    page_title="DeadlinePilot AI - Autonomous Academic Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# 2. Custom CSS styling for high-contrast, professional WCAG-compliant UI
st.markdown("""
<style>
    /* Hero Header Banner Card */
    .hero-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-left: 8px solid #3B82F6;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .header-badge {
        background-color: #2563EB;
        color: #FFFFFF !important;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 0.8px;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .main-title {
        font-size: 2.6rem;
        font-weight: 900;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .subtitle {
        font-size: 1.15rem;
        color: #CBD5E1 !important;
        margin-top: 8px;
        margin-bottom: 0;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* Priority Badges - High Contrast Text */
    .badge-critical {
        background-color: #991B1B;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1px solid #7F1D1D;
        display: inline-block;
    }
    .badge-high {
        background-color: #C2410C;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1px solid #9A3412;
        display: inline-block;
    }
    .badge-medium {
        background-color: #1D4ED8;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1px solid #1E40AF;
        display: inline-block;
    }
    .badge-low {
        background-color: #15803D;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1px solid #166534;
        display: inline-block;
    }

    /* Workflow Pipeline Step Cards - High Contrast & Distinct States */
    .step-card-pending {
        background-color: #F1F5F9;
        color: #334155 !important;
        border: 1.5px solid #CBD5E1;
        border-left: 6px solid #94A3B8;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-radius: 8px;
    }
    .step-card-progress {
        background-color: #EFF6FF;
        color: #1E3A8A !important;
        border: 2px solid #3B82F6;
        border-left: 6px solid #2563EB;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.15);
    }
    .step-card-complete {
        background-color: #F0FDF4;
        color: #14532D !important;
        border: 1.5px solid #86EFAC;
        border-left: 6px solid #16A34A;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-radius: 8px;
    }
    .step-card-warning {
        background-color: #FFFBEB;
        color: #78350F !important;
        border: 1.5px solid #FDE68A;
        border-left: 6px solid #D97706;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-radius: 8px;
    }
    .step-card-error {
        background-color: #FEF2F2;
        color: #7F1D1D !important;
        border: 1.5px solid #FCA5A5;
        border-left: 6px solid #DC2626;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-radius: 8px;
    }

    /* Status Text Badges inside Step Cards */
    .status-badge-pending {
        background-color: #64748B;
        color: #FFFFFF !important;
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }
    .status-badge-progress {
        background-color: #2563EB;
        color: #FFFFFF !important;
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }
    .status-badge-complete {
        background-color: #16A34A;
        color: #FFFFFF !important;
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }
    .status-badge-warning {
        background-color: #D97706;
        color: #FFFFFF !important;
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }

    /* Conflict Warning Cards */
    .conflict-card {
        background-color: #FEF2F2;
        color: #7F1D1D !important;
        border: 1.5px solid #FCA5A5;
        border-left: 6px solid #DC2626;
        padding: 14px 18px;
        margin-bottom: 10px;
        border-radius: 8px;
        font-size: 0.95rem;
    }

    /* Human-in-the-Loop Gating Box */
    .approval-box {
        background-color: #0F172A;
        color: #F8FAFC !important;
        border: 2px dashed #3B82F6;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-top: 24px;
        margin-bottom: 24px;
    }
    .approval-title {
        color: #FFFFFF !important;
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .approval-desc {
        color: #94A3B8 !important;
        font-size: 0.95rem;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


STEP_NAMES = {
    1: "Understanding request",
    2: "Extracting tasks",
    3: "Detecting deadlines",
    4: "Calculating priorities",
    5: "Breaking down tasks",
    6: "Checking conflicts",
    7: "Generating schedule"
}


def render_step_card(step_num, step_name, status, detail=""):
    """Render a high-contrast HTML card for a workflow step."""
    if status == "completed":
        card_class = "step-card-complete"
        badge_html = '<span class="status-badge-complete">✔ COMPLETED</span>'
        icon = "✅"
    elif status == "in_progress":
        card_class = "step-card-progress"
        badge_html = '<span class="status-badge-progress">⏳ IN PROGRESS</span>'
        icon = "🔄"
    elif status == "warning":
        card_class = "step-card-warning"
        badge_html = '<span class="status-badge-warning">⚠️ WARNING</span>'
        icon = "⚠️"
    elif status == "error":
        card_class = "step-card-error"
        badge_html = '<span class="status-badge-error">❌ ERROR</span>'
        icon = "❌"
    else:
        card_class = "step-card-pending"
        badge_html = '<span class="status-badge-pending">💤 PENDING</span>'
        icon = "⚪"

    detail_html = f"<div style='margin-top: 6px; font-size: 0.88rem; opacity: 0.95; font-weight: 500;'>{detail}</div>" if detail else ""

    return f"""
    <div class="{card_class}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 1.05rem;">{icon} Step {step_num}: {step_name}</span>
            {badge_html}
        </div>
        {detail_html}
    </div>
    """


# 3. Session State Initialization
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "workflow_results" not in st.session_state:
    st.session_state.workflow_results = None
if "plan_approved" not in st.session_state:
    st.session_state.plan_approved = False
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []


# 4. Sidebar Configuration
with st.sidebar:
    st.markdown("### ✈️ DeadlinePilot AI")
    st.caption("AI Personal Assistant & Autonomous Agents Challenge")
    st.divider()

    st.markdown("#### ⚙️ Configuration")
    
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        help="Leave blank to use GEMINI_API_KEY from .env file"
    )
    
    effective_api_key = api_key_input if api_key_input.strip() else env_key

    model_option = st.text_input(
        "Gemini Model",
        value=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        help="Default model is gemini-3.8-flash"
    )

    force_demo_option = st.checkbox(
        "⚡ Force Local Demo Mode",
        value=True,
        help="Run built-in local demonstration workflow without making any external Gemini API calls"
    )


    st.divider()
    st.markdown("#### 🗓️ Scheduling Parameters")
    
    ref_date = st.date_input(
        "Reference Date (Today)",
        value=datetime.now().date()
    )
    
    max_hours = st.slider(
        "Max Daily Study Capacity (Hours)",
        min_value=2.0,
        max_value=12.0,
        value=6.0,
        step=0.5
    )

    st.divider()
    st.info(
        "**How DeadlinePilot Works:**\n"
        "1. Extracts raw commitments\n"
        "2. Resolves hard deadlines\n"
        "3. Calculates priority levels\n"
        "4. Decomposes into subtasks\n"
        "5. Audits for schedule conflicts\n"
        "6. Requires human approval before locking plan"
    )


# 5. Header Section (High-Contrast Hero Banner)
st.markdown("""
<div class="hero-header">
    <span class="header-badge">AI Personal Assistant & Autonomous Agents Challenge</span>
    <div class="main-title">✈️ DeadlinePilot AI</div>
    <div class="subtitle">Autonomous Academic Assistant & Workload Scheduler — Turn unstructured student chaos into an achievable study plan.</div>
</div>
""", unsafe_allow_html=True)

# 6. Input Section & Demo Preset Buttons
col_input, col_preset = st.columns([3, 1])

with col_preset:
    st.markdown("#### ⚡ Quick Actions")
    if st.button("📚 Load Student Demo Scenario", use_container_width=True, type="secondary"):
        st.session_state.user_input = SAMPLE_STUDENT_SCENARIO
        st.session_state.workflow_results = None
        st.session_state.plan_approved = False
        st.rerun()

    if st.button("🧹 Clear Input", use_container_width=True):
        st.session_state.user_input = ""
        st.session_state.workflow_results = None
        st.session_state.plan_approved = False
        st.rerun()

with col_input:
    user_text = st.text_area(
        "Describe your assignments, exams, projects, and deadlines:",
        value=st.session_state.user_input,
        height=220,
        placeholder="e.g. I have a Data Structures midterm in 2 days (8 hrs study needed), an OS lab due Saturday midnight (6 hrs), a linear algebra problem set due tomorrow..."
    )
    st.session_state.user_input = user_text


# 7. Agent Execution Pipeline
if st.button("🚀 Launch DeadlinePilot Agent", type="primary", use_container_width=True):
    if not user_text.strip():
        user_text = SAMPLE_STUDENT_SCENARIO
        st.session_state.user_input = user_text

    st.session_state.plan_approved = False
    st.session_state.workflow_results = None
    
    st.markdown("### 🔄 Autonomous Agent Workflow Pipeline")
    workflow_container = st.container()
    
    agent = DeadlinePilotAgent(
        api_key=effective_api_key,
        model_name=model_option
    )

    # Pre-render all 7 steps as PENDING cards for immediate visual clarity
    steps_ui = {}
    for s_num in range(1, 8):
        steps_ui[s_num] = workflow_container.empty()
        steps_ui[s_num].markdown(
            render_step_card(s_num, STEP_NAMES[s_num], "pending", "Queued..."),
            unsafe_allow_html=True
        )

    ref_date_str = ref_date.strftime("%Y-%m-%d")
    
    try:
        workflow_stream = agent.run_workflow_stream(
            user_input=user_text,
            current_date=ref_date_str,
            max_daily_hours=max_hours,
            force_demo=force_demo_option
        )

        for step_update in workflow_stream:
            s_id = step_update.get("step")
            s_name = step_update.get("name", STEP_NAMES.get(s_id, ""))
            s_status = step_update.get("status")
            s_detail = step_update.get("detail", "")

            if s_status == "finished":
                st.session_state.workflow_results = step_update.get("results")
                st.success("🎉 Workflow execution complete! Draft plan ready for human review.")
                break

            if s_id in steps_ui:
                steps_ui[s_id].markdown(
                    render_step_card(s_id, s_name, s_status, s_detail),
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"❌ Agent Execution Error: {str(e)}")
        st.info("Tip: If experiencing a 503/429 API error, check 'Force Local Demo Mode' in the sidebar.")


# 8. Results & Approval Gating View
results = st.session_state.workflow_results

if results:
    st.divider()

    if results.get("is_demo_mode"):
        st.warning("🟡 Demo Mode — Gemini API is temporarily unavailable or quota-limited. Showing a built-in demonstration workflow.")

    prioritized_tasks = results.get("prioritized_tasks", [])
    task_breakdowns = results.get("task_breakdowns", {})
    conflicts = results.get("conflicts", [])
    schedule = results.get("schedule", {})
    validation = results.get("validation", {})

    # Overview Metrics Cards
    st.markdown("### 📊 Workload Intelligence Summary")
    m1, m2, m3, m4 = st.columns(4)
    
    crit_cnt = sum(1 for t in prioritized_tasks if t.get("priority") == "CRITICAL")
    high_cnt = sum(1 for t in prioritized_tasks if t.get("priority") == "HIGH")
    total_subtasks = sum(len(subs) for subs in task_breakdowns.values())
    val_score = validation.get("score", 100)

    m1.metric("Total Tasks Extracted", len(prioritized_tasks))
    m2.metric("Critical / High Urgency", f"{crit_cnt} Crit / {high_cnt} High")
    m3.metric("Actionable Subtasks", total_subtasks)
    m4.metric("Schedule Validity Score", f"{val_score}/100")

    # Conflict Callout Box
    if conflicts:
        st.markdown("#### ⚠️ Detected Scheduling Conflicts & Workload Risks")
        for c in conflicts:
            st.markdown(
                f'<div class="conflict-card"><b>[{c.get("type")}]</b> {c.get("message")}</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # Detailed Tabs
    tab_tasks, tab_schedule, tab_validation = st.tabs(["📋 Prioritized Tasks & Breakdown", "🗓️ Draft Daily Schedule", "🔍 Agent Validation Audit"])

    with tab_tasks:
        st.markdown("#### Extracted & Prioritized Tasks")
        for t in prioritized_tasks:
            p_level = t.get("priority", "MEDIUM")
            badge_class = f"badge-{p_level.lower()}"
            
            with st.expander(f"[{p_level}] {t.get('title')} (Est: {t.get('estimated_hours')} hrs | Deadline: {t.get('deadline_iso')})"):
                c_a, c_b = st.columns([2, 1])
                with c_a:
                    st.write(f"**Type:** {t.get('task_type', 'N/A').title()}")
                    st.write(f"**Description:** {t.get('description', '')}")
                    st.write(f"**Urgency Notes:** {t.get('urgency_notes', 'N/A')}")
                with c_b:
                    st.markdown(f"**Priority Level:** <span class='{badge_class}'>{p_level}</span>", unsafe_allow_html=True)
                    st.write(f"**Days Remaining:** `{t.get('days_left')}`")
                    st.write(f"**Dependencies:** `{t.get('dependencies', [])}`")

                st.markdown("**Actionable Subtasks Breakdown (<2 hrs each):**")
                subs = task_breakdowns.get(t.get("id"), [])
                for sub in subs:
                    st.markdown(f"- 🔹 **{sub.get('title')}** ({sub.get('estimated_hours')} hrs)")

    with tab_schedule:
        st.markdown("#### Daily Study Schedule")
        daily_list = schedule.get("daily_schedule", [])
        if daily_list:
            for day in daily_list:
                st.markdown(f"##### 📅 {day.get('day_name')} ({day.get('date')}) — Total Study: `{day.get('total_hours')} hrs`")
                for item in day.get("items", []):
                    title = item.get("title", "")
                    if "RESERVED EVENT" in title:
                        st.markdown(
                            f" - ⛔ **[{item.get('time_block', 'Morning')}]** <span style='color: #DC2626; font-weight: 800;'>{title}</span> "
                            f"— *{item.get('focus_note', 'Exam event time reserved')}*",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f" - ⏰ **[{item.get('time_block', 'Session')}]** {title} "
                            f"(`{item.get('duration_hours')} hrs`) — *Focus: {item.get('focus_note', '')}*"
                        )
                st.markdown("---")
        else:
            st.info("No daily schedule items generated.")

        unassigned = schedule.get("unassigned_tasks", [])
        if unassigned:
            st.markdown("##### ⚠️ Capacity Bottlenecks & Deferral Recommendations")
            for u in unassigned:
                rec = u.get("deferral_recommendation", "")
                rec_html = f"<br><b>💡 Deferral Recommendation:</b> {rec}" if rec else ""
                st.markdown(
                    f'<div class="conflict-card"><b>[UNASSIGNED OVERFLOW]</b> {u.get("title")} ({u.get("duration_hours")} hrs)<br>'
                    f'<small>{u.get("reason", "Cannot fit before deadline cutoff")}</small>{rec_html}</div>',
                    unsafe_allow_html=True
                )



    with tab_validation:
        st.markdown("#### Autonomous Schedule Audit & Validation")
        st.write(f"**Validation Status:** {'✅ PASSED' if validation.get('valid') else '⚠️ WARNINGS DETECTED'}")
        st.write(f"**Audit Score:** `{val_score} / 100`")
        
        warns = validation.get("warnings", [])
        if warns:
            st.markdown("**Audit Warnings:**")
            for w in warns:
                st.write(f"- ⚠️ {w}")
        else:
            st.success("No constraint violations found. The schedule respects all deadlines, daily capacity caps, and subtask dependencies.")


    # 9. Human-in-the-Loop Approval Gating
    st.divider()
    if not st.session_state.plan_approved:
        st.markdown("""
        <div class="approval-box">
            <div class="approval-title">🛡️ Human-in-the-Loop Approval Required</div>
            <div class="approval-desc">Please review the proposed schedule, task priorities, and conflict audits above.<br>Click <b>APPROVE PLAN</b> to lock in your final study strategy.</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_app1, col_app2, col_app3 = st.columns([1, 2, 1])
        with col_app2:
            if st.button("👍 APPROVE PLAN", type="primary", use_container_width=True):
                st.session_state.plan_approved = True
                st.rerun()

    else:
        st.balloons()
        st.success("✅ **PLAN APPROVED & LOCKED FOR EXECUTION!**")
        st.markdown("### 🎯 Your Approved Execution Checklist")
        
        daily_list = schedule.get("daily_schedule", [])
        for day in daily_list:
            st.markdown(f"#### 📅 {day.get('day_name')} ({day.get('date')})")
            for idx, item in enumerate(day.get("items", [])):
                st.checkbox(
                    f"[{item.get('time_block')}] {item.get('title')} ({item.get('duration_hours')} hrs) — Focus: {item.get('focus_note')}",
                    key=f"chk_{day.get('date')}_{idx}"
                )
        
        st.divider()
        if st.button("🔄 Reset & Build New Plan"):
            st.session_state.workflow_results = None
            st.session_state.plan_approved = False
            st.rerun()
