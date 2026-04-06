import httpx
import redis
from celery import Celery
from celery.schedules import crontab

from shared.config import settings

celery_app = Celery(
    "collector",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.broker_connection_retry_on_startup = True

celery_app.conf.beat_schedule = {
    "collect-prices-every-5-minutes": {
        "task": "collector.tasks.collect_prices",
        "schedule": crontab(minute="*/5"),
    }
}

COINS = [
    "bitcoin", "ethereum", "solana", "cardano",
    "polkadot", "chainlink", "avalanche-2", "uniswap",
    "litecoin", "dogecoin"
]

# Sync Redis client for Celery — no async needed here
sync_redis = redis.from_url(settings.redis_url, decode_responses=True)


@celery_app.task(name="collector.tasks.collect_prices")
def collect_prices():
    url = f"{settings.coingecko_url}/simple/price"
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": "usd",
    }

    with httpx.Client() as client:
        response = client.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

    for coin, values in data.items():
        price = values["usd"]
        sync_redis.set(
            f"price:{coin}",
            str(price),
            ex=settings.price_update_interval * 2
        )
        print(f"Updated {coin}: ${price}")