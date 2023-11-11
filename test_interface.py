
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog
from PyQt5.QtGui import QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
 
        # Create a menu bar and add a "Open Image" action
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_image_action = QAction('Open Image', self)
        open_image_action.triggered.connect(self.browse_image)
        file_menu.addAction(open_image_action)
 
        # Create a QLabel to display the loaded image
        self.image_label = QLabel(self)
        self.setCentralWidget(self.image_label)
 
    def browse_image(self):
        print(self)
        # Open a file dialog to browse for an image file
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image files (*.jpg *.jpeg *.png)')
 
        # Load the selected image and display it in the QLabel
        if filename:
            pixmap = QPixmap(filename)
            self.image_label.setPixmap(pixmap)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())