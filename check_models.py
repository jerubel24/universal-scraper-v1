from google import genai

API_KEY = "AIzaSyDTpPp1e9JYhgR9mAZ5cg7POAXJoKof3PU"
client = genai.Client(api_key=API_KEY)

print("🔍 Checking available models for your API key...")

try:
    # This pulls every model your key is allowed to use
    models = client.models.list()
    print("\n✅ SUCCESS! Here are your available models:")
    for model in models:
        # We only care about models that can 'generateContent'
        if 'generateContent' in model.supported_methods:
            print(f" - {model.name}")
            
except Exception as e:
    print(f"\n❌ ERROR: Could not list models. {e}")