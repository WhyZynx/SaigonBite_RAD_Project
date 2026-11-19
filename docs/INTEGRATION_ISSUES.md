# Báo cáo tổng kiểm tra Integration Issues — SaigonBite

## A. Tổng quan

| Nội dung | Kết quả |
|---|---|
| Nhánh tích hợp | `integration/tv3-admin` |
| HEAD rà soát | `1216ca183ee4165b6d97513b365c87538462d732` |
| Ngày rà soát | 19-11-2026 |
| Customer | TV1 — 524H0040 |
| Kitchen | TV2 — 524H0130 |
| Admin/Manager | TV3 — 524H0021 |
| Tổng mã vấn đề đang theo dõi | 24: 21 còn mở, 3 đã sửa |
| Lỗi mã nguồn còn mở | 2 |
| Vấn đề tích hợp còn mở | 4 |
| Tính năng chưa triển khai còn mở | 6 |
| Giới hạn demo còn mở | 4 |
| Chưa xác minh còn mở | 5 |
| Cần nhóm thống nhất | 9 chủ đề; liệt kê tại phần F |
| Kết luận | **PARTIALLY WORKING** — có kiểm thử SQLite cho một số API/luồng Kitchen; chưa kiểm tra MySQL ghi dữ liệu, trình duyệt đầy đủ hoặc toàn bộ luồng liên module trên cùng một đơn |

| Module | Code/API hiện có theo mã nguồn | Giới hạn được ghi nhận |
|---|---|---|
| Customer | Đọc Hub/Menu, tạo đơn, danh sách/chi tiết/lịch sử đơn | Apply Voucher chưa nối; Customer ID và khoảng cách/phí còn giá trị demo |
| Kitchen | Hub list/filter; confirm/reject; PREPARING/READY; ghi status history | Đã kiểm thử SQLite; MySQL đồng thời và giao diện chưa kiểm chứng |
| Admin | Voucher GET/filter/create/archive | Dashboard, Hub/Menu/Users và update Voucher chưa có luồng hoàn chỉnh; Hub label không được lưu |
| Manager | Sales, Hub Workload, Delivery Reports; repository truy vấn Order/Delivery/Hub | Hai lỗi trình bày/tính Pending; Delivery producer chưa có; một số thời gian demo |

Các con số là mã vấn đề duy nhất, không tính lặp các mục liên module ở phần C. Ba mục đã sửa là KIT-01, KIT-02 và INT-DATA-02.

| Đầu mối | Còn mở | Đã sửa | Ghi chú |
|---|---:|---:|---|
| TV1 — Customer | 3 | 0 | CUS-01–03; phối hợp INT-CUS-KIT-01 |
| TV2 — Kitchen/login | 2 | 2 | KIT-03, AUTH-01; KIT-01/02 đã sửa |
| TV3 — Admin/Manager | 9 | 0 | ADM-01–04, INT-ADMIN-01, MAN-01–04 |
| Backend/Dùng chung | 6 | 1 | INT-DATA-01, INT-AUTH-01, DATA-DB-01, VER-DB-01, VER-UI-01, INT-REPORT-01; INT-DATA-02 đã sửa |
| Phối hợp liên module | 1 | 0 | INT-CUS-KIT-01; tính một lần trong tổng 21 mã còn mở |

Lịch sử merge đã đối chiếu: merge TV2 `07bf1d1` lấy code từ parent `d575ee3`; parser giao hàng được thêm sau trong `1216ca1`. Merge TV1 `4c64205` giữ nguyên `frontend/customer/app.js` và `customer_repository.py` so với parent TV1; thay đổi liên quan là bổ sung `customer_name`/`customer_phone` vào Order Detail. Không thấy merge tráo dữ liệu giao hàng.

## B. Bảng tổng hợp theo module

### 1. Customer — TV1

