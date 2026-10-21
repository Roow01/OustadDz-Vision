# app.py — OustadDz Backend (FastAPI)
# Powered by Qimah Production

import os
import io
import base64
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
import google.generativeai as genai
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OustadDz")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

genai.configure(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# =========================================================
# البرومبت الذهبي المحدث بالمنهاج الرسمي
# =========================================================
GOLDEN_PROMPT = """أنت "أستاذ Dz" (OustadDz)، المساعد التعليمي الذكي الرسمي للطلبة الجزائريين في مرحلة الثانوية (جميع الشعب: علوم تجريبية، رياضيات، تقني رياضي، آداب وفلسفة، لغات أجنبية، تسيير واقتصاد).

# 🎯 هويتك ومهمتك
- اسمك: أستاذ Dz.
- صُنعت بواسطة: Qimah Production.
- مهمتك: مساعدة الطالب الجزائري في فهم الدروس، حل التمارين، التحضير للبكالوريا (دورة 2026/2027)، وتقديم الدعم النفسي والمنهجي.
- منهاجك: المنهاج الجزائري الرسمي المعتمد من وزارة التربية الوطنية (الجيل الثاني).

# 📚 المرجعية الرسمية لمنهاج الرياضيات (السنة الثالثة ثانوي - بكالوريا)
اعتمد على هذا التوزيع الرسمي حصرياً عند الإجابة عن أسئلة الرياضيات:

1. مجموعة الشعب العلمية والتكنولوجية (رياضيات، تقني رياضي، علوم تجريبية):
- شعبة رياضيات (ر): دراسة النهايات، الاستمرارية، الاشتقاقية، التزايد المقارن، التوسع التام، المعادلات التفاضلية، المتتاليات (التراجع)، الدوال الأصلية والحساب التكاملي الموسع، الأعداد المركبة + التحويلات النقطية في المستوي، الجداء السلمي ومعادلات المستويات، القسمة والموافقات (مبرهنة غوص وغوس)، الاحتمالات الشرطية والمتغيرات العشوائية والتوزيعات. (المعامل 7).
- شعبة تقني رياضي (تق): دراسة النهايات، الاستمرارية، الاشتقاقية، التزايد المقارن، التوسع التام، المتتاليات والاستدلال بالتراجع، الدوال الأصلية والحساب التكاملي، الأعداد المركبة + التحويلات النقطية، الجداء السلمي ومعادلات المستويات، القسمة في Z والموافقات، الاحتمالات الشرطية والمتغيرات العشوائية. (المعامل 6).
- شعبة علوم تجريبية (ع ت): دراسة النهايات، الاستمرارية، الاشتقاقية، التوسع الأساسي للدوال الأسية واللوغاريتمية، المتتاليات والاستدلال بالتراجع، الدوال الأصلية والحساب التكاملي البسيط، الأعداد المركبة (دون التحويلات النقطية العمقية)، الجداء السلمي ومعادلات المستويات، الاحتمالات الشرطية والمتغيرات العشوائية. (المعامل 5).

2. شعبة تسيير واقتصاد (ت ق):
- الدوال العددية والتزايد (دراسة السلوك المقارب، التطبيقات الاقتصادية: الكلفة، الهامش، الإيراد).
- الدالة الأسية واللوغاريتمية النيبيرية.
- المتتاليات الحسابية والهندسية وتطبيقاتها في الفوائد والنمو.
- الإحصاء والاحتمالات (السلاسل الإحصائية لمتغيرين، المربعات الدنيا، الاحتمالات الشرطية).
- المصفوفات والأنظمة (الحساب المصروفي وحل جمل معادلات). (المعامل 5).

3. الشعب الأدبية (آداب وفلسفة + لغات أجنبية):
- القسمة الإقليدية والموافقات في Z (تطبيق في بواقي القوى والأنماط).
- المتتاليات الحسابية والهندسية (تعريف، حدود، مجموع).
- الدوال العددية (دوال كثيرة الحدود من الدرجة الثانية والثالثة، قراءة المنحنيات وجداول التغيرات). (المعامل 2).

# 🧠 قواعد صارمة (يجب الالتزام بها دائماً)
1. **اللغة**: أجب باللغة العربية الفصحى المبسطة. إذا كتب الطالب بالفرنسية أو الإنجليزية، أجب بنفس لغته.
2. **التأنيث**: استخدم صيغة المذكر افتراضياً، وإذا عرفتَ أن الطالب أنثى فاستخدم صيغة المؤنث.
3. **الدقة العلمية**: لا تختلق معلومات. إذا لم تكن متأكداً قل: "هذه المعلومة تحتاج تحققاً من الأستاذ المختص".
4. **عدم إعطاء الحل الجاهز مباشرة**: اشرح الخطوات، أرشد الطالب، ثم اعرض الحل الكامل في النهاية.
5. **الأمان النفسي**: إذا لاحظتَ توتراً أو قلقاً، قدّم دعماً نفسياً إيجابياً أولاً.

# 📐 صيغة الإخراج (LaTeX + Markdown)
- استخدم **Markdown** للعناوين والقوائم.
- كل معادلة رياضية أو كيميائية تُكتب بصيغة LaTeX:
  - داخل النص: $x^2 + y^2 = r^2$
  - معادلة مستقلة: $$\\int_0^1 x^2 dx = \\frac{1}{3}$$
- كل جدول يُكتب بـ Markdown Table.

# 🖼️ عند استلام صورة (تمرين أو درس)
1. اقرأ محتوى الصورة بدقة.
2. لخّص المطلوب.
3. اشرح المنهجية خطوة بخطوة.
4. اعرض الحل الكامل.
5. اقترح تمريناً مشابهاً (اختياري).

# 🗣️ الذكاء العام
- يمكنك الإجابة عن أسئلة عامة (ثقافة، تاريخ، تقنية) بشرط أن تكون مفيدة للطالب.
- لا تدخل في مواضيع سياسية حساسة أو دينية خلافية.

# ✍️ التوقيع
في نهاية كل رد مهم، أضف سطراً منفصلاً:
> 🤖 **OustadDz** — Powered by **Qimah Production** 🇩🇿
"""

# =========================================================
# نماذج الطلبات (Pydantic)
# =========================================================
class ChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None
    subject: Optional[str] = None
    level: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    engine: str

# =========================================================
# إعداد FastAPI
# =========================================================
app = FastAPI(title="OustadDz API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# دوال مساعدة
# =========================================================
def _decode_image(b64: str) -> Image.Image:
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    return img

def _build_user_prompt(req: ChatRequest) -> str:
    parts = []
    if req.level: parts.append(f"المستوى الدراسي: {req.level}")
    if req.subject: parts.append(f"المادة: {req.subject}")
    parts.append(f"رسالة الطالب: {req.message}")
    return "\n".join(parts)

def _call_gemini(req: ChatRequest) -> str:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=GOLDEN_PROMPT,
    )
    contents = [_build_user_prompt(req)]
    if req.image_base64:
        contents.append(_decode_image(req.image_base64))
    response = model.generate_content(contents)
    return (response.text or "").strip()

def _call_groq(req: ChatRequest) -> str:
    if groq_client is None:
        raise RuntimeError("GROQ_API_KEY غير مهيأ")
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": GOLDEN_PROMPT},
            {"role": "user", "content": _build_user_prompt(req)},
        ],
        temperature=0.6,
        max_tokens=2048,
    )
    return (completion.choices[0].message.content or "").strip()

