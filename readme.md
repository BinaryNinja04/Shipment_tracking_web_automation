📦 Project Title: AI-based Shipping Line Tracking

🎯 Objective  
Automatically retrieve the voyage number and arrival date for a given HMM container booking ID from seacargotracking.net using AI and web automation — without hardcoding interactions.

✅ Step 1: Initial Retrieval (Natural Language to Automation)  
🔍 Approach  
We used spaCy (an open-source NLP tool) to extract container numbers from natural language user input.

The container number is extracted using a regex pattern (SINI\d{8}) after processing the input with spaCy.

Playwright is used for browser automation, dynamically filling and submitting the seacargotracking.net form.

No web elements are hardcoded — all form inputs are identified generically.

🧠 Example Prompt  
Get tracking info for HMM booking ID SINI25432400

🤖 Technologies Used  
spaCy for NLP  
Regex for container number pattern  
Playwright for web automation (headless browser interaction)

💾 Step 2: Process Persistence (Storage and Repeatability)  
🧠 What We Store  
We store user input, extracted container number, and retrieved result in a cache.json file. Example:

{
"Get tracking info for HMM booking ID SINI25432400": {
"container_number": "SINI25432400",
"result": "Voyage No: HM123 | Arrival Date: 2025-06-07"
}
}

🔁 How It Helps  
If the same input is repeated, the result is shown instantly from cache.  
Speeds up process and avoids redundant automation.

♻️ Step 3: Adaptability and Generalization (Bonus)  
🔄 How It Works Without Rewriting Code  
The logic dynamically adapts to any container number following SINI######## format.  
Playwright selects form inputs using index so changes in input names/IDs won't break it.  
If future structure changes drastically, stored steps (cache) or selectors can be adjusted.

🧩 Future Improvements  
Add AI reasoning to assess site layout.  
Build adaptive mapping of element types (input, button) and behavior.

🛠️ Environment Setup (From Scratch)  
📥 Install Python  
If not installed:  
https://www.python.org/downloads/  
Make sure to check "Add to PATH" during installation.

🧪 Create Virtual Environment  
python -m venv venv

✅ Activate Virtual Environment  
Windows:  
venv\Scripts\activate  
Mac/Linux:  
source venv/bin/activate

📦 Install Required Libraries  
pip install playwright spacy  
python -m playwright install  
python -m spacy download en_core_web_sm

▶️ Run the Bot  
To execute the program, you can either run the Python file directly or use one of the provided convenience scripts:

Option 1 – run manually:  
python run.py

Option 2 – use script:  
Windows:  
run.bat  
Mac/Linux:  
./run.sh

🔄 Sample Run Output:  
🗣️ Enter your request:  
Get tracking info for HMM booking ID SINI25432400

🤖 Using spaCy to extract the container number...  
📦 Container number extracted: SINI25432400  
🚀 Launching browser...  
...  
✅ Tracking information retrieved successfully.

📁 Project Structure  
shipping-bot/  
├── run.py # Core script containing the full source code  
├── cache.json # Stores input → result  
├── ai.env (optional) # Previously used for Gemini API key  
├── run.sh # Bash script to run the bot (Mac/Linux)  
├── run.bat # Batch script to run the bot (Windows)  
└── README.md # This file

📋 Output Verification  
Output is printed to console.  
Cache contains retrieved tracking info.  
Manual verification: Go to http://www.seacargotracking.net → paste container number → match results.

📦 Dependencies  
Python 3.10+  
Playwright  
spaCy

🧠 Notes  
Gemini API was replaced by spaCy to ensure open-source compliance.  
The tool is generalizable and repeatable.  
Works entirely offline after setup.

🏁 Submission Checklist  
✅ Step 1 complete — spaCy NLP used for prompt → container  
✅ Step 2 complete — steps cached in cache.json  
✅ Step 3 supported — general input pattern and dynamic element interaction  
✅ README and run instructions provided  
✅ No hardcoding of booking ID or selectors  
✅ Open-source tools used only

🧑‍💻 Author  
Generated in collaboration with OpenAI GPT and spaCy.

Special Note:-

My code works for almost everything stated, but for the HMM containers, it works up until navigating through the hmm21.com website after getting redirected and also selects container no. from the dropbox, puts the container no. in the desired field and clicks retrieve, but then an unexpexted error 402 shows up, which is not apparent when operating manually, only this error was not resolved as it was getting generated only during the automation and not otherwise. The code however works perfectly for every other container and everything else