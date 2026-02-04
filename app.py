import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="교원 성장 Mate", layout="wide", initial_sidebar_state="collapsed")

# [CSS 스타일은 이전과 동일하게 유지하거나 필요 시 수정 가능]

# 🔗 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def clean_val(val):
    if pd.isna(val) or val == "": return ""
    try: return str(int(float(val))).strip()
    except: return str(val).strip()

# 🔐 세션 상태 초기화
if 'user' not in st.session_state: st.session_state.user = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login'

# --- 인증 로직 (회원가입 & 로그인) ---

if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.8, 1])
    
    with col:
        st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
        
        # A. 회원가입 화면
        if st.session_state.auth_mode == 'signup':
            st.markdown('<div class="auth-box"><div class="auth-title">🌱 회원가입</div>', unsafe_allow_html=True)
            
            with st.form("signup_form"):
                # image_194f26.png의 컬럼 순서에 맞춘 입력창
                new_id = st.text_input("아이디 (id)", placeholder="숫자나 문자로 입력")
                new_pw = st.text_input("비밀번호 (password)", type="password")
                new_name = st.text_input("성함 (name)")
                new_school = st.text_input("소속 학교 (school)")
                
                if st.form_submit_button("가입 신청"):
                    if not (new_id and new_pw and new_name and new_school):
                        st.error("모든 항목을 정확히 입력해주세요.")
                    else:
                        try:
                            # 1. 기존 유저 데이터 읽기
                            df = conn.read(worksheet="users", ttl=0)
                            
                            # 2. 아이디 중복 체크
                            if clean_val(new_id) in df['id'].apply(clean_val).values:
                                st.error("이미 등록된 아이디입니다.")
                            else:
                                # 3. 신규 유저 행 생성 (G열 step1_status는 '미실시'로 고정)
                                new_user = pd.DataFrame([{
                                    "id": new_id,
                                    "password": new_pw,
                                    "name": new_name,
                                    "school": new_school,
                                    "step1_status": "미실시"
                                }])
                                
                                # 4. 시트에 업데이트
                                updated_df = pd.concat([df, new_user], ignore_index=True)
                                conn.update(worksheet="users", data=updated_df)
                                
                                st.success(f"{new_name} 선생님, 가입을 환영합니다! 로그인을 진행해주세요.")
                                st.session_state.auth_mode = 'login'
                                st.rerun()
                        except Exception as e:
                            st.error(f"회원가입 오류: {e}")
            
            if st.button("이미 계정이 있나요? 로그인하러 가기"):
                st.session_state.auth_mode = 'login'
                st.rerun()

        # B. 로그인 화면
        else:
            st.markdown('<div class="auth-box"><div class="auth-title">🚀 로그인</div>', unsafe_allow_html=True)
            with st.form("login_form"):
                uid = st.text_input("아이디")
                upw = st.text_input("비밀번호", type="password")
                if st.form_submit_button("로그인"):
                    df = conn.read(worksheet="users", ttl=0)
                    user_row = df[df['id'].apply(clean_val) == clean_val(uid)]
                    if not user_row.empty and clean_val(user_row.iloc[0]['password']) == clean_val(upw):
                        st.session_state.user = user_row.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("로그인 정보를 다시 확인해주세요.")
            
            if st.button("처음 오셨나요? 회원가입하기"):
                st.session_state.auth_mode = 'signup'
                st.rerun()
else:
    # [로그인 후 대시보드 로직 유지]
    st.title(f"✨ {st.session_state.user['name']} 선생님 반갑습니다!")
