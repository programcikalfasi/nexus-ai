import google.generativeai as genai
import os

# The key user provided earlier
TEST_KEY = "AIzaSyA-NWT__3ptiomnXi1k8SRQpDngSa5lpwA"

def test_key():
    print(f"Testing API Key: {TEST_KEY[:10]}...")
    
    genai.configure(api_key=TEST_KEY)
    
    # List available models to see what this key can access
    print("\nListing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\nAttempting generation with gemini-1.5-flash...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, are you working?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error generating content: {e}")

if __name__ == "__main__":
    test_key()
