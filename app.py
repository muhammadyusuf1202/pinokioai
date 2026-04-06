from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from groq import Groq
import os
import database 
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'pinokioai-secret-2024-xK9mL'

# Groq API kaliti   
api_key = os.environ.get("GROQ_API_KEY")

# --- ROUTES ---

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = database.get_user_by_id(session['user_id'])
    return render_template('landing.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Email va usernameni tekshirish (database.py orqali)
        success, message = database.register_user(username, email, password)
        if success:
            user = database.login_user(email, password)
            session['user_id'] = user['id'] # type: ignore
            session['username'] = user['username'] # type: ignore
            return redirect(url_for('dashboard'))
        else:
            return render_template('register.html', error=message)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = database.login_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Email yoki parol noto'g'ri")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = database.get_user_by_id(user_id)
    
    # URL dan chat_id ni olish (masalan: /dashboard?chat_id=5)
    chat_id = request.args.get('chat_id')
    history = []
    if chat_id:
        history = database.get_chat_history(chat_id, user_id)
        
    return render_template('dashboard.html', user=user, history=history, current_chat_id=chat_id)
@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Bazadan foydalanuvchi ma'lumotlarini olish (agar kerak bo'lsa)
    user = database.get_user_by_id(session['user_id']) 
    return render_template('settings.html', user=user)

@app.route('/chat')
def chat_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Bazadan chatlarni olish
    chats = database.get_user_chats(session['user_id'])
    
    # Agar chatlar bo'lmasa, bo'sh massiv yuboramiz
    return render_template('chat.html', chats=chats if chats else [])

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Kirish talab qilinadi'}), 401
        
    data = request.get_json()
    user_id = session['user_id']
    user_message = data.get('message')
    chat_id = data.get('chat_id')
    model_alias = data.get('model', 'llama')

    # 1. System Prompt - AIga shaxsiyat beramiz
    system_prompt = (
        "Sen PinoikiAI — professional dasturlash yordamchisisan.Sen har doim o'zbekcha gpirishing shart va agar til o'rgtish uchun bo'lsa boshqa tillada gapirishing mumkin. "
        "Javoblaringda kodlarni doimo markdown ```python  ``` (yoki tegishli til nomi) "
        "bloklari ichida ber. Tushuntirishlaring qisqa va aniq bo'lsin." 
        "Agar foydalanuvchi bilan gaplash, judayam kam yozma judayam ko'p yozma"
    )

    # 2. Model tanlash mantiqi
    model_mapping = {
    # Standart Llama modellari
    'llama': 'llama-3.3-70b-versatile',
    'llama_mini': 'llama-3.1-8b-instant',
    
    # Yangi modellar (Rasmdan olindi)
    'llama4_scout': 'meta-llama/llama-4-scout-17b-16e-instruct',
    'qwen3': 'qwen/qwen3-32b',
    
    # Compound modellar
    'compound': 'groq/compound',
    'compound_mini': 'groq/compound-mini',
    
    # GPT OSS modellar
    'gpt_oss_120b': 'openai/gpt-oss-120b',
    'gpt_oss_20b': 'openai/gpt-oss-20b',
    
    # Xavfsizlik modeli
    'safety_gpt': 'openai/gpt-oss-safeguard-20b'
}
    selected_model = model_mapping.get(model_alias, 'llama-3.3-70b-versatile')

    # 3. Agar yangi chat bo'lsa, bazada chat yaratish
    if not chat_id:
        chat_id = database.create_chat(user_id, user_message[:30])

    # 4. Foydalanuvchi xabarini bazaga saqlash
    database.save_message(chat_id, user_id, 'user', user_message)

    try:
        if not api_key:
            print("XATO: GROQ_API_KEY topilmadi!")

        client = Groq(api_key=api_key)
        
        # 5. Xabarlar tuzilishi (System prompt + User message)
        messages_to_send = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        completion = client.chat.completions.create(
            model=selected_model,
            messages=messages_to_send,
            max_tokens=500, # Javob hajmini cheklaydi
            temperature=0.7 
        )
        
        ai_reply = completion.choices[0].message.content
        
        # 6. AI javobini bazaga saqlash (model_used bilan birga)
        database.save_message(chat_id, user_id, 'assistant', ai_reply, model_used=selected_model)
        
        return jsonify({
            'reply': ai_reply, 
            'chat_id': chat_id,
            'model': selected_model
        })
        
    except Exception as e:
        print(f"Groq API xatosi: {e}")
        return jsonify({'error': "AI bilan bog'lanishda xatolik yuz berdi"}), 500

@app.route('/api/search-chats')
def search_chats():
    query = request.args.get('q', '')
    user_id = session.get('user_id')
    results = database.search_user_chats(user_id, query) 
    return jsonify(results)

if __name__ == '__main__':
    database.init_db() 
    app.run(debug=True, port=5000)