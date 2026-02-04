import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 💡 분리된 설문지 모듈 불러오기
try:
    import survey_step1
except ImportError:
    st.error("survey_step1.py 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")

# 🎨 1. 테마 및 디자인 설정
st.set_page_config(page_title="교원 성장 플랫폼", layout="wide")

st.markdown("""
    <style>
    /* 사이드바 메뉴 및 제목 링크 아이콘 숨기기 */
    [data-testid="stSidebarNav"] {display: none;}
    .element-container:has(h1, h2, h3) a { display: none !important; }
    
    .stApp { background-color: #F8F7FF; }
    
    /* 카드 공통 스타일 */
    .status-card {
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 0px;
        transition: 0.3s;
    }
    
    /* 미실시 카드 (회색) */
    .card-gray {
        background-color: #F3F4F6;
        color: #6B7280;
        border: 1px solid #E5E7EB;
    }
    
    /* 실시완료 카드 (초록색) */
    .card-green {
        background-color: #D1FAE5;
        color: #065F46;
        border: 2px solid #10B981;
    }

    /* 버튼 스타일 강제 적용 */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 45px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# 🔗 2. 구글 시트 연결 및 유틸 함수
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    """숫자와 문자 형식을 통일하는 함수"""
    if pd.isna(val) or val == "": return ""
    try:
        return str(int(float(val))).strip()
    except:
        return str(val).strip()

def check_login(user_id, user_pw):
    """로그인 인증 함수"""
    try:
        df = conn.read(worksheet="users", ttl=0)
        df.columns = [c.lower().strip() for c in df.columns]
        df['id_clean'] = df['id'].apply(clean_val)
        target_id = clean_val(user_id)
        
        user_row = df[df['id_clean'] == target_id]
        if not user_row.empty:
            if clean_val(user_row.iloc[0]['password']) == clean_val(user_pw):
                return user_row.iloc[0].to_dict()
        return None
    except:
        return None

# 🔐 3. 세션 초기화
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"

# --- 4. 메인 화면 분기 ---

# A. 로그인 화면
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("")
        st.title("💜 교원 성장 플랫폼")
        with st.form("login_form"):
            uid = st.text_input("아이디")
            upw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("로그인"):
                user_data = check_login(uid, upw)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

# B. 로그인 후 화면
else:
    if st.session_state.page == "survey":
        survey_step1.show_survey(conn, clean_val)
    
    else:
        # 대시보드 진입 시 최신 데이터 동기화
        try:
            current_id = clean_val(st.session_state.user['id'])
            all_users = conn.read(worksheet="users", ttl=0)
            all_users.columns = [c.lower().strip() for c in all_users.columns]
            all_users['id_clean'] = all_users['id'].apply(clean_val)
            updated_row = all_users[all_users['id_clean'] == current_id]
            if not updated_row.empty:
                st.session_state.user = updated_row.iloc[0].to_dict()
        except:
            pass

        user = st.session_state.user
        
        with st.sidebar:
            st.markdown(f"### 🏫 {user.get('school', '학교')}")
            st.write(f"**{user['name']}** 선생님")
            st.divider()
            if st.button("로그아웃"):
                st.session_state.user = None
                st.session_state.page = "dashboard"
                st.rerun()

        st.title(f"✨ {user['name']} 선생님, 반갑습니다!")
        st.subheader("📊 나의 성장 현황")
        
        # 1단계 상태 판별
        s1_raw = str(user.get('step1_status', '')).strip()
        is_done = (s1_raw == "완료")
        
        card_class = "card-green" if is_done else "card-gray"
        status_text = "✅ 실시완료" if is_done else "⚪ 미실시"
        btn_label = "다시 진단하기" if is_done else "진단 시작"
        btn_color = "#10B981" if is_done else "#9CA3AF"

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # 카드와 버튼을 시각적으로 묶음
            st.markdown(f"""
                <div class="status-card {card_class}">
                    <p style="font-size: 0.9rem; margin-bottom: 5px;">1단계: 역량 진단</p>
                    <h3 style="margin-top: 0px; color: inherit;">{status_text}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # 버튼 색상 커스텀 CSS
            st.markdown(f'<style>div[data-testid="column"]:nth-of-type(1) button {{ background-color: {btn_color} !important; color: white !important; }}</style>', unsafe_allow_html=True)
            
            if st.button(btn_label, key="go_step1"):
                st.session_state.page = "survey"
                st.rerun()

        # 나머지 단계 (동일 디자인 유지)
        with col2:
            st.markdown('<div class="status-card card-gray"><p style="font-size:0.9rem;">2단계: 연수 수강</p><h3>미실시</h3></div>', unsafe_allow_html=True)
            st.button("준비중", disabled=True, key="go_step2")
        with col3:
            st.markdown('<div class="status-card card-gray"><p style="font-size:0.9rem;">3단계: 수업 실천</p><h3>미실시</h3></div>', unsafe_allow_html=True)
            st.button("준비중 ", disabled=True, key="go_step3")
        with col4:
            st.markdown('<div class="status-card card-gray"><p style="font-size:0.9rem;">4단계: 최종 인증</p><h3>미실시</h3></div>', unsafe_allow_html=True)
            st.button("준비중  ", disabled=True, key="go_step4")
