USE SaigonBiteDB;

-- 1. Seed Customers (Local & Tourist)
INSERT INTO customers (customer_id, customer_type, name, email, phone, passport_number) VALUES
(1, 'LOCAL', 'Nguyen Minh Anh', 'customer@saigonbite.com', '0901234567', NULL),
(2, 'LOCAL', 'Tran Hoang Nam', 'nam.tran@gmail.com', '0912345678', NULL),
(3, 'TOURIST', 'Emily Carter', 'emily.carter@example.com', NULL, 'P89451230'),
(4, 'LOCAL', 'Le Thu Ha', 'ha.le@gmail.com', '0987654321', NULL);

-- 2. Seed Hubs
INSERT INTO hubs (hub_id, name, address, capacity, status) VALUES
(1, 'District 1 Central Hub', '128 Nguyen Hue, District 1, Ho Chi Minh City', 30, 'OPEN'),
(2, 'District 3 Kitchen Hub', '245 Vo Van Tan, District 3, Ho Chi Minh City', 25, 'OPEN'),
(3, 'District 7 South Hub', '88 Nguyen Van Linh, District 7, Ho Chi Minh City', 25, 'OPEN'),
(4, 'Thu Duc Campus Hub', '15 Vo Van Ngan, Thu Duc City, Ho Chi Minh City', 15, 'OVERLOADED');

-- 3. Seed Brands
INSERT INTO brands (brand_id, name, status) VALUES
(1, 'Com Tam Sai Gon', 'ACTIVE'),
(2, 'Pho Ha Noi Express', 'ACTIVE'),
(3, 'Banh Mi & Tra Sua', 'ACTIVE');

-- 4. Seed Menu Items
INSERT INTO menu_items (menu_item_id, hub_id, brand_id, name, price, is_available) VALUES
(1, 1, 1, 'Com Tam Suon Bi Cha', 55000, TRUE),
(2, 1, 2, 'Pho Bo Tai Nam', 65000, TRUE),
(3, 1, 3, 'Tra Dao Cam Sa', 30000, TRUE),
(4, 1, 1, 'Com Ga Xoi Mo', 50000, FALSE),
(5, 2, 2, 'Bun Bo Hue Dac Bien', 60000, TRUE),
(6, 2, 3, 'Banh Mi Thit Nuong', 35000, TRUE),
(7, 3, 1, 'Com Tam Suon Trung', 50000, TRUE),
(8, 3, 3, 'Tra Sua Tran Chau Duong Den', 38000, TRUE);

-- 5. Seed Vouchers (Exact columns from submitted schema)
INSERT INTO vouchers (voucher_id, code, discount_type, discount_value, min_order, start_date, end_date, status) VALUES
(1, 'BITEWELCOME', 'PERCENT', 20, 150000, '2026-11-01 00:00:00', '2026-12-31 23:59:59', 'ACTIVE'),
(2, 'D1LUNCH25', 'FIXED', 25000, 120000, '2026-11-01 00:00:00', '2026-12-15 23:59:59', 'ACTIVE'),
(3, 'WELCOME10', 'PERCENT', 10, 80000, '2026-11-01 00:00:00', '2026-12-31 23:59:59', 'ACTIVE'),
(4, 'OCTOBER50', 'FIXED', 50000, 200000, '2026-10-01 00:00:00', '2026-10-31 23:59:59', 'EXPIRED'),
(5, 'FLASHVIP', 'PERCENT', 15, 100000, '2026-11-01 00:00:00', '2026-11-30 23:59:59', 'ARCHIVED');

-- 6. Seed Orders (Covering all statuses + Nov 2026 reporting range)
INSERT INTO orders (
    order_id, customer_id, hub_id, voucher_id, status,
    delivery_address, delivery_distance_km, payment_method, payment_status,
    subtotal, delivery_fee, surcharge, discount, total, created_at
) VALUES
(101, 1, 1, 1, 'DELIVERED', '45 Le Loi, District 1, HCMC', 2.4, 'ONLINE', 'PAID', 175000, 15000, 0, 35000, 155000, '2026-11-01 11:15:00'),
(102, 2, 2, NULL, 'DELIVERED', '112 Cach Mang Thang 8, District 3, HCMC', 3.1, 'COD', 'PAID', 130000, 18000, 0, 0, 148000, '2026-11-03 12:05:00'),
(103, 3, 1, 2, 'DELIVERED', '72 Dong Khoi, District 1, HCMC', 1.8, 'ONLINE', 'PAID', 150000, 12000, 0, 25000, 137000, '2026-11-07 18:30:00'),
(104, 4, 3, 3, 'DELIVERED', '105 Nguyen Thi Thap, District 7, HCMC', 4.2, 'ONLINE', 'PAID', 138000, 20000, 0, 13800, 144200, '2026-11-10 19:10:00'),
(105, 1, 1, NULL, 'REJECTED', '90 Pasteur, District 1, HCMC', 2.0, 'COD', 'UNPAID', 50000, 15000, 0, 0, 65000, '2026-11-12 12:40:00'),
(106, 1, 1, 3, 'PENDING', '22 Hai Ba Trung, District 1, HCMC', 2.7, 'COD', 'UNPAID', 120000, 15000, 0, 12000, 123000, '2026-11-15 11:30:00'),
(107, 2, 1, NULL, 'CONFIRMED', '18 Ly Tu Trong, District 1, HCMC', 1.5, 'ONLINE', 'PAID', 110000, 12000, 0, 0, 122000, '2026-11-15 11:35:00'),
(108, 3, 1, NULL, 'PREPARING', '35 Mac Thi Buoi, District 1, HCMC', 1.9, 'ONLINE', 'PAID', 95000, 12000, 0, 0, 107000, '2026-11-15 11:40:00'),
(109, 4, 2, NULL, 'READY', '60 Tran Quoc Thao, District 3, HCMC', 2.2, 'COD', 'UNPAID', 95000, 15000, 0, 0, 110000, '2026-11-15 11:45:00');

