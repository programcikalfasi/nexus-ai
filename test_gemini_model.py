import google.generativeai as genai
import os

TEST_KEY = "AIzaSyA-NWT__3ptiomnXi1k8SRQpDngSa5lpwA"

def test_key():
    genai.configure(api_key=TEST_KEY)
    
    print("\nAttempting generation with gemini-2.0-flash...")
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello!")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with 2.0-flash: {e}")
        
        print("\nAttempting generation with gemini-flash-latest...")
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content("Hello!")
            print(f"Success! Response: {response.text}")
        except Exception as e:
            print(f"Error with flash-latest: {e}")

if __name__ == "__main__":
    test_key()
