import streamlit as st
import time
import re

from pipeline import run_research_pipeline

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchOS · Multi-Agent System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #060610;
    --surface:   #0e0e1e;
    --surface2:  #14142a;
    --border:    #1e1e36;
    --border2:   #2a2a4a;
    --accent:    #6c63ff;
    --accent2:   #48cae4;
    --accent3:   #4fffb0;
    --danger:    #ff5a5a;
    --text:      #e2e2f0;
    --muted:     #5a5a7a;
    --muted2:    #3a3a5a;
    --font-head: 'Space Grotesk', sans-serif;
    --font-mono: 'Fira Code', monospace;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: var(--font-mono) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 5rem !important; max-width: 1100px !important; }

/* ── Ambient background glow ── */
.stApp::before {
    content: '';
    position: fixed;
    top: -200px; left: 50%;
    transform: translateX(-50%);
    width: 900px; height: 600px;
    background: radial-gradient(ellipse at center,
        rgba(108,99,255,0.06) 0%,
        rgba(72,202,228,0.03) 40%,
        transparent 70%);
    pointer-events: none;
    z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    bottom: 0; left: 0; right: 0;
    height: 300px;
    background: radial-gradient(ellipse at 20% 100%,
        rgba(79,255,176,0.04) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2rem;
    position: relative;
}
.hero-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.35em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
}
.hero-eyebrow::before, .hero-eyebrow::after {
    content: '';
    width: 50px; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent));
}
.hero-eyebrow::after {
    background: linear-gradient(90deg, var(--accent), transparent);
}
.hero-title {
    font-family: var(--font-head);
    font-size: clamp(3rem, 6vw, 5rem);
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0 0 0.75rem;
}
.hero-title .t1 { color: #fff; }
.hero-title .t2 {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 60%, var(--accent3) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.1em;
}
.hero-sub span { color: var(--accent); }

/* ── Stat chips ── */
.chip-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}
.chip {
    background: rgba(108,99,255,0.07);
    border: 1px solid rgba(108,99,255,0.18);
    border-radius: 20px;
    padding: 0.28rem 0.9rem;
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    color: rgba(155,150,255,0.8);
    display: inline-block;
}
.chip b { color: var(--accent3); font-style: normal; }

/* ── Input area ── */
.input-wrapper {
    background: rgba(14,14,30,0.85);
    border: 1px solid var(--border2);
    border-radius: 14px;
    padding: 1.2rem 1.6rem 1rem;
    margin: 2rem 0 1.5rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.3s, box-shadow 0.3s;
}
.input-wrapper:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(108,99,255,0.1), 0 10px 35px rgba(108,99,255,0.07);
}
.input-label {
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted2);
    margin-bottom: 0.5rem;
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid var(--border2) !important;
    border-radius: 0 !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 1.05rem !important;
    padding: 0.5rem 0 !important;
    box-shadow: none !important;
    caret-color: var(--accent) !important;
}
.stTextInput > div > div > input:focus {
    border-bottom-color: var(--accent) !important;
    box-shadow: none !important;
}
.stTextInput label { display: none !important; }

/* ── Run button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    padding: 0.65rem 2rem !important;
    text-transform: uppercase !important;
    transition: all 0.25s !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 30px rgba(108,99,255,0.38) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Section label ── */
