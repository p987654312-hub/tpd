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
# 2. 디자인 CSS (메뉴/배지 삭제 포함)
# --------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    
    /* 배경색 */
    [data-testid="stAppViewContainer"] { background-color: #EBF3FF; }
    
    /* UI 숨김 처리 */
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; visibility: hidden !important; }
    .viewerBadge_container__1QSob { display: none !important; }
    #MainMenu { visibility: hidden; }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    
    /* 카드 스타일 */
    .auth-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; }
    .nav-bar { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; margin-bottom: 20px; } 
    .nav-logo { font-size: 20px; font-weight: 800; color: #7c3aed; }
    .welcome-banner { background-color: white; padding: 40px; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 30px; }
    
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
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 3. 데이터 및 상태 관리
# --------------------------------------------------------------------------
# 세션 상태 초기화
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login'
if 'page' not in st.session_state: st.session_state.page = 'dashboard' # 현재 페이지 위치 저장

conn = st.connection("gsheets", type=GSheetsConnection)

def clean_text(text):
    if pd.isna(text) or text == "": return ""
    text = str(text).strip()
    if text.endswith(".0"): return text[:-2]
    return text

def get_data():
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        df['id'] = df['id'].apply(clean_text)
        df['password'] = df['password'].apply(clean_text)
        return df
    except: return None

# --------------------------------------------------------------------------
# 4. 화면 라우팅 (Traffic Control) - 여기가 핵심입니다!
# --------------------------------------------------------------------------

# [A] 비로그인 상태 -> 로그인/회원가입 화면 표시
if st.session_state.user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    
    with c2:
        if st.session_state.auth_mode == 'login':
            # 로그인 폼
            st.markdown("""<div class="auth-card"><h2 style="color:#667eea;">🚀 로그인</h2><p style="color:#888; font-size:0.9rem;">선생님의 성장을 응원합니다.</p></div>""", unsafe_allow_html=True)
            with st.form("login_form"):
                uid = st.text_input("아이디")
                upw = st.text_input("비밀번호", type="password")
                if st.form_submit_button("로그인하기"):
                    df = get_data()
                    if df is not None:
                        clean_uid, clean_upw = clean_text(uid), clean_text(upw)
                        user = df[df['id'] == clean_uid]
                        if not user.empty and user.iloc[0]['password'] == clean_upw:
                            st.session_state.user = user.iloc[0].to_dict()
                            st.session_state.page = 'dashboard' # 로그인 성공 시 대시보드로 이동
                            st.rerun()
                        else: st.error("아이디 또는 비밀번호 오류")
                    else: st.error("연결 실패")
            if st.button("계정이 없으신가요? 회원가입"): st.session_state.auth_mode = 'signup'; st.rerun()

        else:
            # 회원가입 폼
            st.markdown("""<div class="auth-card"><h2 style="color:#667eea;">🌱 회원가입</h2><p style="color:#888;">새로운 아이디를 만들어주세요.</p></div>""", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_id = st.text_input("아이디")
                new_pw = st.text_input("비밀번호", type="password")
                new_name = st.text_input("성함")
                new_school = st.text_input("소속 학교")
                if st.form_submit_button("가입완료"):
                    df = get_data()
                    if df is not None:
                        if clean_text(new_id) in df['id'].values: st.error("이미 존재하는 아이디")
                        else:
                            new_row = pd.DataFrame([{"id": clean_text(new_id), "password": clean_text(new_pw), "name": new_name, "school": new_school, "step1_status": "미실시"}])
                            conn.update(worksheet="users", data=pd.concat([df, new_row], ignore_index=True))
                            st.success("가입 완료! 로그인해주세요."); st.session_state.auth_mode = 'login'; st.rerun()
            if st.button("로그인 화면으로"): st.session_state.auth_mode = 'login'; st.rerun()

# [B] 로그인 완료 상태 -> 페이지 분기 처리
else:
    user = st.session_state.user
    
    # ----------------------------------------------------
    # 상황 1: 대시보드 화면
    # ----------------------------------------------------
    if st.session_state.page == 'dashboard':
        st.markdown(f"""
            <div class="nav-bar">
                <div class="nav-logo">🌱 교원 성장 메이트</div>
                <div style="font-size:14px; color:#555;">{user.get('school', '')} | <b>{user['name']}</b> 님</div>
            </div>
            <div class="welcome-banner">
                <h1 style="font-size: 1.8rem; font-weight: 800;">👏 안녕하세요, <span style="color:#667eea;">{user['name']}</span> 선생님!</h1>
                <p style="color:#6B7280;">아래 카드를 선택하여 진단을 시작해보세요.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        status = str(user.get('step1_status', '미실시'))
        is_step1_done = (status == "완료")
        
        # [Step 1 카드]
        with col1:
            card_class = "step-card" if is_step1_done else "step-card step-card-active"
            btn_text = "✅ 완료" if is_step1_done else "🚀 진단 시작"
            bg_num_color = "#D1FAE5" if not is_step1_done else "#F3F4F6"
            
            st.markdown(f"""
                <div class="{card_class}">
                    <div class="step-bg-number" style="color:{bg_num_color};">01</div>
                    <div class="step-icon">📝</div>
                    <div class="step-title">사전 역량 진단</div>
                    <div class="step-desc">현재 나의 강점과 보완점을 파악합니다.</div>
                </div>
            """, unsafe_allow_html=True)
            
            # 🔥 [버튼 클릭 시] 페이지 상태를 'survey'로 변경하고 리런
            if st.button(btn_text, key="btn_s1", disabled=is_step1_done):
                st.session_state.page = 'survey'
                st.rerun()

        # [나머지 카드들 - 디자인 유지]
        steps = [
            (col2, "02", "🌱", "자기역량 개발계획", "맞춤형 성장 계획 수립"),
            (col3, "03", "📈", "사후 역량 진단", "변화된 역량 재진단"),
            (col4, "04", "🏆", "개발결과 보고서", "성장 과정 기록"),
            (col5, "05", "☑️", "자기실적평가서", "실적 종합 평가")
        ]
        for col, num, icon, title, desc in steps:
            with col:
                st.markdown(f"""<div class="step-card" style="opacity:0.7; bg:#F9FAFB;"><div class="step-bg-number">{num}</div><div class="step-icon">{icon}</div><div class="step-title" style="color:#999;">{title}</div><div class="step-desc">{desc}</div></div>""", unsafe_allow_html=True)
                st.button("🔒 잠김", disabled=True, key=f"btn_s{num}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("로그아웃", key="logout"):
            st.session_state.user = None; st.session_state.page = 'dashboard'; st.rerun()

    # ----------------------------------------------------
    # 상황 2: 설문조사(Step 1) 화면
    # ----------------------------------------------------
    elif st.session_state.page == 'survey':
        try:
            # survey_step1.py 파일이 있다면 불러와서 실행
            import survey_step1
            
            # 뒤로가기 버튼을 survey 파일 안이 아니라 여기서 만들어줄 수도 있음
            if st.button("⬅️ 대시보드로 돌아가기"):
                st.session_state.page = 'dashboard'
                st.rerun()
                
            survey_step1.show_survey(conn, clean_text)
            
        except ImportError:
            # 파일이 없을 경우 임시 화면 표시 (에러 방지용)
            st.markdown("""
                <div class="welcome-banner">
                    <h2>🚧 페이지 준비중</h2>
                    <p>survey_step1.py 파일이 폴더에 있는지 확인해주세요.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("⬅️ 대시보드로 돌아가기"):
                st.session_state.page = 'dashboard'
                st.rerun()
