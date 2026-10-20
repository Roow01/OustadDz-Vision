import os
import gradio as gr
from google import genai
from google.genai import types
import requests

# المفاتيح من إعدادات Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# رابط الصورة (شعار Qimah Production)
BOT_AVATAR_PATH = "https://raw.githubusercontent.com/Roow01/OustadDz/main/Gemini_Generated_Image_9ccjp9ccjp9ccjp9.jpeg"

prompt = """
أنت أستاذ الرياضيات الافتراضي (OustadDz). أنت مساعد ذكي، مدرب، ومرافق تربوي محترف لتلاميذ السنة الثالثة ثانوي في الجزائر (الموسم الدراسي 2026/2027).

[القواعد الصارمة - التزم بها حرفياً]:

1. قفل الهوية والتحية (مرة واحدة فقط):
- أنت أستاذ رياضيات فقط. يُمنع منعاً باتاً ذكر أي مادة أخرى (فيزياء، فلسفة، لغات). إذا سألك التلميذ عن مادة أخرى، اعتذر بلطف وقل أنا متخصص في الرياضيات فقط.
- في أول رسالة فقط، رحب بالتلميذ واطلب اسمه وشعبته.
- يُمنع منعاً باتاً سؤال التلميذ عن اسمه أو جنسه أو شعبته مرة أخرى.

2. الذكاء السلوكي (التذكير والتأنيث):
- إذا كان الاسم مؤنثاً (نسرين، مريم، سارة، مروة...) أو صرحت بذلك، خاطبها بصيغة المؤنث (أهلاً بكِ، مساعدتِك، فهمتِ، أحسنتِ، تريدين).

3. المرونة اللغوية:
- اكتشف لغة التلميذ (عربية، دارجة، فرنسية، إنجليزية) ورد بنفسها.

4. البيداغوجيا والبروتوكول التدريبي (Coaching):
- اشرح المفهوم بتبسيط، أعطِ مثالاً محلولاً خطوة بخطوة، ثم اطرح سؤالاً قصيراً للتأكد من الفهم.
- إذا أخطأ التلميذ، وجهه بلطف ليكتشف الخطأ بنفسه.

5. التصميم البصري للشرح (مهم جداً):
- استخدم العناوين البارزة (مثل ###) لتقسيم الدروس.
- استخدم الرموز التعبيرية (📌، 📊، ⚠️، ✅) لتوضيح النقاط.
- ضع القواعد الهامة داخل صناديق مميزة باستخدام علامة (>) (Blockquote).

6. التدرج السنوي الرسمي (2026/2027):
- الشعب العلمية: المتتاليات، الاستمرارية والاشتقاقية، النهايات، الدوال الأسية واللوغاريتمية، الدوال الأصلية والتكامل، الأعداد المركبة (مع التحويلات لرياضيات وتقني)، الهندسة، الحساب (القسمة والموافقات)، الإحصاء والاحتمالات.
- تسيير واقتصاد: المتتاليات، الاشتقاقية والاستمرارية، النهايات، الدوال، الدوال الأصلية والتكامل، الإحصاء، الاحتمالات.
- آداب وفلسفة: القسمة الإقليدية والموافقات، المتتاليات الحسابية والهندسية، الدوال العددية (درجة 2 و 3)، الإحصاء.

7. الانتقال المباشر للشرح:
- إذا طلب التلميذ درساً، اذكر عنوانه ومحتواه فوراً.
- إذا طلب "الدرس الأول": (علمي: المتتاليات العددية) | (تسيير: المتتاليات) | (آداب: القسمة والموافقات).

8. القيود العلمية الصارمة:
- يُمنع منعاً باتاً استخدام قاعدة لوبيتال (L'Hôpital).
- استخدم تنسيق LaTeX لكتابة المعادلات الرياضية.

9. مراجعة البكالوريا:
- اطرح تمارين من مواضيع البكالوريا السابقة، وانتظر الحل، ثم صحح خطوة بخطوة.

10. الدعم النفسي التربوي:
- إذا لاحظت توتراً، توقف فوراً، طمئنه بأسلوب أبوي حنون، وقدم له نصائح للتهدئة.

11. تحليل الصور:
- إذا أرسل التلميذ صورة لتمرين، قم بتحليلها بعناية واشرح الخطوات بالتفصيل.
"""

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    client = None

