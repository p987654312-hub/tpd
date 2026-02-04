import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --------------------------------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="교원 성장 Mate",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------------------------
# 2. 이미지와 똑같이 만드는 '초강력 CSS'
# --------------------------------------------------------------------------
st.markdown("""
    <style>
    /* 전체 폰트 적용 */
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }

    /* 1. 배경색 (연한 하늘색) */
    [data-testid="stAppViewContainer"] {
        background-color: #EBF3FF;
    }
    
    /* 헤더 숨기기 */
    [data-testid="stHeader"] { visibility: hidden; }
    
    /* 2. 상단 네비게이션 바 스타일 */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background: transparent;
        margin-bottom: 20px;
    }
    .nav-logo { font-size: 20px; font-weight: 800; color: #7c3aed; display: flex; align-items: center; gap: 10px; }
    .nav-user { font-size: 14px; color: #555; }
    
    /* 3. 메인 배너 (흰색 긴 박스) */
    .welcome-banner {
        background-color: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 30px;
        position: relative;
    }
    .sync-badge {
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #E0E7FF;
        color: #4F46E5;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* 4. 카드 공통 스타일 (Step 1~5) */
    .step-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        height: 320px; /* 높이 고정 */
        position: relative;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        transition: 0.3s;
        border: 1px solid transparent;
    }
    .step-card:hover { transform: translateY(-5px); }
    
    /* (활성화된 카드 - Step 2 느낌) */
    .step-card-active {
        border: 2px solid #A7F3D0;
        background-color: #F0FDF4;
    }
    
    .step-bg-number {
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 4rem;
        font-weight: 900;
        color: #F3F4F6;
        z-index: 0;
    }
    .step-icon { font-size: 2.5rem; margin-bottom: 15px; z-index: 1; position: relative; }
    .step-title { font-size: 1.1rem; font-weight: 800; color: #1F2937; margin-bottom: 10px; z-index: 1; position: relative; }
    .step-desc { font-size: 0.85rem; color: #6B7280; line-height: 1.4; margin-bottom: 20px; z-index: 1; position: relative; height: 60px; }

    /* 5. 버튼 스타일 커스텀 */
    div.stButton > button {
        border-radius: 8px;
        font-size: 13px;
        padding: 5px 15px;
        border: none;
        width: 100%;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 3. 데이터 로직 (기존 유지)
# --------------------------------------------------------------------------
if 'user' not in st.session_state: st.session_state.user = None
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except: return None

# --------------------------------------------------------------------------
# 4. 화면 구현
# --------------------------------------------------------------------------

# [A] 로그인 전 화면 (간단하게 유지)
if st.session_state.user is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("""
        <div style="background:white; padding:40px; border-radius:20px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <h2 style="color:#667eea;">🌱 교원 성장 Mate</h2>
            <p style="color:#888;">로그인이 필요합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인"):
                df = get_data()
                if df is not None:
                    user = df[df['id'].astype(str) == str(uid)]
                    if not user.empty and str(user.iloc[0]['password']) == str(upw):
                        st.session_state.user = user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("정보 불일치")
                else: st.error("연결 실패")

# [B] 로그인 후 대시보드 (★ 디자인 집중 구현 ★)
else:
    user = st.session_state.user
    
    # 1. 상단 네비게이션 (HTML로 구현)
    st.markdown(f"""
        <div class="nav-bar">
            <div class="nav-logo">🌱 교원 성장 메이트</div>
            <div class="nav-user">
                신구초 | <span style="color:#667eea; font-weight:bold;">{user['name']}</span> 님 &nbsp; 
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 로그아웃 버튼 (우측 상단 위치 조정용)
    with st.container():
        _, col_logout = st.columns([9, 1])
        if col_logout.button("로그아웃", key="top_logout"):
            st.session_state.user = None
            st.rerun()

    # 2. 메인 배너 (안녕하세요, OOO 선생님!)
    st.markdown(f"""
        <div class="welcome-banner">
            <div class="sync-badge">☁️ 클라우드 동기화 활성 상태</div>
            <h1 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 10px;">
                👏 안녕하세요, <span style="color:#667eea;">{user['name']}</span> 선생님!
            </h1>
            <p style="color:#6B7280; font-size: 1rem;">
                교원 성장 메이트와 함께 단계별로 역량을 진단하고 더 나은 미래를 계획해보세요. 
                모든 데이터는 자동으로 동기화됩니다.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 3. 5단계 카드 그리드 (핵심 UI)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # --- Step 1: 사전 역량 진단 (완료 상태 예시) ---
    with col1:
        st.markdown("""
            <div class="step-card">
                <div class="step-bg-number">01</div>
                <div class="step-icon">📝</div>
                <div class="step-title">사전 역량 진단</div>
                <div class="step-desc">SJT 평가를 통해 현재 나의 강점과 보완점을 파악합니다.</div>
            </div>
        """, unsafe_allow_html=True)
        # 버튼은 HTML 밖에 native streamlit 버튼 사용 (기능 연결을 위해)
        st.button("✅ 완료", disabled=True, key="btn1") # 이미 완료된 느낌

    # --- Step 2: 자기역량 개발계획 (현재 진행중 - 초록색 강조) ---
    with col2:
        # 여기만 step-card-active 클래스 추가
        st.markdown("""
            <div class="step-card step-card-active">
                <div class="step-bg-number" style="color:#D1FAE5;">02</div>
                <div class="step-icon">🌱</div>
                <div class="step-title">자기역량 개발계획</div>
                <div class="step-desc">진단 결과를 바탕으로 맞춤형 성장 계획을 수립합니다.</div>
            </div>
        """, unsafe_allow_html=True)
        # 활성화된 버튼
        if st.button("🚀 진행하기", key="btn2"):
            st.success("2단계 페이지로 이동합니다!")

    # --- Step 3: 사후 역량 진단 ---
    with col3:
        st.markdown("""
            <div class="step-card" style="opacity: 0.7; background:#F9FAFB;">
                <div class="step-bg-number">03</div>
                <div class="step-icon">📈</div>
                <div class="step-title" style="color:#9CA3AF;">사후 역량 진단</div>
                <div class="step-desc">활동 후 변화된 역량을 재진단하여 성장율을 확인합니다.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("🔒 진행전", disabled=True, key="btn3")

    # --- Step 4: 개발결과 보고서 ---
    with col4:
        st.markdown("""
            <div class="step-card" style="opacity: 0.7; background:#F9FAFB;">
                <div class="step-bg-number">04</div>
                <div class="step-icon">🏆</div>
                <div class="step-title" style="color:#9CA3AF;">개발결과 보고서</div>
                <div class="step-desc">1년의 성장 과정을 기록하고 증빙자료를 정리합니다.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("🔒 진행전", disabled=True, key="btn4")

    # --- Step 5: 자기실적평가서 ---
    with col5:
        st.markdown("""
            <div class="step-card" style="opacity: 0.7; background:#F9FAFB;">
                <div class="step-bg-number">05</div>
                <div class="step-icon">☑️</div>
                <div class="step-title" style="color:#9CA3AF;">자기실적평가서</div>
                <div class="step-desc">교사 본인의 실적을 종합적으로 평가하여 제출합니다.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("🔒 진행전", disabled=True, key="btn5")
