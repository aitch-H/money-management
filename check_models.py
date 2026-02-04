from google import genai

# API Key
client = genai.Client(api_key="AIzaSyBIwC2MN6mIRhmRvPHJwhTQ9ZRnIrelXkM")

print("--- မင်းရဲ့ Key နဲ့ အလုပ်လုပ်တဲ့ Model စာရင်း ---")
try:
    # နာမည်သက်သက်ပဲ အရင်ထုတ်ကြည့်မယ်
    for m in client.models.list():
        print(f"Model Name: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")