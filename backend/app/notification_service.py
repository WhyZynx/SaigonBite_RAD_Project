from app.repositories.notification import NotificationRepository


class NotificationService:
    def __init__(self, db):
        self.repository = NotificationRepository(db)

    def notify_order_rejected(self, order_id: int, reason: str):
        return self.repository.create_order_rejected(order_id, reason)
