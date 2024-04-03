import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, pyqtSignal
import cv2
import fitz  # PyMuPDF

class DropBox(QWidget):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super(DropBox, self).__init__(parent)
        self.setMinimumSize(300, 200)
        self.setAcceptDrops(True)
        self.hovered = False
        self.hint_text = "Drag and drop image or PDF here"

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].isLocalFile():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.pdf')):
                event.acceptProposedAction()
                self.hovered = True
                self.update()

    def dragLeaveEvent(self, event):
        self.hovered = False
        self.update()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.pdf')):
            self.file_dropped.emit(file_path)

        self.hovered = False  # Disable hover effect after the file is dropped
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.hovered:
            pen = QPen(Qt.black)
            pen.setWidth(2)
            painter.setPen(pen)

            rect = self.rect().adjusted(0, 0, -1, -1)
            painter.drawRect(rect)

        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)

        painter.drawText(self.rect(), Qt.AlignCenter, self.hint_text)


class OCRApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('OCR Application')
        self.resize(1000, 800)

        self.text_label = QTextEdit(self)
        self.text_label.setPlaceholderText("Recognized Text")
        self.text_label.setReadOnly(True)

        self.drop_box = DropBox(self)
        self.drop_box.file_dropped.connect(self.load_file)

        process_button = QPushButton('Process OCR', self)
        process_button.clicked.connect(self.perform_ocr)

        layout = QVBoxLayout()
        layout.addWidget(self.drop_box)
        layout.addWidget(process_button)
        layout.addWidget(self.text_label)

        self.setLayout(layout)

    def load_file(self, file_path):
        self.text_label.clear()

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.text_label.setPlainText(f"Image file: {file_path}")

        elif file_path.lower().endswith('.pdf'):
            self.image_path = self.convert_pdf_to_image(file_path)
            pixmap = QPixmap(self.image_path)
            self.text_label.setPlainText(f"PDF file: {file_path}")

        else:
            self.image_path = None
            self.text_label.setPlainText("Unsupported file format. Please drop an image or PDF.")

        self.drop_box.hovered = False
        self.update()

    def convert_pdf_to_image(self, pdf_path):
        try:
            pdf_document = fitz.open(pdf_path)
            page = pdf_document[0]  # Assuming we are working with the first page
            image_path = "temp_image.png"

            # Render the PDF page as an image
            pix = page.getPixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)

            # Save the QImage to a file
            img.save(image_path, "PNG")

            pdf_document.close()
            return image_path
        except Exception as e:
            print(f"Error converting PDF to image: {e}")
            return None

    def perform_ocr(self):
        if hasattr(self, 'image_path') and self.image_path:
            text = self.image_to_text(self.image_path)
            self.text_label.setPlainText(f"Recognized Text:\n\n{text}")
        else:
            self.text_label.setPlainText("Please load an image or PDF first.")

    def image_to_text(self, image_path):
        # Your OCR code here
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ocr_app = OCRApp()
    ocr_app.show()
    sys.exit(app.exec_())





