# Using flask to make an api 
# import necessary libraries and functions 
from flask import Flask, jsonify, request 
  
# creating a Flask app 
app = Flask(__name__) 

# store Telegram bot object
global telegram_send_func
global telegram_bot

@app.route('/send', methods = ['POST'])
def send():
    data = request.get_json()

    global telegram_send_func
    global telegram_bot

    telegram_send_func(telegram_bot, "-1002409253277", data['message'])
    return jsonify({'data': data})

@app.route('/test', methods = ['GET'])
def test():
    data = "Test message"

    global telegram_send_func
    global telegram_bot

    telegram_send_func(telegram_bot, "-1002409253277", data)
    return jsonify({'data': 'success?'})
  
  
# driver function 
if __name__ == '__main__': 
  
    app.run(debug = True) 

def start(bot, send_func):
    
    global telegram_send_func
    global telegram_bot
    telegram_send_func = send_func
    telegram_bot = bot

    app.run(debug=True)