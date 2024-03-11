# app.py
import streamlit as st
import subprocess
import os
import openai

# OpenAIのAPIキーを変数で設定
CHATGPT_API_KEY = st.secrets["GPT_API"]
openai.api_key = CHATGPT_API_KEY

# システムプロンプトを設定
system_prompt = "あなたの仕事は、提供された会議メモを確認し、会議中に特定の個人または部門に割り当てられた主要な要点と実行項目に焦点を当てて、重要な情報をまとめた簡潔な要約を作成することです。明確で専門的な言葉を使用し、見出し、小見出し、箇条書きなどの適切な書式を使用して要約を論理的に整理します。概要は理解しやすく、会議の内容の包括的かつ簡潔な概要を提供するものにしてください。特に、各アクション項目の責任者を明確に示すことに重点を置きます。"

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

def summarize_text(text, context):
    prompt = f"{system_prompt}\n\n会議の内容:\n{context}\n\n音声認識結果:\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

st.title("リアルタイム議事録アプリ")

col1, col2 = st.columns(2)

with col1:
    start_button = st.button("開始")
    stop_button = st.button("終了")
    if os.path.exists("output.py"):
        from output import output
        new_texts = [text for timestamp, text in output if timestamp > st.session_state.get('last_timestamp', '')]
        if new_texts:
            st.session_state.last_timestamp = output[-1][0]  # Update the last timestamp
            text_area_content = st.session_state.get('text_area_content', '') + "\n".join(new_texts) + "\n"
            st.session_state.text_area_content = text_area_content
    else:
        text_area_content = ""

    st.text_area("音声認識結果", value=st.session_state.get('text_area_content', ''), height=300, key="text_area")
    context_area = st.text_area("会議の内容", height=200, key="context_area")

with col2:
    summarize_button = st.button("要約")
    if summarize_button:
        text_area_content = st.session_state.get('text_area_content', '')
        context = context_area
        summary = summarize_text(text_area_content, context)
        st.text_area("要約とネクストアクション", value=summary, height=500)

if start_button:
    if not st.session_state.get('process'):
        start_recognition()
        st.success("音声認識を開始しました。")
    else:
        st.warning("音声認識は既に実行中です。")

if stop_button:
    if st.session_state.get('process'):
        stop_recognition()
        st.success("音声認識を終了しました。")
    else:
        st.warning("音声認識は実行されていません。")

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