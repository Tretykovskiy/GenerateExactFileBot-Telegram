import telebot
import requests

# Ваши ключи
bot = telebot.TeleBot('8583388611:AAG5iIK4wG1VCTeimqbc2NpdOcf054FA5ic')
IMAGGA_API_KEY = 'acc_0c796b3b38b8156'
IMAGGA_API_SECRET = '37c523b6f2167168c2623fb371ce03f4'

# Словарь перевода на русский
TRANSLATIONS = {
    'food': 'еда',
    'fruit': 'фрукт',
    'vegetable': 'овощ',
    'meal': 'блюдо',
    'dish': 'блюдо',
    'cuisine': 'кухня',
    'cooking': 'готовка',
    'meat': 'мясо',
    'fish': 'рыба',
    'bread': 'хлеб',
    'cake': 'торт',
    'dessert': 'десерт',
    'drink': 'напиток',
    'beverage': 'напиток',
    'pizza': 'пицца',
    'pasta': 'паста',
    'rice': 'рис',
    'soup': 'суп',
    'salad': 'салат',
    'sandwich': 'сэндвич',
    'burger': 'бургер',
    'apple': 'яблоко',
    'banana': 'банан',
    'orange': 'апельсин',
    'tomato': 'помидор',
    'potato': 'картофель',
    'carrot': 'морковь',
    'onion': 'лук',
    'chicken': 'курица',
    'beef': 'говядина',
    'pork': 'свинина',
    'cheese': 'сыр',
    'milk': 'молоко',
    'egg': 'яйцо',
    'butter': 'масло',
    'coffee': 'кофе',
    'tea': 'чай',
    'juice': 'сок',
    'water': 'вода',
    'ice cream': 'мороженое',
    'chocolate': 'шоколад',
    'sushi': 'суши',
    'steak': 'стейк',
    'sausage': 'колбаса',
    'pancake': 'блин',
    'cookie': 'печенье',
    'pie': 'пирог',
    'yogurt': 'йогурт',
    'noodles': 'лапша',
    'dumpling': 'пельмени',
    'borscht': 'борщ',
    'shashlik': 'шашлык',
    'caviar': 'икра',
    'pelmeni': 'пельмени',
    'blini': 'блины',
    'kvass': 'квас'
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🍕 Привет! Отправь фото еды, и я определю что на ней!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        processing_msg = bot.reply_to(message, "🔍 Анализирую фото...")
        
        # Определяем еду через Imagga
        result = detect_with_imagga(downloaded_file)
        
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.reply_to(message, result)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "❌ Ошибка при обработке фото")

def detect_with_imagga(image_data):
    """
    Определяем объекты на фото через Imagga
    """
    try:
        response = requests.post(
            'https://api.imagga.com/v2/tags',
            auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET),
            files={'image': image_data},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            tags = result['result']['tags']
            
            # Ищем самый вероятный вариант связанный с едой
            best_food = None
            best_confidence = 0
            
            for tag in tags:
                tag_name = tag['tag']['en']
                confidence = tag['confidence']
                
                if confidence > best_confidence and is_food_related(tag_name):
                    best_food = tag_name
                    best_confidence = confidence
            
            if best_food:
                russian_name = translate_to_russian(best_food)
                return f"🍽 На фото: {russian_name}"
            else:
                return "❌ Не удалось определить еду на фото"
        
        else:
            return "❌ Ошибка при анализе фото"
            
    except Exception as e:
        return "❌ Ошибка соединения"

def is_food_related(tag_name):
    """
    Проверяем, относится ли тег к еде
    """
    food_keywords = list(TRANSLATIONS.keys())
    tag_lower = tag_name.lower()
    return any(keyword in tag_lower for keyword in food_keywords)

def translate_to_russian(english_name):
    """
    Переводим английское название на русский
    """
    english_lower = english_name.lower()
    
    # Ищем точное совпадение
    for eng, rus in TRANSLATIONS.items():
        if eng in english_lower:
            return rus.capitalize()
    
    # Если не нашли перевод, возвращаем оригинал
    return english_name.capitalize()

if __name__ == '__main__':
    print("🍕 Бот запущен! Иди в Telegram и отправь /start")
    print("Для остановки нажми Ctrl+C")
    bot.infinity_polling()
