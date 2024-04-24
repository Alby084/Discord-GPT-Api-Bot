with open('.env', 'r') as file:
    content = file.read().strip()
    if content.startswith('BOT_TOKEN = "') and content.endswith('"'):
        token = content.split('"')[1]
        print(token)
    else:
        print("Invalid token format .env")