def call_gemini(contents, system_instruction):
    if not client: return None
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.2)
        )
        return response.text if response.text else None
    except Exception as e:
        return None

def call_groq(contents, system_instruction):
    if not GROQ_API_KEY: return None
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": contents}],
            "temperature": 0.2
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return None
    except Exception as e:
        return None

def chat_response(message, history):
    try:
        # معالجة الرسائل المتعددة (نص + صورة)
        if isinstance(message, dict):
            text_content = message.get("text", "")
            files = message.get("files", [])
            
            if files:
                # إرسال الصورة إلى Gemini للتحليل
                image_path = files[0]
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[
                        types.Part.from_text(text_content if text_content else "حلل هذه الصورة الرياضية واشرحها لي."),
                        types.Part.from_image(image_path)
                    ],
                    config=types.GenerateContentConfig(system_instruction=prompt, temperature=0.2)
                )
                return response.text if response.text else "عذراً، لم أتمكن من تحليل الصورة."
            else:
                message = text_content # إذا كان نصاً فقط

        if len(history) == 0:
            welcome_msg = "أهلاً بك! أنا أستاذك المساعد الافتراضي في الرياضيات للثالثة ثانوي. تفضل، قول لي وش هو اسمك وش هي شعبتك باش ننطلقوا؟"
            return welcome_msg

        conversation_context = ""
        for item in history:
            if isinstance(item, dict):
                role = item.get("role", "user")
                content = item.get("content", "")
                if role == "user":
                    conversation_context += f"Student: {content}\n"
                elif role == "assistant":
                    conversation_context += f"OustadDz: {content}\n"
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                user_msg, bot_msg = item
                conversation_context += f"Student: {user_msg}\nOustadDz: {bot_msg}\n"
        
        conversation_context += f"Student: {message}\nOustadDz:"

        res = call_gemini(conversation_context, prompt)
        if res: return res
        
        res = call_groq(conversation_context, prompt)
        if res: return res

        return "عذراً، الخوادم مشغولة حالياً. يرجى المحاولة بعد قليل."
    
    except Exception as e:
        return "حدث خطأ غير متوقع. يرجى المحاولة."

# ✅ التصميم المريح للعين
custom_css = """
footer {visibility: hidden !important;}
body, .gradio-container { background-color: #ffffff !important; }
.message-wrap .message { 
    font-size: 17px !important; 
    line-height: 1.8 !important; 
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin-bottom: 15px !important;
}
.message-wrap .message.user { 
    background-color: #e3f2fd !important; 
    color: #000 !important;
}
.message-wrap .message.bot { 
    background-color: #f7f7f7 !important; 
    color: #000 !important;
    border: 1px solid #e0e0e0 !important;
}
textarea {
    border-radius: 12px !important;
    border: 2px solid #d0d0d0 !important;
    padding: 15px !important;
    font-size: 16px !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
}
.katex-display { font-size: 1.2em !important; margin: 15px 0 !important; }
"""

# ✅ استخدام MultimodalTextbox لدعم الصور
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.ChatInterface(
        fn=chat_response,
        title="OustadDz - أستاذ الرياضيات",
        description="أهلاً بك! أنا أستاذك المساعد الافتراضي. تفضل، قول لي وش هو اسمك وش هي شعبتك باش ننطلقوا؟",
        multimodal=True,
        textbox=gr.MultimodalTextbox(placeholder="اكتب سؤالك أو أرفق صورة لتمرين...", file_types=["image"]),
        chatbot=gr.Chatbot(
            avatar_images=(None, BOT_AVATAR_PATH),
            latex_delimiters=[
                {"left": "$$", "right": "$$", "display": True},
                {"left": "$", "right": "$", "display": False}
            ]
        )
    )
    gr.HTML("<div translate='no' style='text-align: center; margin-top: 20px; font-weight: bold; color: #666; font-size: 15px;'>Built by Mana Redouane | Vision v1.0</div>")

demo.queue().launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)), pwa=True)
