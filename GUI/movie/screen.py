from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtGui import QPixmap
from GUI.titles import Title
from PyQt6.QtCore import Qt
from GUI.styles import styles
import config
import os 
from controllers.movies.db_calls import not_interested_movie, like_movie

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
   
        
        content_widget = Title_plot(movie)
        buttons_bar = Movie_Buttons_Widget(self)
       
        self.image_widget = Movie_Img_Widget(movie, moviebox)
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
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        liked = self.parent.movie['liked']
        text_like_btn = 'Like' if not liked else 'Liked'
        class_like_btn = 'movie_side_btns' if not liked else 'liked'

        self.like_btn = QPushButton(text_like_btn)
        self.like_btn.clicked.connect(lambda: self.like_movie(parent.movie['imdbId']))
        self.seen_btn = QPushButton('Seen')
        self.seen_btn.clicked.connect(lambda: self.like_movie(parent.movie['imdbId']))

        button_text = 'Interested' if parent.movie['interested'] else 'Not interested'
        self.not_interested = QPushButton(button_text)

        self.not_interested.clicked.connect(
            lambda : self.switch_interest(parent.movie['imdbId']))
        interest_btn_class = 'movie_side_btns' if parent.movie['interested'] else 'not_interested'

        self.not_interested.setObjectName(interest_btn_class)
        self.not_interested.setFixedWidth(200)
        self.seen_btn.setFixedWidth(200)
        self.like_btn.setFixedWidth(200)
        self.like_btn.setObjectName(class_like_btn)
        self.seen_btn.setObjectName('movie_side_btns')

       
        self.layout.addWidget(self.like_btn)
        self.layout.addWidget(self.seen_btn)
        self.layout.addWidget(self.not_interested)
        
    def switch_interest(self, id):
        index = self.parent.parent.poster_idx
        interest =  self.parent.parent.master.suggestions[index]['interested']
        self.parent.parent.master.suggestions[index]['interested'] = not interest

        interest_btn_class = 'movie_side_btns' if not interest else 'not_interested'
        button_text = 'Interested' if not interest else 'Not interested'
        self.not_interested.setObjectName(interest_btn_class)
        self.not_interested.setText(button_text)
        self.not_interested.setStyle(self.style())
        not_interested_movie(id, not interest)
        
    def like_movie(self, id):
        master = self.parent.parent.master
        master.movie_controller.like_movie(id)
        index = self.parent.parent.poster_idx
        liked = master.suggestions[index]['liked']
        self.parent.parent.master.suggestions[index]['liked'] = not liked
       
        text = 'Like' if liked else 'Liked'
        classname = 'movie_side_btns' if liked else 'liked'

        self.like_btn.setText(text)
        self.like_btn.setObjectName(classname)
        self.like_btn.setStyle(self.style())
        like_movie(not liked, id)



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