.section-lbl {
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted2);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-lbl::after {
    content: '';
    flex: 1; height: 1px;
    background: linear-gradient(90deg, var(--border2), transparent);
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(10,10,22,0.9);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.4s, box-shadow 0.4s;
}
.step-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: transparent;
    transition: background 0.4s;
}
.step-card.active {
    border-color: var(--accent);
    box-shadow: 0 0 24px rgba(108,99,255,0.12);
}
.step-card.active::before {
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    animation: scan-top 1.8s linear infinite;
}
@keyframes scan-top {
    0%   { transform: scaleX(0); transform-origin: left;  }
    50%  { transform: scaleX(1); transform-origin: left;  }
    51%  { transform: scaleX(1); transform-origin: right; }
    100% { transform: scaleX(0); transform-origin: right; }
}
.step-card.active::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scan-bot 2.2s linear infinite;
}
@keyframes scan-bot {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
.step-card.done {
    border-color: rgba(79,255,176,0.35);
    box-shadow: 0 0 16px rgba(79,255,176,0.06);
}
.step-card.done::before { background: var(--accent3); }
.step-card.error { border-color: var(--danger); }

.step-icon {
    font-size: 1.2rem;
    width: 2.4rem; height: 2.4rem;
    display: flex; align-items: center; justify-content: center;
    background: rgba(108,99,255,0.08);
    border: 1px solid rgba(108,99,255,0.18);
    border-radius: 9px;
    flex-shrink: 0;
    transition: all 0.3s;
}
.step-card.active .step-icon {
    background: rgba(108,99,255,0.18);
    border-color: var(--accent);
}
.step-card.done .step-icon {
    background: rgba(79,255,176,0.08);
    border-color: rgba(79,255,176,0.35);
}

.step-body { flex: 1; min-width: 0; }
.step-title {
    font-family: var(--font-head);
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
    color: #c0c0d8;
}
.step-desc {
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.04em;
}

.step-badge {
    font-size: 0.55rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
    font-weight: 500;
    flex-shrink: 0;
    margin-top: 0.1rem;
}
.badge-waiting { background: rgba(255,255,255,0.04); color: var(--muted2); }
.badge-running { background: rgba(108,99,255,0.18); color: #9b96ff; }
.badge-done    { background: rgba(79,255,176,0.12); color: var(--accent3); }
.badge-error   { background: rgba(255,90,90,0.14); color: var(--danger); }

/* ── Result panels ── */
.result-panel {
    background: rgba(10,10,20,0.9);
    border: 1px solid var(--border);
    border-radius: 14px;
    margin-bottom: 1.25rem;
    overflow: hidden;
}
.result-head {
    padding: 0.9rem 1.4rem;
    border-bottom: 1px solid var(--border);
    background: rgba(255,255,255,0.02);
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.result-head-icon { font-size: 1rem; }
.result-head-title {
    font-family: var(--font-head);
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #c0c0d8;
}
.result-head-tag {
    margin-left: auto;
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    padding: 0.18rem 0.55rem;
    border-radius: 3px;
    background: rgba(108,99,255,0.14);
    color: #9b96ff;
    text-transform: uppercase;
}
.result-body {
    padding: 1.4rem;
    font-size: 0.75rem;
    line-height: 1.9;
    color: #8080aa;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 420px;
    overflow-y: auto;
}
.result-body::-webkit-scrollbar { width: 3px; }
.result-body::-webkit-scrollbar-track { background: transparent; }
.result-body::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── Stats row ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 1.5rem 0 1.75rem;
}
.stat-box {
    background: rgba(10,10,22,0.9);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-box::after {
    content: '';
    position: absolute;
    bottom: 0; left: 20%; right: 20%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(79,255,176,0.35), transparent);
}
.stat-val {
    font-family: var(--font-head);
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent3);
    letter-spacing: -0.02em;
    line-height: 1;
}
.stat-lbl {
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted2);
    margin-top: 0.4rem;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    border-color: var(--accent) !important;
    color: #9b96ff !important;
    background: rgba(108,99,255,0.08) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Expanders ── */
.streamlit-expanderHeader {
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
.streamlit-expanderContent {
    border: 1px solid var(--border) !important;
    border-top: none !important;
    background: var(--surface) !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border2) 30%, var(--border2) 70%, transparent) !important;
    margin: 2rem 0 !important;
}

/* ── Warning ── */
.stAlert {
    background: rgba(108,99,255,0.08) !important;
    border: 1px solid rgba(108,99,255,0.25) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.75rem !important;
}

