import os
import streamlit as st
from dotenv import load_dotenv
from api import expand_prompt, generate_image, load_gallery_images, delete_image, image_to_b64

load_dotenv()

st.set_page_config(
    page_title="민화 MINHWA — Korean Folk Art Reimagined",
    page_icon="🐯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
#  GLOBAL CSS — 미술관 전시장 테마
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,600&family=Inter:wght@300;400;500;600&display=swap');

/* ── 기본 리셋 ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background-color: #D6C9B0 !important;   /* 갤러리 벽 */
    padding-top: 0 !important;
    max-width: 100% !important;
}
[data-testid="stSidebar"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

[data-testid="stMainBlockContainer"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 0 !important;
}

/* ── 폰트 ── */
h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 400 !important;
    color: #1C1611 !important;
}
p, span, div, label, input, textarea {
    font-family: 'Inter', sans-serif !important;
}

/* ── 네비게이션 ── */
.top-nav {
    background: #F5EDE0;
    border-bottom: 1px solid #C4B49A;
    padding: 1.4rem 4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.nav-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 10px;
    color: #1C1611;
    text-transform: uppercase;
}
.nav-tagline {
    font-size: 0.58rem;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: #8B7355;
    margin-top: 3px;
}
.nav-links {
    display: flex;
    gap: 3rem;
    font-size: 0.62rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #8B7355;
}

/* ── 히어로 ── */
.hero-section {
    background: #F5EDE0;
    border-bottom: 2px solid #C4B49A;
    padding: 5rem 4rem 4rem;
    position: relative;
    overflow: hidden;
}
.hero-bg-text {
    position: absolute;
    top: -3rem; left: 2rem;
    font-family: 'Playfair Display', serif;
    font-size: 22rem;
    color: rgba(139,115,85,0.05);
    line-height: 1;
    pointer-events: none;
    user-select: none;
}
.hero-eyebrow {
    font-size: 0.6rem;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: #8B7355;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    line-height: 1.2;
    color: #1C1611;
    margin-bottom: 0.3rem;
}
.hero-title em { font-style: italic; color: #6B5040; }
.hero-divider {
    width: 60px; height: 2px;
    background: #8B7355;
    margin: 2rem 0;
}
.hero-stats { display: flex; gap: 4rem; }
.stat-block {}
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    color: #1C1611;
    display: block;
    line-height: 1;
}
.stat-label {
    font-size: 0.58rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #8B7355;
    display: block;
    margin-top: 4px;
}

/* ── 섹션 헤더 (갤러리) ── */
.section-header {
    padding: 3rem 4rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 1px solid rgba(0,0,0,0.12);
    margin-bottom: 0;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #F5EDE0;
    font-weight: 400;
}
.section-meta {
    font-size: 0.6rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(245,237,224,0.9);
}

/* ── 액자 프레임 ── */
.wall-cell {
    padding: 2rem 1.5rem 1.5rem;
}
.wire {
    display: flex;
    justify-content: center;
    margin-bottom: 3px;
}
.wire::after {
    content: '';
    width: 1px;
    height: 22px;
    background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.35));
    display: block;
}
.frame-outer {
    background:
        linear-gradient(145deg,
            #7A5C3E 0%, #A07B55 8%, #6B4C30 18%,
            #B8926A 28%, #5C3D24 38%,
            #9A7348 48%, #6B4C30 58%,
            #A07B55 68%, #7A5C3E 78%,
            #5C3D24 88%, #8A6540 100%);
    padding: 9px;
    box-shadow:
        0 40px 80px rgba(0,0,0,0.65),
        0 20px 40px rgba(0,0,0,0.45),
        0  8px 20px rgba(0,0,0,0.3),
        inset 0 0 0 1px rgba(255,255,255,0.12),
        inset 0 0 0 3px rgba(0,0,0,0.35);
    position: relative;
}
.frame-outer::before {
    content: '';
    position: absolute;
    inset: 3px;
    border: 1px solid rgba(255,255,255,0.08);
    pointer-events: none;
    z-index: 1;
}
.frame-mat {
    background: #FDFAF5;
    padding: 14px 14px 36px 14px;
    box-shadow:
        inset 0 0 40px rgba(0,0,0,0.06),
        inset 0 0 0 1px rgba(0,0,0,0.05);
}
.frame-mat img {
    display: block;
    width: 100%;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}

/* ── 뮤지엄 라벨 ── */
.museum-label {
    background: #F5EDE0;
    margin-top: 1.2rem;
    padding: 0.75rem 0.9rem 0.85rem;
    border-left: 2px solid #8B7355;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
}
.label-no {
    font-size: 0.55rem;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: #8B7355;
    margin-bottom: 0.3rem;
}
.label-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.95rem;
    font-style: italic;
    color: #1C1611;
    line-height: 1.35;
    margin-bottom: 0.2rem;
}
.label-medium {
    font-size: 0.62rem;
    color: #8B7355;
    letter-spacing: 0.5px;
}
.label-date {
    font-size: 0.58rem;
    color: #A89070;
    margin-top: 2px;
}

