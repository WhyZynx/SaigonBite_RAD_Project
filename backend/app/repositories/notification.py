from datetime import timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models import Notification, Order


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_customer(self, customer_id: int):
        rows = self.db.scalars(
            select(Notification)
            .where(Notification.customer_id == customer_id)
            .order_by(Notification.created_at.desc(), Notification.notification_id.desc())
        ).all()
        return [self._payload(row) for row in rows]

    def unread_count(self, customer_id: int) -> int:
        return int(
            self.db.scalar(
                select(func.count(Notification.notification_id)).where(
                    Notification.customer_id == customer_id,
                    Notification.is_read.is_(False),
                )
            ) or 0
        )

    def mark_read(self, customer_id: int, notification_id: int):
        notification = self.db.scalar(
            select(Notification).where(
                Notification.notification_id == notification_id,
                Notification.customer_id == customer_id,
            )
        )
        if notification is None:
            raise HTTPException(status_code=404, detail="Notification not found")
        if not notification.is_read:
            notification.is_read = True
            self.db.commit()
        return {"id": notification.notification_id, "is_read": notification.is_read}

    def create_order_rejected(self, order_id: int, reason: str):
        order = self.db.scalar(select(Order).where(Order.order_id == order_id))
        if order is None:
            raise LookupError("Rejected order was not found when creating its notification")

        notification = Notification(
            customer_id=order.customer_id,
            order_id=order_id,
            notification_type="ORDER_REJECTED",
            title=f"Order #{order_id} was rejected",
            message=f"Your order was rejected. Reason: {reason}",
        )
        self.db.add(notification)
        try:
            self.db.commit()
            self.db.refresh(notification)
            return self._payload(notification)
        except IntegrityError:
            self.db.rollback()
            existing = self.db.scalar(
                select(Notification).where(
                    Notification.order_id == order_id,
                    Notification.notification_type == "ORDER_REJECTED",
                )
            )
            if existing is not None:
                return self._payload(existing)
            raise

    @staticmethod
    def _payload(notification: Notification):
        created_at = notification.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        created_at_utc = created_at.astimezone(timezone.utc).isoformat()
        return {
            "id": notification.notification_id,
            "order_id": notification.order_id,
            "notification_type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": created_at_utc,
        }
