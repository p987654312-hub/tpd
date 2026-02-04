import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

try:
    import survey_step1
except ImportError:
    st.error("survey_step1.py 파일을 찾을 수 없습니다.")

# 1. 페이지 설정 및 제목 링크 숨기기
st.set_page_config(page_title="교원 성장 플랫폼", layout="wide")

# 2. 고도화된 웹 스타일 CSS (Streamlit 흔적 지우기)
st.markdown("""
    <style>
    /* 배경 및 폰트 */
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #F0F2F5;
    }
    
    /* 사이드바 숨기기 및 헤더 정리 */
    [data-testid="stSidebarNav"] {display: none;}
    .element-container:has(h1, h2, h3) a { display: none !important; }
    
    /* 웹 스타일 카드 컨테이너 */
    .web-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        border-top: 8px solid #E5E7EB;
    }
    .web-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 상태별 색상 (완료 시 초록 테두리) */
    .card-completed { border-top: 8px solid #10B981 !important; background-color: #F0FFF4; }
    
    /* 커스텀 텍스트 스타일 */
    .card-title { font-size: 1.1rem; color: #6B7280; font-weight: 600; margin-bottom: 10px; }
    .card-status { font-size: 1.5rem; font-weight: 800; margin-bottom: 20px; }
    .status-done { color: #059669; }
    .status-yet { color: #9CA3AF; }

    /* Streamlit 버튼을 일반 웹 버튼처럼 리스타일링 */
    div.stButton > button {
        background-color: #6366F1;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 700;
        width: 100%;
        cursor: pointer;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #4F46E5;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    .completed-btn > div > button {
        background-color: #10B981 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 구글 시트 연결 및 데이터 함수
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

def check_login(user_id, user_pw):
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        df['id_clean'] = df['id'].apply(clean_val)
        target_id = clean_val(user_id)
        user_row = df[df['id_clean'] == target_id]
        if not user_row.empty and clean_val(user_row.iloc[0]['password']) == clean_val(user_pw):
            return user_row.iloc[0].to_dict()
        return None
    except: return None

# 4. 세션 초기화
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "dashboard"

# --- 5. 화면 렌더링 ---
if st.session_state.user is None:
    # [웹 스타일 로그인]
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;'>🚀 EDU Platform</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인하기"):
                user = check_login(uid, upw)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else: st.error("정보가 올바르지 않습니다.")

else:
    if st.session_state.page == "survey":
        survey_step1.show_survey(conn, clean_val)
    else:
        user = st.session_state.user
        
        # 최신 상태 새로고침
        try:
            all_users = conn.read(worksheet="users", ttl=0)
            all_users.columns = [c.lower().strip() for c in all_users.columns]
            updated = all_users[all_users['id'].apply(clean_val) == clean_val(user['id'])].iloc[0].to_dict()
            st.session_state.user = updated
        except: pass

        # 상단 네비게이션 바 느낌의 헤더
        st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; padding: 10px 0px 30px 0px;'>
                <h2>🏫 {user['school']} | {user['name']} 선생님</h2>
                <p style='color: #6366F1; font-weight: bold;'>나의 성장 포인트: 150pt</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        # 카드 레이아웃
        col1, col2, col3, col4 = st.columns(4)
        
        s1_status = str(user.get('step1_status', '')).strip()
        is_done = (s1_status == "완료")
        
        with col1:
            card_style = "card-completed" if is_done else ""
            status_html = "<span class='status-done'>✅ 실시완료</span>" if is_done else "<span class='status-yet'>⚪ 미실시</span>"
            
            st.markdown(f"""
                <div class="web-card {card_style}">
                    <div class="card-title">STEP 01</div>
                    <div class="card-status">{status_html}</div>
                    <p style='font-size: 0.85rem; color: #9CA3AF; margin-bottom: 20px;'>나의 디지털 역량을<br>진단해보세요.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 버튼을 카드 바로 밑에 배치 (CSS로 합쳐진 느낌 구현)
            btn_class = "completed-btn" if is_done else ""
            st.markdown(f"<div class='{btn_class}'>", unsafe_allow_html=True)
            if st.button("진단 시작하기" if not is_done else "다시 진단하기", key="s1_btn"):
                st.session_state.page = "survey"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # 미완료 카드들 예시
        for i, (title, step) in enumerate([("연수 수강", "02"), ("수업 실천", "03"), ("최종 인증", "04")], 2):
            with [col2, col3, col4][i-2]:
                st.markdown(f"""
                    <div class="web-card">
                        <div class="card-title">STEP {step}</div>
                        <div class="card-status"><span class='status-yet'>⚪ 미실시</span></div>
                        <p style='font-size: 0.85rem; color: #9CA3AF; margin-bottom: 20px;'>현재 단계를 완료하면<br>활성화됩니다.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.button("준비중", disabled=True, key=f"s{i}_btn")
