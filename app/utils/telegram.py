import aiohttp
from typing import List, Optional
from app.settings import settings


async def send_telegram_message(chat_id: str, message: str) -> bool:
    """Отправляет сообщение в Telegram чат"""
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not configured")
        return False
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    return True
                else:
                    print(f"Failed to send Telegram message: {response.status}")
                    return False
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


async def send_consultation_payment_notification(
    payment_id: int,
    user_tg_id: int,
    consultations_info: List[dict]
) -> bool:
    """Отправляет уведомление об оплате консультаций"""
    if not settings.INFO_CHAT:
        print("INFO_CHAT not configured")
        return False
    
    # Формируем сообщение
    message = f"💰 <b>Оплачена консультация!</b>\n\n"
    message += f"💰 <b>Свяжитесь с пользователем и специалистом!</b>\n\n"

    message += f"🆔 <b>Платеж:</b> {payment_id}\n"
    message += f"👤 <b>Пользователь:</b> {user_tg_id}\n\n"
    
    message += f"📋 <b>Консультации ({len(consultations_info)}):</b>\n"
    
    for i, consultation in enumerate(consultations_info, 1):
        message += f"{i}. <b>ID:</b> {consultation['id']}\n"
        message += f"   💰 <b>Цена:</b> {consultation['price']} руб.\n"
        if consultation.get('name'):
            message += f"   👤 <b>Имя:</b> {consultation['name']}\n"
        if consultation.get('email'):
            message += f"   📧 <b>Email:</b> {consultation['email']}\n"
        if consultation.get('tg_tag'):
            message += f"   🏷️ <b>Telegram:</b> @{consultation['tg_tag']}\n"
        message += f"   🎯 <b>Специалист ID:</b> {consultation['specialist_id']}\n"
        message += f"   🔧 <b>Сервис ID:</b> {consultation['service_id']}\n\n"
    
    return await send_telegram_message(settings.INFO_CHAT, message)


async def send_consultation_paid_to_user(
    user_tg_id: int,
    payment_id: int,
    consultations_count: int
) -> bool:
    """Отправляет пользователю уведомление об оплате консультации"""
    user_message = f"✅ <b>Ваша консультация оплачена!</b>\n\n"
    user_message += f"📋 <b>Консультаций оплачено:</b> {consultations_count}\n\n"
    user_message += f"👨‍💼 <b>С вами скоро свяжется специалист для проведения консультации.</b>\n\n"
    user_message += f"Спасибо за выбор наших услуг! 🙏"
    
    return await send_telegram_message(str(user_tg_id), user_message)
