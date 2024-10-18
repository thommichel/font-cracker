import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QProgressBar, QFileDialog, QSizePolicy,
    QSlider, QHBoxLayout, QStackedLayout, QTextEdit
)
from PyQt5.QtGui import QPixmap, QPalette, QColor, QIcon, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtSvg import QSvgWidget
import time
import os
from src.font_identify import FontCracker

LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l','m',\
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',\
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',\
           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

class Worker(QThread):
    progress = pyqtSignal(int)
    font_cracker:FontCracker = None
    
    def run(self):
        while True:
            self.progress.emit(int(self.font_cracker.progress))
            time.sleep(0.05)

class Cracker(QThread):
    font_cracker:FontCracker = None
    font_path = None
    letter_path = None
    letter_char = None
    message_path = None 
    threshold = None
    letters = None

    update_img = pyqtSignal(list)

    def set_fields(self, 
        font_path,
        message_path,
        letter_path,
        letter_char,
        letters,
        threshold
    ):
        self.font_path = font_path
        self.message_path = message_path
        self.letter_path = letter_path
        self.letter_char = letter_char
        self.letters = letters
        self.threshold = threshold

    def run(self):
        self.font_cracker.solve_font(
            self.font_path,
            self.message_path,
            self.letter_path,
            self.letter_char,
            self.letters,
            self.threshold
        )
        self.update_img.emit([self.font_cracker.output_image_path, self.font_cracker.message])