| ID | Vấn đề | Tình huống dễ hiểu | Nguyên nhân | Cách sửa/đề xuất | Người phụ trách | Mức độ | Trạng thái |
|---|---|---|---|---|---|---|---|
| CUS-01 | Nút Apply Voucher chưa áp dụng mã | Nhập mã rồi bấm Apply | Giao diện chỉ hiện thông báo chưa kết nối; `placeOrder()` không gửi `voucher_code`; backend chỉ kiểm tra mã nếu yêu cầu có trường này | Nối giao diện với API/luồng kiểm tra đã thống nhất; hiển thị mức giảm và tổng tiền do backend trả | TV1; backend phối hợp nếu cần API xem trước | Trung bình; cao nếu voucher thuộc nghiệm thu | THIẾU TÍNH NĂNG |
| CUS-02 | Customer ID cố định là 1 | Tài khoản khác đặt đơn hoặc xem lịch sử | Frontend gửi `customer_id: 1`; router chỉ cho phép ID 1; phiên đăng nhập chưa ánh xạ hồ sơ riêng | Xác nhận demo chỉ có một Customer hay cần ánh xạ tài khoản sang Customer | TV1; TV2 phối hợp đăng nhập | Thấp cho demo một khách; cao nếu cần nhiều tài khoản | GIỚI HẠN DEMO |
| CUS-03 | Khoảng cách/phí giao hàng là giá trị demo | Đặt từ các địa chỉ hoặc hub khác nhau | Frontend và router dùng 3.5 km; router dùng phí cố định 15.000 và không dùng khoảng cách gửi lên | Ghi rõ giới hạn hoặc thống nhất cách tính theo tuyến trước khi triển khai | TV1; nhóm xác nhận chính sách | Thấp nếu là demo; cao nếu cần tính thực | GIỚI HẠN DEMO |

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
| MAN-02 | Lỗi API Reports bị trình bày như dữ liệu rỗng | API trả 401/403/500 hoặc lỗi mạng | `fetchBackendReport()` trả `null`; `renderReport()` dùng chung trạng thái rỗng cho lỗi và danh sách rỗng | TV3 phân biệt lỗi tải với API thành công nhưng không có dòng; kiểm tra riêng 200 rỗng, 401, 500 | TV3 | Trung bình; che giấu lỗi tải | LỖI — mã nguồn xác nhận, chưa kiểm tra trình duyệt |
| MAN-03 | Thời gian trung bình có giá trị cố định | Xem thời gian chuẩn bị/giao | Hub workload trả 11 phút; Delivery trả 24 phút; Sales dùng mặc định 24 phút khi thiếu delivery có timestamp | Gắn nhãn demo hoặc tính từ dữ liệu thời gian theo yêu cầu | TV3 | Thấp nếu ghi rõ demo; cao nếu coi là số đo thật | GIỚI HẠN DEMO |
| MAN-04 | Cột Pending Orders không đếm riêng trạng thái PENDING | Xem Hub Workload có đơn REJECTED/FAILED/CANCELLED/READY | API tính tổng đơn trừ DELIVERED rồi trả dưới nhãn Pending; giá trị gồm nhiều trạng thái không phải PENDING | TV3 xác nhận ý nghĩa: nếu là trạng thái Pending thì lọc đúng PENDING; nếu là chưa giao thì đổi nhãn cho đúng | TV3 | Trung bình; làm sai cách hiểu báo cáo | LỖI — sai khác nhãn và phép tính đã xác nhận trong mã |

### 4. Backend / Shared

