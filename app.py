# 必要な部品を呼び出します
import streamlit as st
import google.generativeai as genai
import os
from gtts import gTTS
import io
from PIL import Image

# --- ページ設定 (一番最初に書く) ---
st.set_page_config(
    page_title="AIおはなしクリエーター",
    page_icon="🤖",
    layout="centered"
)

# あなたのAPIキーを設定
# このキーはサンプルです。ご自身のキーに置き換えてください。
YOUR_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=YOUR_API_KEY)


# --- サイドバー (入力部分) ---
st.sidebar.title("おはなしの設定 📝")
name = st.sidebar.text_input("きみのなまえは？")
favorite_thing = st.sidebar.text_input("すきなもの（たべもの、おもちゃ、どうぶつなど）はなに？")

# 新機能：テーマを選択
theme = st.sidebar.selectbox(
    "どんなおはなしにする？",
    ("わくわくする冒険", "心あたたまる友情", "ちょっとふしぎな話", "面白いコメディ")
)

# 新機能：物語の長さを選択
length = st.sidebar.slider(
    "おはなしの長さ (文字数)",
    min_value=100,
    max_value=500,
    value=300
)


# --- メイン画面 (出力部分) ---

st.title("AIおはなしクリエーター 🤖📚")
st.write("左のサイドバーで設定して、「おはなしをつくる！」ボタンを押してね！")

if st.sidebar.button("おはなしをつくる！"):
    if name and favorite_thing:
        # プロンプトを新しい設定に合わせて変更
        story_prompt = f"""
        あなたは優しくて想像力豊かな童話作家です。
        以下の情報とルールに従って、子供が楽しめる物語を作ってください。

        # 主人公の情報
        - なまえ: {name}
        - すきなもの: {favorite_thing}
        
        # 物語のルール
        - テーマ: {theme}
        - 文字数: 約{length}文字
        - 物語は必ず主人公の{name}が活躍するようにしてください。
        - {name}の好きなものである「{favorite_thing}」を物語の中で重要なアイテムとして登場させてください。
        - 子供が理解できるように、ひらがなを多く、簡単な言葉で書いてください。
        - 最後に「おしまい」と書いてください。
        """

        with st.spinner(f"{name}ちゃんのおはなしを考えているよ..."):
            # テキストと画像を生成
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(story_prompt)
            story_text = response.text
            
            # 画像生成
            image_prompt = f"A cute children's book illustration in a watercolor style. The scene is about '{theme}'. It features a character named {name} and their favorite thing, {favorite_thing}."
            image_response = model.generate_content(image_prompt)

            # 画面に表示
            st.balloons() 
            st.divider()
            st.header(f"✨ {theme}のおはなし ✨")
            
            # 画像表示
            try:
                img_part = image_response.parts[0]
                img_data = img_part.blob.data
                image = Image.open(io.BytesIO(img_data))
                st.image(image)
            except Exception as e:
                st.warning("今回は、さし絵をうまく描けなかったみたい…")

            # 音声生成と表示
            try:
                tts = gTTS(text=story_text, lang='ja')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3', start_time=0)
            except Exception as e:
                st.warning("音声の作成中にエラーが起きました。")

            # 物語のテキスト表示
            st.write(story_text)
    else:
        st.sidebar.error("なまえとすきなものの両方を入力してね！")