/* ── 다운로드 링크 ── */
.dl-link {
    display: inline-block;
    margin-top: 0.7rem;
    font-size: 0.6rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #8B7355;
    text-decoration: none;
    border-bottom: 1px solid rgba(139,115,85,0.4);
    padding-bottom: 1px;
    transition: color 0.2s;
}
.dl-link:hover { color: #1C1611; border-color: #1C1611; }

/* ── 삭제 버튼 스타일 ── */
[data-testid="stButton"] > button {
    background: transparent !important;
    color: rgba(245,237,224,0.5) !important;
    border: 1px solid rgba(245,237,224,0.2) !important;
    border-radius: 0 !important;
    font-size: 0.55rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 0.35rem 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
    margin-top: 0.4rem !important;
}
[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(245,237,224,0.9) !important;
    border-color: rgba(245,237,224,0.5) !important;
}

/* ── 스튜디오 섹션 헤더 ── */
.studio-header {
    background: #1C1611;
    padding: 4rem 4rem 2.5rem;
    border-top: 3px solid #8B7355;
}
.studio-eyebrow {
    font-size: 0.58rem;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: #8B7355;
    margin-bottom: 0.8rem;
}
.studio-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: #F5EDE0;
    font-weight: 400;
    margin-bottom: 0.4rem;
}
.studio-desc {
    font-size: 0.75rem;
    color: rgba(245,237,224,0.45);
    letter-spacing: 1px;
}

/* ── 스튜디오 폼 영역 ── */
.studio-form-area {
    background: #231E18;
    padding: 2.5rem 4rem 3.5rem;
    border-bottom: 1px solid #3A2E22;
}

