from google import genai
from PIL import Image
import time

# API Key ကို သေချာစစ်ပြီး ထည့်ပါ
client = genai.Client(api_key="AIzaSyAMq2vZL_wdHgc_plDfxBiQHMoVj125Jyk")

def final_test():
    try:
        # မင်းရဲ့ Giant Receipt ပုံလမ်းကြောင်း
        img = Image.open("receipt.jpg")
        
        print("AI က စတင်ဖတ်နေပါပြီ... (စက္ကန့် ၃၀ ခန့် ကြာနိုင်ပါတယ်)")
        
        # Quota သက်သာတဲ့ Lite Model ကို သုံးမယ်
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["What is the total balance on this receipt? Return number only.", img]
        )
        
        if response.text:
            print("-" * 30)
            print(f"✅ Giant Receipt Total: {response.text}")
            print("-" * 30)
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ၃ မိနစ်ခြားပြီး ၂ ကြိမ် စမ်းကြည့်မယ်
for attempt in range(2):
    if final_test():
        break
    else:
        if attempt == 0:
            print("Quota ပြည့်နေပုံရပါတယ်။ ၃ မိနစ် အတိအကျ စောင့်ပြီး ပြန်စမ်းပါမယ်...")
            time.sleep(180) # ၁၈၀ စက္ကန့် စောင့်ခြင်း