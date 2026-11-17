DROP DATABASE IF EXISTS SaigonBiteDB;
CREATE DATABASE SaigonBiteDB
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE SaigonBiteDB;

-- 1. Customers (Single Table Inheritance: LOCAL & TOURIST)
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_type VARCHAR(20) NOT NULL COMMENT 'LOCAL or TOURIST',
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NULL,
    phone VARCHAR(20) NULL,
    passport_number VARCHAR(30) NULL,
    CONSTRAINT chk_customer_type CHECK (customer_type IN ('LOCAL', 'TOURIST'))
) ENGINE=InnoDB;

-- 2. Cloud-Kitchen Hubs
CREATE TABLE hubs (
    hub_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    capacity INT NOT NULL DEFAULT 20,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT 'OPEN, OVERLOADED, CLOSED',
    CONSTRAINT chk_hub_status CHECK (status IN ('OPEN', 'OVERLOADED', 'CLOSED'))
) ENGINE=InnoDB;

-- 3. Virtual Restaurant Brands
CREATE TABLE brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE, INACTIVE',
    CONSTRAINT chk_brand_status CHECK (status IN ('ACTIVE', 'INACTIVE'))
) ENGINE=InnoDB;

-- 4. Menu Items
CREATE TABLE menu_items (
    menu_item_id INT AUTO_INCREMENT PRIMARY KEY,
    hub_id INT NOT NULL,
    brand_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    price INT NOT NULL COMMENT 'Unit price in VND',
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_menu_items_hub FOREIGN KEY (hub_id)
        REFERENCES hubs(hub_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_menu_items_brand FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_menu_price CHECK (price >= 0)
) ENGINE=InnoDB;

-- 5. Promotional Vouchers (UC05 - Admin)
CREATE TABLE vouchers (
    voucher_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    discount_type VARCHAR(20) NOT NULL COMMENT 'PERCENT or FIXED',
    discount_value INT NOT NULL,
    min_order INT NOT NULL DEFAULT 0 COMMENT 'Minimum subtotal in VND',
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT 'ACTIVE, EXPIRED, ARCHIVED',
    CONSTRAINT chk_voucher_type CHECK (discount_type IN ('PERCENT', 'FIXED')),
    CONSTRAINT chk_voucher_status CHECK (status IN ('ACTIVE', 'EXPIRED', 'ARCHIVED')),
    CONSTRAINT chk_voucher_dates CHECK (end_date >= start_date)
) ENGINE=InnoDB;

-- 6. Orders (UC01, UC02, UC03, UC04, UC06)
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    hub_id INT NOT NULL,
    voucher_id INT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING'
        COMMENT 'PENDING, CONFIRMED, REJECTED, PREPARING, READY, DELIVERED, FAILED, CANCELLED',
    delivery_address VARCHAR(255) NOT NULL,
    delivery_distance_km FLOAT NOT NULL,
    payment_method VARCHAR(20) NOT NULL DEFAULT 'COD' COMMENT 'COD',
    payment_status VARCHAR(20) NOT NULL DEFAULT 'UNPAID' COMMENT 'UNPAID, PAID, REFUNDED',
    subtotal INT NOT NULL,
    delivery_fee INT NOT NULL DEFAULT 0,
    surcharge INT NOT NULL DEFAULT 0,
    discount INT NOT NULL DEFAULT 0,
    total INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orders_hub FOREIGN KEY (hub_id)
        REFERENCES hubs(hub_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orders_voucher FOREIGN KEY (voucher_id)
        REFERENCES vouchers(voucher_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_order_status CHECK (
        status IN ('PENDING', 'CONFIRMED', 'REJECTED', 'PREPARING', 'READY', 'DELIVERED', 'FAILED', 'CANCELLED')
    )
) ENGINE=InnoDB;

-- 7. Order Items
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price INT NOT NULL COMMENT 'Snapshot price in VND at order creation',
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_order_items_menu_item FOREIGN KEY (menu_item_id)
        REFERENCES menu_items(menu_item_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_order_item_qty CHECK (quantity > 0)
) ENGINE=InnoDB;

-- 8. Order Status History (UC02, UC03, UC04, UC06)
CREATE TABLE order_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    old_status VARCHAR(30) NULL,
    new_status VARCHAR(30) NOT NULL,
    reason VARCHAR(255) NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 9. Deliveries (1-to-0..1 with Orders, used by UC06 Delivery Reports)
CREATE TABLE deliveries (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    pickup_at DATETIME NULL,
    delivered_at DATETIME NULL,
    outcome VARCHAR(30) NOT NULL DEFAULT 'IN_TRANSIT' COMMENT 'IN_TRANSIT, DELIVERED, LATE, FAILED',
    CONSTRAINT fk_deliveries_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_delivery_outcome CHECK (outcome IN ('IN_TRANSIT', 'DELIVERED', 'LATE', 'FAILED'))
) ENGINE=InnoDB;

-- Performance Indexes for Management Reports & Kitchen Queue
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_hub_status ON orders(hub_id, status);
CREATE INDEX idx_history_order_id ON order_status_history(order_id);
CREATE INDEX idx_deliveries_pickup_at ON deliveries(pickup_at);