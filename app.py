import requests

TOKEN = "CHAGI0BXQVIROXEPLGRKVXCUTPZPGDEDPZOUAIMUHOILYAFMKBCZMAOFZBCNPISG"
PUBLIC_URL = "https://mohsenbor.replit.app/webhook"

data = {
    'url': PUBLIC_URL,
    'type': 'ReceiveUpdate'
}

response = requests.post(f'https://botapi.rubika.ir/v3/{TOKEN}/updateBotEndpoints', json=data)
print(response.text)
