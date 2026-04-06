from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared.database import get_db
from api.models.alert import Alert
from api.models.user import User
from api.schemas.alert import AlertCreate, AlertResponse
from api.security import get_current_user
from api.exceptions import alert_not_found_exception

router = APIRouter()


@router.post("/", response_model=AlertResponse)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = Alert(
        user_id=current_user.id,
        coin=alert_data.coin,
        threshold=alert_data.threshold,
        direction=alert_data.direction,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_active == True,
    ).all()


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id,
    ).first()

    if not alert:
        raise alert_not_found_exception()

    alert.is_active = False
    db.commit()
    return {"message": f"Alert {alert_id} deactivated"}