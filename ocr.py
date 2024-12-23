import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog, QTextEdit)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import pytesseract
from PIL import Image

class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 添加这一行，路径要根据实际安装位置修改
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('OCR 文字识别软件')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建控件
        self.select_btn = QPushButton('选择图片(&O)', self)
        self.select_btn.clicked.connect(self.select_image)
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        
        self.ocr_btn = QPushButton('识别文字(&R)', self)
        self.ocr_btn.clicked.connect(self.perform_ocr)
        
        self.result_text = QTextEdit(self)
        self.result_text.setPlaceholderText('识别结果将显示在这里...')
        
        # 添加控件到布局
        layout.addWidget(self.select_btn)
        layout.addWidget(self.image_label)
        layout.addWidget(self.ocr_btn)
        layout.addWidget(self.result_text)
        
        self.image_path = None
        
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

def main():
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
