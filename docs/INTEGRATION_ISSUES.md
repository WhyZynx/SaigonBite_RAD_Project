# Báo cáo tổng kiểm tra Integration Issues — SaigonBite

## A. Tổng quan

| Nội dung | Kết quả |
|---|---|
| Nhánh tích hợp | `integration/tv3-admin` |
| HEAD rà soát | `cd12cbb94c7916c04e1b6989497f6f631f2da0a2` (`integration/tv3-admin`; merge PR #4 Customer) |
| Ngày rà soát/cập nhật | 21-11-2026 — rà soát sau merge PR #4; kiểm thử lần này ghi tại phần G |
| Commit API Contract | `a106c6e` cập nhật `docs/API_CONTRACT.md`; commit tài liệu nằm trong lịch sử tích hợp |
| Customer | TV1 — 524H0040 |
| Kitchen | TV2 — 524H0130 |
| Admin/Manager | TV3 — 524H0021 |
| Tổng mã vấn đề đang theo dõi | 24: 18 còn mở, 6 đã sửa/đóng trong phạm vi demo |
| Lỗi mã nguồn còn mở | 2 (hai lỗi Manager) |
| Vấn đề tích hợp còn mở | 4 |
| Tính năng chưa triển khai còn mở | 5 |
| Giới hạn demo còn mở | 2 |
| Chưa xác minh còn mở | 5 |
| Cần nhóm thống nhất | 9 chủ đề; liệt kê tại phần F |
| Kết luận | **PARTIALLY WORKING** — các test Backend/SQLite hiện tại đạt; chưa kiểm tra MySQL ghi dữ liệu, trình duyệt đầy đủ hoặc toàn bộ luồng liên module trên cùng một đơn |

| Module | Code/API hiện có theo mã nguồn | Giới hạn được ghi nhận |
|---|---|---|
| Customer | Đọc Hub/Menu, tạo đơn, danh sách/chi tiết/lịch sử đơn; voucher preview và đặt đơn dùng kết quả backend; Customer ánh xạ theo email phiên đăng nhập; Nominatim geocode và OSRM tính tuyến lái xe | Địa chỉ OSM có thể chỉ geocode tới đoạn đường thay vì đúng số nhà; tài khoản/session vẫn là mock |
| Kitchen | Hub list/filter; confirm/reject; PREPARING/READY; ghi status history | Đã kiểm thử SQLite; MySQL đồng thời và giao diện chưa kiểm chứng |
| Admin | Voucher GET/filter/create/update/archive; xem READY orders và mô phỏng READY → DELIVERED; tạo/cập nhật Delivery và Order Status History | Mark as Delivered là demo, không có Shipper thật; Delivery demo không ghi pickup_at nên không đo được thời gian giao thực tế |
| Manager | Sales, Hub Workload, Delivery Reports; truy vấn Orders/Deliveries/Hub và Order Status History | Delivery Report đếm completed theo outcome DELIVERED + delivered_at; Average Delivery Time chỉ tính khi có cặp pickup_at/delivered_at hợp lệ |

Các con số là mã vấn đề duy nhất, không tính lặp các mục liên module ở phần C. Sáu mục đã sửa/đóng là KIT-01, KIT-02, INT-DATA-02 và CUS-01–03. CUS-02/03 được đóng trong phạm vi demo đã ghi rõ; không đồng nghĩa auth hay định tuyến thực tế đã hoàn thiện.

| Đầu mối | Còn mở | Đã sửa | Ghi chú |
|---|---:|---:|---|
| TV1 — Customer | 0 | 3 | CUS-01–03 đã xử lý trong phạm vi demo; phối hợp INT-CUS-KIT-01 |
| TV2 — Kitchen/login | 2 | 2 | KIT-03, AUTH-01; KIT-01/02 đã sửa |
| TV3 — Admin/Manager | 9 | 0 | ADM-01–04, INT-ADMIN-01, MAN-01–04 |
| Backend/Dùng chung | 6 | 1 | INT-DATA-01, INT-AUTH-01, DATA-DB-01, VER-DB-01, VER-UI-01, INT-REPORT-01; INT-DATA-02 đã sửa |
| Phối hợp liên module | 1 | 0 | INT-CUS-KIT-01; tính một lần trong tổng 18 mã còn mở |

Lịch sử merge đã đối chiếu: merge TV2 `07bf1d1` lấy code từ parent `d575ee3`; parser giao hàng được thêm sau trong `1216ca1`. Merge TV1 `4c64205` giữ nguyên `frontend/customer/app.js` và `customer_repository.py` so với parent TV1; thay đổi liên quan là bổ sung `customer_name`/`customer_phone` vào Order Detail. Merge PR #4 hiện tại là `cd12cbb`; diff của merge không thay đổi file Kitchen. Không thấy merge tráo dữ liệu giao hàng.

## B. Bảng tổng hợp theo module

### 1. Customer — TV1

| ID | Vấn đề | Tình huống dễ hiểu | Nguyên nhân | Cách sửa/đề xuất | Người phụ trách | Mức độ | Trạng thái |
|---|---|---|---|---|---|---|---|
| CUS-01 | Nút Apply Voucher chưa áp dụng mã | Nhập mã rồi bấm Apply | Frontend gọi API preview; dùng subtotal, phí giao, discount và total do backend trả để cập nhật checkout. Khi đổi địa chỉ giao, báo giá được lấy lại; khi đặt đơn backend kiểm tra mã và tính tổng cuối lần nữa | Đã nối luồng voucher và dùng kết quả backend cho preview lẫn đơn cuối | TV1; backend phối hợp nếu API đổi | Đã xử lý; vẫn cần trình duyệt nghiệm thu theo tiêu chí đồ án | ĐÃ SỬA |
| CUS-02 | Customer identity phụ thuộc tài khoản demo và hồ sơ DB | Customer khác đăng nhập, đặt đơn hoặc xem lịch sử | Backend không nhận ID từ frontend; ánh xạ email trong phiên đăng nhập tới đúng một hồ sơ Customer. Tài khoản/session vẫn là mock cấu hình sẵn | Đã bỏ ID cố định trong luồng Customer. Giới hạn nhiều tài khoản nằm ở cấu hình mock và hồ sơ tương ứng; triển khai thật cần identity/account store chính thức | TV1; TV2 phối hợp đăng nhập | Thấp trong demo; cao nếu yêu cầu tài khoản thật | ĐÃ SỬA TRONG PHẠM VI DEMO |
| CUS-03 | Nominatim không tìm thấy địa chỉ Hub/Customer khi gửi nguyên văn | Nhập địa chỉ giao thực tế tại Checkout | Truy vấn nguyên văn trước đây thiếu `countrycodes=vn`, không thử truy vấn Hub rút gọn và chỉ trả lỗi chung khi kết quả rỗng | Thêm truy vấn Nominatim `format=jsonv2`, `countrycodes=vn`, `limit=1`; fallback Hub và structured lookup cho Customer; log HTTP status/body; kiểm tra tọa độ trước OSRM; backend tính lại phí khi tạo đơn theo công thức 10.000 + 2.500/km, làm tròn lên 1.000; phụ phí 3.000 nếu trên 5 km; từ chối trên 10 km | TV1 | Đã gọi thật với hai địa chỉ mẫu; OSM trả tọa độ đoạn đường, chưa xác định chính xác cửa nhà | ĐÃ SỬA; CÒN GIỚI HẠN ĐỘ CHÍNH XÁC OSM |

### 2. Kitchen — TV2

| ID | Vấn đề | Tình huống dễ hiểu | Nguyên nhân | Cách sửa/đề xuất | Người phụ trách | Mức độ | Trạng thái |
|---|---|---|---|---|---|---|---|
| KIT-03 | Cập nhật đồng thời chưa kiểm tra trên MySQL | Hai nhân viên cùng đổi trạng thái một đơn | Repository có `with_for_update` và UPDATE có điều kiện; kiểm thử hiện chạy SQLite, chưa có MySQL kiểm thử riêng | Thử hai transaction đồng thời trên database riêng; xác nhận một chuyển tiếp hợp lệ và một history đúng | TV2; phối hợp người cấp MySQL kiểm thử | Trung bình trước khi khẳng định bảo đảm đồng thời trên MySQL | CHƯA XÁC MINH |
| AUTH-01 | Login và session là giả lập trong bộ nhớ | Khởi động lại backend hoặc chạy nhiều tiến trình | Tài khoản demo; session lưu trong bộ nhớ | Chấp nhận nếu đúng phạm vi demo; thống nhất yêu cầu identity trước khi làm auth thật | TV2; TV1/TV3 phối hợp | Thấp cho demo một tiến trình; cao cho triển khai thật | GIỚI HẠN DEMO |

### 3. Admin/Manager — TV3

| ID | Vấn đề | Tình huống dễ hiểu | Nguyên nhân | Cách sửa/đề xuất | Người phụ trách | Mức độ | Trạng thái |
|---|---|---|---|---|---|---|---|
| ADM-01 | Admin Dashboard chưa hoạt động | Chọn Dashboard | Giao diện hiện chỉ có trang Voucher và chặn điều hướng mục khác | Xác nhận Dashboard có trong phạm vi không; nếu có, bổ sung màn hình/API | TV3 | Theo tiêu chí nghiệm thu | THIẾU TÍNH NĂNG |
| ADM-02 | Hub và Menu chưa có trang quản trị | Chọn Hubs & Menu | Không có API quản trị; API Customer chỉ đọc hub/menu | Xác nhận phạm vi và quyền quản trị với TV1/shared | TV3; TV1/shared phối hợp | Theo tiêu chí nghiệm thu | THIẾU TÍNH NĂNG |
| ADM-03 | User Management chưa triển khai | Chọn Users | Không có kho tài khoản/API quản lý; đăng nhập còn giả lập | Xác nhận yêu cầu với TV2 trước khi triển khai | TV3; TV2 phối hợp | Theo tiêu chí nghiệm thu | THIẾU TÍNH NĂNG |
| ADM-04 | Chưa sửa được trường Voucher đã tạo | Sửa mã, mức giảm hoặc thời hạn | API có GET, POST và PATCH archive; không có API cập nhật trường Voucher | Chỉ bổ sung nếu nhóm xác nhận chức năng bắt buộc | TV3 | Theo tiêu chí nghiệm thu | THIẾU TÍNH NĂNG |
| INT-ADMIN-01 | Hub chọn cho Voucher không được lưu | Tạo Voucher theo một Hub rồi tải lại | API nhận nhãn `hub`, nhưng repository không lưu; schema không có quan hệ Voucher-Hub; GET trả nhãn mặc định All hubs | Xác nhận Voucher toàn cục hay theo Hub; chỉnh nhãn/API hoặc thống nhất schema theo quyết định | TV3; shared nếu cần schema | Trung bình nếu người dùng hiểu nhãn là giới hạn áp dụng thật | VẤN ĐỀ TÍCH HỢP |
| MAN-01 | Manager Dashboard, Hub Operations, Order History chưa triển khai | Chọn mục ngoài Reports | Giao diện chỉ có Reports và chặn các mục khác | Xác nhận phạm vi; không xem các mục menu là tính năng hoàn thành | TV3 | Theo tiêu chí nghiệm thu | THIẾU TÍNH NĂNG |
| MAN-02 | Lỗi API Reports bị trình bày như dữ liệu rỗng | `frontend/manager/app.js` | `fetchReport()` ném lỗi khi HTTP không thành công; `renderReport()` phân biệt lỗi tải với dữ liệu rỗng và hiển thị thông báo lỗi | Cần kiểm tra regression với API 200 rỗng và lỗi HTTP; chưa có browser E2E | TV3 | Trung bình | ĐÃ SỬA TRONG CODE; CẦN REGRESSION TEST |
| MAN-03 | Thời gian trung bình có giá trị cố định | `backend/app/routers/reports.py`, `backend/app/repositories/report_repository.py` | Tính thời lượng từ pickup_at và delivered_at hợp lệ; không dùng giá trị phút cố định; thiếu timestamp thì hiển thị — | Bổ sung test Delivery có đủ timestamp, thiếu timestamp và timestamp không hợp lệ | TV3 | Trung bình | ĐÃ SỬA TRONG CODE; CẦN REGRESSION TEST |
| MAN-04 | Cột Pending Orders không đếm riêng trạng thái PENDING | `backend/app/routers/reports.py`, `frontend/manager/app.js` | Đổi cách thể hiện thành Not Delivered; API tính tổng đơn trừ đơn DELIVERED, không gọi nhầm là Pending | Test Hub Workload với nhiều trạng thái để xác nhận KPI và bảng theo Hub | TV3 | Trung bình | ĐÃ SỬA NHÃN; CẦN REGRESSION TEST |

### 4. Backend / Shared

| ID | Vấn đề | Tình huống dễ hiểu | Nguyên nhân | Cách sửa/đề xuất | Người phụ trách | Mức độ | Trạng thái |
|---|---|---|---|---|---|---|---|
| INT-DATA-01 | Recipient, Delivery Phone, Address, Note gộp vào một chuỗi | Customer tạo đơn, Kitchen cần hiển thị riêng từng thông tin | Request/schema chỉ có `delivery_address`; repository lưu chuỗi; Order Detail trả lại chuỗi; Kitchen dựa vào nhãn để tách | Nhóm chốt contract. Không thêm cột/bảng trước khi thống nhất; giữ tương thích Customer/Kitchen | TV1, TV2, backend/shared; TV3 xác nhận schema chung | Trung bình nếu cần truy vấn riêng; thấp nếu chấp nhận chuỗi demo | VẤN ĐỀ TÍCH HỢP |
| INT-AUTH-01 | CSS/JS Customer không có cùng kiểm soát truy cập như trang | Gọi `/customer/app.js` hoặc `/customer/style.css` khi chưa đăng nhập | Middleware bảo vệ trang Customer nhưng không gán vai trò cho hai đường dẫn tài nguyên; API Customer vẫn kiểm tra role | Nhóm xác định tài nguyên có chủ ý công khai hay cần bảo vệ; kiểm tra chính sách trước khi sửa | TV2/shared; TV1 xác nhận chính sách | Thấp trong demo; phụ thuộc yêu cầu bảo mật | VẤN ĐỀ TÍCH HỢP |
| DATA-DB-01 | Số dòng Orders và lịch sử cao hơn seed dự kiến | Đối chiếu dữ liệu database với seed | Lần đọc trước có customers 4, hubs 4, brands 3, menu_items 8, vouchers 5, orders 11, order_items 20, order_status_history 37, deliveries 4; nguồn của 2/4/5 dòng vượt seed trong ba bảng đơn hàng chưa rõ | Chủ sở hữu dữ liệu xác nhận bằng cách chỉ đọc; không xóa/reseed | Backend/shared; chủ sở hữu DB nhóm | Thấp khi chỉ đọc; cần rõ nguồn trước reset | CHƯA XÁC MINH |
| VER-DB-01 | Chưa thử luồng ghi trên MySQL riêng | Tạo đơn → Kitchen cập nhật → Customer/Manager đọc lại | Không có database MySQL thử nghiệm được phép dùng; database nhóm không dùng để thử ghi | Cấp MySQL test riêng, chạy cùng một order_id và kiểm tra history/rollback/đồng thời | Backend/shared và từng chủ module | Cao trước khi tuyên bố MySQL E2E đạt | CHƯA XÁC MINH |
| VER-UI-01 | Chưa nghiệm thu giao diện toàn bộ bằng trình duyệt | Đăng nhập và thao tác các màn hình chính | Chưa có bằng chứng đầy đủ về render, điều hướng, console và network | TV1/TV2/TV3 kiểm tra module mình, sau đó chạy luồng liên module | Mỗi thành viên; shared hỗ trợ route | Trung bình trước nghiệm thu giao diện | CHƯA XÁC MINH |
| INT-REPORT-01 | Delivery Report thiếu cặp timestamp để tính thời lượng | `backend/app/routers/admin.py`, `backend/app/routers/reports.py`, `backend/tests/test_reports.py` | Admin demo ghi `outcome=DELIVERED` và `delivered_at`, không ghi `pickup_at`. Manager đếm Completed Deliveries dựa trên `outcome=DELIVERED` và `delivered_at IS NOT NULL`; Average Delivery Time chỉ tính khi có đủ hai timestamp hợp lệ | Test Admin Delivered → Manager Delivery Report trên cùng order_id; test Delivery thiếu pickup_at và Delivery có đủ timestamp | TV3 | Trung bình | ĐÃ SỬA LOGIC; CHỜ CHẠY TEST |

## C. Lỗi liên module và luồng chính

### C-1. Customer → Kitchen: Note/Phone

| ID | Module liên quan | Luồng bị lỗi | Biểu hiện | Nguyên nhân | Người phối hợp | Hướng xử lý |
|---|---|---|---|---|---|---|
| INT-CUS-KIT-01 | Customer, API, Kitchen | Form → POST → lưu Order → GET Order Detail → Kitchen render | Người dùng báo Recipient `Customer Test12334`, Phone `324324`, Note `1111111`; Kitchen hiện Note là `324324`. Người dùng cũng báo Customer Name `Nguyen Minh Anh`, Account Phone `0901234567`, Distance `3.5 km`. | Chưa xác định cho đơn bị báo. Mã hiện tại ghép nhãn riêng, lưu nguyên chuỗi, trả nguyên chuỗi và parser tách đúng trên dữ liệu thử tổng hợp. | TV1 kiểm tra form/payload; backend kiểm tra dữ liệu lưu/response; TV2 nếu API đúng mà giao diện sai | Tái hiện bằng cùng một order_id trên môi trường riêng; ghi nhận form, payload đã che thông tin, DB và API. Không quy lỗi theo ảnh đơn lẻ |

| Bước truy vết | Bằng chứng trong mã/kiểm thử | Kết quả |
|---|---|---|
| Customer Form | `frontend/customer/index.html` có ID riêng `address`, `recipient`, `phone`, `note`; `placeOrder()` đọc riêng rồi ghép nhãn `Recipient`, `Phone`, `Note` sau địa chỉ | Đã đối chiếu code hiện tại sau PR #4; chưa chạy trình duyệt để xác nhận giá trị DOM thực |
| Request Payload | POST gửi `delivery_address` dạng nhiều dòng; không gửi từng trường riêng | Đã đọc code; không thu payload của đơn người dùng báo |
| SQLite API | Kiểm thử mới POST chuỗi chứa đúng Recipient/Phone/Note, rồi GET Order Detail | PASS: API trả chuỗi giống hệt, không hoán đổi |
| Kitchen parser | Chạy hàm hiện tại với payload nhiều dòng theo định dạng Customer | PASS trong lần rà soát 21-11-2026: Recipient, Phone, Note và Address được tách đúng; không phải browser test |
| Customer UI và Kitchen UI trên trình duyệt | Chưa có công cụ/browser evidence trong lượt này | NOT TESTED |
| Bản ghi thật bị báo | Không truy cập MySQL nhóm, không có request/response của đơn đó | CHƯA XÁC MINH |

### C-2. Customer → Kitchen → Customer → Manager

| Chặng | Điều đã xác minh | Giới hạn/kết quả |
|---|---|---|
| Customer tạo đơn | POST → lưu → GET Order Detail chạy trên SQLite riêng, chuỗi giao hàng giữ nguyên | Không phải MySQL và không chạy từ giao diện trình duyệt |
| Kitchen nhận/lọc đơn | Kiểm thử SQLite lọc theo hub và các trạng thái; API lấy hub có kiểm thử | PASS trên SQLite; chưa kiểm tra chọn hub bằng trình duyệt |
| Kitchen cập nhật trạng thái | SQLite tests xác nhận PENDING → CONFIRMED/REJECTED, CONFIRMED → PREPARING, PREPARING → READY và history | PASS; chưa xác minh khóa đồng thời trên MySQL |
| Customer đọc trạng thái | Kiểm thử Kitchen gọi Order Detail sau khi cập nhật trạng thái và thấy status mới | PASS trong fixture SQLite; không phải cùng đơn vừa POST trong test Customer mới |
| Manager Sales/Hub Workload | API truy vấn bảng Orders theo thời gian; code có thể đọc Order do Customer tạo | Chưa chạy báo cáo trên cùng order_id |
| Manager Delivery Report | Admin tạo/cập nhật Delivery khi đánh dấu đơn đã giao; luồng này ghi delivered_at nhưng không ghi pickup_at | Chưa xác minh phép tính thời lượng với đủ timestamp; xem INT-REPORT-01 |
| Toàn bộ E2E | Chưa chạy một order_id xuyên suốt cả bốn vai trò | NOT TESTED |

## D. Các lỗi đã sửa hoặc xử lý trong phạm vi demo

| ID | Lỗi trước khi sửa | File đã sửa | Cách sửa | Test xác nhận | Kết quả |
|---|---|---|---|---|---|
| KIT-01 | Kitchen cố định Hub ID 1 | Commit `1216ca183ee4165b6d97513b365c87538462d732`: `backend/app/routers/kitchen.py`, `backend/app/repositories/order.py`, `backend/tests/test_kitchen.py`, ba file `frontend/kitchen/` | Thêm API danh sách Hub, bộ chọn hub và lọc queue theo hub đang chọn | SQLite test danh sách Hub/lọc đơn; GET MySQL chỉ đọc trước đó thấy order 111 thuộc hub 2 | Đã sửa; thao tác chọn hub trên browser và MySQL ghi chưa kiểm tra |
| KIT-02 | Kitchen chỉ đọc các trường note riêng, API Customer chỉ trả chuỗi `delivery_address` | Commit `1216ca183ee4165b6d97513b365c87538462d732`: `frontend/kitchen/app.js` | Thêm parser nhãn Recipient/Phone/Note, không đổi schema/API | Node syntax và chạy parser hiện tại với dữ liệu tổng hợp chính xác | PASS cho parser thuần; chưa kiểm tra giao diện/browser và đơn người dùng báo |
| INT-DATA-02 | Pydantic từng cho phép 500 ký tự nhưng Model/SQL giới hạn 255 | `backend/app/schemas.py`; thêm `backend/tests/test_customer.py` | Giới hạn request còn 255 để khớp Model và SQL hiện có; không sửa schema/database | SQLite/Pydantic chấp nhận 255, từ chối 256; POST/GET test chuỗi giao hàng | PASS trên SQLite; chưa ghi MySQL |
| CUS-02 | Customer API/frontend phụ thuộc Customer ID cố định | `backend/app/routers/customer.py`, `frontend/customer/app.js`, `backend/app/auth.py` | Router lấy email phiên đăng nhập để ánh xạ hồ sơ; profile API trả customer_type từ DB và UI hiển thị Local/Tourist; không nhận ID do frontend gửi | `backend/tests/test_customer.py::test_customer_identity_maps_from_session_email` có hồ sơ LOCAL/TOURIST, xác nhận profile trả đúng customer_type và lịch sử/chi tiết được giới hạn theo Customer; không chạy lại trong lần cập nhật này | Đã sửa cho các tài khoản mock có hồ sơ khớp; auth/session vẫn là demo |
| CUS-03 | Địa chỉ nguyên văn bị Nominatim trả về danh sách rỗng, UI báo lỗi Hub chung chung | `backend/app/delivery_fee_service.py`, `backend/app/routers/customer.py`, `frontend/customer/app.js`, `frontend/customer/index.html` | Bổ sung fallback Hub `128 Nguyen Hue, Ho Chi Minh City, Vietnam`; Customer thử structured lookup; cache địa chỉ Hub thành công; pacing Nominatim/OSRM; OSRM nhận `lon,lat`; báo lỗi upstream kèm status/body trong log; checkout hiển thị km theo định dạng `vi-VN` | `backend/tests/test_delivery_fee_service.py`: 10 test mock qua. Gọi thật với Hub `128 Nguyen Hue, District 1, Ho Chi Minh City` và Customer `12 Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh`: OSRM trả 395,1 m (0,395 km), phí 11.000 VND, surcharge 0 VND. Nominatim chỉ trả tọa độ đoạn đường, không phải pin chính xác số nhà | Đã sửa; khoảng cách thật tới cửa nhà phụ thuộc độ chi tiết dữ liệu OSM |
| CUS-01 | Apply Voucher chưa nối và preview chưa dùng tổng backend | `frontend/customer/app.js`, `backend/app/routers/customer.py`, `backend/app/repositories/customer_repository.py` | Apply gọi API preview; checkout hiển thị subtotal, phí, discount và `total` từ server; đổi địa chỉ giao gọi lại preview; khi POST tạo đơn backend kiểm tra voucher và tính lại tổng cuối | `backend/tests/test_customer.py` có test preview, minimum order, voucher đã dùng và tổng đơn; không chạy lại trong lần cập nhật này | Đã sửa trong code; chưa nghiệm thu UI bằng browser |

## E. Việc từng thành viên cần làm

| Thành viên | Module | Việc cần làm | Mức ưu tiên | Điều kiện hoàn thành |
|---|---|---|---|---|
| TV1 — 524H0040 | Customer | CUS-01–03 đã xử lý trong code; CUS-03 dùng Nominatim + OSRM, phí và khoảng cách được backend tính lại; cùng TV2 truy vết INT-CUS-KIT-01 theo cùng order_id | Cần nghiệm thu UI; lưu ý geocode OSM có thể chỉ tới đoạn đường | Test mock 10 case qua; đã kiểm tra live tuyến mẫu 395,1 m, phí 11.000 VND, surcharge 0 VND; preview/order dùng quote backend |
| TV2 — 524H0130 | Kitchen/login | Cùng TV1 tái hiện Note/Phone; thử bộ chọn hub/parser trên trình duyệt; kiểm tra cập nhật đồng thời trên MySQL test; xác nhận chính sách asset/login | Cao trước khi tuyên bố Kitchen/MySQL hoàn tất | Browser evidence; MySQL test chứng minh chuyển tiếp và history không sai khi đua |
| TV3 — 524H0021 | Admin/Manager | Hoàn thiện logic Admin Delivered và Manager Delivery Report; test Hub Workload; đồng bộ tài liệu và kiểm tra UI | Cao trước khi gửi review PR #2 | Test Admin Delivered, Delivery Report và Hub Workload đạt; tài liệu mô tả đúng giới hạn demo; có kết quả test mới |
| Backend/Shared — cần chỉ định | Database/API/report | Chốt delivery contract; cấp DB test; xác minh nguồn dữ liệu vượt seed; thống nhất chủ thể ghi Delivery và status lifecycle | Cao cho API/DB E2E | Có người chịu trách nhiệm được nhóm chỉ định; test dùng DB riêng và theo cùng order_id |
| TV1 + TV2 + Backend | Customer ↔ Kitchen | Truy vết sự cố Note/Phone theo các bước ở phần C | Cao | Xác định được chặng đầu tiên sai; không dựa vào phỏng đoán |

## F. Những nội dung nhóm cần thống nhất

| STT | Nội dung cần thống nhất | Vì sao cần thống nhất | Các phương án | Đề xuất | Thành viên xác nhận |
|---:|---|---|---|---|---|
| 1 | Recipient, Delivery Phone, Address, Special Note | Hiện gộp trong một chuỗi; Kitchen phải tách theo nhãn | Giữ chuỗi gắn nhãn; hoặc thêm trường cấu trúc ở API/model/schema | Tạm giữ contract hiện có đến khi chọn; nếu đổi phải giữ tương thích Customer/Kitchen và duyệt schema | TV1, TV2, TV3, Backend/Shared |
| 2 | API Order Detail cho giao hàng | API hiện trả `delivery_address`, Customer Name/Phone và khoảng cách; không có field riêng cho giao hàng | Tiếp tục parse chuỗi; hoặc thêm field API riêng (có thể additive) | Ưu tiên contract tường minh; không tự đổi khi chưa có đồng thuận | TV1, TV2, Backend |
| 3 | Vòng đời trạng thái đơn | Kitchen xử lý đến READY; enum còn DELIVERED, FAILED, CANCELLED | Giao hàng module khác quản lý; hoặc mở rộng người phụ trách/endpoint | Chốt trạng thái hợp lệ, vai trò chuyển trạng thái và history cho từng bước | TV1, TV2, TV3, Backend |
| 4 | Nguồn ghi pickup_at và cách tính thời lượng giao | Dự án chưa có Shipper; Admin chỉ mô phỏng xác nhận giao hàng | Không ghi pickup_at giả; hoặc bổ sung sự kiện pickup nếu sau này triển khai Shipper | Hiện tại giữ pickup_at NULL với Admin demo. Completed Deliveries không phụ thuộc pickup_at; Average Delivery Time chỉ tính khi có đủ hai timestamp hợp lệ | TV3, backend/shared và delivery owner |
| 5 | Voucher áp dụng toàn hệ thống hay theo Hub | API nhận nhãn hub nhưng database không lưu quan hệ | Voucher global; hoặc thêm quan hệ theo Hub sau khi duyệt | Nếu global, bỏ/đổi nhãn Applicable Hub; nếu theo Hub, thống nhất schema/API và áp dụng voucher | TV1, TV3, Backend |
| 6 | Định nghĩa Pending trong Hub Workload | UI gọi cột là Pending nhưng API tính mọi đơn chưa DELIVERED | Chỉ status PENDING; hoặc mọi đơn chưa giao với nhãn khác | Dùng status PENDING nếu giữ nhãn hiện tại | TV3 |
| 7 | Định nghĩa On-Time Rate | Code đếm outcome DELIVERED; schema có DELIVERED/LATE nhưng không thấy writer cập nhật outcome hoặc ETA | Dựa vào outcome do delivery owner ghi; hoặc thêm quy tắc ETA/giờ hẹn | Chốt ý nghĩa, nguồn dữ liệu và cách ghi trước khi gọi là on-time thực tế | TV3, Backend/Shared, delivery owner |
| 8 | Login/Customer identity | Session còn giả lập; Customer đã ánh xạ theo email phiên đăng nhập tới đúng một hồ sơ DB | Chấp nhận cấu hình mock cho demo; hoặc triển khai identity/account store và session bền vững | Luồng hiện tại không còn cố định Customer ID; xác nhận giới hạn mock trước nghiệm thu thật | TV1, TV2, TV3 |
| 9 | Phạm vi Admin/Manager demo | Dashboard, Hub/Menu/Users, Hub Operations/Order History và update Voucher còn thiếu | Bắt buộc hoàn thiện; hoặc đánh dấu ngoài phạm vi demo | Đối chiếu tiêu chí đồ án trước khi giao làm tính năng | TV3 và nhóm |

## G. Kết quả kiểm thử

Các kết quả trong bảng đầu là log kiểm thử đã ghi nhận trước lần chạy mới ngày 21-11-2026. Bảng tiếp theo ghi riêng kết quả mới; các mục MySQL và trình duyệt vẫn chưa được kiểm thử.

| Kiểm tra | Môi trường | Kết quả | Bằng chứng/ghi chú |
|---|---|---|---|
| `python -m compileall -q app tests` | Backend, Python 3.13 | PASS | Chạy sau sửa giới hạn địa chỉ |
| `pytest -q` | SQLite fixtures | PASS — 16 passed, 93 warnings | Hai test mới: giới hạn 255/256 và POST → GET giữ nguyên thông tin giao hàng; warnings là deprecation từ FastAPI/Starlette/SQLAlchemy |
| `node --check frontend/customer/app.js` | Node 24 | PASS | Chạy sau sửa |
| `node --check frontend/kitchen/app.js` | Node 24 | PASS | Chạy sau sửa |
| `node --check frontend/admin/app.js` | Node 24 | PASS | Chạy sau sửa |
| `node --check frontend/manager/app.js` | Node 24 | PASS | Chạy sau sửa |
| Parser Kitchen trên chuỗi mẫu Note/Phone | Node, hàm lấy trực tiếp từ `frontend/kitchen/app.js` | PASS | Trả đúng Recipient `Customer Test12334`, Phone `324324`, Note `1111111` |
| Customer POST → Order Detail | SQLite riêng trong pytest (kết quả ghi từ lần chạy trước) | PASS | Chuỗi giữ nguyên; customer name/phone lấy từ hồ sơ fixture; khoảng cách và phí do backend lấy theo tuyến hub/điểm đến, không phải hằng số 3.5 |
| Kitchen transitions/history | SQLite riêng trong pytest | PASS | Confirm, reject có lý do, prepare, ready, invalid transition, missing order và history |
| Router registration/import | Import app trong pytest | PASS | TestClient tải ứng dụng và gọi các API Customer/Kitchen được kiểm thử |
| `git diff --check` | Working tree | PASS | Lệnh chạy thành công; README có cảnh báo line ending LF/CRLF, không phải lỗi whitespace từ code vừa sửa |
| MySQL connection/write | Không dùng database nhóm | NOT TESTED | Không đọc `.env`, không chạy SQL, không ghi SaigonBiteDB; chưa có MySQL test riêng |
| MySQL — kết quả đọc trước đây | MySQL 8.0.46, chỉ đọc | Đã kiểm tra trước đó | Đủ 9 bảng, đã đếm 9 khóa ngoại; order 111 từng thấy ở hub 2. Không kết nối lại lượt này; đây không phải kiểm thử ghi |

| Browser UI/E2E | Chưa có browser evidence | NOT TESTED | JavaScript syntax và parser unit probe không chứng minh render, thao tác, console hoặc network |
| Manager API and Reports trên DB test | Chưa chạy riêng | NOT TESTED | Cần test Pending, API error, Delivery có cả pickup_at và delivered_at, duration và dữ liệu cùng order_id |
| Toàn luồng Customer → Kitchen → Customer → Manager | Chưa chạy cùng một order_id | NOT TESTED | Các đoạn riêng có test SQLite, nhưng không phải end-to-end |

### Lần chạy mới nhất — 21-11-2026, tại HEAD `cd12cbb94c7916c04e1b6989497f6f631f2da0a2`

| Kiểm tra | Kết quả | Bằng chứng/giới hạn |
|---|---|---|
| `python -m compileall -q app tests` | PASS | Chạy trong `backend`; exit code 0, không có output |
| `python -m pytest -q` | PASS — 34 passed, 104 warnings in 4.99s | Chạy trong `backend`; fixtures SQLite. Warnings: Starlette/httpx deprecation và SQLAlchemy `datetime.utcnow()` deprecation |
| `node --check` cho kitchen, customer, admin, manager | PASS | Cả bốn lệnh kết thúc exit code 0 |
| Kitchen parser với payload định dạng Customer | PASS | Parser trích Recipient `Test Recipient`, Phone `0900000000`, Note `Leave at reception`, Address `12 Nguyen Hue, District 1` |
| Kitchen status/history và Customer API tests | PASS trong pytest | Test suite hiện tại có coverage list/filter, confirm/reject, PREPARING/READY, history, Customer POST → detail và auth; đây là test SQLite, không phải E2E MySQL |
| MySQL E2E / ghi dữ liệu / concurrency | NOT TESTED | Không kết nối hoặc ghi database nhóm; chưa có MySQL test database được cấp |
| Browser E2E | NOT TESTED | Không kiểm tra render, thao tác thực, console hoặc network trong trình duyệt |
| `git diff --check` | PASS | Chạy sau khi cập nhật tài liệu; không báo lỗi whitespace |

## H. Checklist trước khi tạo PR vào main

| Điều kiện | Trạng thái | Ghi chú |
|---|---|---|
| Customer hoạt động | PARTIAL | Voucher preview/order dùng giá trị backend; identity ánh xạ theo email trong giới hạn mock; khoảng cách dùng Nominatim/OSRM, nhưng độ chính xác tới số nhà phụ thuộc dữ liệu OSM; browser chưa xác minh |
| Kitchen hoạt động | PARTIAL | SQLite statuses/history và hub API đạt; browser, MySQL/concurrency chưa xác minh |
| Admin hoạt động | PARTIAL | Voucher list/create/archive có code; các màn hình khác chưa triển khai |
| Manager Reports hoạt động | PARTIAL | Có API/ giao diện Reports nhưng Pending label/count sai khác; lỗi API bị hiểu như rỗng; một số metrics giả lập |
| API contract thống nhất | NOT YET | Giao hàng còn là chuỗi có nhãn; nhóm cần quyết định field contract |
| Database tương thích | PARTIAL | `delivery_address` API/model/SQL cùng giới hạn 255 sau sửa; MySQL runtime chưa thử |
| Luồng tạo và xử lý đơn hoàn chỉnh | NOT TESTED | Chưa chạy cùng order_id trên toàn hệ thống/MySQL test |
| Không còn lỗi nghiêm trọng | NOT VERIFIED | Còn vấn đề báo cáo và phần chưa xác minh; nhóm cần đánh giá theo tiêu chí nghiệm thu |
| Giới hạn demo đã được ghi rõ | PASS | Customer ID cứng đã bỏ; tài liệu ghi rõ ánh xạ email/mock auth, giới hạn geocode địa chỉ OSM và số liệu thời gian cố định |
| Test mới nhất | PASS | 21-11-2026 tại `cd12cbb`: compileall, 34 pytest và bốn Node syntax checks đạt; Kitchen parser probe đạt. MySQL E2E và Browser E2E vẫn NOT TESTED |

## Kết luận

**PARTIALLY WORKING.** Sau merge PR #4, toàn bộ 34 backend tests, compile check, bốn frontend syntax checks và Kitchen parser probe đạt trong lần review này. Không có file Kitchen thay đổi trong merge PR #4 và không tái hiện được lỗi Kitchen mới. Vẫn chưa có MySQL E2E, concurrency trên MySQL, browser E2E, hoặc một order_id chạy xuyên Customer → Kitchen → Customer → Manager. INT-CUS-KIT-01 vẫn chưa được tái hiện trên đơn người dùng báo; INT-REPORT-01 vẫn cần TV3 xác minh với đủ timestamp. Các giới hạn demo và issue mở khác vẫn giữ trạng thái, owner như các bảng trên.

## Notification feature status - TV2 feature branch

This is a feature-branch update, not a claim that Notification has been merged into `integration/tv3-admin`. The code is on `feature/tv2-notification`, based on `b4db250`.

| Area | Current evidence | Owner / next action | Status |
|---|---|---|---|
| Kitchen rejection to notification | Kitchen commits `REJECTED` and status history first, then calls NotificationService best-effort. Notification persistence failure is logged and does not reverse/fail the rejection. A storage failure can leave a rejected order without a notification; retrying the rejection does not recreate it. | TV2: decide whether this documented best-effort tradeoff meets demo acceptance. | Implemented; MySQL behavior not verified |
| Customer session ownership and badge refresh | Customer endpoints derive identity from the active session email and query/update only rows matching that Customer. Cross-Customer mark-read returns 404. The unread count now loads at page initialization, when opening the bell, and after mark-read; no live refresh occurs while the panel is closed because polling is not used. | TV1: confirm bell, dropdown, read state, count refresh, and opening order detail in a browser. | Backend covered by SQLite tests; browser/UI confirmation pending |
| Database and migration | `database/schema.sql`, SQLAlchemy model and additive migration define the notification columns, FKs, indexes, and unique `(order_id, notification_type)` rule. Fresh database setup creates the table through `schema.sql`; existing databases require the additive migration. The migration selects `SaigonBiteDB` explicitly. | TV3: confirm shared database schema/migration and model integration. For testing, use a disposable DB and a temporary migration copy with `USE` changed; verify `SELECT DATABASE()` before executing. Do not run the checked-in migration against the team database. | Migration not run |
| UTC timestamps | Notification API now emits ISO 8601 timestamps with an explicit `+00:00` UTC offset; a response-level SQLite regression test covers it. | TV2; TV1 to confirm displayed local time in browser. | SQLite verified |

### Tests and verification

After adding the UTC timestamp and duplicate-insert regression tests, `python -m pytest -q` on the backend reports **41 passed** (including existing tests); the seven focused notification tests pass on SQLite. The tests cover rejection, ownership, unread count, mark-read, unauthenticated/wrong-role access, invalid reason, duplicate insertion fallback, and best-effort failure handling.

Not completed: MySQL migration or E2E, browser E2E, and concurrent MySQL transition/insert testing. SQLite tests do not establish MySQL locking, transaction, or migration behavior. The checked-in migration has not been executed.
