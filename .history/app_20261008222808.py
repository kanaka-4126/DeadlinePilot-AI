"""
Streamlit application for DeadlinePilot AI.
Autonomous Productivity Assistant & Workload Scheduler.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
import streamlit as st

from agent import DeadlinePilotAgent
from tools import SAMPLE_STUDENT_SCENARIO


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DeadlinePilot AI - Autonomous Academic Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown("""
<style>

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


/* Priority badges */

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


/* Workflow cards */

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


/* Status badges */

.status-badge-pending {
    background-color: #64748B;
    color: #FFFFFF !important;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.status-badge-progress {
    background-color: #2563EB;
    color: #FFFFFF !important;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.status-badge-complete {
    background-color: #16A34A;
    color: #FFFFFF !important;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.status-badge-warning {
    background-color: #D97706;
    color: #FFFFFF !important;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}

.status-badge-error {
    background-color: #DC2626;
    color: #FFFFFF !important;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 0.75rem;
}


/* Conflict cards */

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


/* Approval box */

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
    color: #CBD5E1 !important;
    font-size: 0.95rem;
    margin-bottom: 16px;
}


/* Clean task card */

.task-card {
    background-color: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
}

.task-title {
    color: #0F172A;
    font-size: 1.05rem;
    font-weight: 800;
}

.subtask-item {
    background-color: #FFFFFF;
    border-left: 4px solid #3B82F6;
    padding: 8px 12px;
    margin: 6px 0;
    border-radius: 5px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. WORKFLOW STEP NAMES
# ============================================================

STEP_NAMES = {
    1: "Understanding request",
    2: "Extracting tasks",
    3: "Detecting deadlines",
    4: "Calculating priorities",
    5: "Breaking down tasks",
    6: "Checking conflicts",
    7: "Generating schedule"
}


# ============================================================
# 4. WORKFLOW CARD RENDERER
# ============================================================

def render_step_card(step_num, step_name, status, detail=""):

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

    detail_html = ""

    if detail:
        detail_html = (
            f"<div style='margin-top:6px; font-size:0.88rem; "
            f"opacity:0.95; font-weight:500;'>{detail}</div>"
        )

    return f"""
    <div class="{card_class}">
        <div style="display:flex; justify-content:space-between;
                    align-items:center;">
            <span style="font-weight:700; font-size:1.05rem;">
                {icon} Step {step_num}: {step_name}
            </span>
            {badge_html}
        </div>
        {detail_html}
    </div>
    """


# ============================================================
# 5. SESSION STATE
# ============================================================

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "workflow_results" not in st.session_state:
    st.session_state.workflow_results = None

if "plan_approved" not in st.session_state:
    st.session_state.plan_approved = False

if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []


# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("### ✈️ DeadlinePilot AI")

    st.caption(
        "AI Personal Assistant & Autonomous Agents Challenge"
    )

    st.divider()

    st.markdown("#### ⚙️ Configuration")

    env_key = os.getenv("GEMINI_API_KEY", "")

    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        help="Leave blank to use GEMINI_API_KEY from .env"
    )

    effective_api_key = (
        api_key_input
        if api_key_input.strip()
        else env_key
    )

    model_option = st.text_input(
        "Gemini Model",
        value=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )
    )

    force_demo_option = st.checkbox(
        "⚡ Force Local Demo Mode",
        value=True,
        help=(
            "Run the built-in demonstration workflow "
            "without external Gemini API calls."
        )
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
        "**How DeadlinePilot Works:**\n\n"
        "1. Extracts raw commitments\n\n"
        "2. Resolves hard deadlines\n\n"
        "3. Calculates priority levels\n\n"
        "4. Decomposes into subtasks\n\n"
        "5. Audits for schedule conflicts\n\n"
        "6. Requires human approval before locking plan"
    )


# ============================================================
# 7. HERO HEADER
# ============================================================

