Jal-Vistaar: AI Chatbot for INGRES
Jal-Vistaar is a full-stack web application that serves as an intelligent virtual assistant for the India Ground Water Resource Estimation System (INGRES). It allows users to query groundwater data in a conversational manner, tailored to different user personas like farmers, scientists, and policymakers.

This application uses a Python Flask backend to process data and generate insights, and a vanilla JavaScript frontend for the user interface.

Features
Persona-Driven AI: Chatbot responses are tailored to the selected user persona (e.g., Civilian, Farmer, Scientist).

Multilingual Support: The user can select their preferred language for interaction.

Backend Data Processing: The application reads and processes groundwater data from a CSV file using the pandas library.

Dynamic Graph Generation: The Python backend can generate and display graphs (e.g., bar charts) in the chat in response to user queries asking for comparisons.

Production-Ready Frontend: Uses a static, pre-compiled Tailwind CSS file, removing the need for a CDN in a production environment.

Secure API Calls: All communication with the AI model is handled by the backend, keeping API keys and logic secure.

Project Structure
jal-vistaar/
│
├── app.py                  # Main Flask application file
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── data/
│   └── Combined_Ingres.csv # The groundwater dataset
│
├── static/
│   ├── script.js           # Frontend JavaScript logic
│   ├── styles.css          # Pre-compiled Tailwind CSS
│   └── generated_charts/   # Directory for saving generated graphs
│
└── templates/
    └── index.html          # The main HTML file for the UI

Setup and Installation
Prerequisites
Python 3.8 or higher

pip (Python package installer)

1. Clone the Repository
Clone or download the project files into a directory on your local machine.

2. Set Up a Virtual Environment (Recommended)
It's highly recommended to use a virtual environment to manage project dependencies.

# Navigate to the project directory
cd jal-vistaar

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

3. Install Dependencies
Install the required Python packages using requirements.txt.

pip install -r requirements.txt

4. Set Up Google Gemini API Key
This application uses the Google Gemini API. You need to get an API key from Google AI Studio.

Once you have your key, create an environment variable named GEMINI_API_KEY.

# On macOS/Linux:
export GEMINI_API_KEY='YOUR_API_KEY'

# On Windows (Command Prompt):
set GEMINI_API_KEY=YOUR_API_KEY

The application will not run without this key.

How to Run the Application
Make sure your virtual environment is activated and the API key is set.

From the root directory of the project (jal-vistaar/), run the Flask application:

flask run

Open your web browser and navigate to:

https://www.google.com/search?q=http://127.0.0.1:5000

You should now see the Jal-Vistaar chatbot interface and can start interacting with it.

How It Works
The user interacts with the index.html page.

When a user sends a message, script.js sends a POST request to the /chat endpoint of the Flask backend.

The app.py backend receives the request, reads the Combined_Ingres.csv file, and filters the data based on keywords in the user's query.

If the query asks for a comparison, a graph is generated using matplotlib and saved to the static/generated_charts folder.

The backend constructs a detailed prompt (including the filtered data) and sends it to the Gemini API.

The AI's text response and the URL of any generated graph are sent back to the frontend.

script.js receives the response and dynamically updates the chat window with the new message and/or graph.# Jal_Vistaar
# Jal_Vistaar
