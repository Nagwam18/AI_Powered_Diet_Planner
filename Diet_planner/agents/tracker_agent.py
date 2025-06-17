from crewai import Agent, Task
from crewai.llm import LLM
from dotenv import load_dotenv
import os

load_dotenv()

tracker_agent = Agent(
    role="متابع خطة التغذية",
    goal="تقييم مدى التزام المستخدم بالخطة الغذائية اليومية بشكل رقمي فقط بدون تقديم توصيات إضافية أو نصائح.",
    backstory="خبير تحليل تغذية يقوم بمقارنة الخطة الغذائية المقترحة بما تناوله المستخدم فعليًا لحساب نسبة الالتزام فقط.",
    verbose=True,
    allow_delegation=False,
    llm=LLM(
        model="gemini/gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )
)

track_progress_task = Task(
    description=(
        "قارن بين الخطة الغذائية المقترحة للمستخدم (تشمل الوجبات والمكونات فقط) "
        "وما تم تناوله فعليًا خلال اليوم. احسب نسبة الالتزام كنسبة مئوية دقيقة (مثلاً: 80%).\n"
        "- لا تقدم أي توصيات أو نصائح أو تحفيز.\n"
        "- أخرج النسبة في سطر واحد فقط، متبوعًا بإيموجي يعكس مستوى الالتزام:\n"
        "  🟢🔥 إذا كانت النسبة 85% أو أكثر\n"
        "  🟡👍 إذا كانت بين 70% و84%\n"
        "  🟠⚠️ إذا كانت بين 50% و69%\n"
        "  🔴❌ إذا كانت أقل من 50%\n\n"
        "الخطة الغذائية المقترحة:\n"
        "{{planned_meal}}\n\n"
        "ما تم تناوله فعليًا:\n"
        "{{eaten_meal}}\n\n"
        "العوامل الخارجية:\n"
        "{{external_factors}}"
    ),
    expected_output="سطر واحد فقط يحتوي على النسبة المئوية + الإيموجي المناسب بدون شرح أو تعليق.",
    agent=tracker_agent,
    inputs=["planned_meal", "eaten_meal", "external_factors"]
)
