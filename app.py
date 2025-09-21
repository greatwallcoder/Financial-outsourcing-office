# app.py — شات + رفع صورة بدل PDF
import streamlit as st
from openai import OpenAI
import base64, os

st.set_page_config(page_title="FOO", page_icon='🏗', layout="wide")

# ==== مفتاح OpenAI ====

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

st.title("Financial outsourcing office 🏗")
st.caption("ارفع مخطط كصورة (PNG/JPG/WEBP) واسأل سؤالك. سنرسل الصورة مع الرسالة للمودل.")

# ===== 1) رفع صورة =====
img = st.file_uploader("ارفع صورة للمخطط", type=["png", "jpg", "jpeg", "webp"])

# عرض المحادثة السابقة
if "history" not in st.session_state:
    st.session_state.history = []
for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

user_msg = st.chat_input("اكتب سؤالك (مثال: قدّر تكلفة المشروع من المخطط المرفق)")
if user_msg:
    st.session_state.history.append(("user", user_msg))
    with st.chat_message("user"):
        st.markdown(user_msg)

    with st.chat_message("assistant"):
        if not img:
            st.warning("ارفع صورة أولاً ثم أرسل سؤالك.")
        else:
            with st.spinner("جارٍ الإرسال لـ OpenAI…"):
                try:
                    # حوّل الصورة إلى data URL (base64) لإرسالها مباشرة
                    mime = {
                        "png": "image/png",
                        "jpg": "image/jpeg",
                        "jpeg": "image/jpeg",
                        "webp": "image/webp",
                    }[img.name.split(".")[-1].lower()]
                    b64 = base64.b64encode(img.read()).decode("utf-8")
                    data_url = f"data:{mime};base64,{b64}"

                    system_hint = (
                        "أنت مهندس كميات سعودي. حلّل صورة المخطط المرفوعة وأعطِ تقديراً تقريبياً "
                        "للتكلفة على البنود الرئيسية (هيكل، معماري، كهرباء، ميكانيكا) مع افتراضات مختصرة. "
                        "رد بالعربية المختصرة."
                    )

                    resp = client.responses.create(
                        model="gpt-5",  # أو gpt-4.1-mini
                        input=[{
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": f"{system_hint}\n\nسؤال المستخدم: {user_msg}"},
                                {"type": "input_image", "image_url": data_url},
                            ],
                        }],
                    )

                    answer = getattr(resp, "output_text", None) or "ما وصل نص رد."
                    st.session_state.history.append(("assistant", answer))
                    st.markdown(answer)
                except Exception as e:
                    st.error(f"تعذّر الحصول على رد: {e}")

st.caption("⚠️ ملاحظة: قراءة التفاصيل من الصور قد تكون محدودة؛ النتائج تقديرية وليست عرض سعر ملزم.")