| ID | Vấn đề | Tình huống dễ hiểu | Nguyên nhân | Cách sửa/đề xuất | Người phụ trách | Mức độ | Trạng thái |
|---|---|---|---|---|---|---|---|
| INT-DATA-01 | Recipient, Delivery Phone, Address, Note gộp vào một chuỗi | Customer tạo đơn, Kitchen cần hiển thị riêng từng thông tin | Request/schema chỉ có `delivery_address`; repository lưu chuỗi; Order Detail trả lại chuỗi; Kitchen dựa vào nhãn để tách | Nhóm chốt contract. Không thêm cột/bảng trước khi thống nhất; giữ tương thích Customer/Kitchen | TV1, TV2, backend/shared; TV3 xác nhận schema chung | Trung bình nếu cần truy vấn riêng; thấp nếu chấp nhận chuỗi demo | VẤN ĐỀ TÍCH HỢP |
| INT-AUTH-01 | CSS/JS Customer không có cùng kiểm soát truy cập như trang | Gọi `/customer/app.js` hoặc `/customer/style.css` khi chưa đăng nhập | Middleware bảo vệ trang Customer nhưng không gán vai trò cho hai đường dẫn tài nguyên; API Customer vẫn kiểm tra role | Nhóm xác định tài nguyên có chủ ý công khai hay cần bảo vệ; kiểm tra chính sách trước khi sửa | TV2/shared; TV1 xác nhận chính sách | Thấp trong demo; phụ thuộc yêu cầu bảo mật | VẤN ĐỀ TÍCH HỢP |
| DATA-DB-01 | Số dòng Orders và lịch sử cao hơn seed dự kiến | Đối chiếu dữ liệu database với seed | Lần đọc trước có customers 4, hubs 4, brands 3, menu_items 8, vouchers 5, orders 11, order_items 20, order_status_history 37, deliveries 4; nguồn của 2/4/5 dòng vượt seed trong ba bảng đơn hàng chưa rõ | Chủ sở hữu dữ liệu xác nhận bằng cách chỉ đọc; không xóa/reseed | Backend/shared; chủ sở hữu DB nhóm | Thấp khi chỉ đọc; cần rõ nguồn trước reset | CHƯA XÁC MINH |
| VER-DB-01 | Chưa thử luồng ghi trên MySQL riêng | Tạo đơn → Kitchen cập nhật → Customer/Manager đọc lại | Không có database MySQL thử nghiệm được phép dùng; database nhóm không dùng để thử ghi | Cấp MySQL test riêng, chạy cùng một order_id và kiểm tra history/rollback/đồng thời | Backend/shared và từng chủ module | Cao trước khi tuyên bố MySQL E2E đạt | CHƯA XÁC MINH |
| VER-UI-01 | Chưa nghiệm thu giao diện toàn bộ bằng trình duyệt | Đăng nhập và thao tác các màn hình chính | Chưa có bằng chứng đầy đủ về render, điều hướng, console và network | TV1/TV2/TV3 kiểm tra module mình, sau đó chạy luồng liên module | Mỗi thành viên; shared hỗ trợ route | Trung bình trước nghiệm thu giao diện | CHƯA XÁC MINH |
| INT-REPORT-01 | Delivery Report không có luồng tạo/cập nhật Delivery từ Kitchen | Kitchen đưa đơn đến READY; Manager xem Delivery Report | Mã ứng dụng hiện đọc bảng `deliveries` để báo cáo nhưng không có đoạn code tạo/cập nhật Delivery; Kitchen chỉ cập nhật Order status | Nhóm xác định ai quản lý giao hàng và thời điểm ghi Delivery; nối lifecycle sau khi thống nhất | Backend/shared; TV2/TV3 phối hợp | Cao nếu yêu cầu báo cáo phản ánh đơn vừa xử lý | VẤN ĐỀ TÍCH HỢP — thiếu điểm nối dữ liệu đã xác nhận |

## C. Lỗi liên module và luồng chính

### C-1. Customer → Kitchen: Note/Phone

| ID | Module liên quan | Luồng bị lỗi | Biểu hiện | Nguyên nhân | Người phối hợp | Hướng xử lý |
|---|---|---|---|---|---|---|
| INT-CUS-KIT-01 | Customer, API, Kitchen | Form → POST → lưu Order → GET Order Detail → Kitchen render | Người dùng báo Recipient `Customer Test12334`, Phone `324324`, Note `1111111`; Kitchen hiện Note là `324324`. Người dùng cũng báo Customer Name `Nguyen Minh Anh`, Account Phone `0901234567`, Distance `3.5 km`. | Chưa xác định cho đơn bị báo. Mã hiện tại ghép nhãn riêng, lưu nguyên chuỗi, trả nguyên chuỗi và parser tách đúng trên dữ liệu thử tổng hợp. | TV1 kiểm tra form/payload; backend kiểm tra dữ liệu lưu/response; TV2 nếu API đúng mà giao diện sai | Tái hiện bằng cùng một order_id trên môi trường riêng; ghi nhận form, payload đã che thông tin, DB và API. Không quy lỗi theo ảnh đơn lẻ |

| Bước truy vết | Bằng chứng trong mã/kiểm thử | Kết quả |
|---|---|---|
| Customer Form | `frontend/customer/index.html` có ID riêng `address`, `recipient`, `phone`, `note`; `placeOrder()` đọc riêng rồi ghép nhãn | Mã nguồn cho thấy ý định tách trường; chưa chạy trình duyệt để xác nhận giá trị DOM thực |
| Request Payload | POST gửi `delivery_address` dạng nhiều dòng; không gửi từng trường riêng | Đã đọc code; không thu payload của đơn người dùng báo |
| SQLite API | Kiểm thử mới POST chuỗi chứa đúng Recipient/Phone/Note, rồi GET Order Detail | PASS: API trả chuỗi giống hệt, không hoán đổi |
| Kitchen parser | Chạy trực tiếp hàm `parseDeliveryDetails()` hiện tại với cùng dữ liệu tổng hợp | PASS: Recipient `Customer Test12334`, Phone `324324`, Note `1111111`, Address `Test street 12` |
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
| Manager Delivery Report | Báo cáo truy vấn bảng Deliveries; không tìm thấy code tạo/cập nhật Delivery | Luồng giao hàng/báo cáo chưa nối; xem INT-REPORT-01 |
| Toàn bộ E2E | Chưa chạy một order_id xuyên suốt cả bốn vai trò | NOT TESTED |