class FirstStage(QWidget):
    def __init__(self, transition_callback, w_size):
        super().__init__()
        self.w_size = w_size
        self.transition_callback = transition_callback
        self.init_ui()

    def update_box(self, value):
        str_value = str(value/100)
        if self.text_box2.text() != str_value:
            self.text_box2.setText(str_value)

    def update_slider(self, value):
        try:
            int_value = int(float(value)*100)
        except:
            return
        if int_value != self.prcnt_match.value():
            self.prcnt_match.setValue(int_value)

    def filter_space(self, ltrs:str):
        ltrs = ltrs.replace(' ', '')
        ltrs = ltrs.replace('\n', '')
        ltrs = ltrs.replace('\r', '')
        return ltrs.split(',')
    
    def toggle_state(self):
        if self.enable_folder.isChecked():
            self.enable_folder.setText("MODE: Font File")
            self.folder_select = False
        else:
            self.enable_folder.setText("MODE: Font Folder")
            self.folder_select = True


    def init_ui(self):
        layout = QVBoxLayout()

        
        self.title = QLabel()
        self.title.setText('FONT-CRACKER')
        thresh_palette = self.title.palette()
        thresh_palette.setColor(QPalette.WindowText, QColor('white'))
        self.title.setPalette(thresh_palette)
        t_font = QFont('OldEnglish', int(self.w_size[0] * 0.0085))
        t_font.setBold(True)
        self.title.setFont(t_font)
        self.title.setAlignment(Qt.AlignCenter)


        # SVG Image
        logo = QHBoxLayout()
        self.svg_widget = QSvgWidget("res/logo/wizard.svg")  # Change to your SVG file path
        self.svg_widget.setFixedSize(
            int(self.w_size[1]*0.5), int(self.w_size[1]*0.5))  # Set a fixed size for the SVG widget
        logo.addWidget(self.svg_widget)
        layout.addWidget(self.title)
        layout.addLayout(logo)

        # File Selection Buttons
        self.button_info = {
            "Select Font File/Dir": {},
            "Select Encoded Img": {},
            "Select Single Letter": {},
        }
        for name, info in self.button_info.items():
            button_lyt = QHBoxLayout()
            button_desc = QLabel()
            button_palette = button_desc.palette()
            button_palette.setColor(QPalette.WindowText, QColor('white'))
            button_desc.setPalette(button_palette)
            button_desc.setFont(QFont('Arial', int(self.w_size[0] * 0.0047)))
            button_desc.setText("NOT SET")
            button_desc.setFixedWidth(int(self.w_size[0] * 0.2))

            button = QPushButton(name)
            button.clicked.connect(self.open_file_dialog)
            button.setFont(QFont('Arial', int(self.w_size[0] * 0.0047)))
            button.setFixedWidth(int(self.w_size[0] * 0.2))
            
            info["path"] = None
            info["button"] = button
            info["label"] = button_desc
            info["layout"] = button_lyt

            button_lyt.addWidget(button)
            button_lyt.addWidget(button_desc)
        
        enable_lyt = QHBoxLayout()
        fillah = QLabel()
        fillah.setFont(QFont('Arial', int(self.w_size[0] * 0.0047)))
        fillah.setText("")
        fillah.setFixedWidth(int(self.w_size[0] * 0.2))
        self.folder_select = False
        self.enable_folder = QPushButton("MODE: Font File")
        self.enable_folder.setFont(QFont('Arial', int(self.w_size[0] * 0.0047)))
        self.enable_folder.setFixedWidth(int(self.w_size[0] * 0.2))
        self.enable_folder.setCheckable(True)
        self.enable_folder.clicked.connect(self.toggle_state)
        enable_lyt.addWidget(self.enable_folder)
        enable_lyt.addWidget(fillah)
        layout.addLayout(enable_lyt)


        for name, info in self.button_info.items():
            layout.addLayout(info["layout"])

        letter_lyt = QHBoxLayout()
        letter_filler = QLabel()
        letter_filler.setFont(QFont('Arial', int(self.w_size[0] * 0.0047)))
        letter_filler.setText("")
        letter_filler.setFixedWidth(int(self.w_size[0] * 0.2))

        self.text_box1 = QLineEdit(self)
        self.text_box1.setPlaceholderText("Enter the character of the single letter")
        self.text_box1.setFont(QFont('Arial', int(self.w_size[0] * 0.0047)))
        self.text_box1.setFixedWidth(int(self.w_size[0] * 0.2))
        letter_lyt.addWidget(self.text_box1)
        letter_lyt.addWidget(letter_filler)
        layout.addLayout(letter_lyt)

        thresh_pnl = QHBoxLayout()
        inner_thresh_pnl = QVBoxLayout()
        inner_thresh_pnl.setAlignment(Qt.AlignCenter)
        self.thresh_desc = QLabel()
        self.thresh_desc.setText('Enter the Percent Match Threshold')
        thresh_palette = self.thresh_desc.palette()
        thresh_palette.setColor(QPalette.WindowText, QColor('white'))
        self.thresh_desc.setPalette(thresh_palette)
        self.thresh_desc.setFont(QFont('Arial', int(self.w_size[0] * 0.0047)))
        self.thresh_desc.setAlignment(Qt.AlignCenter)
        inner_thresh_pnl.addWidget(self.thresh_desc)
        self.prcnt_match = QSlider(Qt.Horizontal)
        self.prcnt_match.setMinimum(0)
        self.prcnt_match.setMaximum(100)
        self.prcnt_match.setValue(40)
        self.prcnt_match.setTickPosition(QSlider.TicksBelow)
        self.prcnt_match.setTickInterval(1)
        self.prcnt_match.setFixedWidth(int(self.w_size[0]*0.7))
        self.prcnt_match.valueChanged.connect(self.update_box)
        self.prcnt_match.setStyleSheet("""
            QSlider::handle:horizontal {
                background: #ec8023;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)

        thresh_pnl.addWidget(self.prcnt_match)
        

        self.text_box2 = QLineEdit(self)
        self.text_box2.setText(str(self.prcnt_match.value()/100))
        self.text_box2.setFont(QFont('Arial', int(self.w_size[0] * 0.004)))
        self.text_box2.setFixedWidth(int(self.w_size[0]*0.02))
        self.text_box2.textChanged.connect(self.update_slider)
        thresh_pnl.addWidget(self.text_box2)
        inner_thresh_pnl.addLayout(thresh_pnl)
        layout.addLayout(inner_thresh_pnl)
        # self.prcnt_match.value()

        self.letter_box = QLineEdit(self)
        self.letter_box.setPlaceholderText("Letters/Numbers to search seperated by commas")
        self.letter_box.setText(', '.join(LETTERS))
        self.letter_box.setFont(QFont('Arial', int(self.w_size[0] * 0.004)))
        # self.letter_box.setFixedHeight(int(self.w_size[1] * 0.2))
        layout.addWidget(self.letter_box)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setFont(QFont('Arial', int(self.w_size[0] * 0.006)))
        self.submit_button.setStyleSheet("background-color: #ec8023; color: white;")
        self.submit_button.setFixedWidth(int(self.w_size[0]*0.2))
        self.submit_button.setFixedHeight(int(self.w_size[1]*0.05))
        layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        button = self.sender()
        if self.folder_select and button.text() == "Select Font File/Dir":
            file_name = QFileDialog.getExistingDirectory(self, "Select Folder")
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select a File", "", "All (*);", options=options)
        if file_name:
            print(file_name, 'added')
            info = self.button_info[button.text()]
            info["path"] = file_name
            info["label"].setText(file_name.split('/')[-1])

    def submit(self):
        print('submit')
        if all([x["path"] is not None for _, x in self.button_info.items()]) and self.text_box1.text() and self.text_box2.text():       # FIX THIS AND ADD IN OTHER DICT STUFF ]) and self.text_box1.text() and self.text_box2.text():
            paths = [x["path"] for k, x in self.button_info.items()]
            letters = self.filter_space(self.letter_box.text())
            self.transition_callback(paths, self.text_box1.text(), self.text_box2.text(), letters)

class SecondStage(QWidget):
    def __init__(self, w_size, paths, t1,t2, letters):
        super().__init__()
        self.w_size = w_size
        self.encoded_path = paths[1]
        self.paths = paths
        self.t1 = t1
        self.t2 = float(t2)
        self.letters = letters
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Image
        self.image_label = QLabel()
        pixmap = self.get_pixmap(self.encoded_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # Text Box
        self.text_box = QTextEdit(self)
        self.text_box.setPlaceholderText("Result text box")
        self.text_box.setText(f"")  # Display the inputs
        self.text_box.setFont(QFont('Arial', int(self.w_size[0]*0.004)))
        self.text_box.setFixedHeight(int(self.w_size[0]*0.05))
        layout.addWidget(self.text_box)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #ec8023;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.font_cracker = FontCracker()
        self.worker = Worker()
        self.worker.font_cracker = self.font_cracker
        self.worker.progress.connect(self.update_progress)
        
        self.cracker = Cracker()
        self.cracker.set_fields(self.paths[0], self.paths[1], self.paths[2], self.t1, self.letters, self.t2)
        self.cracker.update_img.connect(self.message_solved)
        self.cracker.font_cracker = self.font_cracker


        self.worker.start()
        self.cracker.start()

        self.setLayout(layout)

    def message_solved(self, msg):
        self.text_box.setText(msg[1])
        pixmap = self.get_pixmap(msg[0])
        self.image_label.setPixmap(pixmap)
        

    def get_pixmap(self, path):
        pixmap = QPixmap(path)  # Change to a valid image path

        width = pixmap.width()
        height = pixmap.height()
        ratio = width/height
        if width > height:
            width = round(self.w_size[0] * 0.98)
            height = round(width/ratio)
        else:
            height = round(self.w_size[1] * 0.8)
            width = round(height*ratio)
        self.image_label.setPixmap(pixmap)
        pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.FastTransformation)
        return pixmap

    def update_progress(self, value):
        self.progress_bar.setValue(int(value))

class MainWindow(QWidget):
    def __init__(self, w_size):
        super().__init__()
        self.w_size = w_size
        self.setWindowTitle("Two Stage GUI")
        self.first_stage = FirstStage(self.show_second_stage, self.w_size)
        self.layout = QStackedLayout()
        self.layout.addWidget(self.first_stage)
        self.setLayout(self.layout)
        self.setFixedSize(self.w_size[0], self.w_size[1])

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('#195394'))
        self.setPalette(palette)

        self.setWindowIcon(QIcon('res/logo/wizard.svg'))
        self.setWindowTitle("Font Cracker")


    def show_second_stage(self, text1, text2, text3, letters):
        self.second_stage = SecondStage(self.w_size, text1, text2, text3, letters)
        self.layout.itemAt(0).widget().setParent(None)  # Remove first stage
        self.layout.addWidget(self.second_stage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow(
        (int(app.primaryScreen().size().width()*.98),
         int(app.primaryScreen().size().height()*.98))
    )
    main_window.show()
    sys.exit(app.exec_())
