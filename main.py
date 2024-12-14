import cv2
import numpy as np
import face_recognition
import os
import pyodbc
import time
import datetime
from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports
# ****************************************************************************************************
std_Id = 0
loginState = 0
ser = ""
selected_com_port = ""
selected_baud_rate = 0
# Function to clear the current frame (hide all widgets)
def clear_frame():
    for widget in app.winfo_children():
        widget.pack_forget()

# Tạo kết nối SQL với Python:
conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};\
    Server=DESKTOP-CFU7HGJ\MSSQLSERVER03;\
    Database=ThuVien;\
    Trusted_Connection=yes;'
)

# Hàm để so sánh tên sinh viên nhận dạng với cơ sở dữ liệu sinh viên
def find_student_by_name(name, students_db):
    for student in students_db:
        if student[0] == name:  # So sánh không phân biệt chữ hoa/thường
            return student
    return None  # Trả về None nếu không tìm thấy sinh viên

# ****************************************************************************************************
# Connect to the databas
def getdataStudent():
    cursor = conn.cursor()
    # Fetch data from the SQLite table
    cursor.execute("SELECT * FROM SinhVien")
    data = cursor.fetchall()
    return data
# Close the database connection
Studient = getdataStudent()
# ****************************************************************************************************\

def dis_connection():
    global ser
    ser.close()
    if ser.is_open:
        messagebox.showinfo("Kết nối thành công", f"Kết nối đến MCU thành công!")
    else:
        messagebox.showerror("Ngắt kết nối thành công", "Ngắt kết nối đến cổng COM.")
# Connect to the databas
def getdata():
    cursor = conn.cursor()
    # Fetch data from the SQLite table
    cursor.execute("SELECT * FROM Sach")
    data = cursor.fetchall()
    return data

# Connect to the databas
def getdataBill():
    cursor = conn.cursor()
    # Fetch data from the SQLite table
    cursor.execute("SELECT * FROM Phieu")
    data = cursor.fetchall()
    return data
# Close the database connection
data = getdata()
# print(data)

def insertBill(MaSV, MaBook, SLM, DayRent):
    cursor = conn.cursor()
    # Chèn dữ liệu vào bảng Phieu
    cursor.execute("""
        INSERT INTO Phieu (MaSV, MaSach, SoLuongMuon, NgayMuon)
        VALUES (?, ?, ?, ?)
    """, (MaSV, MaBook, SLM, DayRent))

    # Lưu thay đổi và trả về MaPhieu vừa tạo
    conn.commit()
                                           
    # Đóng kết nối sau khi hoàn thành
    cursor.close()

    
def removeBook(book_id):
    cursor = conn.cursor()
    
    # SQL query to delete the book from the "Sach" table based on the book's ID
    cursor.execute("DELETE FROM Sach WHERE [Mã Sách] = ?", (book_id,))
    # Commit the transaction to apply the changes to the database
    conn.commit()
    print(f"Book with ID {book_id} has been deleted from the database.")

# ****************************************************************************************************
def decreaseBook(book_id):
    cursor = conn.cursor()
    
    # SQL query to decrease the quantity (Số lượng) of the book with the given ID
    cursor.execute("""
        UPDATE Sach 
        SET SoLuong = SoLuong - 1
        WHERE MaSach = ?
    """, (book_id,))
    
    # Commit the transaction to save the changes to the database
    conn.commit()
    
    print(f"Decreased the quantity of book with ID {book_id} by 1.")
# ****************************************************************************************************

def gettime():
    now = datetime.datetime.utcnow()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    return now
print(gettime())

# ****************************************************************************************************
# Load images from the folder
path = 'ImagesBasic'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

# Function to encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print("Encoder Completed")

# ****************************************************************************************************
# Define a video capture object
cap = cv2.VideoCapture(0)

# Set video capture properties (optional, to set width and height)
width, height = 600, 400
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# ****************************************************************************************************
# Create a GUI app
app = tk.Tk()
app.title("Face Recognition App")
app.geometry("1600x700")

# Bind the app with Escape keyboard to quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())

# ****************************************************************************************************
# Create a label to display the camera feed
label_widget = Label(app)
label_widget.pack()