## D. Các lỗi đã sửa

| ID | Lỗi trước khi sửa | File đã sửa | Cách sửa | Test xác nhận | Kết quả |
|---|---|---|---|---|---|
| KIT-01 | Kitchen cố định Hub ID 1 | Commit `1216ca183ee4165b6d97513b365c87538462d732`: `backend/app/routers/kitchen.py`, `backend/app/repositories/order.py`, `backend/tests/test_kitchen.py`, ba file `frontend/kitchen/` | Thêm API danh sách Hub, bộ chọn hub và lọc queue theo hub đang chọn | SQLite test danh sách Hub/lọc đơn; GET MySQL chỉ đọc trước đó thấy order 111 thuộc hub 2 | Đã sửa; thao tác chọn hub trên browser và MySQL ghi chưa kiểm tra |
| KIT-02 | Kitchen chỉ đọc các trường note riêng, API Customer chỉ trả chuỗi `delivery_address` | Commit `1216ca183ee4165b6d97513b365c87538462d732`: `frontend/kitchen/app.js` | Thêm parser nhãn Recipient/Phone/Note, không đổi schema/API | Node syntax và chạy parser hiện tại với dữ liệu tổng hợp chính xác | PASS cho parser thuần; chưa kiểm tra giao diện/browser và đơn người dùng báo |
| INT-DATA-02 | Pydantic từng cho phép 500 ký tự nhưng Model/SQL giới hạn 255 | `backend/app/schemas.py`; thêm `backend/tests/test_customer.py` | Giới hạn request còn 255 để khớp Model và SQL hiện có; không sửa schema/database | SQLite/Pydantic chấp nhận 255, từ chối 256; POST/GET test chuỗi giao hàng | PASS trên SQLite; chưa ghi MySQL |

## E. Việc từng thành viên cần làm

| Thành viên | Module | Việc cần làm | Mức ưu tiên | Điều kiện hoàn thành |
|---|---|---|---|---|
| TV1 — 524H0040 | Customer | Nối Apply Voucher nếu thuộc phạm vi; xác nhận demo Customer ID cố định và phí/khoảng cách; cùng TV2 truy vết INT-CUS-KIT-01 | Cao cho lỗi Note/Phone; các mục khác theo nghiệm thu | Payload của cùng order_id có đúng giá trị form; voucher gửi và tổng tiền đúng nếu được yêu cầu |
| TV2 — 524H0130 | Kitchen/login | Cùng TV1 tái hiện Note/Phone; thử bộ chọn hub/parser trên trình duyệt; kiểm tra cập nhật đồng thời trên MySQL test; xác nhận chính sách asset/login | Cao trước khi tuyên bố Kitchen/MySQL hoàn tất | Browser evidence; MySQL test chứng minh chuyển tiếp và history không sai khi đua |
| TV3 — 524H0021 | Admin/Manager | Xác nhận phạm vi màn hình thiếu; sửa báo lỗi Reports; thống nhất Pending metric; làm rõ Voucher Hub; gắn nhãn/tính lại metrics demo | Cao cho MAN-02/MAN-04; còn lại theo nghiệm thu | 200 rỗng khác 401/500; Pending có định nghĩa đúng; dữ liệu hub/voucher và metrics nhất quán |
| Backend/Shared — cần chỉ định | Database/API/report | Chốt delivery contract; cấp DB test; xác minh nguồn dữ liệu vượt seed; thống nhất chủ thể ghi Delivery và status lifecycle | Cao cho API/DB E2E | Có người chịu trách nhiệm được nhóm chỉ định; test dùng DB riêng và theo cùng order_id |
| TV1 + TV2 + Backend | Customer ↔ Kitchen | Truy vết sự cố Note/Phone theo các bước ở phần C | Cao | Xác định được chặng đầu tiên sai; không dựa vào phỏng đoán |

## F. Những nội dung nhóm cần thống nhất

