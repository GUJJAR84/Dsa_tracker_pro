import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
from collections import Counter
import random
import database as db
import re

# ─── Page Config ────────────────────────────────────────────
st.set_page_config(page_title="DSA Tracker Pro", page_icon="🚀", layout="wide")

# ─── Premium CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-primary: #0f172a;
    --bg-card: #1e293b;
    --bg-card-hover: #334155;
    --accent: #6366f1;
    --accent-light: #818cf8;
    --accent-glow: rgba(99,102,241,0.15);
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
    --text: #f1f5f9;
    --text-muted: #94a3b8;
    --border: #334155;
}

.stApp {
    font-family: 'Inter', sans-serif;
}

/* ── Metric Cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px 22px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.12);
}
div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
    font-size: 28px !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    color: #22c55e !important;
    font-weight: 600 !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid #334155;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    padding: 4px 0;
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.4) !important;
}

/* ── Progress bars ── */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa) !important;
    border-radius: 8px !important;
}
div[data-testid="stProgress"] {
    height: 10px !important;
}

/* ── Expanders ── */
details {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
details summary {
    font-weight: 600 !important;
    padding: 12px 16px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 14px !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    border-bottom-color: #6366f1 !important;
    color: #6366f1 !important;
}

/* ── Custom Cards (HTML) ── */
.stat-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.stat-card .number { font-size: 36px; font-weight: 800; color: #f1f5f9; }
.stat-card .label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.stat-card.green .number { color: #22c55e; }
.stat-card.yellow .number { color: #eab308; }
.stat-card.red .number { color: #ef4444; }
.stat-card.purple .number { color: #a78bfa; }

.streak-banner {
    background: linear-gradient(135deg, #f59e0b22, #f9731622);
    border: 1px solid #f59e0b44;
    border-radius: 12px;
    padding: 12px 20px;
    text-align: center;
    font-size: 16px;
    margin: 10px 0;
}

.milestone-badge {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 14px;
    display: inline-block;
    margin: 4px;
    box-shadow: 0 2px 10px rgba(99,102,241,0.3);
}

.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #94a3b8;
}
.empty-state .icon { font-size: 48px; margin-bottom: 12px; }
.empty-state .title { font-size: 18px; font-weight: 600; color: #64748b; margin-bottom: 8px; }
.empty-state .desc { font-size: 14px; color: #94a3b8; }

.tag-pill {
    display: inline-block;
    background: #6366f122;
    color: #818cf8;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    margin: 2px 3px;
    border: 1px solid #6366f133;
}
</style>
""", unsafe_allow_html=True)



# ─── Motivational Messages ──────────────────────────────────
MOTIVATIONAL = [
    "Every problem you solve makes you stronger 💪",
    "Consistency beats intensity. Keep showing up! 🔥",
    "You're building patterns that last a lifetime 🧠",
    "The best time to solve is now. Let's go! 🚀",
    "Small daily improvements lead to big results 📈",
    "DSA is a marathon, not a sprint. Pace yourself! 🏃",
    "Master the pattern, master the interview 🎯",
]

def get_streak_msg(streak):
    if streak == 0: return "Start your streak today! 🌱"
    if streak < 3: return f"🔥 {streak}-day streak — keep it going!"
    if streak < 7: return f"🔥🔥 {streak}-day streak — you're on fire!"
    if streak < 14: return f"🔥🔥🔥 {streak}-day streak — UNSTOPPABLE!"
    if streak < 30: return f"⚡ {streak}-day streak — LEGENDARY status!"
    return f"👑 {streak}-day streak — you're a DSA MACHINE!"

def get_milestone_badges(solved):
    badges = []
    for m in [5, 10, 25, 50, 75, 100, 125, 150]:
        if solved >= m:
            badges.append(m)
    return badges

# ─── NeetCode 150 ───────────────────────────────────────────
NEETCODE_150 = {
    "Arrays & Hashing": ["Contains Duplicate","Valid Anagram","Two Sum","Group Anagrams","Top K Frequent Elements","Encode and Decode Strings","Product of Array Except Self","Valid Sudoku","Longest Consecutive Sequence"],
    "Two Pointers": ["Valid Palindrome","Two Sum II","3Sum","Container With Most Water","Trapping Rain Water"],
    "Sliding Window": ["Best Time to Buy and Sell Stock","Longest Substring Without Repeating Characters","Longest Repeating Character Replacement","Permutation in String","Minimum Window Substring","Sliding Window Maximum"],
    "Stack": ["Valid Parentheses","Min Stack","Evaluate Reverse Polish Notation","Generate Parentheses","Daily Temperatures","Car Fleet","Largest Rectangle in Histogram"],
    "Binary Search": ["Binary Search","Search a 2D Matrix","Koko Eating Bananas","Find Minimum in Rotated Sorted Array","Search in Rotated Sorted Array","Time Based Key-Value Store","Median of Two Sorted Arrays"],
    "Linked List": ["Reverse Linked List","Merge Two Sorted Lists","Reorder List","Remove Nth Node From End of List","Copy List with Random Pointer","Add Two Numbers","Linked List Cycle","Find The Duplicate Number","LRU Cache","Merge K Sorted Lists","Reverse Nodes in K-Group"],
    "Trees": ["Invert Binary Tree","Maximum Depth of Binary Tree","Diameter of Binary Tree","Balanced Binary Tree","Same Tree","Subtree of Another Tree","Lowest Common Ancestor of BST","Binary Tree Level Order Traversal","Binary Tree Right Side View","Count Good Nodes in Binary Tree","Validate Binary Search Tree","Kth Smallest Element in a BST","Construct Binary Tree from Preorder and Inorder Traversal","Binary Tree Maximum Path Sum","Serialize and Deserialize Binary Tree"],
    "Tries": ["Implement Trie","Design Add and Search Words Data Structure","Word Search II"],
    "Heap / Priority Queue": ["Kth Largest Element in a Stream","Last Stone Weight","K Closest Points to Origin","Kth Largest Element in an Array","Task Scheduler","Design Twitter","Find Median from Data Stream"],
    "Backtracking": ["Subsets","Combination Sum","Permutations","Subsets II","Combination Sum II","Word Search","Palindrome Partitioning","Letter Combinations of a Phone Number","N-Queens"],
    "Graphs": ["Number of Islands","Max Area of Island","Clone Graph","Walls and Gates","Rotting Oranges","Pacific Atlantic Water Flow","Surrounded Regions","Course Schedule","Course Schedule II","Graph Valid Tree","Number of Connected Components","Redundant Connection","Word Ladder"],
    "Advanced Graphs": ["Reconstruct Itinerary","Min Cost to Connect All Points","Network Delay Time","Swim in Rising Water","Alien Dictionary","Cheapest Flights Within K Stops"],
    "1-D Dynamic Programming": ["Climbing Stairs","Min Cost Climbing Stairs","House Robber","House Robber II","Longest Palindromic Substring","Palindromic Substrings","Decode Ways","Coin Change","Maximum Product Subarray","Word Break","Longest Increasing Subsequence","Partition Equal Subset Sum"],
    "2-D Dynamic Programming": ["Unique Paths","Longest Common Subsequence","Best Time to Buy and Sell Stock with Cooldown","Coin Change II","Target Sum","Interleaving String","Longest Increasing Path in a Matrix","Distinct Subsequences","Edit Distance","Burst Balloons","Regular Expression Matching"],
    "Greedy": ["Maximum Subarray","Jump Game","Jump Game II","Gas Station","Hand of Straights","Merge Triplets to Form Target Triplet","Partition Labels","Valid Parenthesis String"],
    "Intervals": ["Insert Interval","Merge Intervals","Non-overlapping Intervals","Meeting Rooms","Meeting Rooms II","Minimum Interval to Include Each Query"],
    "Math & Geometry": ["Rotate Image","Spiral Matrix","Set Matrix Zeroes","Happy Number","Plus One","Pow(x, n)","Multiply Strings","Detect Squares"],
    "Bit Manipulation": ["Single Number","Number of 1 Bits","Counting Bits","Reverse Bits","Missing Number","Sum of Two Integers","Reverse Integer"],
}
ALL_PATTERNS = sorted(NEETCODE_150.keys()) + ["Other"]
TOTAL_NEETCODE = sum(len(v) for v in NEETCODE_150.values())

def get_leetcode_url(name):
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # remove special chars
    slug = re.sub(r'\s+', '-', slug)            # spaces to hyphens
    slug = re.sub(r'-+', '-', slug).strip('-')  # clean double hyphens
    return f"https://leetcode.com/problems/{slug}/"

# ─── Load from SQLite ──────────────────────────────────────
settings = db.get_settings()
problems_list = db.get_problems()
solved_count = len(problems_list)

# ─── Sidebar ────────────────────────────────────────────────
st.sidebar.markdown("# 🚀 DSA Tracker Pro")
st.sidebar.markdown("---")

if settings["start_date"] is None:
    st.sidebar.subheader("Set Start Date")
    start = st.sidebar.date_input("When did you start?", date.today())
    if st.sidebar.button("🎯 Start Journey", type="primary"):
        db.update_settings(start_date=str(start))
        st.rerun()
else:
    start_date = datetime.strptime(settings["start_date"], "%Y-%m-%d").date()
    days_elapsed = (date.today() - start_date).days
    current_week = min((days_elapsed // 7) + 1, 12)
    st.sidebar.metric("📅 Day", f"{days_elapsed + 1} / 84")
    st.sidebar.metric("📆 Week", f"{current_week} / 12")
    st.sidebar.metric("🔥 Streak", f"{settings['streak']} days")

st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "📊 Dashboard", "💻 DSA Tracker", "📖 Problem Solutions",
    "🗺️ NeetCode 150", "🔄 Revision Tracker", "🔍 Search & Filter",
    "📚 Learning (Short)", "🏗️ Projects (Long)", "📈 Analytics"
])

st.sidebar.markdown("---")
# Export Button
if problems_list:
    md_lines = ["# My DSA Solutions\n"]
    for p in problems_list:
        md_lines.append(f"\n## {p['name']}")
        md_lines.append(f"**Platform:** {p.get('platform','N/A')} | **Difficulty:** {p['difficulty']} | **Pattern:** {p['pattern']}")
        md_lines.append(f"**Date:** {p['date']} | **Time:** {p.get('time_taken',0)} min | **Confidence:** {p.get('confidence','-')}/5\n")
        if p.get("problem_url"): md_lines.append(f"**Link:** {p['problem_url']}\n")
        if p.get("approach"): md_lines.append(f"### Approach\n{p['approach']}\n")
        if p.get("code"):
            lang = p.get("language","java").lower()
            md_lines.append(f"### Solution ({p.get('language','Java')})\n```{lang}\n{p['code']}\n```\n")
        if p.get("time_complexity") or p.get("space_complexity"):
            md_lines.append(f"**Time:** {p.get('time_complexity','–')} | **Space:** {p.get('space_complexity','–')}\n")
        if p.get("key_learnings"): md_lines.append(f"### Key Learnings\n{p['key_learnings']}\n")
        if p.get("mistakes"): md_lines.append(f"### Mistakes\n{p['mistakes']}\n")
        md_lines.append("---")
    st.sidebar.download_button("📥 Export Solutions (MD)", "\n".join(md_lines), "dsa_solutions.md", "text/markdown")

    # CSV Export
    csv_header = "Name,Platform,Difficulty,Pattern,Language,Date,Time(min),Confidence,Independent,Time Complexity,Space Complexity,URL\n"
    csv_rows = []
    for p in problems_list:
        row = [
            p['name'], p.get('platform',''), p['difficulty'], p['pattern'],
            p.get('language',''), p.get('date',''), str(p.get('time_taken',0)),
            str(p.get('confidence','')), str(p.get('independent',False)),
            p.get('time_complexity',''), p.get('space_complexity',''),
            p.get('problem_url','')
        ]
        csv_rows.append(",".join(f'"{c}"' for c in row))
    csv_data = csv_header + "\n".join(csv_rows)
    st.sidebar.download_button("📥 Export CSV", csv_data, "dsa_problems.csv", "text/csv", key="csv_export")

st.sidebar.markdown("---")
st.sidebar.caption("Built for the **15 LPA Journey** 🎯")

# ═══════════════════════════════════════════════════════════
# ─── DASHBOARD ─────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Progress Dashboard")

    if settings["start_date"]:
        # Motivational quote
        st.markdown(f"> *{random.choice(MOTIVATIONAL)}*")

        # Streak banner
        st.markdown(f'<div class="streak-banner">{get_streak_msg(settings["streak"])}</div>', unsafe_allow_html=True)

        # Milestone badges
        badges = get_milestone_badges(solved_count)
        if badges:
            badge_html = "".join(f'<span class="milestone-badge">🏆 {b} solved</span>' for b in badges)
            st.markdown(f"<div style='margin:10px 0'>{badge_html}</div>", unsafe_allow_html=True)

        # Key Metrics
        topics_data = db.get_topics()
        projects_data = db.get_projects()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("DSA Solved", f"{solved_count} / 150", f"{round(solved_count/150*100)}%")
        completed_topics = sum(1 for t in topics_data.values() if t['studied'] and t['built'] and t['posted'])
        c2.metric("Topics", f"{completed_topics} / {len(topics_data)}", f"{round(completed_topics/max(len(topics_data),1)*100)}%")
        deployed = sum(1 for p in projects_data.values() if p['deployed'])
        c3.metric("Projects", f"{deployed} / {len(projects_data)}", f"{round(deployed/max(len(projects_data),1)*100)}%")
        c4.metric("LinkedIn", settings['linkedin_posts'], "Keep posting!")

        st.markdown("---")

        # Progress overview with percentage labels
        st.subheader("📈 Overall Progress")
        pc1, pc2 = st.columns(2)
        with pc1:
            pct = round(solved_count/150*100)
            st.markdown(f"**DSA Progress** — `{pct}%`")
            st.progress(min(solved_count/150, 1.0))
            pct2 = round(completed_topics/max(len(topics_data),1)*100)
            st.markdown(f"**Learning Topics** — `{pct2}%`")
            st.progress(min(completed_topics/max(len(topics_data),1), 1.0))
        with pc2:
            total_pp = sum(sum(1 for k, v in p.items() if k in ('week1','week2','week3','week4','deployed') and v) for p in projects_data.values())
            total_possible = len(projects_data) * 5 if projects_data else 1
            pct3 = round(total_pp/total_possible*100)
            st.markdown(f"**Projects** — `{pct3}%`")
            st.progress(min(total_pp/total_possible, 1.0))
            pct4 = round(min(settings['linkedin_posts']/36, 1.0)*100)
            st.markdown(f"**LinkedIn Activity** — `{pct4}%`")
            st.progress(min(settings['linkedin_posts']/36, 1.0))

        # ── Weak Pattern Alerts ──
        if problems_list:
            today = date.today()
            pattern_stats = {}
            for p in problems_list:
                pat = p['pattern']
                if pat not in pattern_stats:
                    pattern_stats[pat] = {'count': 0, 'conf_sum': 0, 'last_date': '2000-01-01'}
                pattern_stats[pat]['count'] += 1
                pattern_stats[pat]['conf_sum'] += p.get('confidence', 3)
                if p.get('date', '') > pattern_stats[pat]['last_date']:
                    pattern_stats[pat]['last_date'] = p.get('date', '')

            weak_patterns = []
            for pat in NEETCODE_150:
                if pat not in pattern_stats:
                    weak_patterns.append(f"⚠️ **{pat}** — not started yet")
                else:
                    ps = pattern_stats[pat]
                    avg_conf = ps['conf_sum'] / ps['count']
                    try:
                        last_d = datetime.strptime(ps['last_date'], "%Y-%m-%d").date()
                        days_ago = (today - last_d).days
                    except (ValueError, TypeError):
                        days_ago = 999
                    if avg_conf < 3:
                        weak_patterns.append(f"🟡 **{pat}** — avg confidence {avg_conf:.1f}/5")
                    elif days_ago >= 7:
                        weak_patterns.append(f"🔵 **{pat}** — last practiced {days_ago}d ago")

            if weak_patterns:
                st.markdown("---")
                st.subheader("⚡ Weak Pattern Alerts")
                for wp in weak_patterns[:5]:
                    st.markdown(wp)

        st.markdown("---")

        # Daily Goal
        st.subheader("🎯 Today's Progress")
        today_str = str(date.today())
        today_solved = sum(1 for p in problems_list if p.get("date") == today_str)

        gc1, gc2 = st.columns([1, 2])
        with gc1:
            daily_target = st.number_input("Daily target", 1, 10, settings.get("daily_target", 3), key="daily_target_input")
            if daily_target != settings.get("daily_target", 3):
                db.update_settings(daily_target=daily_target)
        with gc2:
            if today_solved >= daily_target:
                st.success(f"✅ Daily goal crushed! {today_solved}/{daily_target} solved today! 🎉")
            else:
                remaining = daily_target - today_solved
                st.info(f"📝 {today_solved}/{daily_target} solved today — {remaining} more to go! Go to **💻 DSA Tracker** to log.")

        # ── Weekly Summary ──
        week_start = str(date.today() - timedelta(days=date.today().weekday()))
        week_problems = [p for p in problems_list if p.get("date", "") >= week_start]
        if week_problems:
            st.markdown("---")
            st.subheader("📅 This Week")
            wc1, wc2, wc3, wc4 = st.columns(4)
            wc1.metric("Solved", len(week_problems))
            w_easy = sum(1 for p in week_problems if p["difficulty"] == "Easy")
            w_med = sum(1 for p in week_problems if p["difficulty"] == "Medium")
            w_hard = sum(1 for p in week_problems if p["difficulty"] == "Hard")
            wc2.metric("Breakdown", f"🟢{w_easy} 🟡{w_med} 🔴{w_hard}")
            w_timed = [p for p in week_problems if p.get("time_taken", 0) > 0]
            wc3.metric("Avg Time", f"{round(sum(p['time_taken'] for p in w_timed)/len(w_timed))} min" if w_timed else "—")
            w_patterns = len({p["pattern"] for p in week_problems})
            wc4.metric("Patterns", f"{w_patterns} covered")

        # ── Next Up Suggestion ──
        solved_names_lower = {p["name"].lower().strip() for p in problems_list}
        next_problem = None
        next_category = None
        for cat, probs in NEETCODE_150.items():
            for pname in probs:
                if pname.lower().strip() not in solved_names_lower:
                    next_problem = pname
                    next_category = cat
                    break
            if next_problem:
                break
        if next_problem:
            url = get_leetcode_url(next_problem)
            st.markdown("---")
            st.subheader("🎯 Next Up")
            st.markdown(f"**{next_category}** → [{next_problem}]({url})")
            st.caption("Your next unsolved NeetCode 150 problem")

        # ── Random Problem Picker ──
        all_unsolved = [(cat, p) for cat, probs in NEETCODE_150.items() for p in probs if p.lower().strip() not in solved_names_lower]
        if all_unsolved:
            st.markdown("---")
            st.subheader("🎲 Can't Decide?")
            if st.button("🎲 Pick a Random Problem", key="random_pick"):
                cat, rp = random.choice(all_unsolved)
                st.session_state["random_problem"] = (cat, rp)
            if "random_problem" in st.session_state:
                rcat, rpname = st.session_state["random_problem"]
                rurl = get_leetcode_url(rpname)
                st.success(f"**{rcat}** → [{rpname}]({rurl})")

        st.markdown("---")

        # Quick daily log
        st.subheader("📝 Quick Activity Log")
        with st.form("daily_log_form"):
            ql1, ql2, ql3 = st.columns(3)
            with ql1:
                commits_today = st.number_input("GitHub commits today", 0, 20, 0)
            with ql2:
                posted_today = st.checkbox("Posted on LinkedIn today?")
            with ql3:
                st.write("")  # spacing
            if st.form_submit_button("Log Activity", type="primary"):
                new_commits = settings['github_commits'] + commits_today
                new_linkedin = settings['linkedin_posts'] + (1 if posted_today else 0)
                today = str(date.today())
                new_streak = settings['streak']
                if settings['last_active'] == str(date.today() - timedelta(days=1)):
                    new_streak += 1
                elif settings['last_active'] != today:
                    new_streak = 1
                db.update_settings(github_commits=new_commits, linkedin_posts=new_linkedin,
                                   streak=new_streak, last_active=today)
                st.success(f"✅ Logged! Streak: {new_streak} days 🔥")
                st.balloons()
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🎯</div>
            <div class="title">Welcome to DSA Tracker Pro!</div>
            <div class="desc">Set your start date in the sidebar to begin your journey →</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ─── DSA TRACKER ───────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
elif page == "💻 DSA Tracker":
    st.title("💻 Log a DSA Problem")

    # Stats bar
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Total Solved", f"{solved_count} / 150")
    today_str = str(date.today())
    today_count = sum(1 for p in problems_list if p.get("date") == today_str)
    sc2.metric("Today", f"{today_count} problems")
    neetcode_solved = sum(1 for cat in NEETCODE_150.values() for p in cat if p.lower() in {x["name"].lower() for x in problems_list})
    sc3.metric("NeetCode 150", f"{neetcode_solved} / {TOTAL_NEETCODE}")

    st.progress(min(solved_count/150, 1.0))
    st.markdown("---")

    # ── Add Problem Form ──
    st.subheader("➕ New Problem")

    # Pre-fill from NeetCode roadmap
    prefill_name = st.session_state.get("prefill_name", "")
    prefill_platform = st.session_state.get("prefill_platform", "NeetCode 150")
    prefill_pattern = st.session_state.get("prefill_pattern", "1-D Dynamic Programming")
    prefill_url = st.session_state.get("prefill_url", "")
    # Clear prefill after use
    if prefill_name:
        st.info(f"✨ Pre-filled from NeetCode roadmap: **{prefill_name}**")
        for k in ["prefill_name","prefill_platform","prefill_pattern","prefill_url"]:
            if k in st.session_state:
                del st.session_state[k]

    # Check for duplicates
    existing_names = {p["name"].lower().strip() for p in problems_list}

    platform_options = ["NeetCode 150", "LeetCode", "GeeksforGeeks", "Other"]
    pattern_options = ALL_PATTERNS
    prefill_platform_idx = platform_options.index(prefill_platform) if prefill_platform in platform_options else 0
    prefill_pattern_idx = pattern_options.index(prefill_pattern) if prefill_pattern in pattern_options else 0

    with st.form("add_problem_form", clear_on_submit=True):
        # Row 1
        fc1, fc2 = st.columns([2, 1])
        with fc1:
            problem_name = st.text_input("Problem Name *", value=prefill_name, placeholder="e.g. Two Sum")
        with fc2:
            platform = st.selectbox("Platform", platform_options, index=prefill_platform_idx)

        # Row 2
        fc3, fc4, fc5 = st.columns(3)
        with fc3:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        with fc4:
            pattern = st.selectbox("Pattern / Category", pattern_options, index=prefill_pattern_idx)
        with fc5:
            language = st.selectbox("Language", ["Java", "Python", "C++", "JavaScript", "C", "Go", "TypeScript"])

        problem_url = st.text_input("Problem URL (optional)", value=prefill_url, placeholder="https://leetcode.com/problems/...")

        # Approach & Code
        approach = st.text_area("💡 Your Approach", placeholder="Initial thoughts → Pattern recognized → Step by step approach...", height=120)
        code = st.text_area("💾 Solution Code", placeholder="Paste your solution code here...", height=180)

        # Complexity & Time
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            time_complexity = st.selectbox("Time Complexity", ["", "O(1)","O(log n)","O(n)","O(n log n)","O(n²)","O(n³)","O(2^n)","O(n!)"])
        with cc2:
            space_complexity = st.selectbox("Space Complexity", ["", "O(1)","O(log n)","O(n)","O(n²)"])
        with cc3:
            time_taken = st.number_input("Time (minutes)", 0, 300, 0)

        # Meta
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            independent = st.checkbox("Solved independently")
        with mc2:
            confidence = st.slider("Confidence", 1, 5, 3)
        with mc3:
            tags_input = st.text_input("Tags (comma sep)", placeholder="revisit, tricky")

        # Company tags
        companies_input = st.text_input("🏢 Companies (comma sep)", placeholder="Google, Amazon, Meta")

        # Learnings
        lc1, lc2 = st.columns(2)
        with lc1:
            key_learnings = st.text_area("📝 Key Learnings", height=80, placeholder="What did you learn from this?")
        with lc2:
            mistakes = st.text_area("⚠️ Mistakes Made", height=80, placeholder="What to avoid next time?")

        submitted = st.form_submit_button("✅ Add Problem", type="primary")

        if submitted:
            if not problem_name:
                st.error("❌ Please enter a problem name!")
            elif problem_name.lower().strip() in existing_names:
                st.warning(f"⚠️ '{problem_name}' already exists! Edit it in **📖 Problem Solutions** instead.")
            else:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
                companies = [c.strip() for c in companies_input.split(",") if c.strip()] if companies_input else []
                db.add_problem({
                    "name": problem_name.strip(), "platform": platform, "problem_url": problem_url,
                    "difficulty": difficulty, "pattern": pattern, "language": language,
                    "approach": approach, "code": code,
                    "time_complexity": time_complexity, "space_complexity": space_complexity,
                    "time_taken": time_taken, "independent": independent, "confidence": confidence,
                    "tags": tags, "companies": companies,
                    "key_learnings": key_learnings, "mistakes": mistakes,
                    "date": str(date.today()), "revision_count": 0, "last_revised": None
                })
                st.success(f"✅ Added: **{problem_name}**")
                st.balloons()
                st.rerun()

    # Recent problems
    st.markdown("---")
    st.subheader("📋 Recently Solved")
    if problems_list:
        for prob in reversed(problems_list[-8:]):
            diff_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}[prob['difficulty']]
            stars = "⭐" * prob.get("confidence", 0)
            ind = " · ✅ Independent" if prob.get('independent') else ""
            st.markdown(f"{diff_icon} **{prob['name']}** — {prob.get('platform','')} · {prob['pattern']} · {stars}{ind} · `{prob['date']}`")
    else:
        st.markdown('<div class="empty-state"><div class="icon">📝</div><div class="title">No problems yet</div><div class="desc">Fill out the form above to log your first DSA problem!</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ─── PROBLEM SOLUTIONS (with edit & delete) ───────────────
# ═══════════════════════════════════════════════════════════
elif page == "📖 Problem Solutions":
    st.title("📖 Solution Journal")
    problems = problems_list
    if not problems:
        st.markdown('<div class="empty-state"><div class="icon">📚</div><div class="title">No solutions saved yet</div><div class="desc">Head to <b>💻 DSA Tracker</b> to log your first problem!</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"**{len(problems)} problems** in your journal")

        # Inline search + sort
        srch_col, sort_col = st.columns([2, 1])
        with srch_col:
            sol_search = st.text_input("🔎 Quick search", "", placeholder="Type problem name...", key="sol_search")
        with sort_col:
            sort_by = st.selectbox("Sort by", ["Date (newest)","Date (oldest)","Difficulty","Confidence ↑","Confidence ↓"])
        sorted_probs = list(enumerate(problems))
        if sort_by == "Date (newest)":
            sorted_probs.sort(key=lambda x: x[1].get("date",""), reverse=True)
        elif sort_by == "Date (oldest)":
            sorted_probs.sort(key=lambda x: x[1].get("date",""))
        elif sort_by == "Difficulty":
            sorted_probs.sort(key=lambda x: {"Easy":0,"Medium":1,"Hard":2}.get(x[1]["difficulty"],1))
        elif sort_by == "Confidence ↑":
            sorted_probs.sort(key=lambda x: x[1].get("confidence",3))
        else:
            sorted_probs.sort(key=lambda x: x[1].get("confidence",3), reverse=True)

        # Apply inline search filter
        if sol_search:
            sorted_probs = [(i, p) for i, p in sorted_probs if sol_search.lower() in p["name"].lower()]
            st.caption(f"Showing {len(sorted_probs)} result(s) for '{sol_search}'")

        # Pagination
        ITEMS_PER_PAGE = 10
        total_items = len(sorted_probs)
        total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        if "sol_page" not in st.session_state:
            st.session_state.sol_page = 1
        current_page = st.session_state.sol_page
        if current_page > total_pages:
            current_page = total_pages
        start_idx = (current_page - 1) * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
        page_probs = sorted_probs[start_idx:end_idx]

        if total_pages > 1:
            pg1, pg2, pg3 = st.columns([1, 2, 1])
            with pg1:
                if st.button("← Previous", disabled=(current_page <= 1), key="prev_page"):
                    st.session_state.sol_page = current_page - 1
                    st.rerun()
            with pg2:
                st.markdown(f"<div style='text-align:center'>Page **{current_page}** of **{total_pages}** ({total_items} problems)</div>", unsafe_allow_html=True)
            with pg3:
                if st.button("Next →", disabled=(current_page >= total_pages), key="next_page"):
                    st.session_state.sol_page = current_page + 1
                    st.rerun()

        for real_idx, prob in page_probs:
            prob_id = prob.get('id')
            diff_icon = {"Easy":"🟢","Medium":"🟡","Hard":"🔴"}[prob['difficulty']]
            stars = "⭐" * prob.get("confidence", 0)
            with st.expander(f"{diff_icon} {prob['name']} — {prob.get('platform','')} · {prob['pattern']} · {prob['date']} {stars}"):
                # Check if in edit mode
                is_editing = st.session_state.get(f"edit_{real_idx}", False)

                if is_editing:
                    # ── EDIT MODE ──
                    st.markdown("### ✏️ Editing...")
                    ed_approach = st.text_area("Approach", value=prob.get("approach",""), key=f"ed_app_{real_idx}", height=120)
                    ed_code = st.text_area("Code", value=prob.get("code",""), key=f"ed_code_{real_idx}", height=150)
                    edc1, edc2, edc3 = st.columns(3)
                    with edc1:
                        ed_tc = st.selectbox("Time Complexity", ["","O(1)","O(log n)","O(n)","O(n log n)","O(n²)","O(n³)","O(2^n)","O(n!)"],
                                             index=["","O(1)","O(log n)","O(n)","O(n log n)","O(n²)","O(n³)","O(2^n)","O(n!)"].index(prob.get("time_complexity","")) if prob.get("time_complexity","") in ["","O(1)","O(log n)","O(n)","O(n log n)","O(n²)","O(n³)","O(2^n)","O(n!)"] else 0,
                                             key=f"ed_tc_{real_idx}")
                    with edc2:
                        ed_sc = st.selectbox("Space Complexity", ["","O(1)","O(log n)","O(n)","O(n²)"],
                                             index=["","O(1)","O(log n)","O(n)","O(n²)"].index(prob.get("space_complexity","")) if prob.get("space_complexity","") in ["","O(1)","O(log n)","O(n)","O(n²)"] else 0,
                                             key=f"ed_sc_{real_idx}")
                    with edc3:
                        ed_conf = st.slider("Confidence", 1, 5, prob.get("confidence",3), key=f"ed_conf_{real_idx}")
                    ed_learn = st.text_area("Key Learnings", value=prob.get("key_learnings",""), key=f"ed_learn_{real_idx}", height=80)
                    ed_mistakes = st.text_area("Mistakes", value=prob.get("mistakes",""), key=f"ed_mis_{real_idx}", height=80)

                    save_c, cancel_c = st.columns(2)
                    with save_c:
                        if st.button("💾 Save Changes", key=f"save_edit_{real_idx}", type="primary"):
                            db.update_problem(prob_id,
                                approach=ed_approach, code=ed_code,
                                time_complexity=ed_tc, space_complexity=ed_sc,
                                confidence=ed_conf, key_learnings=ed_learn,
                                mistakes=ed_mistakes)
                            st.session_state[f"edit_{real_idx}"] = False
                            st.success("✅ Saved!")
                            st.rerun()
                    with cancel_c:
                        if st.button("Cancel", key=f"cancel_edit_{real_idx}"):
                            st.session_state[f"edit_{real_idx}"] = False
                            st.rerun()
                else:
                    # ── VIEW MODE ──
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    mc1.markdown(f"**Difficulty:** {prob['difficulty']}")
                    mc2.markdown(f"**Platform:** {prob.get('platform','N/A')}")
                    mc3.markdown(f"**Confidence:** {stars}")
                    mc4.markdown(f"**Time:** {prob.get('time_taken',0)} min")

                    if prob.get("problem_url"):
                        st.markdown(f"🔗 [Open Problem]({prob['problem_url']})")
                    if prob.get("tags"):
                        tags_html = " ".join(f'<span class="tag-pill">{t}</span>' for t in prob["tags"])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    if prob.get("companies"):
                        comp_html = " ".join(f'<span class="tag-pill" style="background:#f59e0b22;color:#f59e0b;border-color:#f59e0b33">🏢 {c}</span>' for c in prob["companies"])
                        st.markdown(comp_html, unsafe_allow_html=True)
                    if prob.get("approach"):
                        st.markdown("#### 💡 Approach")
                        st.markdown(prob["approach"])
                    if prob.get("code"):
                        st.markdown(f"#### 💾 Solution ({prob.get('language','Java')})")
                        st.code(prob["code"], language=prob.get("language","java").lower())
                    ccc1, ccc2 = st.columns(2)
                    if prob.get("time_complexity"):
                        ccc1.markdown(f"**⏱ Time:** `{prob['time_complexity']}`")
                    if prob.get("space_complexity"):
                        ccc2.markdown(f"**💾 Space:** `{prob['space_complexity']}`")
                    if prob.get("key_learnings"):
                        st.markdown("#### 📝 Key Learnings")
                        st.markdown(prob["key_learnings"])
                    if prob.get("mistakes"):
                        st.markdown("#### ⚠️ Mistakes")
                        st.markdown(prob["mistakes"])
                    st.markdown(f"**Independent:** {'✅' if prob.get('independent') else '❌'} | **Revised:** {prob.get('revision_count',0)}x")

                    # ── Action buttons ──
                    st.markdown("---")
                    ac1, ac2, ac3 = st.columns([1, 1, 3])
                    with ac1:
                        if st.button("✏️ Edit", key=f"edit_btn_{real_idx}"):
                            st.session_state[f"edit_{real_idx}"] = True
                            st.rerun()
                    with ac2:
                        if st.button("🗑️ Delete", key=f"del_{real_idx}"):
                            st.session_state[f"confirm_del_{real_idx}"] = True
                    if st.session_state.get(f"confirm_del_{real_idx}"):
                        st.warning(f"⚠️ Are you sure you want to delete **{prob['name']}**? This cannot be undone.")
                        yc1, yc2 = st.columns(2)
                        with yc1:
                            if st.button("Yes, delete it", key=f"yes_del_{real_idx}", type="primary"):
                                db.delete_problem(prob_id)
                                st.success("Deleted!")
                                st.rerun()
                        with yc2:
                            if st.button("Cancel", key=f"cancel_del_{real_idx}"):
                                st.session_state[f"confirm_del_{real_idx}"] = False
                                st.rerun()

# ═══════════════════════════════════════════════════════════
# ─── NEETCODE 150 ROADMAP ─────────────────────────────────
# ═══════════════════════════════════════════════════════════
elif page == "🗺️ NeetCode 150":
    st.title("🗺️ NeetCode 150 Roadmap")
    solved_names = {p["name"].lower().strip() for p in problems_list}
    neetcode_solved = sum(1 for cat in NEETCODE_150.values() for p in cat if p.lower().strip() in solved_names)

    nc1, nc2, nc3 = st.columns(3)
    nc1.metric("Solved", f"{neetcode_solved} / {TOTAL_NEETCODE}")
    nc2.metric("Remaining", f"{TOTAL_NEETCODE - neetcode_solved}")
    pct = round(neetcode_solved / TOTAL_NEETCODE * 100)
    nc3.metric("Completion", f"{pct}%")
    st.progress(min(neetcode_solved / TOTAL_NEETCODE, 1.0) if TOTAL_NEETCODE else 0)
    st.markdown("---")
    st.caption("🔗 Click any problem name to open it on LeetCode · [View on NeetCode.io](https://neetcode.io/roadmap)")

    for category, prob_list in NEETCODE_150.items():
        cat_solved = sum(1 for p in prob_list if p.lower().strip() in solved_names)
        is_done = cat_solved == len(prob_list)
        icon = "✅" if is_done else "📂"
        pct_cat = round(cat_solved / len(prob_list) * 100)
        with st.expander(f"{icon} **{category}** — {cat_solved}/{len(prob_list)} ({pct_cat}%)"):
            for prob_name in prob_list:
                is_s = prob_name.lower().strip() in solved_names
                url = get_leetcode_url(prob_name)
                check = "✅" if is_s else "⬜"
                pc1, pc2 = st.columns([5, 1])
                with pc1:
                    st.markdown(f"{check} [{prob_name}]({url})")
                with pc2:
                    if not is_s:
                        btn_key = f"solve_{category}_{prob_name}".replace(' ','_')
                        if st.button("📝 Solve", key=btn_key, help="Pre-fill DSA Tracker form"):
                            st.session_state.prefill_name = prob_name
                            st.session_state.prefill_platform = "NeetCode 150"
                            st.session_state.prefill_pattern = category
                            st.session_state.prefill_url = url
                            st.rerun()

# ═══════════════════════════════════════════════════════════
# ─── REVISION TRACKER ─────────────────────────────────────
# ═══════════════════════════════════════════════════════════
elif page == "🔄 Revision Tracker":
    st.title("🔄 Revision & Spaced Repetition")
    problems = problems_list
    if not problems:
        st.markdown('<div class="empty-state"><div class="icon">🔄</div><div class="title">Nothing to revise yet</div><div class="desc">Solve some problems first, then come back to revise!</div></div>', unsafe_allow_html=True)
    else:
        st.info("💡 Problems are ranked by: **low confidence** + **days since last solved/revised**")

        today = date.today()
        revision_list = []
        for idx, p in enumerate(problems):
            last_str = p.get("last_revised") or p.get("date", str(today))
            try:
                last_d = datetime.strptime(last_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                last_d = today
            days_since = (today - last_d).days
            conf = p.get("confidence", 3)
            priority = (5 - conf) * 10 + days_since
            revision_list.append((idx, p, days_since, conf, priority))
        revision_list.sort(key=lambda x: -x[4])

        tab_urgent, tab_all = st.tabs(["🔴 Needs Revision", "📋 All Problems"])

        with tab_urgent:
            urgent = [r for r in revision_list if r[3] <= 3 or r[2] >= 3]
            if not urgent:
                st.success("🎉 All caught up! No urgent revisions needed.")
            for idx, p, days, conf, pri in urgent:
                urgency = "🔴" if conf <= 1 or days >= 14 else "🟡" if conf <= 2 or days >= 7 else "🟢"
                with st.expander(f"{urgency} {p['name']} — {p['difficulty']} · {'⭐'*conf} · {days}d ago"):
                    st.markdown(f"**Pattern:** {p['pattern']} | **Platform:** {p.get('platform','')}")
                    if p.get("approach"):
                        st.markdown(f"**Approach:** {p['approach'][:300]}{'...' if len(p.get('approach','')) > 300 else ''}")
                    if p.get("code"):
                        st.code(p["code"], language=p.get("language","java").lower())
                    if p.get("mistakes"):
                        st.warning(f"**Past Mistakes:** {p['mistakes']}")
                    if st.button(f"✅ Mark Revised", key=f"rev_{idx}"):
                        new_conf = min(p.get("confidence",3) + 1, 5)
                        db.update_problem(p['id'],
                            revision_count=p.get("revision_count",0) + 1,
                            last_revised=str(today),
                            confidence=new_conf)
                        st.success(f"Revised! Confidence → {new_conf}/5")
                        st.rerun()

        with tab_all:
            for idx, p, days, conf, pri in revision_list:
                st.markdown(f"{'⭐'*conf} **{p['name']}** — {days}d ago · Revised {p.get('revision_count',0)}x")

# ═══════════════════════════════════════════════════════════
# ─── SEARCH & FILTER ──────────────────────────────────────
# ═══════════════════════════════════════════════════════════
elif page == "🔍 Search & Filter":
    st.title("🔍 Search & Filter Problems")
    problems = problems_list
    if not problems:
        st.markdown('<div class="empty-state"><div class="icon">🔍</div><div class="title">Nothing to search</div><div class="desc">Start logging problems to use search!</div></div>', unsafe_allow_html=True)
    else:
        # Collect all tags for the filter
        all_tags = sorted({t for p in problems for t in p.get("tags", []) if t})

        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            search_q = st.text_input("🔎 Search by name", "")
        with fc2:
            f_plat = st.selectbox("Platform", ["All","NeetCode 150","LeetCode","GeeksforGeeks","Other"])
        with fc3:
            f_diff = st.selectbox("Difficulty", ["All","Easy","Medium","Hard"])
        with fc4:
            f_pat = st.selectbox("Pattern", ["All"] + ALL_PATTERNS)

        # Second row of filters
        ff1, ff2 = st.columns(2)
        with ff1:
            f_tag = st.selectbox("🏷️ Tag", ["All"] + all_tags) if all_tags else "All"
        with ff2:
            f_conf = st.selectbox("⭐ Confidence", ["All", "1 ⭐", "2 ⭐⭐", "3 ⭐⭐⭐", "4 ⭐⭐⭐⭐", "5 ⭐⭐⭐⭐⭐"])

        # Third row: company filter
        all_companies = sorted({c for p in problems for c in p.get("companies", []) if c})
        if all_companies:
            f_company = st.selectbox("🏢 Company", ["All"] + all_companies)
        else:
            f_company = "All"

        filtered = problems
        if search_q:
            filtered = [p for p in filtered if search_q.lower() in p["name"].lower()]
        if f_plat != "All":
            filtered = [p for p in filtered if p.get("platform") == f_plat]
        if f_diff != "All":
            filtered = [p for p in filtered if p["difficulty"] == f_diff]
        if f_pat != "All":
            filtered = [p for p in filtered if p["pattern"] == f_pat]
        if f_tag != "All":
            filtered = [p for p in filtered if f_tag in p.get("tags", [])]
        if f_conf != "All":
            conf_val = int(f_conf[0])
            filtered = [p for p in filtered if p.get("confidence", 3) == conf_val]
        if f_company != "All":
            filtered = [p for p in filtered if f_company in p.get("companies", [])]

        st.markdown(f"**{len(filtered)}** result(s)")
        st.markdown("---")

        for p in filtered:
            diff_icon = {"Easy":"🟢","Medium":"🟡","Hard":"🔴"}[p['difficulty']]
            with st.expander(f"{diff_icon} {p['name']} — {p.get('platform','')} · {p['pattern']} · {p['date']}"):
                if p.get("approach"):
                    st.markdown(f"**Approach:** {p['approach']}")
                if p.get("code"):
                    st.code(p["code"], language=p.get("language","java").lower())
                st.markdown(f"**Time:** `{p.get('time_complexity','-')}` | **Space:** `{p.get('space_complexity','-')}` | **Confidence:** {'⭐'*p.get('confidence',0)}")

# ═══════════════════════════════════════════════════════════
# ─── LEARNING (SHORT GOALS) — Enhanced ───────────────────
# ═══════════════════════════════════════════════════════════
elif page == "📚 Learning (Short)":
    st.title("📚 Learning Journey")

    all_topics = db.get_topics()
    total = len(all_topics)
    completed = sum(1 for t in all_topics.values() if t.get('studied') and t.get('built') and t.get('posted'))
    in_progress = sum(1 for t in all_topics.values() if (t.get('studied') or t.get('built') or t.get('posted')) and not (t.get('studied') and t.get('built') and t.get('posted')))

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("✅ Completed", f"{completed} / {total}")
    mc2.metric("🔄 In Progress", in_progress)
    mc3.metric("📊 Completion", f"{round(completed/total*100) if total else 0}%")
    st.progress(min(completed/total, 1.0) if total else 0)
    st.markdown("---")

    # Week groupings for built-in topics
    topics_display = {
        "01_bias_variance": ("Bias-Variance Tradeoff", "Week 1-2: ML Foundations"),
        "02_cross_validation": ("Cross-Validation", "Week 1-2: ML Foundations"),
        "03_feature_scaling": ("Feature Scaling", "Week 1-2: ML Foundations"),
        "04_evaluation_metrics": ("Evaluation Metrics", "Week 1-2: ML Foundations"),
        "05_gradient_boosting": ("Gradient Boosting", "Week 3-4: Advanced ML"),
        "06_imbalanced_data": ("Imbalanced Data", "Week 3-4: Advanced ML"),
        "07_feature_engineering": ("Feature Engineering", "Week 3-4: Advanced ML"),
        "08_shap_explainability": ("SHAP Explainability", "Week 3-4: Advanced ML"),
        "09_vector_databases": ("Vector Databases", "Week 5-6: AI/LLM Stack"),
        "10_rag_basics": ("RAG Basics", "Week 5-6: AI/LLM Stack"),
        "11_langchain": ("LangChain", "Week 5-6: AI/LLM Stack"),
        "12_mlflow": ("MLflow", "Week 5-6: AI/LLM Stack"),
        "13_transformers": ("Transformers", "Week 7-8: Deep Learning"),
        "14_finetuning_llms": ("Fine-tuning LLMs", "Week 7-8: Deep Learning"),
        "15_diffusion_models": ("Diffusion Models", "Week 7-8: Deep Learning"),
        "16_multimodal_ai": ("Multi-modal AI", "Week 7-8: Deep Learning"),
    }

    # Group by week
    current_group = None
    for tid in list(topics_display.keys()) + [k for k in all_topics if k not in topics_display]:
        if tid in topics_display:
            tname, group = topics_display[tid]
        else:
            tname = tid.replace('_', ' ').title()
            group = "Custom Topics"

        if group != current_group:
            current_group = group
            st.markdown(f"### {group}")

        td = all_topics[tid]
        all_done = td.get('studied') and td.get('built') and td.get('posted')
        any_started = td.get('studied') or td.get('built') or td.get('posted')
        icon = "✅" if all_done else "🔄" if any_started else "📖"

        with st.expander(f"{icon} **{tname}**"):
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                s = st.checkbox("📖 Studied", value=td.get('studied', False), key=f"{tid}_s")
                if s != td.get('studied', False):
                    db.upsert_topic(tid, studied=s); st.rerun()
            with ec2:
                b = st.checkbox("🔨 Built Project", value=td.get('built', False), key=f"{tid}_b")
                if b != td.get('built', False):
                    db.upsert_topic(tid, built=b); st.rerun()
            with ec3:
                p = st.checkbox("📝 Posted/Blogged", value=td.get('posted', False), key=f"{tid}_p")
                if p != td.get('posted', False):
                    db.upsert_topic(tid, posted=p); st.rerun()

            # Notes
            notes = st.text_area("📓 Study Notes", value=td.get('notes', ''), key=f"{tid}_notes",
                                 placeholder="Key concepts, formulas, cheat-sheet...", height=100)
            if notes != td.get('notes', ''):
                db.upsert_topic(tid, notes=notes)

            # Resources
            resources = st.text_input("🔗 Resource Links", value=td.get('resources', ''), key=f"{tid}_res",
                                      placeholder="Paste article/video URLs (comma separated)")
            if resources != td.get('resources', ''):
                db.upsert_topic(tid, resources=resources)

            # Show saved resource links as clickable
            if td.get('resources'):
                for link in td['resources'].split(','):
                    link = link.strip()
                    if link:
                        st.markdown(f"  ↳ [{link[:60]}{'...' if len(link)>60 else ''}]({link})")

    # ── Add Custom Topic ──
    st.markdown("---")
    st.subheader("➕ Add Custom Topic")
    with st.form("add_topic_form", clear_on_submit=True):
        new_topic = st.text_input("Topic Name", placeholder="e.g. SQL Joins, Docker Basics")
        add_topic = st.form_submit_button("Add Topic", type="primary")
        if add_topic and new_topic:
            tid_new = new_topic.lower().replace(' ', '_').replace('-', '_')
            if tid_new not in all_topics:
                db.add_topic(tid_new)
                st.success(f"✅ Added: {new_topic}")
                st.rerun()
            else:
                st.warning("Topic already exists!")

# ═══════════════════════════════════════════════════════════
# ─── PROJECTS (LONG GOALS) — Enhanced ────────────────────
# ═══════════════════════════════════════════════════════════
elif page == "🏗️ Projects (Long)":
    st.title("🏗️ Project Progress")

    projects_display = {
        "anomaly_detection": "🔍 Anomaly Detection System",
        "m5_forecasting": "📈 M5 Demand Forecasting",
        "ticket_classifier": "🎫 Ticket Classifier NLP",
    }

    # Stats
    all_projects = db.get_projects()
    total_proj = len(all_projects)
    deployed_count = sum(1 for p in all_projects.values() if p.get('deployed'))
    pc1, pc2, pc3 = st.columns(3)
    pc1.metric("Total Projects", total_proj)
    pc2.metric("Deployed", f"{deployed_count} / {total_proj}")
    overall_prog = sum(sum(1 for k in ['week1','week2','week3','week4','deployed'] if p.get(k)) for p in all_projects.values())
    pc3.metric("Overall", f"{round(overall_prog/(total_proj*5)*100) if total_proj else 0}%")
    st.markdown("---")

    for pid, pd in all_projects.items():
        pname = projects_display.get(pid, f"📁 {pid.replace('_',' ').title()}")
        prog = sum(1 for k in ['week1','week2','week3','week4','deployed'] if pd.get(k)) / 5
        status_icon = "✅" if prog == 1.0 else "🔄" if prog > 0 else "📋"

        with st.expander(f"{status_icon} **{pname}** — {round(prog*100)}% complete"):
            # Description & links
            desc = st.text_input("📝 Description", value=pd.get('description',''), key=f"{pid}_desc",
                                  placeholder="What is this project about?")
            if desc != pd.get('description',''): db.upsert_project(pid, description=desc)

            lc1, lc2, lc3 = st.columns(3)
            with lc1:
                tech = st.text_input("🛠️ Tech Stack", value=pd.get('tech_stack',''), key=f"{pid}_tech",
                                      placeholder="Python, Scikit-learn, Flask")
                if tech != pd.get('tech_stack',''): db.upsert_project(pid, tech_stack=tech)
            with lc2:
                gh = st.text_input("🔗 GitHub URL", value=pd.get('github_url',''), key=f"{pid}_gh",
                                    placeholder="https://github.com/...")
                if gh != pd.get('github_url',''): db.upsert_project(pid, github_url=gh)
            with lc3:
                demo = st.text_input("🌐 Live Demo URL", value=pd.get('demo_url',''), key=f"{pid}_demo",
                                      placeholder="https://...")
                if demo != pd.get('demo_url',''): db.upsert_project(pid, demo_url=demo)

            # Show links as clickable
            link_parts = []
            if pd.get('github_url'): link_parts.append(f"[GitHub]({pd['github_url']})")
            if pd.get('demo_url'): link_parts.append(f"[Live Demo]({pd['demo_url']})")
            if link_parts:
                st.markdown(" · ".join(link_parts))

            st.markdown("---")

            # Weekly milestones with task descriptions
            weeks = [("week1","Week 1"),("week2","Week 2"),("week3","Week 3"),("week4","Week 4")]
            for wk_key, wk_label in weeks:
                wc1, wc2 = st.columns([1, 4])
                with wc1:
                    val = st.checkbox(wk_label, value=pd.get(wk_key, False), key=f"{pid}_{wk_key}")
                    if val != pd.get(wk_key, False):
                        db.upsert_project(pid, **{wk_key: val}); st.rerun()
                with wc2:
                    task_key = f"{wk_key}_tasks"
                    tasks = st.text_input(
                        f"Tasks for {wk_label}", value=pd.get(task_key, ''), key=f"{pid}_{task_key}",
                        placeholder=f"e.g. EDA, baseline model, data cleaning...",
                        label_visibility="collapsed"
                    )
                    if tasks != pd.get(task_key, ''):
                        db.upsert_project(pid, **{task_key: tasks})

            # Deploy
            dep_val = st.checkbox("🚀 Deployed to production", value=pd.get('deployed', False), key=f"{pid}_deployed")
            if dep_val != pd.get('deployed', False):
                db.upsert_project(pid, deployed=dep_val); st.rerun()

            st.progress(prog)

    # ── Add Custom Project ──
    st.markdown("---")
    st.subheader("➕ Add New Project")
    with st.form("add_project_form", clear_on_submit=True):
        np_name = st.text_input("Project Name", placeholder="e.g. Sentiment Analysis Dashboard")
        np_desc = st.text_input("Description (optional)", placeholder="What will you build?")
        np_submit = st.form_submit_button("Create Project", type="primary")
        if np_submit and np_name:
            pid_new = np_name.lower().replace(' ', '_').replace('-', '_')
            if pid_new not in all_projects:
                db.add_project(pid_new, {'description': np_desc})
                st.success(f"✅ Created: {np_name}")
                st.rerun()
            else:
                st.warning("Project already exists!")

# ═══════════════════════════════════════════════════════════
# ─── ANALYTICS (with Plotly Charts) ──────────────────────
# ═══════════════════════════════════════════════════════════
elif page == "📈 Analytics":
    st.title("📈 Analytics & Insights")
    problems = problems_list

    if not problems:
        st.markdown('<div class="empty-state"><div class="icon">📈</div><div class="title">No data yet</div><div class="desc">Solve problems to see analytics!</div></div>', unsafe_allow_html=True)
    else:
        # ── Row 1: Difficulty Pie + Pattern Bar ──
        st.subheader("📊 Problem Distribution")
        ch1, ch2 = st.columns(2)

        with ch1:
            diff_counts = Counter(p["difficulty"] for p in problems)
            fig_diff = go.Figure(data=[go.Pie(
                labels=list(diff_counts.keys()),
                values=list(diff_counts.values()),
                hole=0.5,
                marker=dict(colors=["#22c55e","#eab308","#ef4444"]),
                textinfo="label+value",
                textfont=dict(size=14),
            )])
            fig_diff.update_layout(
                title="Difficulty Distribution",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"), height=350, margin=dict(t=40, b=20, l=20, r=20),
                showlegend=False,
            )
            st.plotly_chart(fig_diff, use_container_width=True)

        with ch2:
            pat_counts = Counter(p["pattern"] for p in problems)
            sorted_pats = pat_counts.most_common()
            fig_pat = go.Figure(data=[go.Bar(
                x=[c for _, c in sorted_pats],
                y=[p for p, _ in sorted_pats],
                orientation="h",
                marker=dict(color="#6366f1", cornerradius=6),
                text=[c for _, c in sorted_pats],
                textposition="outside",
            )])
            fig_pat.update_layout(
                title="Pattern Breakdown",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"), height=350, margin=dict(t=40, b=20, l=120, r=40),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_pat, use_container_width=True)

        st.markdown("---")

        # ── Row 2: Platform + Confidence ──
        st.subheader("🏷️ Platform & Confidence")
        ch3, ch4 = st.columns(2)

        with ch3:
            plat_counts = Counter(p.get("platform","Unknown") for p in problems)
            fig_plat = go.Figure(data=[go.Pie(
                labels=list(plat_counts.keys()),
                values=list(plat_counts.values()),
                hole=0.5,
                marker=dict(colors=["#6366f1","#06b6d4","#f59e0b","#94a3b8"]),
                textinfo="label+value",
            )])
            fig_plat.update_layout(
                title="Platform Distribution",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"), height=300, margin=dict(t=40,b=20,l=20,r=20),
                showlegend=False,
            )
            st.plotly_chart(fig_plat, use_container_width=True)

        with ch4:
            conf_counts = Counter(p.get("confidence",3) for p in problems)
            fig_conf = go.Figure(data=[go.Bar(
                x=[f"{'⭐'*i} ({i})" for i in range(1,6)],
                y=[conf_counts.get(i,0) for i in range(1,6)],
                marker=dict(
                    color=["#ef4444","#f97316","#eab308","#22c55e","#06b6d4"],
                    cornerradius=6
                ),
                text=[conf_counts.get(i,0) for i in range(1,6)],
                textposition="outside",
            )])
            fig_conf.update_layout(
                title="Confidence Distribution",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"), height=300, margin=dict(t=40,b=40,l=20,r=20),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_conf, use_container_width=True)

        st.markdown("---")

        # ── Row 3: Independence & Time ──
        st.subheader("🧠 Independence & Time")
        ic1, ic2, ic3 = st.columns(3)
        ind_count = sum(1 for p in problems if p.get("independent"))
        ic1.metric("Independent Solves", f"{ind_count} / {len(problems)}", f"{round(ind_count/len(problems)*100)}%")
        avg_conf = sum(p.get("confidence",3) for p in problems)/len(problems)
        ic2.metric("Avg Confidence", f"{avg_conf:.1f} / 5.0")
        timed = [p for p in problems if p.get("time_taken",0) > 0]
        if timed:
            avg_time = sum(p["time_taken"] for p in timed)/len(timed)
            ic3.metric("Avg Solve Time", f"{round(avg_time)} min")
        else:
            ic3.metric("Avg Solve Time", "—")

        # Time by difficulty
        if timed:
            st.markdown("---")
            st.subheader("⏱ Avg Time by Difficulty")
            tc1, tc2, tc3 = st.columns(3)
            for col, diff in zip([tc1,tc2,tc3], ["Easy","Medium","Hard"]):
                times = [p["time_taken"] for p in timed if p["difficulty"] == diff]
                col.metric(f"{'🟢🟡🔴'[['Easy','Medium','Hard'].index(diff)]} {diff}",
                           f"{round(sum(times)/len(times))} min" if times else "—")

        st.markdown("---")

        # ── Daily Activity Heatmap ──
        st.subheader("📅 Daily Activity")
        date_counts = Counter(p.get("date","") for p in problems)
        if date_counts:
            dates = sorted(date_counts.keys())
            # Fill in gaps
            start = datetime.strptime(dates[0], "%Y-%m-%d").date()
            end = date.today()
            all_dates = []
            all_counts = []
            d = start
            while d <= end:
                ds = str(d)
                all_dates.append(ds)
                all_counts.append(date_counts.get(ds, 0))
                d += timedelta(days=1)

            fig_heat = go.Figure(data=[go.Bar(
                x=all_dates, y=all_counts,
                marker=dict(
                    color=all_counts,
                    colorscale=[[0,"#1e293b"],[0.01,"#312e81"],[0.5,"#6366f1"],[1,"#a78bfa"]],
                    cornerradius=4,
                ),
            )])
            fig_heat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"), height=200, margin=dict(t=10,b=30,l=30,r=10),
                xaxis=dict(showgrid=False, tickformat="%b %d"),
                yaxis=dict(showgrid=False, dtick=1),
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("---")

        # ── Time Complexity Distribution ──
        st.subheader("📐 Complexity Distribution")
        tc_counts = Counter(p.get("time_complexity","") for p in problems if p.get("time_complexity"))
        if tc_counts:
            fig_tc = go.Figure(data=[go.Bar(
                x=list(tc_counts.keys()), y=list(tc_counts.values()),
                marker=dict(color="#06b6d4", cornerradius=6),
                text=list(tc_counts.values()), textposition="outside",
            )])
            fig_tc.update_layout(
                title="Time Complexity Used",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"), height=280, margin=dict(t=40,b=30,l=30,r=20),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_tc, use_container_width=True)
        else:
            st.info("No complexity data logged yet.")

        st.markdown("---")

        # ── Pattern Performance Table ──
        st.subheader("📋 Performance by Pattern")
        pat_perf = {}
        for p in problems:
            pat = p["pattern"]
            if pat not in pat_perf:
                pat_perf[pat] = {"count": 0, "conf": [], "time": [], "ind": 0}
            pat_perf[pat]["count"] += 1
            pat_perf[pat]["conf"].append(p.get("confidence", 3))
            if p.get("time_taken", 0) > 0:
                pat_perf[pat]["time"].append(p["time_taken"])
            if p.get("independent"):
                pat_perf[pat]["ind"] += 1

        table_md = "| Pattern | Solved | Avg ⭐ | Avg ⏱ | Independent |\n|---|---|---|---|---|\n"
        for pat in sorted(pat_perf, key=lambda x: pat_perf[x]["count"], reverse=True):
            pp = pat_perf[pat]
            avg_c = sum(pp["conf"]) / len(pp["conf"])
            avg_t = f"{round(sum(pp['time'])/len(pp['time']))} min" if pp["time"] else "—"
            ind_pct = f"{round(pp['ind']/pp['count']*100)}%"
            stars = "⭐" * round(avg_c)
            table_md += f"| {pat} | {pp['count']} | {stars} ({avg_c:.1f}) | {avg_t} | {ind_pct} |\n"
        st.markdown(table_md)

        st.markdown("---")
        st.subheader("📊 Overall Stats")
        oc1, oc2 = st.columns(2)
        oc1.metric("Total DSA Problems", solved_count)
        oc1.metric("GitHub Commits", settings['github_commits'])
        oc2.metric("LinkedIn Posts", settings['linkedin_posts'])
        oc2.metric("Current Streak", f"{settings['streak']} days")
