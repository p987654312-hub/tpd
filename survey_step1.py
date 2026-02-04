import streamlit as st
import pandas as pd
from datetime import datetime

def show_survey(conn, clean_val):
    st.title("📝 1단계: 사전 역량 진단")
    st.markdown("---")
    st.info("선생님의 역량 진단 결과는 두 번째 시트에 기록되며, 완료 시 대시보드 상태가 업데이트됩니다.")
    
    with st.form("survey_form"):
        st.subheader("📊 역량 점수 입력")
        
        # 구글 시트(diagnosis_results) 컬럼명과 일치하게 설정
        s1 = st.slider("1. 생활지도 역량", 1, 5, 3)
        s2 = st.slider("2. 수업설계 역량", 1, 5, 3)
        s3 = st.slider("갈등관리 역량", 1, 5, 3)
        
        st.divider()
        comment = st.text_area("플랫폼에 바라는 점")

        col1, col2 = st.columns(2)
        submit_btn = col1.form_submit_button("✅ 진단 완료 및 제출")
        cancel_btn = col2.form_submit_button("🏠 돌아가기")

        if submit_btn:
            try:
                # 1. diagnosis_results 시트에 결과 추가
                df_results = conn.read(worksheet="diagnosis_results", ttl=0)
                user_id = clean_val(st.session_state.user['id'])
                
                new_data = pd.DataFrame([{
                    "user_id": user_id,
                    "1.생활지도": s1,
                    "2.수업설계": s2,
                    "갈등관리": s3,
                    "total_score": s1 + s2 + s3,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                
                updated_results = pd.concat([df_results, new_data], ignore_index=True)
                conn.update(worksheet="diagnosis_results", data=updated_results)

                # 2. users 시트 상태 업데이트
                df_users = conn.read(worksheet="users", ttl=0)
                df_users.columns = [c.lower().strip() for c in df_users.columns]
                
                # ID 매칭을 위한 임시 처리
                df_users['id_temp'] = df_users['id'].apply(clean_val)
                target_idx = df_users[df_users['id_temp'] == user_id].index
                
                if not target_idx.empty:
                    # 정확하게 '완료' 기입 (앞뒤 공백 제거)
                    df_users.loc[target_idx, 'step1_status'] = "완료"
                    final_users = df_users.drop(columns=['id_temp'])
                    conn.update(worksheet="users", data=final_users)
                    
                    # 세션 갱신 (즉시 반영용)
                    st.session_state.user['step1_status'] = "완료"

                st.balloons()
                st.success("성공적으로 제출되었습니다!")
                st.session_state.page = "dashboard"
                st.rerun()
                
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {e}")
                st.info("구글 시트의 컬럼 헤더가 'user_id', '1.생활지도', '2.수업설계', '갈등관리', 'total_score', 'date' 인지 확인해주세요.")

        if cancel_btn:
            st.session_state.page = "dashboard"
            st.rerun()