-- 7. Seed Order Items
INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price) VALUES
(101, 1, 2, 55000),
(101, 2, 1, 65000),
(102, 5, 1, 60000),
(102, 6, 2, 35000),
(103, 2, 2, 65000),
(103, 3, 1, 30000),
(104, 7, 2, 50000),
(104, 8, 1, 38000),
(105, 4, 1, 50000),
(106, 1, 1, 55000),
(106, 2, 1, 65000),
(107, 1, 2, 55000),
(108, 2, 1, 65000),
(108, 3, 1, 30000),
(109, 5, 1, 60000),
(109, 6, 1, 35000);

-- 8. Seed Order Status History
INSERT INTO order_status_history (order_id, old_status, new_status, reason, changed_at) VALUES
(101, NULL, 'PENDING', NULL, '2026-11-01 11:15:00'),
(101, 'PENDING', 'CONFIRMED', NULL, '2026-11-01 11:17:00'),
(101, 'CONFIRMED', 'PREPARING', NULL, '2026-11-01 11:18:00'),
(101, 'PREPARING', 'READY', NULL, '2026-11-01 11:28:00'),
(101, 'READY', 'DELIVERED', NULL, '2026-11-01 11:42:00'),
(102, NULL, 'PENDING', NULL, '2026-11-03 12:05:00'),
(102, 'PENDING', 'CONFIRMED', NULL, '2026-11-03 12:07:00'),
(102, 'CONFIRMED', 'PREPARING', NULL, '2026-11-03 12:08:00'),
(102, 'PREPARING', 'READY', NULL, '2026-11-03 12:20:00'),
(102, 'READY', 'DELIVERED', NULL, '2026-11-03 12:35:00'),
(103, NULL, 'PENDING', NULL, '2026-11-07 18:30:00'),
(103, 'PENDING', 'CONFIRMED', NULL, '2026-11-07 18:32:00'),
(103, 'CONFIRMED', 'PREPARING', NULL, '2026-11-07 18:33:00'),
(103, 'PREPARING', 'READY', NULL, '2026-11-07 18:43:00'),
(103, 'READY', 'DELIVERED', NULL, '2026-11-07 18:56:00'),
(104, NULL, 'PENDING', NULL, '2026-11-10 19:10:00'),
(104, 'PENDING', 'CONFIRMED', NULL, '2026-11-10 19:12:00'),
(104, 'CONFIRMED', 'PREPARING', NULL, '2026-11-10 19:14:00'),
(104, 'PREPARING', 'READY', NULL, '2026-11-10 19:26:00'),
(104, 'READY', 'DELIVERED', NULL, '2026-11-10 19:48:00'),
(105, NULL, 'PENDING', NULL, '2026-11-12 12:40:00'),
(105, 'PENDING', 'REJECTED', 'Com Ga Xoi Mo is temporarily out of stock', '2026-11-12 12:42:00'),
(106, NULL, 'PENDING', NULL, '2026-11-15 11:30:00'),
(107, NULL, 'PENDING', NULL, '2026-11-15 11:35:00'),
(107, 'PENDING', 'CONFIRMED', NULL, '2026-11-15 11:37:00'),
(108, NULL, 'PENDING', NULL, '2026-11-15 11:40:00'),
(108, 'PENDING', 'CONFIRMED', NULL, '2026-11-15 11:41:00'),
(108, 'CONFIRMED', 'PREPARING', NULL, '2026-11-15 11:43:00'),
(109, NULL, 'PENDING', NULL, '2026-11-15 11:45:00'),
(109, 'PENDING', 'CONFIRMED', NULL, '2026-11-15 11:46:00'),
(109, 'CONFIRMED', 'PREPARING', NULL, '2026-11-15 11:48:00'),
(109, 'PREPARING', 'READY', NULL, '2026-11-15 11:58:00');

-- 9. Seed Deliveries (For UC06 Delivery Performance Report)
INSERT INTO deliveries (delivery_id, order_id, pickup_at, delivered_at, outcome) VALUES
(1, 101, '2026-11-01 11:29:00', '2026-11-01 11:42:00', 'DELIVERED'),
(2, 102, '2026-11-03 12:21:00', '2026-11-03 12:35:00', 'DELIVERED'),
(3, 103, '2026-11-07 18:44:00', '2026-11-07 18:56:00', 'DELIVERED'),
(4, 104, '2026-11-10 19:27:00', '2026-11-10 19:48:00', 'LATE');