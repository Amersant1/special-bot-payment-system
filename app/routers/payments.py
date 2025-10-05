from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta
import decimal
import aiohttp
from app.models import Payment, User, Subscription, SubscriptionType, PaymentType, Consultation
from app.settings import settings
from app.utils.robokassa import verify_payment_signature
from app.utils.telegram import send_consultation_payment_notification, send_consultation_paid_to_user

router = APIRouter()


@router.get("/robokassa/callback")
async def robokassa_callback(request: Request):
    """Единственный эндпоинт для обработки всех платежей от Робокассы"""
    params = dict(request.query_params)
    
    # Извлекаем параметры из callback
    payment_id = int(params.get("InvId"))
    tg_id = int(params.get("Shp_id"))
    shp_type = params.get("Shp_type", "subscription")  # Используем Shp_type как в backend
    subscription_type_str = params.get("Shp_subscription_type", "unlimited")
    out_sum = decimal.Decimal(params.get("OutSum", "0"))
    signature_value = params.get("SignatureValue", "")
    
    custom_params = {k: v for k, v in params.items() if k.startswith("Shp_")}
    if not verify_payment_signature(
        out_sum=out_sum,
        invoice_id=payment_id,
        signature_value=signature_value,
        **custom_params
    ):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    payment = await Payment.get_or_none(id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.price != int(out_sum):
        raise HTTPException(status_code=400, detail="Amount mismatch")

    # Отмечаем платеж как оплаченный
    payment.is_paid = True
    payment.paid_at = datetime.now()
    await payment.save()

    # Определяем тип платежа по Shp_type и обрабатываем соответственно
    if shp_type == "subscription":
        await _process_subscription_payment(payment, subscription_type_str)
    elif shp_type == "material":
        await _process_material_payment(payment)
    elif shp_type == "consultation":
        await _process_consultation_payment(payment)
    else:
        # Fallback на payment_type из базы, если Shp_type не определен
        if payment.payment_type == PaymentType.SUBSCRIPTION:
            await _process_subscription_payment(payment, subscription_type_str)
        elif payment.payment_type == PaymentType.MATERIAL:
            await _process_material_payment(payment)
        elif payment.payment_type == PaymentType.CONSULTATION:
            await _process_consultation_payment(payment)

    return f"OK{payment_id}"


async def _process_subscription_payment(payment: Payment, subscription_type_str: str):
    """Обработка платежа за подписку"""
    user = await payment.user
    subscription, _ = await Subscription.get_or_create(user=user)

    # Определяем тип подписки
    subscription_type = SubscriptionType(subscription_type_str)
    
    # Определяем дату начала подписки
    now = datetime.now()
    date_start = now
    if (subscription.subscription_type != SubscriptionType.FREE and 
        subscription_type == SubscriptionType.SPECIAL and 
        subscription.expires_at):
        date_start = subscription.expires_at

    # Определяем срок действия подписки
    if subscription_type in [SubscriptionType.UNLIMITED, SubscriptionType.PREMIUM]:
        expires_at = date_start + timedelta(days=30)
    elif subscription_type == SubscriptionType.SPECIAL:
        expires_at = date_start + timedelta(days=90)
    else:
        raise HTTPException(status_code=400, detail="Unknown subscription type")

    # Обновляем подписку
    subscription.payment = payment
    subscription.subscription_type = subscription_type
    subscription.expires_at = expires_at
    subscription.is_active = True
    await subscription.save()
    send_consultation_payment_notification


async def _process_material_payment(payment: Payment):
    """Обработка платежа за материал"""
    # Получаем материалы по ID из поля material_ids
    if payment.material_ids:
        # Вызываем backend эндпоинт для отправки материалов
        await send_materials_via_backend(
            tg_id=payment.user_id,
            material_ids=payment.material_ids,
            message="Ваши материалы готовы! Спасибо за покупку."
        )


async def _process_consultation_payment(payment: Payment):
    """Обработка платежа за консультацию"""
    # Получаем все консультации, связанные с этим платежом
    consultations = await Consultation.filter(payment=payment)
    
    if not consultations:
        print(f"No consultations found for payment {payment.id}")
        return
    
    # Помечаем все консультации как оплаченные
    consultations_info = []
    for consultation in consultations:
        consultation.is_paid = True
        await consultation.save()
        
        # Собираем информацию о консультации для уведомления
        consultations_info.append({
            "id": consultation.id,
            "price": consultation.price,
            "name": consultation.name,
            "email": consultation.email,
            "tg_tag": consultation.tg_tag,
            "specialist_id": consultation.specialist_id,
            "service_id": consultation.service_id
        })
    
    # Отправляем уведомление админу в Telegram
    await send_consultation_payment_notification(
        payment_id=payment.id,
        user_tg_id=payment.user_id,
        consultations_info=consultations_info
    )
    
    # Отправляем уведомление пользователю
    await send_consultation_paid_to_user(
        user_tg_id=payment.user_id,
        payment_id=payment.id,
        consultations_count=len(consultations_info)
    )
    
    # Дополнительное уведомление о завершении обработки
    print(f"✅ Consultation payment {payment.id} processed successfully for user {payment.user_id}")
    print(f"📊 Processed {len(consultations_info)} consultations")


async def send_materials_via_backend(tg_id: int, material_ids: list, message: str):
    """Вызывает backend эндпоинт для отправки материалов пользователю."""
    backend_url = f"{settings.BACKEND_URL}/materials/send-after-payment"
    
    payload = {
            "tg_id": tg_id,
            "material_ids": material_ids,
            "message": message
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(backend_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Materials sent successfully: {result}")
                else:
                    print(f"Failed to send materials: {response.status} - {await response.text()}")
    except Exception as e:
        print(f"Error calling backend: {e}")

