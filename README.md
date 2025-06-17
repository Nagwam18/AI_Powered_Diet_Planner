# 🥗 Smart AI Diet Assistant

Welcome to the **Smart AI Diet Assistant**!
This application helps you achieve a healthier lifestyle through AI-powered meal planning, commitment tracking, and motivational support.

---

## ✨ Key Features

* **Personalized Meal Planning**
  Custom meal plans based on your personal data (weight, height, age, gender, activity level), goals (loss, gain, maintenance), and preferences (diet type, allergies, medical conditions).
* **Commitment Tracking**
  Compare planned meals with actual intake and view progress in a Pie Chart.
* **Motivational Support**
  Receive AI-generated messages and tips to stay on track.
* **Comprehensive HTML Report**
  Download a full report covering your plan, commitment evaluation, and insights.

---

## 🚀 Technologies Used

| Tool                          | Purpose                    |
| ----------------------------- | -------------------------- |
| **Python**                    | Core language              |
| **Dash**                      | Web app framework          |
| **Dash Bootstrap Components** | Responsive UI components   |
| **CrewAI**                    | Multi-agent orchestration  |
| **Google Gemini API**         | LLM for content generation |
| **python-dotenv**             | Environment variables      |
| **Plotly**                    | Interactive charts         |
| **Pandas**                    | Data handling              |
| **Gunicorn**                  | Production WSGI server     |

---

## ⚙️ Setup & Local Execution

### Prerequisites

* Python 3.9+
* `pip` (Python package manager)

### Steps

1. **Clone the repository**

   ```bash
   git clone <your-github-repo-url>
   cd Diet_planner
   ```
2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   # venv\Scripts\activate     # Windows
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Set your Gemini API key**

   ```env
   # .env  (in project root)
   GEMINI_API_KEY=your_actual_key_here
   ```
5. **Run the app locally**

   ```bash
   gunicorn app:server -b 0.0.0.0:8050
   # then open http://127.0.0.1:8050
   ```

---

## 👩‍💻 Run in Google Colab (Optional)

1. Upload the project folder to Google Drive.
2. Mount Drive in Colab:

   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
3. Install requirements:

   ```bash
   !pip install -r /content/drive/MyDrive/Diet_planner/requirements.txt
   !pip install pyngrok
   ```
4. Uncomment the Colab block in `app.py` and run:

   ```python
   # inside app.py
   if __name__ == '__main__':
       port = 8050
       from pyngrok import ngrok
       tunnel = ngrok.connect(port)
       print('Public URL:', tunnel.public_url)
       app.run_server(host='0.0.0.0', port=port)
   ```

---

## ☁️ Deployment on Hugging Face Spaces

### Required Structure

```text
Diet_planner/
├── app.py               # Dash application
├── requirements.txt     # Python dependencies
├── huggingface.yaml     # Hugging Face config
├── .env                 # Not committed (use HF secrets)
├── agents/              # CrewAI agents
│   ├── __init__.py
│   ├── meal_planner_agent.py
│   ├── tracker_agent.py
│   └── motivation_agent.py
├── assets/              # Static files (CSS, images)
│   ├── style.css
│   └── background.jpg
└── .gitignore
```

### `huggingface.yaml`

```yaml
sdk: gradio
python_version: 3.9
app_file: app.py
```

### `requirements.txt`

```txt
dash
dash-bootstrap-components
Flask
gunicorn
python-dotenv
crewai
pydantic>=2.0.0
agentops
requests
google-generativeai
langchain-google-genai
plotly
pandas
fpdf2
```

### Final lines in `app.py`

```python
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=7860)
```

### Deployment Steps

1. Push the project to GitHub.
2. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
3. Click **Create New Space** → choose `Gradio` as SDK.
4. Link your GitHub repo.
5. Add `GEMINI_API_KEY` as a secret in HF settings.
6. Wait for build → your app is live!

---

## 📝 Notes

* **Localization**: The UI and reports are in Arabic.
* **Security**: Do **not** commit `.env`; use HF Secrets instead.
* **API Quotas**: Monitor Gemini usage to avoid overages.

---

> *Built with love, Dash, and plenty of healthy snacks!*
