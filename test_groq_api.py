import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def test_groq_api():
    """Test if Groq API key is working"""
    
    print("🔑 Testing Groq API Key...")
    print(f"API Key: {GROQ_API_KEY[:20]}...{GROQ_API_KEY[-10:] if GROQ_API_KEY else 'NOT FOUND'}")
    print("-" * 50)
    
    if not GROQ_API_KEY:
        print("❌ ERROR: GROQ_API_KEY not found in environment variables!")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": "Hello! Please respond with 'API is working correctly' if you can see this message."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        print("📡 Sending test request to Groq API...")
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data["choices"][0]["message"]["content"]
            
            print("✅ SUCCESS: Groq API is working!")
            print(f"🤖 AI Response: {ai_response}")
            return True
        
        elif response.status_code == 401:
            print("❌ ERROR: Invalid API key (401 Unauthorized)")
            print("💡 Please check if your API key is correct")
            return False
        
        elif response.status_code == 429:
            print("⚠️ WARNING: Rate limit exceeded (429)")
            print("💡 Please wait a moment and try again")
            return False
        
        else:
            print(f"❌ ERROR: API request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
        print("💡 Please check your internet connection")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Connection failed")
        print("💡 Please check your internet connection")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: Unexpected error occurred: {e}")
        return False

def get_new_api_key_instructions():
    """Provide instructions for getting a new API key"""
    print("\n" + "="*60)
    print("🔑 HOW TO GET A NEW GROQ API KEY:")
    print("="*60)
    print("1. Visit: https://console.groq.com/")
    print("2. Sign up or log in to your account")
    print("3. Go to 'API Keys' section")
    print("4. Click 'Create API Key'")
    print("5. Copy the generated key")
    print("6. Replace the key in your .env file")
    print("\n💡 Note: Groq API is free with generous limits!")
    print("="*60)

def check_env_file():
    """Check if .env file exists and has the correct format"""
    print("\n🔍 Checking .env file...")
    
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        with open('.env', 'r') as f:
            content = f.read()
            
        print("📄 .env file content:")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        if 'GROQ_API_KEY=' in content:
            print("✅ GROQ_API_KEY found in .env file")
        else:
            print("❌ GROQ_API_KEY not found in .env file")
            print("💡 Make sure your .env file contains: GROQ_API_KEY=your_key_here")
    else:
        print("❌ .env file not found")
        print("💡 Create a .env file with: GROQ_API_KEY=your_key_here")

if __name__ == "__main__":
    print("🚀 GROQ API KEY TESTER")
    print("="*60)
    
    # Check .env file
    check_env_file()
    
    # Test API
    api_working = test_groq_api()
    
    if not api_working:
        get_new_api_key_instructions()
    
    print("\n" + "="*60)
    print("🏁 Test completed!")
    print("="*60)
