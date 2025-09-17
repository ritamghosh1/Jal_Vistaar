import os
import re
import uuid
import pandas as pd
import openai
from flask import Flask, render_template, request, jsonify, url_for
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for servers
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
import traceback # Added for more detailed error logging

# --- Configuration ---
load_dotenv() # Load environment variables from a .env file

# Make sure to set the OPENAI_API_KEY environment variable in your .env file
try:
    # Configure OpenAI client
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
except KeyError:
    print("FATAL: OPENAI_API_KEY environment variable not set.")
    print("Please create a .env file and add the line: OPENAI_API_KEY='your-key-here'")
    exit()

# Ensure the directory for generated charts exists
static_dir = os.path.join(os.path.dirname(__file__), 'static')
charts_dir = os.path.join(static_dir, 'generated_charts')
if not os.path.exists(charts_dir):
    os.makedirs(charts_dir)

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Data Loading ---
df = None
try:
    csv_filename = 'groundwater_data.xlsx'
    csv_path = os.path.join(os.path.dirname(__file__), csv_filename)
    
    # **FIXED CODE**: Added quoting=3 to tell the parser to ignore quote characters, resolving the final parsing issue.
    df = pd.read_excel(csv_path)
    
    # Basic data cleaning
    df.rename(columns={'Stage of Ground Water Extraction (%)': 'ExtractionPercentage'}, inplace=True)
    df['ExtractionPercentage'] = pd.to_numeric(df['ExtractionPercentage'], errors='coerce')
    df.dropna(subset=['ExtractionPercentage', 'STATE', 'DISTRICT', 'Year'], inplace=True)
    
    # **ADDED DEBUGGING**: Print columns and head to confirm successful loading.
    print("--- CSV Data Loaded Successfully ---")
    print("Columns:", df.columns.tolist())
    print("Data Head:")
    print(df.head())
    print("------------------------------------")


except FileNotFoundError:
    print(f"FATAL: The data file was not found at the expected path: {csv_path}")
    print(f"Please make sure the file '{csv_filename}' is in the same directory as your app.py file.")
    # The app will still run, but the chat function will report an error.
except pd.errors.ParserError as e:
    print(f"FATAL: Could not parse the CSV file. Error: {e}")
    # The app will still run, but the chat function will report an error.
except Exception as e:
    print(f"An unexpected error occurred during data loading: {e}")
    traceback.print_exc()


# --- Helper Functions ---
def find_relevant_data(query):
    """
    Finds relevant data from the DataFrame based on keywords in the query.
    """
    if df is None:
        return pd.DataFrame()

    query_lower = query.lower()
    # Simple keyword extraction for locations by looking for capitalized words
    locations = list(set([word.strip() for word in re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b', query) if len(word) > 2]))

    if not locations:
         return df.sample(n=min(5, len(df)))

    # Filter by state or district using the extracted locations
    filtered_df = df[
        df['STATE'].str.lower().isin([loc.lower() for loc in locations]) |
        df['DISTRICT'].str.lower().isin([loc.lower() for loc in locations])
    ]

    if filtered_df.empty:
        return df.sample(n=min(5, len(df)))
    return filtered_df

def generate_comparison_graph(data, query):
    """
    Generates a bar chart if the query seems to ask for a comparison.
    Returns the path to the saved image or None.
    """
    comparison_keywords = ['compare', 'vs', 'versus', 'between']
    if not any(keyword in query.lower() for keyword in comparison_keywords):
        return None
    
    if data.empty or len(data) < 2:
        return None

    try:
        plt.figure(figsize=(10, 6))
        data['LocationLabel'] = data['DISTRICT'] + ' (' + data['Year'].astype(str) + ')'
        
        sns.barplot(
            x='ExtractionPercentage',
            y='LocationLabel',
            data=data.sort_values('ExtractionPercentage', ascending=False),
            palette='viridis'
        )
        plt.title('Groundwater Extraction Comparison')
        plt.xlabel('Stage of Ground Water Extraction (%)')
        plt.ylabel('Location')
        plt.tight_layout()

        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(charts_dir, filename)
        plt.savefig(filepath)
        plt.close()
        
        return url_for('static', filename=f'generated_charts/{filename}')
    except Exception as e:
        print(f"Error generating graph: {e}")
        return None

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # **FIXED CODE**: Wrapped the entire function in a try...except block for robust error handling.
    try:
        if df is None:
            return jsonify({
                'text': "I'm sorry, the server could not load the groundwater data file. Please ask the administrator to check the server logs."
            }), 500

        # Use .get_json() which returns None on failure instead of raising an exception
        data = request.get_json() 
        if not data:
            print("Error: Request body is not valid JSON or Content-Type header is not 'application/json'.")
            return jsonify({'error': 'Request must be JSON'}), 400

        prompt = data.get('prompt')
        persona = data.get('persona')
        language = data.get('language')

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        relevant_data = find_relevant_data(prompt)
        image_url = generate_comparison_graph(relevant_data, prompt)
        data_json_str = relevant_data.to_json(orient='records')

        system_prompt = f"""You are "Jal-Vistaar", an expert AI assistant for INGRES.
        **CRITICAL INSTRUCTIONS:**
        1.  **Data Source:** Base your answers STRICTLY on the following JSON data: {data_json_str}. Do not use external knowledge. If the data is empty or irrelevant, state that you couldn't find specific data for the query.
        2.  **User Persona:** Tailor your response for a '{persona}'. For example, a farmer needs practical advice, while a scientist needs technical details.
        3.  **Language:** Respond in '{language}'.
        4.  **Stage of Extraction Categories:** Use these rules for 'ExtractionPercentage': <= 70% is 'Safe'; > 70% and <= 90% is 'Semi-Critical'; > 90% and <= 100% is 'Critical'; > 100% is 'Over-Exploited'.
        5.  **Be Conversational:** Acknowledge the user's persona and question. If a graph has been generated, refer to it in your answer.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = response.choices[0].message.content
        
        return jsonify({
            'text': response_text,
            'imageUrl': image_url    
        })

    except Exception as e:
        # **FIXED CODE**: Added detailed traceback logging to the terminal.
        print(f"An unexpected error occurred in the /chat route: {e}")
        traceback.print_exc() # This will print the full error stack trace to your terminal
        return jsonify({'text': "An unexpected error occurred on the server. Please check the logs."}), 500

if __name__ == '__main__':
    app.run(debug=True)