/* ── Code blocks ── */
.stCodeBlock {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
pre { background: var(--surface) !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
STEPS = [
    ("🔍", "Search Agent",  "Querying Tavily for recent, reliable sources"),
    ("📄", "Reader Agent",  "Scraping top URLs for raw content"),
    ("✍️",  "Writer Agent",  "Synthesising research into a structured report"),
    ("🧐", "Critic Agent",  "Reviewing the report and providing feedback"),
]


def render_steps(current: int):
    for i, (icon, title, desc) in enumerate(STEPS):
        if i < current:
            card_cls, badge_cls, badge_txt = "done",  "badge-done",    "✓ done"
        elif i == current:
            card_cls, badge_cls, badge_txt = "active","badge-running", "⚡ live"
        else:
            card_cls, badge_cls, badge_txt = "",       "badge-waiting", "waiting"

        st.markdown(f"""
        <div class="step-card {card_cls}">
            <div class="step-icon">{icon}</div>
            <div class="step-body">
                <div class="step-title">{title}</div>
                <div class="step-desc">{desc}</div>
            </div>
            <span class="step-badge {badge_cls}">{badge_txt}</span>
        </div>
        """, unsafe_allow_html=True)


def result_panel(icon: str, title: str, tag: str, content: str):
    st.markdown(f"""
    <div class="result-panel">
        <div class="result-head">
            <span class="result-head-icon">{icon}</span>
            <span class="result-head-title">{title}</span>
            <span class="result-head-tag">{tag}</span>
        </div>
        <div class="result-body">{content}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">// multi-agent research system</div>
    <h1 class="hero-title">
        <span class="t1">Research</span><span class="t2">OS</span>
    </h1>
    <p class="hero-sub">
        <span>Search</span> · <span>Scrape</span> · <span>Write</span> · <span>Critique</span>
        &nbsp;—&nbsp; Powered by LangGraph &amp; Groq
    </p>
    <div class="chip-row">
        <span class="chip"><b>4</b> orchestrated agents</span>
        <span class="chip">Tavily web search</span>
        <span class="chip">LangGraph pipeline</span>
        <span class="chip">Groq inference</span>
        <span class="chip">Live status tracking</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1])

with col_in:
    st.markdown(
        '<div class="input-wrapper">'
        '<div class="input-label">// research topic</div>',
        unsafe_allow_html=True
    )
    topic = st.text_input(
        "topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025 ...",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_btn:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_btn = st.button("▶  Run", use_container_width=True)


# ── Pipeline execution ────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("// enter a research topic first")
        st.stop()

    st.markdown("<hr>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.6], gap="large")

    with left_col:
        st.markdown(
            '<div class="section-lbl">// pipeline status</div>',
            unsafe_allow_html=True,
        )
        step_slot = st.empty()

    with right_col:
        st.markdown(
            '<div class="section-lbl">// live output</div>',
            unsafe_allow_html=True,
        )
        live_slot = st.empty()

    # ── Run with per-step feedback ──────────────────────────────────────────
    state = {}
    error = None
    start_time = time.time()

    try:
        # Step 0: Search
        with step_slot:
            render_steps(0)
        with live_slot:
            with st.spinner("Search agent querying the web..."):
                from tools import search_web_raw, format_search_results
                search_results = search_web_raw(query=topic, max_results=5)
                state["search_results"] = format_search_results(search_results)

        # Step 1: Reader
        with step_slot:
            render_steps(1)
        with live_slot:
            with st.spinner("Reader agent scraping sources..."):
                from tools import scrape_url_raw
                urls = re.findall(r"https?://[^\s)\]>\"']+", state["search_results"])
                urls = list(dict.fromkeys(urls))
                chunks = []
                for url in urls[:3]:
                    content = scrape_url_raw(url=url, timeout=8)
                    if not content.startswith("Could not scrape URL:"):
                        chunks.append(f"Source: {url}\n{content}")
                state["scraped_content"] = (
                    "\n\n".join(chunks)
                    if chunks
                    else "No source could be scraped successfully."
                )

        # Step 2: Writer
        with step_slot:
            render_steps(2)
        with live_slot:
            with st.spinner("Writer agent drafting the report..."):
                from agents import writer_chain
                research_combined = (
                    f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                    f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
                )
                state["report"] = writer_chain.invoke({
                    "topic": topic,
                    "research": research_combined,
                })

        # Step 3: Critic
        with step_slot:
            render_steps(3)
        with live_slot:
            with st.spinner("Critic agent reviewing the report..."):
                from agents import critic_chain
                state["feedback"] = critic_chain.invoke({"report": state["report"]})

        # All done
        with step_slot:
            render_steps(4)

    except Exception as e:
        error = str(e)

    elapsed = round(time.time() - start_time, 1)

    # ── Results ──────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    if error:
        st.markdown(f"""
        <div class="result-panel" style="border-color:var(--danger)">
            <div class="result-head" style="background:rgba(255,90,90,0.06)">
                <span class="result-head-icon">❌</span>
                <span class="result-head-title">Pipeline Error</span>
                <span class="result-head-tag" style="background:rgba(255,90,90,0.14);color:var(--danger)">failed</span>
            </div>
            <div class="result-body" style="color:var(--danger)">{error}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        urls_found   = len(re.findall(r"https?://[^\s)\]>\"']+", state.get("search_results", "")))
        words_written = len(state.get("report", "").split())

        # ── Stats row
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-val">{elapsed}s</div>
                <div class="stat-lbl">Total Time</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{urls_found}</div>
                <div class="stat-lbl">URLs Found</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{words_written:,}</div>
                <div class="stat-lbl">Words Written</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">4</div>
                <div class="stat-lbl">Agents Used</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Report
        result_panel("📑", "Final Research Report", "writer · output", state.get("report", ""))

        # ── Critic feedback
        result_panel("🧐", "Critic Feedback", "critic · review", state.get("feedback", ""))

        # ── Raw data expanders
        with st.expander("🔎  Raw Search Results"):
            st.code(state.get("search_results", ""), language=None)

        with st.expander("🌐  Scraped Web Content"):
            st.code(state.get("scraped_content", ""), language=None)

        # ── Download
        report_txt = (
            f"RESEARCH REPORT: {topic}\n{'='*60}\n\n"
            f"{state.get('report','')}\n\n"
            f"{'='*60}\nCRITIC FEEDBACK\n{'='*60}\n\n"
            f"{state.get('feedback','')}"
        )
        st.download_button(
            label="⬇  Download Report (.txt)",
            data=report_txt,
            file_name=f"research_{topic[:40].replace(' ', '_')}.txt",
            mime="text/plain",
        )


# ── Empty / idle state ────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="
        text-align: center;
        padding: 5rem 2rem 4rem;
        color: var(--muted2);
    ">
        <div style="
            font-size: 2.8rem;
            margin-bottom: 1.5rem;
            opacity: 0.2;
            animation: float 4s ease-in-out infinite;
            display: inline-block;
        ">⬡</div>
        <p style="font-size:0.78rem;letter-spacing:0.08em;line-height:2;color:var(--muted2)">
            Enter a topic above and hit
            <strong style="color:var(--accent);font-weight:500">▶ Run</strong>
            to ignite the pipeline.<br>
            Four agents will <span style="color:var(--muted)">search</span>,
            <span style="color:var(--muted)">scrape</span>,
            <span style="color:var(--muted)">write</span>, and
            <span style="color:var(--muted)">critique</span> — automatically.
        </p>
        <p style="font-size:0.65rem;margin-top:0.75rem;opacity:0.5;letter-spacing:0.1em">
            Powered by LangGraph · Groq · Tavily
        </p>
    </div>
    <style>
    @keyframes float {
        0%,100% { transform: translateY(0); }
        50%      { transform: translateY(-10px); }
    }
    </style>
    """, unsafe_allow_html=True)