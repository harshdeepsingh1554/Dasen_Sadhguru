from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import requests
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# MongoDB setup



uri = "mongodb+srv://harshupocof1:Lh8.v!rV_ZnkY3w@cluster0.9trtciw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['quotes_db']

# Hardcoded admin credentials
ADMIN_USER = 'admin'
ADMIN_PASS = 'password'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/user_dashboard', methods=['GET'])
def home():
    username = session.get('username')
    return render_template('home.html',username=username)


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
        data = request.get_json()
        action = data.get("action")

        username = data.get('username')
        password = data.get('password')

        if action == "signin":
            if username == ADMIN_USER and password == ADMIN_PASS:
                session['admin'] = True
                return jsonify({"success": True, "message": "Admin login successful", "redirect": "/add_quote"})

            user = collection.find_one({"username": username})
            if user and user['password'] == password:
                session['user'] = True
                session['username'] = username.upper()
                return jsonify({"success": True, 
                                "message": "Login successful", 
                                "redirect": "/user_dashboard",
                                "username": username })
            else:
                return jsonify({"success": False, "message": "Invalid credentials"}), 401

        elif action == "signup":
            if collection.find_one({"username": username}):
                return jsonify({"success": False, "message": "Username already exists"}), 400

            collection.insert_one({"username": username, "password": password})
            return jsonify({"success": True, "message": "User created successfully. Please log in."})

    # GET request → return HTML page
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
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
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env variable
    app.run(host="0.0.0.0", port=port)





