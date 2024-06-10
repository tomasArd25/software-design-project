import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QSettings

class Edit_window(QWidget):
    def __init__(self, mode):
        super().__init__()

        self.settings_cstm = QSettings('tomasArd25', 'SysInfo')

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle('Edit')
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout(self)

        # Combo box for font size selection
        self.font_size_cb = QComboBox(self)
        self.font_size_cb.addItems(["Small", "Medium", "Large"])
        self.font_size_cb.currentIndexChanged.connect(self.set_font_size)

        # Sample label
        self.label = QLabel("Sample Text", self)

        # Button to toggle dark/light mode
        self.toggle_button = QPushButton("Toggle Dark/Light Mode", self)
        self.toggle_button.clicked.connect(self.toggle_dark)

        self.layout.addWidget(self.font_size_cb)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.toggle_button)

    def load_settings(self):
        # Load saved font size setting
        self.font_size = self.settings_cstm.value("font_size", "Medium")
        self.font_size_cb.setCurrentText(self.font_size)
        self.set_font_size()

        # Load saved mode setting
        self.mode = self.settings_cstm.value("mode", "light")
        self.apply_mode()

    def toggle_dark(self):
        if self.mode == "light":
            self.mode = "dark"
        else:
            self.mode = "light"
        
        self.apply_mode()

    def apply_mode(self):
        if self.mode == "light":
            self.apply_light_mode()
        else:
            self.apply_dark_mode()

        self.settings_cstm.setValue("mode", self.mode)

    def apply_light_mode(self):
        self.setStyleSheet("background-color: #EEEEEE;")
        self.update_widget_stylesheet(
            color="black",
            background_color="#DFDFDF"
        )

    def apply_dark_mode(self):
        self.setStyleSheet("background-color: #111111;")
        self.update_widget_stylesheet(
            color="white",
            background_color="#202020"
        )

    def update_widget_stylesheet(self, color, background_color):
        self.label.setStyleSheet(f"QLabel{{color: {color}; font-size: 30px; font-weight: bold;}}")
        self.set_font_size()

    def set_font_size(self):
        font_size_cb = self.font_size_cb.currentText()
        if font_size_cb == "Small":
            font_size = 9
        elif font_size_cb == "Medium":
            font_size = 12
        elif font_size_cb == "Large":
            font_size = 15

        self.label.setStyleSheet(f"QLabel{{font-size: {font_size}px; font-weight: bold;}}")
        self.settings_cstm.setValue("font_size", font_size_cb)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Edit_window("light")  # Initial mode can be set to "light" or "dark"
    window.show()
    sys.exit(app.exec_())
