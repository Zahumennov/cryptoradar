from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from shared.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coin = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)
    direction = Column(String, nullable=False)  # "above" or "below"
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.coin} {self.direction} {self.threshold}>"