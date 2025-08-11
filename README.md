# AtliQ Tees: Talk to a Database

An end-to-end LLM project that allows users to query a t-shirt inventory database using natural language. The system converts natural language questions into SQL queries and executes them on the database.

## Quick Start for GitHub Codespaces

### 1. Set up your environment

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Get Google API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 3. Configure environment
```bash
# Edit the .env file
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env
```

### 4. Initialize the database
```bash
sudo service mysql start 
mysql -u root -p -h 127.0.0.1 -P 3306 atliq_tshirts
```

### 5. Run the application
```bash
streamlit run main.py
```

## Features

- **Natural Language Queries**: Ask questions in plain English
- **SQLite Database**: Lightweight database perfect for Codespaces
- **Google Gemini AI**: Uses latest Google AI models
- **Few-Shot Learning**: Learns from examples to generate better queries
- **Streamlit UI**: Beautiful web interface
- **Sample Data**: Pre-populated with t-shirt inventory data

## Sample Questions

Try asking these questions:

- How many total t-shirts are left in stock?
- How many t-shirts do we have left for Nike in XS size and white color?
- How much is the total price of the inventory for all S-size t-shirts?
- How much sales amount will be generated if we sell all small size Adidas shirts today after discounts?
- How many white color Levi's shirts do we have?
- If we sell all the Levi's T-shirts today with discounts applied, how much revenue will we generate?

## Sample Answers

<!-- image attached in Assets-->
<img src="Assets/sample.png" alt="Sample Answer" />
