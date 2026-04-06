from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from shared.redis_client import get_redis

router = APIRouter()


@router.get("/")
async def get_all_prices(redis: Redis = Depends(get_redis)):
    keys = await redis.keys("price:*")

    if not keys:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No prices available yet. Collector may not have run."
        )

    prices = {}
    for key in keys:
        coin = key.replace("price:", "")
        price = await redis.get(key)
        if price:
            prices[coin] = float(price)

    return {"prices": prices}


@router.get("/{coin}")
async def get_coin_price(coin: str, redis: Redis = Depends(get_redis)):
    price = await redis.get(f"price:{coin.lower()}")

    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{coin} not found. It may not be tracked yet."
        )

    return {
        "coin": coin.lower(),
        "price": float(price),
        "currency": "usd"
    }