/* ── 폼 입력 필드 (스튜디오용) ── */
[data-testid="stTextArea"] textarea {
    background: #2C2318 !important;
    border: 1px solid #4A3828 !important;
    border-radius: 0 !important;
    color: #F5EDE0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: rgba(245,237,224,0.3) !important; }
[data-testid="stTextArea"] textarea:focus {
    border-color: #8B7355 !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input {
    background: #2C2318 !important;
    border: 1px solid #4A3828 !important;
    border-radius: 0 !important;
    color: #F5EDE0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #8B7355 !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: rgba(245,237,224,0.3) !important; }

/* ── 레이블 (스튜디오) ── */
label[data-testid="stWidgetLabel"] p,
[data-testid="stSelectbox"] label p,
[data-testid="stSlider"] label p,
[data-testid="stSelectSlider"] label p {
    font-size: 0.6rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: #8B7355 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── 생성 버튼 ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: #8B7355 !important;
    color: #F5EDE0 !important;
    border: none !important;
    border-radius: 0 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    padding: 0.85rem 2.5rem !important;
    margin-top: 0.4rem !important;
    transition: all 0.25s !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #F5EDE0 !important;
    color: #1C1611 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #2C2318 !important;
    border: 1px solid #4A3828 !important;
    border-radius: 0 !important;
    color: #F5EDE0 !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #8B7355 !important;
}
[data-testid="stSelectSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #8B7355 !important;
}

/* ── 알림 ── */
[data-testid="stAlert"] { border-radius: 0 !important; }

/* ── 리프레시 버튼 (section-header 안) ── */
.refresh-btn-area [data-testid="stButton"] > button {
    background: transparent !important;
    color: rgba(245,237,224,0.6) !important;
    border: 1px solid rgba(245,237,224,0.25) !important;
    border-radius: 0 !important;
    font-size: 0.58rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin-top: 0 !important;
}

/* ── 푸터 ── */
.footer {
    background: #1C1611;
    padding: 1.8rem 4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #3A2E22;
}
.footer-brand {
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    letter-spacing: 6px;
    color: #8B7355;
}
.footer-copy {
    font-size: 0.55rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4A3828;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════
gallery_images = load_gallery_images()
work_count = len(gallery_images)


# ══════════════════════════════════════════════════════════════
#  NAV
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="top-nav">
  <div>
    <div class="nav-logo">민화 MINHWA</div>
    <div class="nav-tagline">Korean Folk Art, Reimagined by AI · 2026</div>
  </div>
  <div class="nav-links">
    <span>Collection</span>
    <span>Studio</span>
    <span>About</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-section">
  <div class="hero-bg-text">"</div>
  <div class="hero-eyebrow">조선의 민화 · Gemini AI · 현대적 재해석</div>
  <div class="hero-title">
    전통 민화, <em>AI로</em><br>다시 태어나다.
  </div>
  <div class="hero-divider"></div>
  <div class="hero-stats">
    <div class="stat-block">
      <span class="stat-num">{work_count}</span>
      <span class="stat-label">전시 작품 수</span>
    </div>
    <div class="stat-block">
      <span class="stat-num">Gemini</span>
      <span class="stat-label">AI 엔진</span>
    </div>
    <div class="stat-block">
      <span class="stat-num">조선</span>
      <span class="stat-label">시대적 배경</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  GALLERY WALL
# ══════════════════════════════════════════════════════════════
# 섹션 헤더 (HTML)
st.markdown(f"""
<div class="section-header">
  <div class="section-title">민화 컬렉션</div>
  <div class="section-meta">{work_count}점 &nbsp;·&nbsp; AI 재해석 &nbsp;·&nbsp; 2026</div>
</div>
""", unsafe_allow_html=True)

# 새로고침 버튼 (작게)
_, refresh_area = st.columns([10, 1])
with refresh_area:
    st.markdown('<div class="refresh-btn-area">', unsafe_allow_html=True)
    if st.button("Refresh", key="refresh_top"):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if not gallery_images:
    st.markdown("""
    <div style="text-align:center; padding:6rem 0; color:rgba(245,237,224,0.35);
                font-family:'Playfair Display',serif; font-style:italic; font-size:1.4rem;">
      — The gallery awaits its first creation —
    </div>
    """, unsafe_allow_html=True)
else:
    GRID = 3
    for row_start in range(0, len(gallery_images), GRID):
        cols = st.columns(GRID, gap="small")
        for ci, col in enumerate(cols):
            idx = row_start + ci
            if idx >= len(gallery_images):
                break
            item = gallery_images[idx]
            work_no = work_count - idx
            style_display = item["style"].replace("-", " ").title() if item["style"] else "AI Art"

            with col:
                # 프레임 (base64 HTML 렌더링)
                try:
                    b64 = image_to_b64(item["path"])
                    st.markdown(f"""
                    <div class="wall-cell">
                      <div class="wire"></div>
                      <div class="frame-outer">
                        <div class="frame-mat">
                          <img src="data:image/png;base64,{b64}" alt="{item['title']}">
                        </div>
                      </div>
                      <div class="museum-label">
                        <div class="label-no">No. {work_no:03d} &nbsp;·&nbsp; 민화 MINHWA</div>
                        <div class="label-title">{item['title']}</div>
                        <div class="label-medium">AI Digital Art &nbsp;·&nbsp; {style_display}</div>
                        <div class="label-date">{item['created']} &nbsp;·&nbsp; {item['size_kb']} KB</div>
                      </div>
                      <a class="dl-link"
                         href="data:image/png;base64,{b64}"
                         download="canvas_{work_no:03d}.png">
                        Download Work
                      </a>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    st.error("이미지 로드 실패")
                    continue

                # 삭제 버튼
                if st.button("Remove from Gallery", key=f"del_{idx}", use_container_width=False):
                    if delete_image(item["path"]):
                        st.rerun()


# ══════════════════════════════════════════════════════════════
#  STUDIO — AI 에이전트 파이프라인
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="studio-header">
  <div class="studio-eyebrow">창작 스튜디오 · AI Agent Pipeline</div>
  <div class="studio-title">새 민화 작품 만들기</div>
  <div class="studio-desc">
    그리고 싶은 민화 주제를 한글로 입력하면 AI가 프롬프트를 만들고 이미지를 생성합니다.
  </div>
</div>
<div class="studio-form-area"></div>
""", unsafe_allow_html=True)

if "preview_text" not in st.session_state:
    st.session_state.preview_text = ""

with st.container():
    user_input = st.text_input(
        "민화 주제",
        placeholder="예: 까치와 호랑이, 서당에서 훈장님과 학동들, 단오날 개울가 풍경",
    )

    p_col, g_col, _ = st.columns([1, 1, 4])
    with p_col:
        preview_btn = st.button("프롬프트 미리보기", key="preview")
    with g_col:
        generate_btn = st.button("작품 생성하기", type="primary", use_container_width=True)

if preview_btn:
    if not user_input.strip():
        st.warning("민화 주제를 먼저 입력해 주세요.")
    else:
        with st.spinner("AI가 프롬프트를 작성하는 중..."):
            ok, expanded = expand_prompt(user_input)
        if ok:
            st.session_state.preview_text = expanded
        else:
            st.error(expanded)

if st.session_state.preview_text:
    st.markdown('<div style="margin:0.5rem 0 0.5rem; font-size:0.62rem; letter-spacing:3px; text-transform:uppercase; color:#8B7355;">AI Generated Prompt</div>', unsafe_allow_html=True)
    st.code(st.session_state.preview_text, language="text")

if generate_btn:
    if not user_input.strip():
        st.warning("민화 주제를 입력해 주세요.")
    else:
        with st.spinner("① AI가 민화 프롬프트를 작성하는 중..."):
            ok, expanded_prompt = expand_prompt(user_input)

        if not ok:
            st.error(expanded_prompt)
        else:
            with st.spinner("② AI가 민화를 그리는 중... (30~60초)"):
                success, result = generate_image(
                    prompt=expanded_prompt,
                    title=user_input,
                )
            if success:
                st.success("작품이 갤러리에 추가되었습니다! 위로 스크롤하면 확인할 수 있습니다.")
                st.rerun()
            else:
                st.error(result)


# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <div class="footer-brand">민화 MINHWA</div>
  <div class="footer-copy">© 2026 &nbsp;·&nbsp; Korean Folk Art Reimagined by AI</div>
</div>
""", unsafe_allow_html=True)
