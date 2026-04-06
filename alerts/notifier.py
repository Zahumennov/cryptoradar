import httpx
from shared.config import settings


def send_telegram_message(telegram_id: str, message: str) -> bool:
    url = f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage"
    payload = {
        "chat_id": telegram_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
    except httpx.HTTPError as e:
        print(f"Failed to send Telegram message: {e}")
        return False


def format_alert_message(
    coin: str,
    direction: str,
    threshold: float,
    current_price: float,
) -> str:
    direction_text = "risen above" if direction == "above" else "dropped below"
    return (
        f"🚨 <b>CryptoRadar Alert</b>\n\n"
        f"<b>{coin.upper()}</b> has {direction_text} your threshold!\n\n"
        f"Your threshold: <b>${threshold:,.2f}</b>\n"
        f"Current price: <b>${current_price:,.2f}</b>"
    )