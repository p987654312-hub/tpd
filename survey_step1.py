import streamlit as st
import pandas as pd
from datetime import datetime

def show_survey(conn, clean_val):
    st.title("📝 1단계: 사전 역량 진단")
    st.markdown("---")
    
    with st.form("survey_form"):
        st.subheader("📊 역량 점수 입력")
        # 시트(image_194b6c.png)의 컬럼명과 일치하도록 구성
        score_1 = st.slider("1. 생활지도 역량", 1, 5, 3)
        score_2 = st.slider("2. 수업설계 역량", 1, 5, 3)
        score_3 = st.slider("갈등관리 역량", 1, 5, 3)
        
        st.divider()
        q_comment = st.text_area("플랫폼에 바라는 점이나 기타 의견")

        submit_btn = st.form_submit_button("✅ 진단 완료 및 제출")

        if submit_btn:
            try:
                # 💡 [작업 1] 두 번째 시트(diagnosis_results)에 설문 데이터 추가
                # ---------------------------------------------------------
                df_results = conn.read(worksheet="diagnosis_results", ttl=0)
                user_id = str(st.session_state.user['id']).strip()
                total_score = score_1 + score_2 + score_3
                
                # 시트의 컬럼명과 정확히 일치해야 합니다.
                new_row = pd.DataFrame([{
                    "user_id": user_id,
                    "1.생활지도": score_1,
                    "2.수업설계": score_2,
                    "갈등관리": score_3,
                    "total_score": total_score,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                
                # 기존 데이터 아래에 새 행 추가
                updated_results = pd.concat([df_results, new_row], ignore_index=True)
                conn.update(worksheet="diagnosis_results", data=updated_results)


                # 💡 [작업 2] 첫 번째 시트(users)의 상태를 '완료'로 변경
                # ---------------------------------------------------------
                df_users = conn.read(worksheet="users", ttl=0)
                
                # ID 매칭을 위해 보조 컬럼 생성 (오류 방지용)
                df_users['id_str'] = df_users['id'].apply(clean_val)
                user_idx = df_users[df_users['id_str'] == user_id].index
                
                if not user_idx.empty:
                    # 해당 사용자의 step1_status 컬럼(image_194f26.png의 G열)을 '완료'로 변경
                    df_users.loc[user_idx, 'step1_status'] = "완료"
                    
                    # 보조 컬럼 제거 후 시트 업데이트
                    final_users = df_users.drop(columns=['id_str'])
                    conn.update(worksheet="users", data=final_users)
                    
                    # 세션 상태도 즉시 업데이트 (대시보드 새로고침 없이 반영)
                    st.session_state.user['step1_status'] = "완료"

                st.balloons()
                st.success("데이터 저장 및 상태 업데이트가 완료되었습니다!")
                
                # 대시보드로 복귀
                st.session_state.page = "dashboard"
                st.rerun()
                
            except Exception as e:
                st.error(f"⚠️ 저장 오류 발생: {e}")
                st.info("구글 시트의 컬럼명(user_id, 1.생활지도 등)이 코드와 똑같은지 확인해주세요.")

    if st.button("🏠 취소하고 돌아가기"):
        st.session_state.page = "dashboard"
        st.rerun()
