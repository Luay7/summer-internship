import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# تحميل المفتاح من ملف .env الموجود في المجلد الرئيسي
load_dotenv() 
api_key = os.getenv("GEMINI_API_KEY")

# تشغيل العميل بأمان
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='أهلاً جمناي، أنا لؤي وهذا أول سكربت مؤمن ومرتب بالكامل في المشروع الجديد.',
    config=types.GenerateContentConfig(temperature=0.7)
)

print(response.text)