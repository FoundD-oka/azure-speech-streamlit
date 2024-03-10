# app.py
import streamlit as st
import subprocess
import os

def start_recognition():
    global process
    if os.path.exists("output.py"):
        os.remove("output.py")
    with open("output.py", "w") as f:
        f.write("output = []\n")
    process = subprocess.Popen(["python", "s2t.py"])

def stop_recognition():
    global process
    if process:
        with open("stop_flag", "w") as f:
            f.write("stop")
        process.wait()
        process = None

st.title("リアルタイム議事録アプリ")

if "process" not in st.session_state:
    st.session_state.process = None
    st.session_state.last_timestamp = ""

start_button = st.button("開始")
stop_button = st.button("終了")

if start_button:
    if not st.session_state.process:
        start_recognition()
        st.success("音声認識を開始しました。")
    else:
        st.warning("音声認識は既に実行中です。")

if stop_button:
    if st.session_state.process:
        stop_recognition()
        st.success("音声認識を終了しました。")
    else:
        st.warning("音声認識は実行されていません。")

if os.path.exists("output.py"):
    from output import output
    new_texts = [text for timestamp, text in output if timestamp > st.session_state.last_timestamp]
    if new_texts:
        st.session_state.last_timestamp = output[-1][0]  # Update the last timestamp
        text_area_content = st.session_state.get('text_area_content', '') + "\n".join(new_texts) + "\n"
        st.session_state.text_area_content = text_area_content
else:
    text_area_content = ""

with st.form(key='text_area_form', clear_on_submit=True):
    st.text_area("認識結果", value=st.session_state.get('text_area_content', ''), height=300, key="text_area")
    submitted = st.form_submit_button(label='更新')

# テキストエリアを最下部にスクロールするためのJavaScriptコード
scroll_script = """
<script>
window.addEventListener('load', function() {
    var textArea = document.querySelector('.stTextArea textarea');
    textArea.scrollTop = textArea.scrollHeight;
});
</script>
"""

# JavaScriptコードをレンダリング
st.components.v1.html(scroll_script, height=0)