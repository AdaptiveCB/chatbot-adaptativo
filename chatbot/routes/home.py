from flask import redirect
from chatbot import app, mongo

@app.route('/')
def home():
  return redirect("https://mitsuoysharag.github.io/TesisChatbotDocente_Vue")
