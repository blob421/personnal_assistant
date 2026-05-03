from PyQt6.QtWidgets import QWidget, QVBoxLayout
from GUI.titles import Title
from PyQt6.QtCore import Qt
from GUI.styles import styles

class MovieScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet(styles['movie'])
        layout.setContentsMargins(0, 0 , 0 ,0)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)


        self.title = Title('Movies')
        self.MovieBox = MovieBox()
        layout.addWidget(self.title, 1)
        layout.addWidget(self.MovieBox, 9)


class MovieBox(QWidget):
    def __init__(self):
        super().__init__()   
        self.layout = QVBoxLayout()
        self.setObjectName('movie_box')

    def add_item(self, item):
        widget = Movie_Item()
        self.layout.addWidget(widget)

  
    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

class Movie_Item(QWidget):
    def __init__(self):
        super().__init__()    
          