| STT | Nội dung cần thống nhất | Vì sao cần thống nhất | Các phương án | Đề xuất | Thành viên xác nhận |
|---:|---|---|---|---|---|
| 1 | Recipient, Delivery Phone, Address, Special Note | Hiện gộp trong một chuỗi; Kitchen phải tách theo nhãn | Giữ chuỗi gắn nhãn; hoặc thêm trường cấu trúc ở API/model/schema | Tạm giữ contract hiện có đến khi chọn; nếu đổi phải giữ tương thích Customer/Kitchen và duyệt schema | TV1, TV2, TV3, Backend/Shared |
| 2 | API Order Detail cho giao hàng | API hiện trả `delivery_address`, Customer Name/Phone và khoảng cách; không có field riêng cho giao hàng | Tiếp tục parse chuỗi; hoặc thêm field API riêng (có thể additive) | Ưu tiên contract tường minh; không tự đổi khi chưa có đồng thuận | TV1, TV2, Backend |
| 3 | Vòng đời trạng thái đơn | Kitchen xử lý đến READY; enum còn DELIVERED, FAILED, CANCELLED | Giao hàng module khác quản lý; hoặc mở rộng người phụ trách/endpoint | Chốt trạng thái hợp lệ, vai trò chuyển trạng thái và history cho từng bước | TV1, TV2, TV3, Backend |
| 4 | Thời điểm tạo/cập nhật Delivery | Manager Delivery Report đọc `deliveries`, hiện không có đoạn code ghi bảng này | Tạo Delivery khi READY; khi giao nhận bắt đầu; hoặc giao cho module/ứng dụng khác | Chỉ định owner và sự kiện ghi; không tạo record ngầm trong Kitchen trước khi thống nhất | TV2, TV3, Backend |
| 5 | Voucher áp dụng toàn hệ thống hay theo Hub | API nhận nhãn hub nhưng database không lưu quan hệ | Voucher global; hoặc thêm quan hệ theo Hub sau khi duyệt | Nếu global, bỏ/đổi nhãn Applicable Hub; nếu theo Hub, thống nhất schema/API và áp dụng voucher | TV1, TV3, Backend |
| 6 | Định nghĩa Pending trong Hub Workload | UI gọi cột là Pending nhưng API tính mọi đơn chưa DELIVERED | Chỉ status PENDING; hoặc mọi đơn chưa giao với nhãn khác | Dùng status PENDING nếu giữ nhãn hiện tại | TV3 |
| 7 | Định nghĩa On-Time Rate | Code đếm outcome DELIVERED; schema có DELIVERED/LATE nhưng không thấy writer cập nhật outcome hoặc ETA | Dựa vào outcome do delivery owner ghi; hoặc thêm quy tắc ETA/giờ hẹn | Chốt ý nghĩa, nguồn dữ liệu và cách ghi trước khi gọi là on-time thực tế | TV3, Backend/Shared, delivery owner |
| 8 | Login/Customer identity | Tài khoản/session giả lập; Customer ID bị cố định 1 | Chấp nhận demo một khách; hoặc ánh xạ account → customer_id và session bền vững | Ghi rõ giới hạn demo; không tự thêm bảng tài khoản | TV1, TV2, TV3 |
| 9 | Phạm vi Admin/Manager demo | Dashboard, Hub/Menu/Users, Hub Operations/Order History và update Voucher còn thiếu | Bắt buộc hoàn thiện; hoặc đánh dấu ngoài phạm vi demo | Đối chiếu tiêu chí đồ án trước khi giao làm tính năng | TV3 và nhóm |

## G. Kết quả kiểm thử

