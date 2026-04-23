import streamlit as st
from gtts import gTTS
import base64
import io
import time

# 웹페이지 설정
st.set_page_config(page_title="아빠표 받아쓰기", page_icon="✏️")

# --- 함수 정의 ---
@st.cache_data(show_spinner=False)
def generate_audio_bytes(text, speed_option):
    mp3_fp = io.BytesIO()
    # 선택된 옵션에 따라 slow 모드 결정
    is_slow = True if speed_option == "느리게 (추천)" else False
    
    tts = gTTS(text=", " + text, lang='ko', slow=is_slow)
    tts.write_to_fp(mp3_fp)
    return mp3_fp.getvalue()

def play_audio(audio_bytes):
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

# --- 세션 상태 초기화 ---
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

# --- 1단계: 문제 입력 화면 (SETUP) ---
if st.session_state.step == 'SETUP':
    st.title("✏️ 덕현초 2학년 1반 예쁜 전유하 받아쓰기 준비")
    st.write("공부할 문장을 입력하고, 읽기 속도를 선택해 주세요.")
    
    # [추가] 속도 선택 라디오 버튼
    st.session_state.speed = st.radio(
        "📢 읽기 속도를 선택하세요",
        ["보통", "느리게"],
        horizontal=True
    )
    
    input_text = st.text_area("문장 입력 (엔터로 구분)", 
                             placeholder="예:\n날씨가 맑아요.\n공책을 샀어요.",
                             height=200)
    
    if st.button("시험 시작하기 🚀"):
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        if len(lines) > 0:
            st.session_state.quiz_list = lines
            st.session_state.current_idx = 0
            st.session_state.last_played_idx = -1
            st.session_state.step = 'EXAM'
            st.rerun()
        else:
            st.warning("최소 한 문장 이상 입력해 주세요!")

# --- 2단계: 시험 진행 화면 (EXAM) ---
elif st.session_state.step == 'EXAM':
    idx = st.session_state.current_idx
    total = len(st.session_state.quiz_list)
    current_sentence = st.session_state.quiz_list[idx]
    
    # [수정] 음성 생성 시 저장된 속도 옵션을 함께 전달
    audio_data = generate_audio_bytes(current_sentence, st.session_state.speed)
    
    if st.session_state.last_played_idx != idx:
        play_audio(audio_data)
        st.session_state.last_played_idx = idx

    st.title(f"✍️ 제 {idx + 1}번 문제")
    st.write(f"⏱ 현재 모드: **{st.session_state.speed}**") # 현재 속도 표시
    st.progress((idx + 1) / total)
    
    if st.button("🔊 다시 들려주기"):
        play_audio(audio_data)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if idx > 0:
            if st.button("⬅️ 이전 문제로"):
                st.session_state.current_idx -= 1
                st.session_state.last_played_idx = -1 
                st.rerun()
    with col2:
        if idx < total - 1:
            if st.button("다음 문제로 ➡️"):
                st.session_state.current_idx += 1
                st.rerun()
        else:
            if st.button("시험 종료 및 결과 확인 🏁"):
                st.session_state.step = 'RESULT'
                st.rerun()

# --- 3단계: 결과 확인 화면 (RESULT) ---
elif st.session_state.step == 'RESULT':
    st.title("🎉 시험 끝! 정답을 확인해요")
    for i, q in enumerate(st.session_state.quiz_list):
        st.info(f"**{i+1}번:** {q}")
    
    if st.button("새로운 시험 준비하기 🔄"):
        st.session_state.step = 'SETUP'
        st.session_state.quiz_list = []
        st.session_state.last_played_idx = -1
        st.rerun()
