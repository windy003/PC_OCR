import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QTextEdit)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt
import pytesseract
from PIL import Image
import pystray
import threading
import keyboard
from PIL import ImageGrab
import win32clipboard
import io
import cv2
import os
import pyperclip
import tkinter as tk
from tkinter import ttk

class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # 获取图标路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 exe
            application_path = sys._MEIPASS
        else:
            # 如果是源代码运行
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(application_path, "icon.ico")
        
        # 设置应用图标
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)  # 设置窗口图标
        QApplication.instance().setWindowIcon(icon)  # 设置应用程序图标
        
        self.initUI()
        
        # 重写关闭事件
        self.closeEvent = self.handle_close
        
    def initUI(self):
        self.setWindowTitle('OCR 文字识别软件')
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 设置窗口大小为屏幕的80%
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        # 计算窗口位置使其居中
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        # 设置窗口大小和位置
        self.setGeometry(x, y, width, height)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建控件
        self.select_btn = QPushButton('选择图片(&O)', self)
        self.select_btn.clicked.connect(self.select_image)
        
        # 添加从剪贴板导入按钮
        self.clipboard_btn = QPushButton('从剪贴板导入(&V)', self)
        self.clipboard_btn.clicked.connect(self.handle_clipboard)
        
        # 添加清除按钮
        self.clear_btn = QPushButton('清除图片(&C)', self)
        self.clear_btn.clicked.connect(self.clear_image)
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        
        self.ocr_btn = QPushButton('识别文字(&R)', self)
        self.ocr_btn.clicked.connect(self.perform_ocr)
        
        self.result_text = QTextEdit(self)
        self.result_text.setPlaceholderText('识别结果将显示在这里...')
        
        # 添加控件到布局
        layout.addWidget(self.select_btn)
        layout.addWidget(self.clipboard_btn)  # 添加新按钮
        layout.addWidget(self.clear_btn)  # 添加清除按钮
        layout.addWidget(self.image_label)
        layout.addWidget(self.ocr_btn)
        layout.addWidget(self.result_text)
        
        self.image_path = None
        
        # 设置快捷键
        self.clipboard_btn.setShortcut('Alt+V')  # 使用 Alt+V 作为快捷键
        self.clear_btn.setShortcut('Alt+C')     # 使用 Alt+C 作为快捷键
    
    def handle_clipboard(self):
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, list):  # 如果是文件列表
                for file_path in image:
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        self.image_path = file_path
                        pixmap = QPixmap(file_path)
                        self.update_image_display(pixmap)
                        break
            elif image:  # 如果是直接复制的图片
                # 保存临时文件
                temp_path = "temp_clipboard.png"
                image.save(temp_path)
                self.image_path = temp_path
                pixmap = QPixmap(temp_path)
                self.update_image_display(pixmap)
        except Exception as e:
            self.result_text.setText(f'处理剪贴板出错：{str(e)}')
    
    def update_image_display(self, pixmap):
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
    
    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
    def perform_ocr(self):
        if not self.image_path:
            self.result_text.setText('请先选择一张图片！')
            return
            
        try:
            # 执行OCR识别
            image = Image.open(self.image_path)
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            self.result_text.setText(text)
        except Exception as e:
            self.result_text.setText(f'识别出错：{str(e)}')
    
    def clear_image(self):
        """清除当前显示的图片和识别结果"""
        self.image_label.clear()  # 清除图片显示
        self.result_text.clear()  # 清除识别结果
        self.image_path = None    # 清除图片路径
        
        # 删除临时文件（如果存在）
        if os.path.exists("temp_clipboard.png"):
            try:
                os.remove("temp_clipboard.png")
            except Exception as e:
                print(f"删除临时文件失败：{str(e)}")
    
    def handle_close(self, event):
        """处理窗口关闭事件"""
        event.ignore()  # 忽略关闭事件
        self.hide()     # 隐藏窗口而不是关闭

def create_tray_icon(app_window):
    # 获取图标路径
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
        
    icon_path = os.path.join(application_path, "icon.ico")
    
    # 使用 .ico 文件作为托盘图标
    icon_image = Image.open(icon_path)
    
    def on_quit():
        icon.stop()
        app_window.close()  # 关闭主窗口
        QApplication.instance().quit()  # 退出应用
        
    def on_show():
        app_window.show()
        app_window.activateWindow()  # 激活窗口
    
    menu = pystray.Menu(
        pystray.MenuItem("显示主窗口", on_show),
        pystray.MenuItem("退出", on_quit)
    )
    
    icon = pystray.Icon(
        "OCR工具",  # 图标名称
        icon_image,  # 图标图像
        "OCR工具",  # 鼠标悬停时显示的文字
        menu
    )
    
    icon.run()

def handle_clipboard():
    try:
        # 尝试从剪贴板获取图片
        image = ImageGrab.grabclipboard()
        
        # 处理不同类型的剪贴板内容
        if isinstance(image, list):  # 如果是文件列表
            for file_path in image:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    img = Image.open(file_path)
                    ocr_image(img)  # 直接处理图片对象
                    break  # 只处理第一个图片
        elif image:  # 如果是直接复制的图片
            ocr_image(image)  # 直接处理图片对象
            
    except Exception as e:
        print(f"处理剪贴板出错: {e}")

def ocr_image(image):
    try:
        # 保存临时文件
        temp_path = "temp_clipboard.png"
        image.save(temp_path)
        
        # 调用你现有的OCR处理逻辑
        img = cv2.imread(temp_path)
        result = ocr.ocr(img)
        
        # 处理OCR结果
        if result:
            text = result[0][1][0]  # 获取识别的文本
            pyperclip.copy(text)  # 将结果复制到贴板
            print(f"识别结果：{text}")
            
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"OCR处理出错: {e}")

def setup_hotkey():
    keyboard.add_hotkey('ctrl+v', handle_clipboard)

def main():
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    
    # 设置热键
    setup_hotkey()
    
    # 创建托盘图标线程，传入主窗口引用
    tray_thread = threading.Thread(target=lambda: create_tray_icon(window), daemon=True)
    tray_thread.start()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