# ****************************************************************************************************
# Function to open the camera and process each frame
def open_camera():
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        return

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Resize image for faster processing
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)

        if faceDis[matchIndex] < 0.35 and matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.putText(img, name, ((x1 + 6), y1 - 6), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
            
            # If the name is found in classNames, transition to Library screen
                # Tìm kiếm sinh viên theo tên
            student = find_student_by_name(name, Studient)
    
            # Studient
            if student:
                print(f"{name} found in the database. Moving to Library Screen.")
                show_library_screen(name)  # Pass student object to the library screen
                return
            else:
                print(f"{name} not found in the database. Access Denied.")
        else:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.putText(img, "Unknown", ((x1 + 6), y1 - 6), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

    # Convert the image to a format that Tkinter can display
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    captured_image = Image.fromarray(image)
    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Display the image on the Tkinter label
    label_widget.photo_image = photo_image
    label_widget.configure(image=photo_image)

    # Repeat the process after every 10ms
    label_widget.after(10, open_camera)

# ****************************************************************************************************
# Function to show the library screen
def show_library_screen(user_name):
    loginState = 1
    # Dừng camera khi vào màn hình thư viện
    cap.release()

    # Ẩn feed camera
    label_widget.pack_forget()

    # Tạo frame thư viện mới
    library_frame = Frame(app)
    library_frame.pack(fill="both", expand=True)

    # Thêm thông báo chào mừng
    welcome_label = Label(library_frame, text=f"Welcome {user_name}, Here are some books!", font=("Arial", 20))
    welcome_label.pack(pady=20)

    # Thêm bảng sách
    tree = ttk.Treeview(library_frame, columns=("Mã Sách", "Tên Sách", "Tác Giả", "Năm Xuất Bản", "Nhà Xuất Bản", "Thể loại", "Số lượng"), show="headings")
    tree.heading("Mã Sách", text="Mã Sách")
    tree.heading("Tên Sách", text="Tên Sách")
    tree.heading("Tác Giả", text="Tác Giả")
    tree.heading("Năm Xuất Bản", text="Năm Xuất Bản")
    tree.heading("Nhà Xuất Bản", text="Nhà Xuất Bản")
    tree.heading("Thể loại", text="Thể loại")
    tree.heading("Số lượng", text="Số lượng")

    # Lấy dữ liệu từ cơ sở dữ liệu
    books = getdata()
    std_Id = user_name
    # Chèn dữ liệu vào bảng
    for book in books:
        book_id, book_title, author, publication_year, publisher, genre, quantity = book
        tree.insert("", "end", values=(book_id, book_title, author, publication_year, publisher, genre, quantity))

    tree.pack(pady=20)

    # Thêm nút "Get"
    def on_get_button_click():
        # Vô hiệu hóa các nút
        get_button.config(state="disabled")
        back_button.config(state="disabled")

        # Hiển thị thông báo "In progress"
        progress_label = Label(library_frame, text="In progress...", font=("Arial", 16))
        progress_label.pack(pady=20)

        # Sau 4 giây, ẩn thông báo và xóa sách
        library_frame.after(4000, lambda: [progress_label.pack_forget(),
                                          updateTable(),
                                          get_button.config(state="normal"),
                                          back_button.config(state="normal")])



        # Gọi hàm insertBill
        selected_item = tree.selection()
        if selected_item:
            # Extract the book code (first column)
            selected_book = tree.item(selected_item[0])  # Get the first selected item
            book_id = selected_book['values'][0]  # First column contains "Mã Sách"
            decreaseBook(book_id)
            # You can now use the `book_id` for your further processing (e.g., storing or displaying it)
            print(f"Book ID: {book_id}")
            DayRent = gettime()
            insertBill(std_Id, book_id, 1, DayRent)
            global ser
            datasent = str(book_id).encode('utf-8')
            ser.write(datasent)
            # Get the selected item (book) from the Treeview
            selected_item = tree.selection()

            # You can also display it on the GUI
            book_id_label = Label(library_frame, text=f"Book ID: {book_id}", font=("Arial", 14))
            book_id_label.pack(pady=20)
            # Clear the label after 4 seconds
            library_frame.after(4000, book_id_label.pack_forget)  # Removes the label after 4 seconds

        else:
            print("No book selected")

    def updateTable():
        # First, clear the existing rows in the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Re-fetch data from the database after an operation like "decreaseBook"
        books = getdata()

        # Insert updated data into the Treeview
        for book in books:
            book_id, book_title, author, publication_year, publisher, genre, quantity = book
            tree.insert("", "end", values=(book_id, book_title, author, publication_year, publisher, genre, quantity))
        tree.pack(pady=20)
    get_button = Button(
        library_frame,
        text="Get",
        command=on_get_button_click,
        width=20,  # Set the width of the button (in characters)
        height=3,  # Set the height of the button (in characters)
        font=("Arial", 16),  # Set a larger font size
        bg="black",  # Set a background color (optional)
        fg="white",  # Set a foreground (text) color (optional)
        relief="raised",  # Set button style (optional)
        bd=5  # Set border width (optional)
    )
    get_button.pack(pady=20)

    # Thêm nút "Back to Camera"
    def go_back_to_camera():
        # Thoát khỏi màn hình thư viện và quay lại camera
        cap.release()
        library_frame.pack_forget()
        # Thực hiện lại quá trình mở camera và hiển thị lại video
        # cap.open(0)
        # open_camera()  # Nếu bạn có hàm open_camera để tiếp tục feed camera
    back_button = Button(
        library_frame,
        text="Back to Camera",
        command=go_back_to_camera,
        width=20,  # Set the width of the button (in characters)
        height=3,  # Set the height of the button (in characters)
        font=("Arial", 16),  # Set a larger font size
        bg="black",  # Set a background color (optional)
        fg="white",  # Set a foreground (text) color (optional)
        relief="raised",  # Set button style (optional)
        bd=5  # Set border width (optional)
    )
    # back_button = Button(library_frame, text="Back to Camera", command=go_back_to_camera)
    back_button.pack(pady=20)

# Chạy hàm để hiển thị giao diện thư viện
# ****************************************************************************************************
# Create the menu bar
# Hàm kiểm tra kết nối COM
def check_connection():
    print(f"COM Port: {selected_com_port}\n")
    print(f"Baudrate: {selected_baud_rate}\n")
    com_port = selected_com_port  # Lấy cổng COM từ combobox
    baud_rate = selected_baud_rate  # Lấy baudrate từ combobox
    
    if not com_port or not baud_rate:
        messagebox.showerror("Lỗi", "Vui lòng chọn cả cổng COM và Baudrate.")
        return
    
    try:
        # Mở cổng COM
        global ser
        ser = serial.Serial(com_port, baud_rate, timeout=100)
        # Kiểm tra kết nối
        if ser.is_open:
            messagebox.showinfo("Kết nối thành công", f"Kết nối đến {com_port} thành công!")
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối đến cổng COM.")
        # ser.close()  # Đóng cổng sau khi kiểm tra
    except serial.SerialException as e:
        messagebox.showerror("Lỗi", f"Không thể kết nối: {str(e)}")

menubar = Menu(app)
def showHistory():
    # Ẩn feed camera
    label_widget.pack_forget()

    # Tạo frame thư viện mới
    library_frame = Frame(app)
    library_frame.pack(fill="both", expand=True)

    # Thêm thông báo chào mừng
    welcome_label = Label(library_frame, text=f"Here are some books!", font=("Arial", 20))
    welcome_label.pack(pady=20)

    # Thêm bảng sách
    tree = ttk.Treeview(library_frame, columns=("Mã Phiếu", "Mã Sinh Viên", "Mã Sách", "Số lượng mượn", "Ngày mượn"), show="headings")
    tree.heading("Mã Phiếu", text="Mã Phiếu")
    tree.heading("Mã Sinh Viên", text="Mã Sinh Viên")
    tree.heading("Mã Sách", text="Mã Sách")
    tree.heading("Số lượng mượn", text="Số lượng mượn")
    tree.heading("Ngày mượn", text="Ngày mượn")

    # Lấy dữ liệu từ cơ sở dữ liệu
    bills = getdataBill()
    print(bills)
    # Chèn dữ liệu vào bảng
    for book in bills:
        book_id, book_title, author, publication_year, publisher = book
        tree.insert("", "end", values=(book_id, book_title, author, publication_year, publisher))

    tree.pack(pady=20)

# Function for 'Login' action
def login_action():
    clear_frame()
    print("Login clicked")
    cap.open(0)
    open_camera()
    label_widget.pack()  # Show the label widget for camera feed

# Hàm để lấy danh sách các cổng COM có sẵn
def get_com_ports():
    ports = serial.tools.list_ports.comports()
    port_list = [port.device for port in ports]  # Lấy tên các cổng COM
    return port_list

# Function for 'SetUp' action - màn hình Setup
def setup_action():
    clear_frame()  # Xóa frame hiện tại
    print("Setup clicked")

    # Tạo một frame mới cho Setup
    setup_frame = Frame(app)
    setup_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Tiêu đề
    setup_label = Label(setup_frame, text="Cài Đặt Hệ Thống", font=("Arial", 20))
    setup_label.pack(pady=20)

    # Cài đặt COM Port
    tk.Label(setup_frame, text="Chọn Cổng COM:").pack(pady=5)
    com_combobox = ttk.Combobox(setup_frame, values=get_com_ports(), state="readonly", width=20)
    com_combobox.set("COM1")  # Giá trị mặc định
    com_combobox.pack(pady=5)

    # Cài đặt Baudrate
    tk.Label(setup_frame, text="Chọn Baudrate:").pack(pady=5)
    baud_combobox = ttk.Combobox(setup_frame, values=["9600", "19200", "38400", "57600", "115200"], state="readonly", width=20)
    baud_combobox.set("9600")  # Giá trị mặc định
    baud_combobox.pack(pady=5)

    
    # Nút Lưu Cài Đặt
    def save_settings():
        global selected_com_port
        global selected_baud_rate

        selected_com_port = com_combobox.get()
        selected_baud_rate = baud_combobox.get()
        print(f"COM Port: {selected_com_port}, Baudrate: {selected_baud_rate}")

        # Có thể lưu cài đặt vào file hoặc cơ sở dữ liệu nếu cần
        # Ví dụ: Lưu vào một file cấu hình
        with open("settings.txt", "w") as f:
            f.write(f"COM Port: {selected_com_port}\n")
            f.write(f"Baudrate: {selected_baud_rate}\n")

        messagebox.showinfo("Cài Đặt", "Cài đặt đã được lưu thành công!")

    save_button = Button(setup_frame, text="Lưu Cài Đặt", command=save_settings, width=20, height=2, font=("Arial", 16), bg="black", fg="white", relief="raised", bd=5)
    save_button.pack(pady=20)

    # Nút Quay Lại
    def go_back():
        setup_frame.pack_forget()  # Ẩn frame Setup
        login_action()  # Quay lại màn hình chính

    ConnectionBtn = Button(setup_frame, text="Connection", command=check_connection, width=20, height=2, font=("Arial", 16), bg="black", fg="white", relief="raised", bd=5)
    ConnectionBtn.pack(pady=20)

    DisconnectBtn = Button(setup_frame, text="Disconnection", command=dis_connection, width=20, height=2, font=("Arial", 16), bg="black", fg="white", relief="raised", bd=5)
    DisconnectBtn.pack(pady=20)


# Function for 'Library' action
def library_action():
    clear_frame()
    print("Library clicked")
    # Implement Library functionality here
# Function for 'Library' action
def history():
    clear_frame()
    print("Library clicked")
    showHistory()
    # Implement Library functionality here

# def setupCom():


# Create 'File' menu
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Login", command=login_action)

setup_menu = Menu(menubar, tearoff=0)
setup_menu.add_command(label="SetUp", command=setup_action)

library_menu = Menu(menubar, tearoff=0)
library_menu.add_command(label="Library", command=library_action)

history_menu = Menu(menubar, tearoff=0)
history_menu.add_command(label="History", command=history)

menubar.add_cascade(label="Login", menu=file_menu)
menubar.add_cascade(label="SetUp", menu=setup_menu)
menubar.add_cascade(label="Library", menu=library_menu)
menubar.add_cascade(label="History", menu=history_menu)

# Add menu to the window
app.config(menu=menubar)
# Cài đặt chế độ toàn màn hình
# app.attributes("-fullscreen", True)
# Run the GUI main loop
app.mainloop()

# ****************************************************************************************************
# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
