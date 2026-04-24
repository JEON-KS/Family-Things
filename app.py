import streamlit as st
from gtts import gTTS
import base64
import io
import time
import random  # [추가] 랜덤 기능을 위해 필요합니다.

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="아빠표 받아쓰기", page_icon="✏️")

# --- [함수 정의] ---

@st.cache_data(show_spinner=False)
def generate_audio_bytes(text, speed_option):
    """음성 파일을 생성하고 캐싱합니다."""
    mp3_fp = io.BytesIO()
    is_slow = True if speed_option == "느리게" else False
    
    # 목소리 생성
    tts = gTTS(text=", " + text, lang='ko', slow=is_slow)
    tts.write_to_fp(mp3_fp)
    return mp3_fp.getvalue()

def play_audio(audio_bytes):
    """브라우저에서 음성을 자동 재생합니다."""
    b64 = base64.b64encode(audio_bytes).decode()
    unique_id = str(time.time()).replace('.', '')
    
    html_code = f"""
    <div id="wrapper_{unique_id}" style="display:none;">
        <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    </div>
    """
    st.components.v1.html(html_code, height=0)

# --- [세션 상태 초기화] ---

if 'step' not in st.session_state:
    st.session_state.step = 'SETUP'
if 'quiz_list' not in st.session_state:
    st.session_state.quiz_list = []
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'last_played_idx' not in st.session_state:
    st.session_state.last_played_idx = -1
if 'speed' not in st.session_state:
    st.session_state.speed = "보통"

# --- [1단계: 설정 화면 (SETUP)] ---

if st.session_state.step == 'SETUP':
    st.title("✏️ 덕현초 2학년 1반 예쁜 전유하의 받아쓰기 공부")
    st.subheader("오늘도 백점을 향해 화이팅! 💪")
    st.write("---")
    
    # 속도 선택
    speed_options = ["보통", "느리게"]
    st.session_state.speed = st.radio(
        "📢 읽기 속도를 선택하세요",
        speed_options,
        index=speed_options.index(st.session_state.speed),
        horizontal=True
    )
    
    # 문제 입력
    input_text = st.text_area("공부할 문장들을 입력해 주세요 (엔터로 구분)", 
                             placeholder="예:\n날씨가 아주 맑아요.\n공책에 글씨를 써요.",
                             height=200)
    
    if st.button("시험 시작하기 🚀", use_container_width=True):
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        if len(lines) > 0:
            # --- [핵심 수정] 리스트 순서를 무작위로 섞습니다 ---
            random.shuffle(lines) 
            # ----------------------------------------------
            st.session_state.quiz_list = lines
            st.session_state.current_idx = 0
            st.session_state.last_played_idx = -1
            st.session_state.step = 'EXAM'
            st.rerun()
        else:
            st.warning("공부할 문장을 먼저 입력해 주세요!")

# --- [2단계: 시험 화면 (EXAM)] ---

elif st.session_state.step == 'EXAM':
    idx = st.session_state.current_idx
    total = len(st.session_state.quiz_list)
    current_sentence = st.session_state.quiz_list[idx]
    
    audio_data = generate_audio_bytes(current_sentence, st.session_state.speed)
    
    if st.session_state.last_played_idx != idx:
        play_audio(audio_data)
        st.session_state.last_played_idx = idx

    st.title(f"✍️ 제 {idx + 1} 번 문제")
    st.info(f"⏱ 현재 모드: **{st.session_state.speed}** 속도로 읽어주는 중")
    
    st.progress((idx + 1) / total)
    st.write("문장을 잘 듣고 종이에 예쁘게 적어보세요.")
    
    if st.button("🔊 다시 들려주기", use_container_width=True):
        play_audio(audio_data)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if idx > 0:
            if st.button("⬅️ 이전 문제", use_container_width=True):
                st.session_state.current_idx -= 1
                st.session_state.last_played_idx = -1 
                st.rerun()
    with col2:
        if idx < total - 1:
            if st.button("다음 문제 ➡️", use_container_width=True):
                st.session_state.current_idx += 1
                st.rerun()
        else:
            if st.button("시험 종료 🏁", use_container_width=True, type="primary"):
                st.session_state.step = 'RESULT'
                st.rerun()

# --- [3단계: 결과 화면 (RESULT)] ---

elif st.session_state.step == 'RESULT':
    st.title("🎉 시험 끝! 정말 고생했어 유하야!")
    st.balloons()
    
    st.write("### 📝 오늘 나온 문제 정답 (섞인 순서)")
    for i, q in enumerate(st.session_state.quiz_list):
        st.success(f"**{i+1}번:** {q}")
    
    st.write("---")
    if st.button("처음으로 돌아가기 🔄", use_container_width=True):
        st.session_state.step = 'SETUP'
        st.session_state.quiz_list = []
        st.session_state.last_played_idx = -1
        st.rerun()
