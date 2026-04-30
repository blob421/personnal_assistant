from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton, 
                             QListWidgetItem, QInputDialog, QMessageBox,   QDialog,  QLineEdit, QMenu)
from GUI.styles import styles
from GUI.home.prompt_history import Prompt_label
from PyQt6.QtCore import Qt, QSize

from utilities.db_calls import delete_keyword, add_keyword_gui, add_contact, load_contacts, delete_contact


class RightMenu(QWidget):
    def __init__(self,  name, vocal_handler, left_menu):
        super().__init__()
        self.left_menu = left_menu
        layout = QVBoxLayout()
        self.name = name
        self.keywords = None
      
        self.vocal_handler = vocal_handler
        
           

        self.setLayout(layout)
        self.setStyleSheet(styles[name])
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        
        self.setMinimumWidth(200)
        self.setMaximumWidth(330)

        self.title = Prompt_label('Watched')
        self.title.setObjectName('title_contact_List')
        self.title.setFixedHeight(65)

        self.items_list = ItemsList(self, self.keywords)

        add_button = AddButton('Add +', self, self.name)

       

        layout.addWidget(self.title)
        layout.addWidget(self.items_list)
        layout.addWidget(add_button)


    
class ItemsList(QListWidget):
    def __init__(self, menu , keywords=None):
        super().__init__()
        self.menu = menu
        self.setStyleSheet(styles[menu.name])
       
        if keywords:
            for k in keywords:
               self.add_item(k, 'keywords')
        else:
            contacts = load_contacts()
          
            menu.vocal_handler.contacts = contacts
            if contacts:
                for k, v in contacts.items():
                    self.add_item({'alias': v, 'email': k}, 'contacts')


    def add_item(self, unit, type):

        item = QListWidgetItem()
       
        if type == 'keywords':

            widget = KeywordsListWidget(unit, self.menu, item)
        else:
            widget = ContactListWidget(unit, self.menu, item)

        item.setSizeHint(QSize(0, 90))
        self.addItem(item)  
        self.setItemWidget(item, widget)

class ListWidget(QWidget):
    def __init__(self, menu, widget_item):
        super().__init__()    
        self.menu = menu   
        self.widget_item = widget_item
      
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5, 5 , 5 , 5)
        self.setMinimumHeight(90)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('list_item')

        self.x_btn = QPushButton('X')
        
        self.x_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.x_btn.setObjectName('x_btn')


        self.x_btn.setFixedSize(35,35)


class ContactListWidget(ListWidget):
    def __init__(self, unit, menu, widget_item):
        super().__init__(menu, widget_item)
        contact_widget = ContactWidget(unit['email'], unit['alias'])
        self.layout.addWidget(contact_widget)
        self.layout.addWidget(self.x_btn, alignment=Qt.AlignmentFlag.AlignTop)
        self.x_btn.clicked.connect(lambda: self.delete_c(unit['alias']))

    def delete_c(self, name):
        reply = QMessageBox.question(
        self,
        "Confirm deletion",
        f"Delete {name} from contacts'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

        if reply == QMessageBox.StandardButton.Yes:
            delete_contact(name)
            row = self.menu.items_list.row(self.widget_item)
            self.menu.items_list.takeItem(row) 
    
            self.menu.items_list.removeItemWidget(self.widget_item)
            self.menu.left_menu.left_cont.bottom.load_messages()
      
class ContactWidget(QWidget):
    def __init__(self, email_str, alias_str):
        super().__init__()
        self.setObjectName('contact_unit')
        layout = QVBoxLayout()
        self.setLayout(layout)
        email = QLabel(email_str)
        alias = QLabel(alias_str)
        alias.setObjectName('contact_alias')
        email.setObjectName('contact_email')
        layout.addWidget(alias)
        layout.addWidget(email)

class KeywordsListWidget(ListWidget):
    def __init__(self, label_name, menu, widget_item):
        super().__init__(menu, widget_item)
      
        label = QLabel(label_name)
        label.setObjectName('keyword_label')

        self.x_btn.clicked.connect(lambda: self.delete_k(label_name))

        self.layout.addWidget(label)
        self.layout.addWidget(self.x_btn)


    def delete_k(self, keyword):
        dialog = QMessageBox()
        reply = dialog.question(self,
        "Confirm deletion",
        f"Delete keyword : '{keyword}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
  
      
        

        if reply == QMessageBox.StandardButton.Yes:
            delete_keyword(keyword)
            row = self.menu.keywords_list.row(self.widget_item)
            self.menu.keywords_list.takeItem(row) 
            self.menu.vocal_handler.keywords.remove(keyword)
            self.menu.keywords_list.removeItemWidget(self.widget_item)


       
class TwoInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter contact")
        self.setMinimumSize(350, 150)

        layout = QVBoxLayout(self)

        # First input
        layout.addWidget(QLabel("Alias:"))
        self.input1 = QLineEdit()
        self.input1.setMaxLength(19)
        layout.addWidget(self.input1)

        # Second input
        layout.addWidget(QLabel("Email:"))
        self.input2 = QLineEdit()
        layout.addWidget(self.input2)

        # Buttons
        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def getValues(self):
        return self.input1.text(), self.input2.text(), self.result() == QDialog.DialogCode.Accepted
    

class AddButton(QPushButton):
    def __init__(self, label_name, menu, type):
        super().__init__()
        self.menu = menu
        self.setText(label_name)
        if type == 'keywords':
            self.clicked.connect(self.add_keyword)
        else:
            self.clicked.connect(self.add_contact_button)

        self.setStyleSheet(styles['dialogs'])
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def add_keyword(self):
        text, ok = QInputDialog.getText(
            self,                     # parent → centers on your window
            "Enter keyword",          # title
            "Type the new keyword:"   # label
        )
      
        if text and ok :
            add_keyword_gui(text)
            self.menu.vocal_handler.keywords.add(text)
            self.menu.keywords_list.add_item(text)

    def add_contact_button(self):
        dialog = TwoInputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            alias = dialog.input1.text()
            email = dialog.input2.text()
    
            contact = {'alias': alias, 'email': email}
            add_contact(contact)
            self.menu.left_menu.left_cont.bottom.contacts[email] = alias
            self.menu.left_menu.left_cont.bottom.load_messages()
            self.menu.vocal_handler.contacts[alias] = email
            self.menu.items_list.add_item(contact, 'contacts')
   
       