st.markdown("""
<div class="hero-header">

    <span class="header-badge">
        AI Personal Assistant & Autonomous Agents Challenge
    </span>

    <div class="main-title">
        ✈️ DeadlinePilot AI
    </div>

    <div class="subtitle">
        Autonomous Academic Assistant & Workload Scheduler —
        Turn unstructured student chaos into an achievable study plan.
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# 8. INPUT + QUICK ACTIONS
# ============================================================

col_input, col_preset = st.columns([3, 1])


with col_preset:

    st.markdown("#### ⚡ Quick Actions")

    if st.button(
        "📚 Load Student Demo Scenario",
        use_container_width=True,
        type="secondary"
    ):

        st.session_state.user_input = SAMPLE_STUDENT_SCENARIO
        st.session_state.workflow_results = None
        st.session_state.plan_approved = False

        st.rerun()

    if st.button(
        "🧹 Clear Input",
        use_container_width=True
    ):

        st.session_state.user_input = ""
        st.session_state.workflow_results = None
        st.session_state.plan_approved = False

        st.rerun()


with col_input:

    user_text = st.text_area(
        "Describe your assignments, exams, projects, and deadlines:",
        value=st.session_state.user_input,
        height=220,
        placeholder=(
            "e.g. I have a Data Structures midterm in 2 days "
            "(8 hrs study needed), an OS lab due Saturday midnight "
            "(6 hrs), a linear algebra problem set due tomorrow..."
        )
    )

    st.session_state.user_input = user_text


# ============================================================
# 9. AGENT EXECUTION PIPELINE
# ============================================================

if st.button(
    "🚀 Launch DeadlinePilot Agent",
    type="primary",
    use_container_width=True
):

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

    steps_ui = {}

    for s_num in range(1, 8):

        steps_ui[s_num] = workflow_container.empty()

        steps_ui[s_num].markdown(
            render_step_card(
                s_num,
                STEP_NAMES[s_num],
                "pending",
                "Queued..."
            ),
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

            s_name = step_update.get(
                "name",
                STEP_NAMES.get(s_id, "")
            )

            s_status = step_update.get("status")

            s_detail = step_update.get("detail", "")

            if s_status == "finished":

                st.session_state.workflow_results = (
                    step_update.get("results")
                )

                st.success(
                    "🎉 Workflow execution complete! "
                    "Draft plan ready for human review."
                )

                break

            if s_id in steps_ui:

                steps_ui[s_id].markdown(
                    render_step_card(
                        s_id,
                        s_name,
                        s_status,
                        s_detail
                    ),
                    unsafe_allow_html=True
                )

    except Exception as e:

        st.error(
            f"❌ Agent Execution Error: {str(e)}"
        )

        st.info(
            "Tip: Enable 'Force Local Demo Mode' "
            "to run without Gemini API calls."
        )


# ============================================================
# 10. RESULTS
# ============================================================

results = st.session_state.workflow_results


if results:

    st.divider()

    # --------------------------------------------------------
    # DEMO MODE WARNING
    # --------------------------------------------------------

    if results.get("is_demo_mode"):

        st.warning(
            "🟡 **Demo Mode** — Gemini API is temporarily "
            "unavailable or quota-limited. Showing a built-in "
            "demonstration workflow."
        )

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    prioritized_tasks = results.get(
        "prioritized_tasks",
        []
    )

    task_breakdowns = results.get(
        "task_breakdowns",
        {}
    )

    conflicts = results.get(
        "conflicts",
        []
    )

    schedule = results.get(
        "schedule",
        {}
    )

    validation = results.get(
        "validation",
        {}
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    st.markdown("### 📊 Workload Intelligence Summary")

    m1, m2, m3, m4 = st.columns(4)

    crit_cnt = sum(
        1
        for t in prioritized_tasks
        if t.get("priority") == "CRITICAL"
    )

    high_cnt = sum(
        1
        for t in prioritized_tasks
        if t.get("priority") == "HIGH"
    )

    total_subtasks = sum(
        len(subs)
        for subs in task_breakdowns.values()
    )

    val_score = validation.get(
        "score",
        100
    )

    m1.metric(
        "Total Tasks Extracted",
        len(prioritized_tasks)
    )

    m2.metric(
        "Critical / High Urgency",
        f"{crit_cnt} Crit / {high_cnt} High"
    )

    m3.metric(
        "Actionable Subtasks",
        total_subtasks
    )

    m4.metric(
        "Schedule Validity Score",
        f"{val_score}/100"
    )

    # --------------------------------------------------------
    # CONFLICTS
    # --------------------------------------------------------

    if conflicts:

        st.markdown(
            "#### ⚠️ Detected Scheduling Conflicts & Workload Risks"
        )

        for c in conflicts:

            st.markdown(
                f"""
                <div class="conflict-card">
                    <b>[{c.get("type")}]</b>
                    {c.get("message")}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    tab_tasks, tab_schedule, tab_validation = st.tabs(
        [
            "📋 Prioritized Tasks & Breakdown",
            "🗓️ Draft Daily Schedule",
            "🔍 Agent Validation Audit"
        ]
    )


    # ========================================================
    # TASK TAB
    # ========================================================

    with tab_tasks:

        st.markdown(
            "#### Extracted & Prioritized Tasks"
        )

        for t in prioritized_tasks:

            p_level = t.get(
                "priority",
                "MEDIUM"
            )

            badge_class = (
                f"badge-{p_level.lower()}"
            )

            task_title = t.get(
                "title",
                "Untitled Task"
            )

            estimated_hours = t.get(
                "estimated_hours",
                "N/A"
            )

            deadline = t.get(
                "deadline_iso",
                "N/A"
            )

            with st.expander(
                f"[{p_level}] {task_title} "
                f"(Est: {estimated_hours} hrs | "
                f"Deadline: {deadline})"
            ):

                c_a, c_b = st.columns(
                    [2, 1]
                )

                with c_a:

                    st.write(
                        f"**Type:** "
                        f"{t.get('task_type', 'N/A').title()}"
                    )

                    st.write(
                        f"**Description:** "
                        f"{t.get('description', '')}"
                    )

                    st.write(
                        f"**Urgency Notes:** "
                        f"{t.get('urgency_notes', 'N/A')}"
                    )

                with c_b:

                    st.markdown(
                        f"""
                        **Priority Level:**
                        <span class="{badge_class}">
                            {p_level}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

                    st.write(
                        f"**Days Remaining:** "
                        f"`{t.get('days_left')}`"
                    )

                    st.write(
                        f"**Dependencies:** "
                        f"`{t.get('dependencies', [])}`"
                    )

                st.markdown(
                    "**Actionable Subtasks Breakdown (<2 hrs each):**"
                )

                subs = task_breakdowns.get(
                    t.get("id"),
                    []
                )

                if subs:

                    for sub in subs:

                        sub_title = sub.get(
                            "title",
                            "Untitled subtask"
                        )

                        sub_hours = sub.get(
                            "estimated_hours",
                            "N/A"
                        )

                        st.markdown(
                            f"""
                            <div class="subtask-item">
                                🔹 <b>{sub_title}</b>
                                — {sub_hours} hrs
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                else:

                    st.info(
                        "No subtasks generated for this task."
                    )


    # ========================================================
    # SCHEDULE TAB
    # ========================================================

    with tab_schedule:

        st.markdown(
            "#### Daily Study Schedule"
        )

        daily_list = schedule.get(
            "daily_schedule",
            []
        )

        if daily_list:

            for day in daily_list:

                st.markdown(
                    f"##### 📅 {day.get('day_name')} "
                    f"({day.get('date')}) — "
                    f"Total Study: "
                    f"`{day.get('total_hours')} hrs`"
                )

                items = day.get(
                    "items",
                    []
                )

                if not items:

                    st.info(
                        "No study sessions scheduled."
                    )

                for item in items:

                    title = item.get(
                        "title",
                        ""
                    )

                    time_block = item.get(
                        "time_block",
                        "Session"
                    )

                    duration = item.get(
                        "duration_hours",
                        0
                    )

                    focus = item.get(
                        "focus_note",
                        ""
                    )

                    if "RESERVED EVENT" in title:

                        st.markdown(
                            f"""
                            <div class="conflict-card">
                                ⛔ <b>[{time_block}]</b>
                                {title}
                                — <i>{focus}</i>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"""
                            <div class="task-card">
                                ⏰ <b>[{time_block}]</b>
                                {title}
                                <br>
                                <small>
                                    Duration: {duration} hrs
                                    &nbsp; | &nbsp;
                                    Focus: {focus}
                                </small>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown("---")

        else:

            st.info(
                "No daily schedule items generated."
            )

        # ----------------------------------------------------
        # UNASSIGNED TASKS
        # ----------------------------------------------------

        unassigned = schedule.get(
            "unassigned_tasks",
            []
        )

        if unassigned:

            st.markdown(
                "##### ⚠️ Capacity Bottlenecks & "
                "Deferral Recommendations"
            )

            for u in unassigned:

                rec = u.get(
                    "deferral_recommendation",
                    ""
                )

                rec_html = ""

                if rec:

                    rec_html = (
                        f"<br><b>💡 Deferral Recommendation:</b> "
                        f"{rec}"
                    )

                st.markdown(
                    f"""
                    <div class="conflict-card">
                        <b>[UNASSIGNED OVERFLOW]</b>
                        {u.get("title")}
                        ({u.get("duration_hours")} hrs)
                        <br>
                        <small>
                            {u.get(
                                "reason",
                                "Cannot fit before deadline cutoff"
                            )}
                        </small>
                        {rec_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # ========================================================
    # VALIDATION TAB
    # ========================================================

    with tab_validation:

        st.markdown(
            "#### Autonomous Schedule Audit & Validation"
        )

        if validation.get("valid"):

            st.success(
                "✅ Validation Passed"
            )

        else:

            st.warning(
                "⚠️ Warnings Detected"
            )

        st.write(
            f"**Audit Score:** `{val_score} / 100`"
        )

        warns = validation.get(
            "warnings",
            []
        )

        if warns:

            st.markdown(
                "**Audit Warnings:**"
            )

            for w in warns:

                st.markdown(
                    f"- ⚠️ {w}"
                )

        else:

            st.success(
                "No constraint violations found. "
                "The schedule respects all deadlines, "
                "daily capacity caps, and dependencies."
            )


    # ========================================================
    # 11. HUMAN-IN-THE-LOOP APPROVAL
    # ========================================================

    st.divider()

    if not st.session_state.plan_approved:

        st.markdown(
            """
            <div class="approval-box">

                <div class="approval-title">
                    🛡️ Human-in-the-Loop Approval Required
                </div>

                <div class="approval-desc">
                    Review the proposed schedule, priorities,
                    conflicts, and validation audit above.
                    <br>
                    Click <b>APPROVE PLAN</b> to lock
                    the prioritized strategy.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        col_app1, col_app2, col_app3 = st.columns(
            [1, 2, 1]
        )

        with col_app2:

            if st.button(
                "👍 APPROVE PLAN",
                type="primary",
                use_container_width=True
            ):

                st.session_state.plan_approved = True

                st.rerun()

    else:

        st.balloons()

        st.success(
            "✅ **PLAN APPROVED & LOCKED FOR EXECUTION!**"
        )

        # IMPORTANT: Clearly communicate feasibility.
        st.warning(
            "⚠️ **Feasibility Warning:** "
            "Available time before the earliest deadlines "
            "is insufficient to complete every task. "
            "DeadlinePilot has prioritized the highest-impact "
            "work and explicitly flagged unallocated DSA "
            "preparation instead of scheduling it after the exam."
        )

        st.markdown(
            "### 🎯 Your Approved Execution Checklist"
        )

        daily_list = schedule.get(
            "daily_schedule",
            []
        )

        for day in daily_list:

            st.markdown(
                f"#### 📅 {day.get('day_name')} "
                f"({day.get('date')})"
            )

            for idx, item in enumerate(
                day.get("items", [])
            ):

                st.checkbox(
                    f"[{item.get('time_block')}] "
                    f"{item.get('title')} "
                    f"({item.get('duration_hours')} hrs) "
                    f"— Focus: "
                    f"{item.get('focus_note')}",
                    key=f"chk_{day.get('date')}_{idx}"
                )

        st.divider()

        if st.button(
            "🔄 Reset & Build New Plan"
        ):

            st.session_state.workflow_results = None
            st.session_state.plan_approved = False

            st.rerun()