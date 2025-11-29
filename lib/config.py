"""Configuration for the recommendation system."""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Model selection
# Gemini 2.5 Flash Lite: 15 req/min, 1000 req/day (best free tier limits)
GENERATIVE_MODEL = "gemini-2.5-flash-lite"

# Business rules for product filtering
MIN_STOCK = 1
MIN_RATING_DEFAULT = 3.5

# LLM instance
llm = genai.GenerativeModel(GENERATIVE_MODEL)