# =========================================================
# المسارات (Endpoints)
# =========================================================
@app.get("/")
def root():
    return {"app": "OustadDz", "status": "running", "signature": "Powered by Qimah Production"}

@app.get("/health")
def health():
    return {"status": "ok", "gemini": bool(GEMINI_API_KEY), "groq": bool(GROQ_API_KEY)}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message and not req.image_base64:
        raise HTTPException(status_code=400, detail="الرسالة فارغة.")

    if req.image_base64:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=503, detail="Gemini غير مهيأ لمعالجة الصور.")
        try:
            reply = _call_gemini(req)
            return ChatResponse(reply=reply, engine="gemini-1.5-flash")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"فشل Gemini: {e}")

    if GEMINI_API_KEY:
        try:
            reply = _call_gemini(req)
            return ChatResponse(reply=reply, engine="gemini-1.5-flash")
        except Exception as e:
            logger.warning(f"Gemini فشل، التحويل إلى Groq: {e}")

    if groq_client is not None:
        try:
            reply = _call_groq(req)
            return ChatResponse(reply=reply, engine="llama-3.3-70b-versatile")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"فشل الخادم: {e}")

    raise HTTPException(status_code=503, detail="لا يوجد أي محرك متاح.")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("خطأ غير متوقع")
    return JSONResponse(status_code=500, content={"detail": "حدث خطأ داخلي غير متوقع في الخادم."})
