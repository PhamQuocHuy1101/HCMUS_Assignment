### Bài viết này mình mô tả việc tạo 1 crawler đơn gian để crawl dữ liệu từ trang web về. Theo yêu cầu đồ án của môn học Web Science (ĐH KHTN HCM).

# Thông tin

Work flow của crawler được mô tả như sau:

    - Request đến trang web.
    - Xử lý thông tin từ trang web.
    - Lưu trữ các đường link để tiếp tục công việc crawl và cứ thế tiếp tục.

Để xây dựng crawler ta tiến hành các việc lần lược và phát hiện ra các yêu cầu trong từng bước cụ thể:

### Request đến trang web:
    - Đường link cần request 'die'.
    - Request quá nhiều, server sẽ hiểu làm là một cuộc 'tấn công mạng'. Cần hạn chế việc này nếu không crawler của
    mình sẽ tắt trong thời gian ngắn.

### Xử lý thông tin lấy về được:
    - Có cần tải về các tập tin hình ảnh, âm thanh, video, .. hay không? Nếu không cần thiết thì phải lược bỏ 
    trong quá trình crawl để công việc không quá nặng nề.
    - Có nhất thiết phải lưu toàn bộ nội dung crawl được hết trong cơ sở dữ liệu không? Như đoạn nội dung "machine 
    learning and big data are leading the next period". Thông tin lưu lại sau khi crawl nếu được dùng trong việc 
    search dữ liệu sau đó, thì việc giữ lại từ 'and', 'the', 'are' có có ảnh hưởng đến kết quả search? 'learning' 
    hay 'leading' thay bằng 'learn', 'lead' có ảnh hưởng đến kết quả search? Rõ ràng, các từ không mang ý nghĩa 
    của câu trong truy vấn hay các từ mang hậu tố, tiền tố ta không cân phải lưu lại trên cơ sở dũ liệu, do đó ta
    thường rút gọn nội dung trước khi lưu. Công việc lọc này có thể dựa trên danh sách các từ không mang ý nghĩa,
    và rút gọn các từ mang hậu/tiền tố có sẵn (được lựa chọn --> tra cứu trên mạng).

### Lưu trữ các link mới đề tiếp tục công việc:
    - Khi duyệt 1 trang, ta tìm hết các liên kết có trong trang đó, ta được tập hợp các link mới, tuy nhiên không 
    phải tất cả các link lấy được đều đáng để crawl tiếp. Ta phải tổ chức dữ liệu để không phải crawl lại các 
    trang đã crawl. 
    - Các crawler không thể hoạt động mà không có 'điểm để dừng', cần thiết lập 1 độ sâu nhất định để tránh việc 
    crawl quá sâu, hoặc bound các trang miền để không crawl qua khỏi các trang đấy.
    - Các link có nhiều thể hiện khác nhau, tuy cùng 1 trang nhưng link lại khác nhau đôi chút. Việc cần làm là 
    format các link về cùng 1 dạng 'chuẩn'.

Việc tạo crawler trước hết cần hiểu công việc của crawler cần làm gì. Trong phần này, công việc của crawler đơn
giản là tải nội dung html của trang web về và lưu lại, có nhiều crawler cùng lúc thực hiện công việc này. Ta sẽ
thiết kế các cấu trúc dữ liệu lưu trữ trong python để tiện khi sử dụng.

# Code trong thư mục Source.

### Hàm xử  lý khi nhận 1 url:
    - Ta sẽ dùng module requests của python để lấy nội dung của trang web, cũng có thể dùng module này để xứ lý
    content của trang web khi lấy về, tuy nhiên, việc này không cho hiệu xuất cao. Ở đây mình giới thiều module
    BeautifulSoup, rất hiệu quả trong việc xử lý content của trang web, BeautifulSoup tổ chức cây DOM theo html,
    có thể tìm nội dung tag, text (hàm find_all) trong cây đó dễ dàng, để biết thêm về BeautifulSoup bạn cần xem
    thêm về document của nó (theo mình nên đọc về kiến trúc của BeautifulSoup cho rõ rồi dùng các hàm thì tra cứu,
    như vậy sẽ mau hơn, khi làm quen dần thì các hàm thông dụng sẽ thuộc thôi).
    - Bên cạnh đó, khi lọc các thành phân của 1 trang, mình có hay sử dụng 're' đây chính là module regression 
    trong python. Đây là module rất tốt trong truy xuất nội dung theo pattern, một số chổ trong code mình có dùng 
    như trong windows 10 mình dang dùng thì không tạo được thư mục có tên chứa vài kí tự đặc biệt như ^ \ ' < > 
    nên mình dùng re để loại bỏ đi. Các pattern của re các bạn lên document của python để đọc, cũng rất dễ nhớ 
    (module này mình làm việc rất nhiêu, mình nghĩ nó cần thiết, nếu có thời gian các bạn nên thuộc các pattern
    để tiện sau này).

### Tạo các thread để crawl:
    - Ta sẽ tạo ra 1 nơi chứa các url cần crawl, khi đó các crawler sẽ lấy ra 1 phần tử và crawl, sau đó sẽ đưa 
    vào các url mới crawl được, điều đáng nói là có nhiều crawler? Nếu crawler 1 lấy url và đang trong qúa trình
    process, crawler 2 khác đã thực hiện xong process của nó và ghi vào các url trong đó có url mà crawler 1 đang
    process??? Như vậy các crawler sẽ làm việc xoay tròn mãi mãi. Giải quyết vấn đề này, ta cần chọn thêm 1 nơi 
    chứa các url đã crawl rồi, để trước khi thêm các url mới vào cần đối chiếu với nó.
    - Việc đến đây vẫn còn vấn đề. Ta sẽ không lưu lại những url đã thực hiện rồi, nhưng không đảm bảo ta sẽ không
    thực hiện crawl lại nhiều lần (năm trong chỗ chứa các url chưa crawl có nhiều cái giống nhau). Vì vậy cần thêm 
    1 nơi chứa tất cả các url tìm được.
    - Để thiết kế theo hướng dừng crawler lại theo độ sâu, nêu trong code sẽ có các list lưu url tạm thời cho từng 
    crawler. Sau 1 bậc của độ sâu thì gom lại và cập nhật chung với nhau.
    - Khi chọn nơi lưu các url cần crawl, mình dùng class Queue trong python, nó sẽ đảm bảo chờ cho việc lấy 1 phần
    tử ra ngoài tuần tự và không cho các thread (crawler) dừng khi không được cho phép (Queue.join). Nơi lưu lại các
    url đã crawl, mình dùng set trong python, nó hỗ trợ việc tìm xem 1 phần tử có tồn tại không nhanh nhờ dùng hàm
    hash. (bạn xem them trên document của python để hiểu cấu trúc dữ liệu này).

***(Cảm ơn bạn giành thời gian đọc, minh hy vọng bài viết giúp ích cho bạn).***

17.11.2018 11:04 pm ----------------------------------------------------------------------------------------------
