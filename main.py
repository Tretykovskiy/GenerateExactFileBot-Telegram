import telebot
import requests

bot = telebot.TeleBot('8583388611:AAG5iIK4wG1VCTeimqbc2NpdOcf054FA5ic')

# Твои ключи от Imagga
IMAGGA_API_KEY = 'acc_0c796b3b38b8156'
IMAGGA_API_SECRET = '37c523b6f2167168c2623fb371ce03f4'

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
                    "🍕 Отправь фото еды, и я определю что на ней!")

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
            
            # Фильтруем и форматируем результаты
            food_tags = []
            for tag in tags[:8]:  # Берем топ-8 тегов
                tag_name = tag['tag']['en']
                confidence = tag['confidence']
                
                # Фильтруем по уверенности и убираем мусорные теги
                if confidence > 5 and is_food_related(tag_name):
                    food_tags.append(f"• {tag_name} ({confidence:.1f}%)")
            
            if food_tags:
                return "🍽 На фото распознано:\n" + "\n".join(food_tags[:5])  # Показываем топ-5
            else:
                return "❌ Не удалось определить еду на фото"
        
        else:
            return f"❌ Ошибка API: {response.status_code}"
            
    except Exception as e:
        return f"❌ Ошибка соединения: {e}"

def is_food_related(tag_name):
    """
    Проверяем, относится ли тег к еде
    """
    food_keywords = [
        'food', 'fruit', 'vegetable', 'meal', 'dish', 'cuisine', 'cooking',
        'meat', 'fish', 'bread', 'cake', 'dessert', 'drink', 'beverage',
        'pizza', 'pasta', 'rice', 'soup', 'salad', 'sandwich', 'burger',
        'apple', 'banana', 'orange', 'tomato', 'potato', 'carrot', 'onion',
        'chicken', 'beef', 'pork', 'cheese', 'milk', 'egg', 'butter'
    ]
    
    tag_lower = tag_name.lower()
    return any(keyword in tag_lower for keyword in food_keywords)

# Запуск бота
if __name__ == '__main__':
    print("🍕 Бот для распознавания еды запущен!")
    print("Используем Imagga API")
    bot.infinity_polling()
