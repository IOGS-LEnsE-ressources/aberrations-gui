import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QTextEdit
)
from PyQt6.QtCore import Qt

# Styles CSS
widget_style = """background-color: #f0f0f0; /* Couleur de fond */
    border: 1px solid #ccc; /* Bordure grise */
    border-radius: 10px; /* Coins arrondis */
    padding: 10px; /* Espacement intérieur */"""

button_style = """
    QPushButton {
        background-color: #4CAF50; /* Green */
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    QPushButton:hover {
        background-color: #45a049; /* Darker green */
    }
    QPushButton:pressed {
        background-color: #2e7d32; /* Even darker green */
    }
"""

label_style = """QLabel {
    color: #333; /* Text color */
    font-size: 16px; /* Font size */
    margin: 4px 2px; /* Margin */
}"""

line_edit_style = """QLineEdit {
    background-color: #fff; /* White background */
    border: 1px solid #ccc; /* Light gray border */
    padding: 10px; /* Padding */
    font-size: 16px; /* Font size */
    border-radius: 5px; /* Rounded corners */
    margin: 4px 2px; /* Margin */
}

QLineEdit:focus {
    border-color: #4CAF50; /* Green border on focus */
}

QCheckBox {
    font-size: 16px; /* Font size */
    margin: 4px 2px; /* Margin */
}"""

checkbox_style = """QCheckBox::indicator {
    width: 20px;
    height: 20px;
}

QCheckBox::indicator:unchecked {
    border: 1px solid #ccc; /* Light gray border */
    background-color: #fff; /* White background */
    border-radius: 5px; /* Rounded corners */
}

QCheckBox::indicator:checked {
    border: 1px solid #4CAF50; /* Green border */
    background-color: #4CAF50; /* Green background */
    border-radius: 5px; /* Rounded corners */
}"""

combobox_style = """
    QComboBox {
        background-color: #fff; /* White background */
        border: 1px solid #ccc; /* Light gray border */
        padding: 8px; /* Padding */
        font-size: 16px; /* Font size */
        border-radius: 5px; /* Rounded corners */
        margin: 4px 2px; /* Margin */
    }

    QComboBox::drop-down {
        border: none; /* No border for the dropdown arrow */
        width: 20px; /* Width of the dropdown arrow area */
    }

    QComboBox::down-arrow {
        image: url(down_arrow.png); /* Replace with your own arrow icon */
    }

    QComboBox::down-arrow:on {
        /* Optional: Style when dropdown is pressed */
        top: 1px;
        left: 1px;
    }

    QComboBox::down-arrow:off {
        /* Optional: Style when dropdown is not pressed */
        top: 1px;
        left: 1px;
    }

    QComboBox::down-arrow:pressed {
        /* Optional: Style when dropdown is pressed */
        top: 2px;
        left: 2px;
    }

    QComboBox::down-arrow:disabled {
        /* Optional: Style when dropdown is disabled */
        image: url(disabled_down_arrow.png); /* Replace with your own disabled arrow icon */
    }

    QComboBox::drop-down:hover {
        /* Optional: Hover effect for dropdown arrow */
        background-color: #f0f0f0;
    }

    QComboBox::down-arrow:hover {
        /* Optional: Hover effect for dropdown arrow */
        background-color: #f0f0f0;
    }
"""

# Fenêtre principale PyQt6
class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PyQt6 Test Window')
        self.setGeometry(100, 100, 800, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Layout supérieur
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # Label et LineEdit dans le layout supérieur
        self.label_name = QLabel("Name:")
        self.label_name.setStyleSheet(label_style)
        top_layout.addWidget(self.label_name)
        
        self.lineedit_name = QLineEdit()
        self.lineedit_name.setStyleSheet(line_edit_style)
        top_layout.addWidget(self.lineedit_name)

        self.label_age = QLabel("Age:")
        self.label_age.setStyleSheet(label_style)
        top_layout.addWidget(self.label_age)
        
        self.lineedit_age = QLineEdit()
        self.lineedit_age.setStyleSheet(line_edit_style)
        top_layout.addWidget(self.lineedit_age)

        # Layout des boutons
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        self.button_submit = QPushButton("Submit")
        self.button_submit.setStyleSheet(button_style)
        buttons_layout.addWidget(self.button_submit)
        
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.setStyleSheet(button_style)
        buttons_layout.addWidget(self.button_cancel)

        # Layout des cases à cocher
        checkbox_layout = QHBoxLayout()
        main_layout.addLayout(checkbox_layout)

        self.checkbox_option1 = QCheckBox("Option 1")
        self.checkbox_option1.setStyleSheet(checkbox_style)
        checkbox_layout.addWidget(self.checkbox_option1)
        
        self.checkbox_option2 = QCheckBox("Option 2")
        self.checkbox_option2.setStyleSheet(checkbox_style)
        checkbox_layout.addWidget(self.checkbox_option2)

        # Layout du ComboBox
        combobox_layout = QHBoxLayout()
        main_layout.addLayout(combobox_layout)

        self.combobox = QComboBox()
        self.combobox.setStyleSheet(combobox_style)
        self.combobox.addItems(["Choice 1", "Choice 2", "Choice 3"])
        combobox_layout.addWidget(self.combobox)

        # Layout du QTextEdit
        textedit_layout = QVBoxLayout()
        main_layout.addLayout(textedit_layout)

        self.textedit = QTextEdit()
        textedit_layout.addWidget(self.textedit)

        # Layout imbriqué
        nested_layout = QGridLayout()
        main_layout.addLayout(nested_layout)

        self.label_nested_1 = QLabel("Nested Label 1")
        self.label_nested_1.setStyleSheet(label_style)
        nested_layout.addWidget(self.label_nested_1, 0, 0)
        
        self.label_nested_2 = QLabel("Nested Label 2")
        self.label_nested_2.setStyleSheet(label_style)
        nested_layout.addWidget(self.label_nested_2, 0, 1)
        
        self.button_nested = QPushButton("Nested Button")
        self.button_nested.setStyleSheet(button_style)
        nested_layout.addWidget(self.button_nested, 1, 0, 1, 2)

        # Connexion des signaux
        self.button_submit.clicked.connect(self.submit)
        self.button_cancel.clicked.connect(self.cancel)

    def submit(self):
        name = self.lineedit_name.text()
        age = self.lineedit_age.text()
        selected_option1 = self.checkbox_option1.isChecked()
        selected_option2 = self.checkbox_option2.isChecked()
        selected_choice = self.combobox.currentText()
        text_content = self.textedit.toPlainText()

        print(f"Name: {name}")
        print(f"Age: {age}")
        print(f"Option 1: {selected_option1}")
        print(f"Option 2: {selected_option2}")
        print(f"Selected Choice: {selected_choice}")
        print(f"Text Content: {text_content}")

    def cancel(self):
        self.lineedit_name.clear()
        self.lineedit_age.clear()
        self.checkbox_option1.setChecked(False)
        self.checkbox_option2.setChecked(False)
        self.combobox.setCurrentIndex(0)
        self.textedit.clear()
        print("Canceled")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
