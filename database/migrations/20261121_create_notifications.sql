USE SaigonBiteDB;

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT NOT NULL AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_id INT NOT NULL,
    notification_type VARCHAR(30) NOT NULL DEFAULT 'ORDER_REJECTED',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_id),
    CONSTRAINT uq_notifications_order_type UNIQUE (order_id, notification_type),
    KEY ix_notifications_customer_created (customer_id, created_at),
    KEY ix_notifications_customer_read (customer_id, is_read),
    CONSTRAINT fk_notifications_customer FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notifications_order FOREIGN KEY (order_id)
        REFERENCES orders (order_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
