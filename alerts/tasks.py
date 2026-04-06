import redis
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import SessionLocal
from api.models.alert import Alert
from api.models.user import User 
from alerts.notifier import send_telegram_message, format_alert_message

celery_app = Celery(
    "alerts",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.broker_connection_retry_on_startup = True

celery_app.conf.beat_schedule = {
    "check-alerts-every-minute": {
        "task": "alerts.tasks.check_alerts",
        "schedule": crontab(minute="*"),
    }
}

sync_redis = redis.from_url(settings.redis_url, decode_responses=True)


@celery_app.task(name="alerts.tasks.check_alerts")
def check_alerts():
    db: Session = SessionLocal()

    try:
        active_alerts = db.query(Alert).filter(
            Alert.is_active == True
        ).all()

        print(f"Checking {len(active_alerts)} active alerts...")

        for alert in active_alerts:
            price_str = sync_redis.get(f"price:{alert.coin}")

            if price_str is None:
                print(f"No price found for {alert.coin}, skipping")
                continue

            current_price = float(price_str)
            triggered = False

            if alert.direction == "above" and current_price > alert.threshold:
                triggered = True
            elif alert.direction == "below" and current_price < alert.threshold:
                triggered = True

            if triggered:
                print(f"Alert {alert.id} triggered! {alert.coin} = ${current_price}")

                if alert.user.telegram_id:
                    message = format_alert_message(
                        coin=alert.coin,
                        direction=alert.direction,
                        threshold=alert.threshold,
                        current_price=current_price,
                    )
                    send_telegram_message(alert.user.telegram_id, message)

                alert.is_active = False
                db.commit()

    finally:
        db.close()