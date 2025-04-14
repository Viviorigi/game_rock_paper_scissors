import random
import cv2
import hand_detection_lib as handlib
import os

detector = handlib.handDetector()
cam = cv2.VideoCapture(0)

def draw_results(frame, user_draw):
    # ----- THÊM DÒNG NÀY -----
    overlay_size = (200, 200) # Chiều rộng 200, chiều cao 200 (hoặc kích thước khác bạn muốn)
    # -------------------------

    # Lấy kích thước khung hình để tính toán vị trí nếu cần
    frame_h, frame_w, _ = frame.shape

    # Cho máy sinh ra lựa chọn ngẫu nhiên
    com_draw = random.randint(0,2)

    # === Vẽ hình, viết chữ theo user_draw ===
    frame = cv2.putText(frame, 'You', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2, cv2.LINE_AA)

    # Kiểm tra xem user_draw có hợp lệ không trước khi đọc file
    if user_draw != -1:
        user_img_path = os.path.join("pix", str(user_draw) + ".png")
        if os.path.exists(user_img_path):
            s_img_user = cv2.imread(user_img_path)
            # ----- THAY ĐỔI CÁC DÒNG SAU -----
            s_img_user = cv2.resize(s_img_user, overlay_size) # Resize ảnh
            x_offset_user = 50
            y_offset_user = 100
            # Đảm bảo không vẽ ra ngoài khung hình (an toàn hơn)
            end_y_user = min(y_offset_user + overlay_size[1], frame_h)
            end_x_user = min(x_offset_user + overlay_size[0], frame_w)
            img_h_user = end_y_user - y_offset_user
            img_w_user = end_x_user - x_offset_user
            # Chỉ gán phần ảnh và phần frame thực sự tồn tại
            frame[y_offset_user:end_y_user, x_offset_user:end_x_user] = s_img_user[:img_h_user, :img_w_user]
            # ---------------------------------
        else:
            print(f"Warning: User image not found at {user_img_path}")
            frame = cv2.putText(frame, '?', (50 + overlay_size[0]//2, 100 + overlay_size[1]//2),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)
    else:
         frame = cv2.putText(frame, '?', (50 + overlay_size[0]//2, 100 + overlay_size[1]//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)


    # === Vẽ hình, viết chữ theo com_draw ===
    frame = cv2.putText(frame, 'Computer', (frame_w - overlay_size[0] - 50, 50), cv2.FONT_HERSHEY_SIMPLEX, # Điều chỉnh x_offset cho chữ
                        1, (0, 0, 255), 2, cv2.LINE_AA)
    
    com_img_path = os.path.join("pix",str(com_draw) + ".png")
    if os.path.exists(com_img_path):
        s_img_com = cv2.imread(com_img_path)
        # ----- THAY ĐỔI CÁC DÒNG SAU -----
        s_img_com = cv2.resize(s_img_com, overlay_size) # Resize ảnh
        # Tính toán x_offset để căn lề phải (ví dụ cách lề phải 50px)
        x_offset_com = frame_w - overlay_size[0] - 50
        y_offset_com = 100
        # Đảm bảo không vẽ ra ngoài khung hình
        end_y_com = min(y_offset_com + overlay_size[1], frame_h)
        end_x_com = min(x_offset_com + overlay_size[0], frame_w)
        img_h_com = end_y_com - y_offset_com
        img_w_com = end_x_com - x_offset_com
        # Chỉ gán phần ảnh và phần frame thực sự tồn tại
        frame[y_offset_com:end_y_com, x_offset_com:end_x_com] = s_img_com[:img_h_com, :img_w_com]
        # ---------------------------------
    else:
        print(f"Warning: Computer image not found at {com_img_path}")
        frame = cv2.putText(frame, '?', (frame_w - overlay_size[0], 100 + overlay_size[1]//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)

    # === Kiểm tra và hiển thị kết quả ===
    result = "INVALID HAND" # Kết quả mặc định nếu user_draw không hợp lệ
    if user_draw == com_draw:
          result="DRAW!"
    elif (user_draw==0) and (com_draw==1):
          result="YOU WIN!"
    elif (user_draw==1) and (com_draw==2):
          result="YOU WIN!"
    elif (user_draw==2) and (com_draw==0):
          result="YOU WIN!"
    else:
          result="YOU LOSE!"

    # Đặt text kết quả ở giữa phía dưới
    text_size, _ = cv2.getTextSize(result, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_x = (frame_w - text_size[0]) // 2
    text_y = frame_h - 50 # Cách đáy 50px
    frame = cv2.putText(frame, result, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 0, 255), 2, cv2.LINE_AA)           
    return frame # Trả về frame đã được vẽ kết quả

last_frame_with_results = None
show_results = False

while True:
    ret, frame = cam.read()
    if not ret:
        print("Error reading frame from camera")
        break
    
    display_frame = cv2.flip(frame,1)   

    # Đưa hình ảnh vào detector
    detected_frame, hand_lms = detector.findHands(display_frame) # Vẽ lên display_frame
    n_fingers = detector.count_finger(hand_lms)

    user_draw = -1 # 0: Lá, 1: Đấm, 2 Kéo
    instruction_text = "Show Dam(1), La(0), or Keo(2)"
    if n_fingers==0: 
        user_draw = 1
        instruction_text = "Detected: Dam (1)"
    elif n_fingers==2:
        user_draw = 2
        instruction_text = "Detected: Keo (2)"
    elif n_fingers ==5:
        user_draw = 0
        instruction_text = "Detected: La (0)"
    elif n_fingers!=-1:
        instruction_text = "Invalid Hand! Show 0, 2, or 5 fingers."
    

    # Hiển thị hướng dẫn hoặc trạng thái phát hiện
    cv2.putText(display_frame, instruction_text, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(display_frame, "Bam space de choi", (80, frame.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2, cv2.LINE_AA)

    key = cv2.waitKey(1) 

    if key == ord("q"):
        break
    elif key == ord(" "): 
        if user_draw != -1: 
            last_frame_with_results = draw_results(frame.copy(), user_draw) 
            show_results = True
        else:
            print("Cannot play: Invalid hand gesture detected!")
            show_results = False 

    # Hiển thị khung hình
    if show_results and last_frame_with_results is not None:
        cv2.imshow("game", last_frame_with_results)
        
    else:
        cv2.imshow("game", display_frame) 
        show_results = False 

cam.release()
cv2.destroyAllWindows()