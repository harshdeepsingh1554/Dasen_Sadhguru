from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['quotes_db']


# Hardcoded admin credentials
ADMIN_USER = 'admin'
ADMIN_PASS = 'password'


@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')


@app.route('/chat', methods=['POST'])
def chat():
    collection = db['quotes']
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"reply": "Please provide a valid message."}), 400

    mood = user_message.strip().lower()

    try:
        if mood not in ['random']:
            # Fetch from MongoDB
            quote_data = collection.aggregate([
                {"$match": {"mood": mood}},
                {"$sample": {"size": 1}}
            ])
            result = next(quote_data, None)
            if result:
                full_quote = f"[{mood.upper()}] \"{result['quote']}\" — {result['author']}"
            else:
                full_quote = "No quote found for this mood."
           
        else:
            
             # ZenQuotes API fallback
            response = requests.get('https://zenquotes.io/api/random')
            quote_data = response.json()
            quote = quote_data[0]['q']
            author = quote_data[0]['a']
            full_quote = f"[{mood.upper()}] \"{quote}\" — {author}"

        return jsonify({"reply": full_quote})

    except Exception as e:
        print("Error fetching quote:", e)
        return jsonify({"reply": "Sorry, I couldn't get a quote right now."}), 500


# ---------- Admin login/logout ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        collection = db['users']
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('add_quote'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))


# ---------- Add Quote Page ----------
@app.route('/add-quote', methods=['GET', 'POST'])
def add_quote():
    collection = db['quotes']
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        mood = request.form['mood'].strip().lower()
        quote = request.form['quote']
        author = request.form['author']

        if mood and quote and author:
            collection.insert_one({
                "mood": mood,
                "quote": quote,
                "author": author
            })
            return render_template('add_quote.html', success=True)

    return render_template('add_quote.html')
if __name__ == '__main__':
    app.run(debug=True)