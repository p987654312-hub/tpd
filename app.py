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
# 2. 디자인 CSS (로그인 & 대시보드 공통)
# --------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }

    /* 배경색 (연한 하늘색) */
    [data-testid="stAppViewContainer"] { background-color: #EBF3FF; }
    [data-testid="stHeader"] { visibility: hidden; }
    
    /* 카드 공통 스타일 */
    .auth-card {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* 대시보드 스타일 */
    .nav-bar { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; margin-bottom: 20px; }
    .nav-logo { font-size: 20px; font-weight: 800; color: #7c3aed; }
    .welcome-banner { background-color: white; padding: 40px; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 30px; position: relative; }
    
    .step-card { background-color: white; padding: 25px; border-radius: 20px; height: 320px; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.02); transition: 0.3s; border: 1px solid transparent; }
    .step-card:hover { transform: translateY(-5px); }
    .step-card-active { border: 2px solid #A7F3D0; background-color: #F0FDF4; }
    
    .step-bg-number { position: absolute; top: 10px; right: 20px; font-size: 4rem; font-weight: 900; color: #F3F4F6; z-index: 0; }
    .step-icon { font-size: 2.5rem; margin-bottom: 15px; z-index: 1; position: relative; }
    .step-title { font-size: 1.1rem; font-weight: 800; color: #1F2937; margin-bottom: 10px; z-index: 1; position: relative; }
    .step-desc { font-size: 0.85rem; color: #6B7280; line-height: 1.4; margin-bottom: 20px; z-index: 1; position: relative; height: 60px; }

    /* 버튼 스타일 */
    div.stButton > button { border-radius: 8px; font-size: 14px; padding: 10px; border: none; width: 100%; font-weight: 600; background-color: #667eea; color: white; }
    div.stButton > button:hover { background-color: #5a67d8; }
    /* 보조 버튼 (회원가입 전환용) 스타일 */
    .switch-btn { background-color: transparent !important; color: #667eea !important; border: 1px solid #667eea !important; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 3. 데이터 로직
# --------------------------------------------------------------------------
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login' # login / signup

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

# [A] 로그인 전 화면 (로그인 & 회원가입 전환)
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    
    with c2:
        # A-1. 로그인 모드
        if st.session_state.auth_mode == 'login':
            st.markdown("""
            <div class="auth-card">
                <h2 style="color:#667eea; margin-bottom:5px;">🚀 로그인</h2>
                <p style="color:#888; font-size:0.9rem;">선생님의 성장을 응원합니다.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                uid = st.text_input("아이디")
                upw = st.text_input("비밀번호", type="password")
                if st.form_submit_button("로그인하기"):
                    df = get_data()
                    if df is not None:
                        user = df[df['id'].astype(str) == str(uid)]
                        if not user.empty and str(user.iloc[0]['password']) == str(upw):
                            st.session_state.user = user.iloc[0].to_dict()
                            st.rerun()
                        else: st.error("아이디 또는 비밀번호가 틀렸습니다.")
                    else: st.error("시트 연결 실패")
            
            # 회원가입 전환 버튼
            if st.button("계정이 없으신가요? 회원가입", key="go_signup"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

        # A-2. 회원가입 모드 (복구됨!)
        else:
            st.markdown("""
            <div class="auth-card">
                <h2 style="color:#667eea; margin-bottom:5px;">🌱 회원가입</h2>
                <p style="color:#888; font-size:0.9rem;">새로운 아이디를 만들어주세요.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("signup_form"):
                new_id = st.text_input("아이디")
                new_pw = st.text_input("비밀번호", type="password")
                new_name = st.text_input("성함")
                new_school = st.text_input("소속 학교")
                
                if st.form_submit_button("가입완료"):
                    df = get_data()
                    if df is not None:
                        if str(new_id) in df['id'].astype(str).values:
                            st.error("이미 존재하는 아이디입니다.")
                        else:
                            new_row = pd.DataFrame([{
                                "id": new_id, "password": new_pw, 
                                "name": new_name, "school": new_school, 
                                "step1_status": "미실시"
                            }])
                            updated_df = pd.concat([df, new_row], ignore_index=True)
                            conn.update(worksheet="users", data=updated_df)
                            st.success("가입되었습니다! 로그인해주세요.")
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                    else: st.error("시트 연결 실패")
            
            # 로그인 전환 버튼
            if st.button("이미 계정이 있으신가요? 로그인", key="go_login"):
                st.session_state.auth_mode = 'login'
                st.rerun()

# [B] 로그인 후 대시보드 (5단계 디자인 유지)
else:
    user = st.session_state.user
    
    # 상단바
    st.markdown(f"""
        <div class="nav-bar">
            <div class="nav-logo">🌱 교원 성장 메이트</div>
            <div style="font-size:14px; color:#555;">{user.get('school', '')} | <b>{user['name']}</b> 님</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 배너
    st.markdown(f"""
        <div class="welcome-banner">
            <h1 style="font-size: 1.8rem; font-weight: 800;">👏 안녕하세요, <span style="color:#667eea;">{user['name']}</span> 선생님!</h1>
            <p style="color:#6B7280;">교원 성장 메이트와 함께 단계별로 역량을 진단해보세요.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 5단계 카드 레이아웃
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # 상태에 따른 카드 렌더링 (예시: 1단계 미실시 상태면 1번 활성, 2번 비활성)
    status = str(user.get('step1_status', '미실시'))
    is_step1_done = (status == "완료")
    
    # --- Step 1 ---
    with col1:
        card_class = "step-card" if is_step1_done else "step-card step-card-active"
        btn_text = "✅ 완료" if is_step1_done else "🚀 진단 시작"
        bg_num_color = "#D1FAE5" if not is_step1_done else "#F3F4F6" # 활성 시 초록 숫자
        
        st.markdown(f"""
            <div class="{card_class}">
                <div class="step-bg-number" style="color:{bg_num_color};">01</div>
                <div class="step-icon">📝</div>
                <div class="step-title">사전 역량 진단</div>
                <div class="step-desc">현재 나의 강점과 보완점을 파악합니다.</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(btn_text, key="btn_s1", disabled=is_step1_done):
            try:
                import survey_step1
                # 여기서 페이지 전환 로직 등 필요 (현재는 메시지만)
                st.session_state.page = "survey" 
                st.rerun() 
            except: st.error("설문 파일(survey_step1.py)이 없습니다.")

    # --- Step 2 ---
    with col2:
        # 1단계가 끝나야 2단계 활성화
        card_class = "step-card step-card-active" if is_step1_done else "step-card"
        opacity = "1" if is_step1_done else "0.7"
        
        st.markdown(f"""
            <div class="{card_class}" style="opacity:{opacity};">
                <div class="step-bg-number">02</div>
                <div class="step-icon">🌱</div>
                <div class="step-title">자기역량 개발계획</div>
                <div class="step-desc">맞춤형 성장 계획을 수립합니다.</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("준비중", key="btn_s2", disabled=True)

    # --- Step 3, 4, 5 (생략 없이 동일 패턴 적용) ---
    steps = [
        (col3, "03", "📈", "사후 역량 진단", "변화된 역량을 재진단합니다."),
        (col4, "04", "🏆", "개발결과 보고서", "성장 과정을 기록합니다."),
        (col5, "05", "☑️", "자기실적평가서", "실적을 종합 평가합니다.")
    ]
    
    for col, num, icon, title, desc in steps:
        with col:
            st.markdown(f"""
                <div class="step-card" style="opacity: 0.7; background:#F9FAFB;">
                    <div class="step-bg-number">{num}</div>
                    <div class="step-icon">{icon}</div>
                    <div class="step-title" style="color:#9CA3AF;">{title}</div>
                    <div class="step-desc">{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            st.button("🔒 잠김", disabled=True, key=f"btn_s{num}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("로그아웃", key="logout"):
        st.session_state.user = None
        st.rerun()
