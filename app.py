from flask import Flask, jsonify, render_template, redirect, url_for, request, session
from flask_restful import Resource, Api, reqparse
import markdown
from assistant import authentication
from assistant.generator import chat_response, reset_chat
from assistant.general_chatbot import response , reset

app = Flask(__name__)
api = Api(app)

basic_questions_and_responses = {
    'thank': 'I am glad I was able to help. Good luck with your project. Necroder at your service 24/7.',
    'hello': "Hello, I am Necroder, I am a super helpful coding assistant. No bug goes from my sight uncaught. How may I help you today?",
    'bye': 'Happy coding. Do not let a bug get you down :)',
}

parser = reqparse.RequestParser()
parser.add_argument('email', type=str, required=True, help="Email cannot be blank!")
parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")
parser.add_argument('query', type=str, required=True, help="Query cannot be blank!")


class HomePage(Resource):
    # get method for homepage
    def get(self):
        return {'response':"home page"}, 200
    
class ChatResponse(Resource):
    def get(self):
        # get method for chat-response
        return jsonify({'response':"Hello, I am Necroder, I am a super helpful coding assistant. No bug goes from my sight uncaught. How may I help you today?"})

    def post(self):
        # post method for chat response
        args = parser.parse_args()
        prompt = args['query']

        try:
            for question, answer in basic_questions_and_responses.items():
                if question in prompt.lower():
                    return jsonify({'response': answer})
            response_text = chat_response(prompt)
            return jsonify({'response': format_markdown(response_text)})
        except Exception:
            return jsonify({'response': "Error generating answer"})

class GeneralChatResponse(Resource):
    def get(self):
        return jsonify({'response': "Hello, I am Necroder, I am a super helpful coding assistant. No bug goes from my sight uncaught. How may I help you today?"})

    def post(self):
        args = parser.parse_args()
        prompt = args['query']

        try:
            for question, answer in basic_questions_and_responses.items():
                if question in prompt.lower():
                    return jsonify({'response': answer})
            response_text = response(prompt)
            return jsonify({'response': format_markdown(response_text)})
        except Exception:
            return jsonify({'response': "Error generating answer"})

class SignUp(Resource):
    def post(self):
        if "user" in session: 
            return f"Hi {session['user']}"
        
        args = parser.parse_args()
        email = args['email']
        password = args['password']

        try:
            authentication.sign_up(email, password)
        except Exception:
            return jsonify({'response': "Failed to Sign Up"})

class LoginPage(Resource):
    def post(self):
        if "user" in session: 
            return f"Hi {session['user']}"

        args = parser.parse_args()
        email = args['email']
        password = args['password']

        try:
            user = authentication.log_in(email, password)
            session['user'] = email
            return jsonify({'response': "Login successful"})
        except Exception:
            return jsonify({'response': "Incorrect Email or Password"})

class Logout(Resource):
    def get(self):
        session.pop('user')
        return jsonify({'response': "Logged out successfully"})

class UserDetails(Resource):
    def get(self):
        if "user" in session:
            return jsonify({'response': authentication.get_user_details()})
        return jsonify({'response': "User not logged in"})

class ForgotPassword(Resource):
    def post(self):
        args = parser.parse_args()
        email = args['email']

        try:
            authentication.reset_password(email)
            return jsonify({'response': "Password Reset Email Sent"})
        except Exception:
            return jsonify({'response': "Failed to Reset Password"})

class ResetChat(Resource):
    def get(self):
        reset_chat()
        return jsonify({'response': "Chat history reset successfully"})

class GeneralReset(Resource):
    def get(self):
        reset()
        return jsonify({'response': "General chat history reset successfully"})

# Helper function to format markdown text
def format_markdown(markdown_text):
    return markdown.markdown(markdown_text)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Authenticate user (use your authentication logic here)
        if authentication.log_in(email, password):
            session['user'] = email
            return redirect(url_for('chat_page'))  # Redirect to chat page after successful login
        else:
            return jsonify({'response': "Incorrect Email or Password"})
    return render_template('login.html')

# Add resources to the API
api.add_resource(HomePage, "/", "/home")
api.add_resource(ChatResponse, "/ask")
api.add_resource(GeneralChatResponse, "/askgeneral")
api.add_resource(SignUp, "/signup")
api.add_resource(LoginPage, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(UserDetails, "/user-details")
api.add_resource(ForgotPassword, "/forgot-password")
api.add_resource(ResetChat, "/reset-chat")
api.add_resource(GeneralReset, "/generalreset")

if __name__ == "__main__":
    app.run()
