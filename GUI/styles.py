styles = {
   
  

    'screen_title': """
                            background-color: white;
                            color: black;
                           
                            padding: 10px;
                            padding-right: 200;
                            font-size: 18px;
                            font-weight: bold;
                        """,


    'option_panel': """QWidget#option_panel {
                    background-color: #1B2A49;
                    padding: 10px;
               
                    border-radius: 10px;
                    border: 2px solid white;
                    border-left: 0px;
                    }
""",
   'options': """
                     OptionsContainer {
                     padding-left: 50px;
                     padding-top: 20px;
                     border-bottom: 1px solid grey;
                     padding-bottom: 10px;
                     color: white;
                     font-size: 33px;
                         }

                     QLabel {
                     font-size: 33px;
                     }

                     TimeWidget {
                     font-size: 33px;
                     }

""",
   'titles': """   
            font-size: 40px;
            font-weight: bold;
            color: white;
            background-color: #326fa8;
       
             """,

    'options_container': """
font-size: 30px;
  color: white;
  border-bottom: 1px solid white;
                         """,

    'checkboxes': """
            QCheckBox::indicator {
                width: 30px;
                height: 30px;
                border: 2px solid black;
                background-color: grey;
                border-radius: 10px;
            }

            QCheckBox::indicator:checked {
                background-color: lightgreen;
            }
""", 

  'history': """

          Prompt_label {
                font-size: 30px;
                background-color: black;
                color: white;
                
          }
          
          Prompt_history {
                background-color: black;
                color: white;
                font-size: 22px;
            
                font-weight: bold;

          }
     
          #prompt_unit {
               border-bottom: 1px solid grey; background-color: black; padding-left: 20px; 
                        
          }
          QLabel {
           border-bottom: 1px solid grey; font-size: 29px;
          }


          #unit_type_label {
             font-size: 24px; 
          }
          #unit_content_label {
             font-size: 24px; padding-left:10px; padding-right: 10px;
          }
          #unit_time_label {
            font-size: 24px
          }
          
"""

,
     
       'keywords': """
                 Prompt_label {
                     font-size: 30px;
                  color: white;
                 }

                 KeywordsMenu {
              
                border: 1px solid grey;
                 background-color: #1f293b;
                }

                KeyWordsList {
                 font-size: 26px;
                  margin-top: 12px;
                  color: white;
                }
                QLabel {
                font-size: 30px;
                }
                QPushButton {
                font-size: 25px;
                }
     

""",
      'dialogs': """
 QInputDialog {
        font-size: 26px;
        min-width: 400px;
        min-height: 300px;
    }
    QLabel {
        font-size: 26px;
    }
    QLineEdit {
        font-size: 24px;
        padding: 6px;
    }
    QPushButton {
        font-size: 24px;
        padding: 6px 14px;
    }

"""


    
}