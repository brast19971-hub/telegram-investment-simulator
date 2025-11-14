from flask import Flask, request, jsonify, render_template
import random
import json
from datetime import datetime
import os

app = Flask(__name__)

# Данные об инвестиционных инструментах
INVESTMENT_OPTIONS = {
    'stocks': {'name': '📈 Акции', 'risk': 'высокий', 'icon': '📈'},
    'bonds': {'name': '🏛️ Облигации', 'risk': 'низкий', 'icon': '🏛️'},
    'crypto': {'name': '₿ Криптовалюта', 'risk': 'очень высокий', 'icon': '₿'},
    'real_estate': {'name': '🏠 Недвижимость', 'risk': 'средний', 'icon': '🏠'},
    'etf': {'name': '📊 ETF', 'risk': 'средний', 'icon': '📊'},
    'gold': {'name': '🥇 Золото', 'risk': 'низкий', 'icon': '🥇'}
}

# Хранилище данных пользователей
users_data = {}

class InvestmentSimulator:
    def calculate_returns(self, investment_type, amount):
        """Рассчитывает доходность инвестиций"""
        returns_ranges = {
            'stocks': (-0.12, 0.20),
            'bonds': (0.03, 0.07),
            'crypto': (-0.25, 0.40),
            'real_estate': (0.01, 0.15),
            'etf': (-0.05, 0.12),
            'gold': (-0.02, 0.10)
        }
        
        min_return, max_return = returns_ranges[investment_type]
        return_rate = random.uniform(min_return, max_return)
        profit = amount * return_rate
        
        return {
            'profit': round(profit, 2),
            'return_rate': round(return_rate * 100, 2),
            'new_amount': round(amount + profit, 2)
        }
    
    def get_market_news(self):
        """Генерирует случайные рыночные новости"""
        news = [
            "📰 Рынок акций показывает рост благодаря сильным отчетам компаний",
            "⚠️ Волатильность на крипторынке из-за новых регуляций",
            "📉 Процентные ставки остаются стабильными",
            "🚀 Технологический сектор демонстрирует рекордные показатели",
            "🌍 Мировые рынки реагируют на геополитические события"
        ]
        return random.choice(news)

simulator = InvestmentSimulator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init_user', methods=['POST'])
def init_user():
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in users_data:
        users_data[user_id] = {
            'balance': 10000.00,
            'portfolio': {},
            'history': [],
            'total_invested': 0,
            'total_profit': 0,
            'game_started': datetime.now().isoformat()
        }
    
    return jsonify(users_data[user_id])

@app.route('/api/invest', methods=['POST'])
def invest():
    data = request.json
    user_id = data.get('user_id')
    investment_type = data.get('type')
    amount = float(data.get('amount'))
    
    if user_id not in users_data:
        return jsonify({'error': 'User not found'}), 404
    
    user = users_data[user_id]
    
    if amount > user['balance']:
        return jsonify({'error': 'Недостаточно средств'}), 400
    
    # Вычитаем сумму инвестиции из баланса
    user['balance'] -= amount
    
    # Рассчитываем доходность
    result = simulator.calculate_returns(investment_type, amount)
    
    # Обновляем портфель
    if investment_type in user['portfolio']:
        user['portfolio'][investment_type] += result['new_amount']
    else:
        user['portfolio'][investment_type] = result['new_amount']
    
    # Добавляем в историю
    investment_record = {
        'type': investment_type,
        'amount': amount,
        'profit': result['profit'],
        'return_rate': result['return_rate'],
        'timestamp': datetime.now().isoformat(),
        'name': INVESTMENT_OPTIONS[investment_type]['name']
    }
    
    user['history'].append(investment_record)
    user['total_invested'] += amount
    user['total_profit'] += result['profit']
    
    # Получаем рыночные новости
    news = simulator.get_market_news()
    
    response = {
        'success': True,
        'investment_result': result,
        'new_balance': round(user['balance'], 2),
        'portfolio': user['portfolio'],
        'news': news,
        'investment_record': investment_record
    }
    
    return jsonify(response)

@app.route('/api/get_investment_options', methods=['GET'])
def get_investment_options():
    return jsonify(INVESTMENT_OPTIONS)

@app.route('/api/get_user_data', methods=['GET'])
def get_user_data():
    user_id = request.args.get('user_id')
    if user_id in users_data:
        return jsonify(users_data[user_id])
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)