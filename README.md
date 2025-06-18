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

## 📝 Notes

* **Localization**: The UI and reports are in Arabic.
* **Security**: Do **not** commit `.env`; use HF Secrets instead.
* **API Quotas**: Monitor Gemini usage to avoid overages.

---

> *Built with love, Dash, and plenty of healthy snacks!*
