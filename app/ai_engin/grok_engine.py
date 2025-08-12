import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GroqInterface:
    def __init__(self, model="llama3-70b-8192", temperature=0.7, max_tokens=1024, live=True):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.live = live
        self.chat_history = []  # Multi-turn chat context

    def send_prompt(self, prompt):
        if not self.live:
            print("[!] Simulated mode: returning test response.")
            return "Simulated LLM response."

        # Add user input to chat history
        self.chat_history.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            reply = response.choices[0].message.content
            # Append assistant reply to history
            self.chat_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"[Error]: {str(e)}"

    def reset(self):
        """Clear chat history."""
        self.chat_history = []

    def set_model(self, model_name):
        self.model = model_name

    def toggle_live(self, live_mode: bool):
        """Enable or disable live API usage."""
        self.live = live_mode
