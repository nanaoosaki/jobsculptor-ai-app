# Simple script to create a proper .env file
with open('.env', 'w', encoding='utf-8') as f:
    f.write('CLAUDE_API_KEY=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\n')
    f.write('FLASK_SECRET_KEY=random_secure_string_for_flask_session\n')
 
print("Created .env file successfully!") 