| Kiểm tra | Môi trường | Kết quả | Bằng chứng/ghi chú |
|---|---|---|---|
| `python -m compileall -q app tests` | Backend, Python 3.13 | PASS | Chạy sau sửa giới hạn địa chỉ |
| `pytest -q` | SQLite fixtures | PASS — 16 passed, 93 warnings | Hai test mới: giới hạn 255/256 và POST → GET giữ nguyên thông tin giao hàng; warnings là deprecation từ FastAPI/Starlette/SQLAlchemy |
| `node --check frontend/customer/app.js` | Node 24 | PASS | Chạy sau sửa |
| `node --check frontend/kitchen/app.js` | Node 24 | PASS | Chạy sau sửa |
| `node --check frontend/admin/app.js` | Node 24 | PASS | Chạy sau sửa |
| `node --check frontend/manager/app.js` | Node 24 | PASS | Chạy sau sửa |
| Parser Kitchen trên chuỗi mẫu Note/Phone | Node, hàm lấy trực tiếp từ `frontend/kitchen/app.js` | PASS | Trả đúng Recipient `Customer Test12334`, Phone `324324`, Note `1111111` |
| Customer POST → Order Detail | SQLite riêng trong pytest | PASS | Chuỗi giữ nguyên; customer name/phone lấy từ hồ sơ fixture; khoảng cách backend vẫn là 3.5 theo hằng số hiện tại |
| Kitchen transitions/history | SQLite riêng trong pytest | PASS | Confirm, reject có lý do, prepare, ready, invalid transition, missing order và history |
| Router registration/import | Import app trong pytest | PASS | TestClient tải ứng dụng và gọi các API Customer/Kitchen được kiểm thử |
| `git diff --check` | Working tree | PASS | Lệnh chạy thành công; README có cảnh báo line ending LF/CRLF, không phải lỗi whitespace từ code vừa sửa |
| MySQL connection/write | Không dùng database nhóm | NOT TESTED | Không đọc `.env`, không chạy SQL, không ghi SaigonBiteDB; chưa có MySQL test riêng |
| MySQL — kết quả đọc trước đây | MySQL 8.0.46, chỉ đọc | Đã kiểm tra trước đó | Đủ 9 bảng, đã đếm 9 khóa ngoại; order 111 từng thấy ở hub 2. Không kết nối lại lượt này; đây không phải kiểm thử ghi |

| Browser UI/E2E | Chưa có browser evidence | NOT TESTED | JavaScript syntax và parser unit probe không chứng minh render, thao tác, console hoặc network |
| Manager API và Reports trên DB kiểm thử | Chưa chạy riêng | NOT TESTED | Cần test Pending, lỗi API, Delivery records và dữ liệu cùng order_id |
| Toàn luồng Customer → Kitchen → Customer → Manager | Chưa chạy cùng một order_id | NOT TESTED | Các đoạn riêng có test SQLite, nhưng không phải end-to-end |

## H. Checklist trước khi tạo PR vào main

| Điều kiện | Trạng thái | Ghi chú |
|---|---|---|
| Customer hoạt động | PARTIAL | SQLite API tạo/xem đơn đạt; voucher UI, browser và identity nhiều khách chưa hoàn tất |
| Kitchen hoạt động | PARTIAL | SQLite statuses/history và hub API đạt; browser, MySQL/concurrency chưa xác minh |
| Admin hoạt động | PARTIAL | Voucher list/create/archive có code; các màn hình khác chưa triển khai |
| Manager Reports hoạt động | PARTIAL | Có API/ giao diện Reports nhưng Pending label/count sai khác; lỗi API bị hiểu như rỗng; một số metrics giả lập |
| API contract thống nhất | NOT YET | Giao hàng còn là chuỗi có nhãn; nhóm cần quyết định field contract |
| Database tương thích | PARTIAL | `delivery_address` API/model/SQL cùng giới hạn 255 sau sửa; MySQL runtime chưa thử |
| Luồng tạo và xử lý đơn hoàn chỉnh | NOT TESTED | Chưa chạy cùng order_id trên toàn hệ thống/MySQL test |
| Không còn lỗi nghiêm trọng | NOT VERIFIED | Còn vấn đề báo cáo và phần chưa xác minh; nhóm cần đánh giá theo tiêu chí nghiệm thu |
| Giới hạn demo đã được ghi rõ | PASS | Tài liệu ghi Customer ID, khoảng cách/phí, login và số liệu thời gian cố định |
| Test đã chạy lại | PASS | Compile, 16 pytest và bốn lệnh Node syntax đã chạy sau sửa |

## Kết luận

**PARTIALLY WORKING.** Có bằng chứng SQLite rằng Customer API giữ nguyên Recipient/Phone/Note qua tạo đơn và Order Detail; parser Kitchen tách đúng chuỗi mẫu; Kitchen state transitions và history đạt trong SQLite. Chưa tái hiện được dữ liệu của đơn người dùng báo, chưa kiểm tra trình duyệt hoặc MySQL ghi dữ liệu. Không có bằng chứng cho thấy merge đã tráo Phone/Note. Sai lệch contract (một chuỗi so với trường Note riêng) có từ trước tích hợp; nguyên nhân của giá trị bị tráo vẫn chưa xác định.
