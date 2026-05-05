from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtGui import QPixmap
from GUI.titles import Title
from PyQt6.QtCore import Qt
from GUI.styles import styles
import config
import os 




class MovieScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet(styles['movie'])
        layout.setContentsMargins(0, 0 , 0 ,0)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.movie_controller = None
   
        self.title = Title('Movies')
        self.MovieBox = MovieBox(self)
        layout.addWidget(self.title, 1)
        layout.addWidget(self.MovieBox, 9)

    def init_movies(self):
        self.MovieBox.movies = []
        self.suggestions = self.movie_controller.best_movies
      
        for idx, m in enumerate(self.suggestions):
            self.suggestions[idx]['poster_path'] = os.path.join(config.POSTERS_PATH, f'{m['imdbId']}.jpg')
            self.MovieBox.add_item(m)
        self.MovieBox.show_poster()
        

class MovieBox(QWidget):
    def __init__(self, master):
        super().__init__()   
        self.master = master
        self.layout = QHBoxLayout()
        self.setObjectName('movie_box')
        self.setLayout(self.layout)
        self.movies = []
      
        self.poster_idx = 0

    def add_item(self, item):
        widget = Movie_Item(item, self)
        self.movies.append(widget)
    
    def show_poster(self, next=False):
        self.clear_layout()
   
        if self.poster_idx == 2:
            self.poster_idx = 0
        else: 
            self.poster_idx += 1

        self.layout.addWidget(self.movies[self.poster_idx], 3)
        
  
    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)


class Movie_Item(QWidget):
    def __init__(self, movie, moviebox):
        super().__init__()
        self.parent = moviebox
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.movie = movie
   
        self.image_widget = Movie_Img_Widget(movie, moviebox)
        content_widget = Title_plot(movie)
        buttons_bar = Movie_Buttons_Widget(self)
       
     
        layout.addWidget(self.image_widget, 3)
        layout.addWidget(content_widget, 6)
        layout.addWidget(buttons_bar, 1)
 


class Title_plot(QWidget):
    def __init__(self, movie):
        super().__init__()    
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setObjectName('movie_content')
        title_label = QLabel(movie['title'])
        plot_label = QLabel(movie['plot'])
        plot_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label.setObjectName('movie_title')
        title_label.setFixedHeight(100)
        plot_label.setObjectName('movie_plot')
        plot_label.setWordWrap(True)

        self.layout.addWidget(title_label)
        self.layout.addWidget(plot_label)



class Movie_Buttons_Widget(QWidget):
    def __init__(self, parent):
        super().__init__()    
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.parent = parent
      

        self.like_btn = Movie_Button('liked', parent, self)
        self.seen_btn = Movie_Button('seen', parent, self)
        self.not_interested = Movie_Button('interested', parent, self)
        
       
        self.layout.stretch(1)
        self.layout.addWidget(self.like_btn)
        self.layout.addWidget(self.seen_btn)
        self.layout.addWidget(self.not_interested)
        self.scramble = QPushButton('Scramble')
        self.scramble.setObjectName('scramble')
        self.scramble.clicked.connect(self.parent.parent.master.movie_controller.signals_worker.scramble.emit)
        self.layout.addWidget(self.scramble, alignment=Qt.AlignmentFlag.AlignBottom)
        

    def switch_interest(self):
        self.not_interested.invert()
        self.parent.parent.master.movie_controller.signals_worker.interested.emit()
        
    def like_movie(self):
        self.like_btn.invert()
        self.parent.parent.master.movie_controller.signals_worker.liked.emit()

    def handle_seen(self):
        self.seen_btn.invert()
        self.parent.parent.master.movie_controller.signals_worker.seen.emit()


class MoveSuggestionWidget(QWidget):
    def __init__(self, grandparent):
        super().__init__()    
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
   
        move_btn = QPushButton('>')
        move_btn.setObjectName('next_btn')
        move_btn.clicked.connect(grandparent.show_poster)
        move_btn.setMaximumWidth(200)
        layout.addWidget(move_btn)


class Movie_Img_Widget(QWidget):
    def __init__(self, movie, parent):
        super().__init__()    
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        image_label = PosterLabel(movie['poster_path'])
        image_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        move_suggestion_widget = MoveSuggestionWidget(parent)
        self.layout.addWidget(image_label, 9)
        self.layout.addWidget(move_suggestion_widget, 1)



class PosterLabel(QLabel):
    def __init__(self, path):
        super().__init__()
        self.original = QPixmap(path)

        # Important: DO NOT let Qt stretch the pixmap itself
        self.setScaledContents(False)

        # Let the label grow and shrink freely
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

    def resizeEvent(self, event):
        if not self.original.isNull():
            scaled = self.original.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)

        super().resizeEvent(event)


class Movie_Button(QPushButton):
    def __init__(self, type, movie_item, buttons_widget):
        super().__init__()
        self.type = type
        self.movie_item = movie_item
        self.setFixedWidth(200)
        self.imdbId = movie_item.movie['imdbId']
        self.option_idx = 1
        self.class_options = {'liked': ['movie_side_btns', 'liked'], 
                              'interested': ['movie_side_btns', 'not_interested'],
                              'seen': ['movie_side_btns', 'seen']}
        
        self.text_options = {'liked': ['Like', 'Liked'], 
                              'interested': ['Interested', 'Not Interested'],
                              'seen': ['Not seen', 'Seen']}

        if type == 'liked':
            self.clicked.connect(buttons_widget.like_movie)
            if not movie_item.movie['liked']:
                self.option_idx = 0

        elif type == 'interested':
            self.clicked.connect(buttons_widget.switch_interest)

            if movie_item.movie['interested']:
                self.option_idx = 0


        elif type == 'seen':
            self.clicked.connect(buttons_widget.handle_seen)

            if not movie_item.movie['seen']:
                self.option_idx = 0
           

        self.text = self.text_options[type][self.option_idx]
        self.setObjectName(self.class_options[type][self.option_idx])
        self.setText(self.text)


    def invert(self):
   
  
        if self.option_idx == 0:
            self.setText(self.text_options[self.type][1])
            self.option_idx = 1
            self.setObjectName(self.class_options[self.type][1])
        else:
            self.setText(self.text_options[self.type][0])
            self.option_idx = 0
            self.setObjectName(self.class_options[self.type][0])       
                
        self.setStyle(self.movie_item.style())

    