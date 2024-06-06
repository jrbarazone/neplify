from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# Configurar la clave de la API de OpenAI
openai.api_key = ""

@appmy_secret = os.environ['openai.api_key ='].route('/completar', methods=['POST'])
def completar():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    
    return jsonify(response.choices[0].text)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    forward_url = 'https://webhook.site/gpt'
    
    # Reenviar la solicitud a Webhook.site
    response = requests.post(forward_url, json=data)
    
    return jsonify({'status': 'forwarded', 'response_code': response.status_code})

if __name__ == '__main__':
    app.run(debug=True)
