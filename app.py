import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, send
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'user': {'password': 'pass'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
@login_required
def index():
    return render_template('index.html', user = current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Login feito com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha inválidos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.')
    return redirect(url_for('login'))

def get_rasa_response(message):
        rasa_url = "http://localhost:5005/webhooks/rest/webhook"
        payload = {
            "sender": "user",
            "message": message
        }
        response = requests.post(rasa_url, json=payload)
        if response.status_code == 200:
            responses = response.json()
            if responses:
                return responses[0].get("text", "")
            return "Desculpe, não consegui entender... Pode repetir?"

@socketio.on('message')
@login_required
def handle_message(msg):
    print(f"Mensagem: {msg}")
    response_text = get_rasa_response(msg)
    send(f"Bot: {response_text}", broadcast=True)

if __name__ =='__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

# http://127.0.0.1:5000/


