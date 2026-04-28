styles = {

    'left_menu': """
                #left_menu {
                    background-color: #656075;
                    border-radius: 12px; 

                }
                Image_button {
                border-radius: 12px;
                background-color: lightgrey;
                
                }
                ButtonContainer {
                padding-top:8px; padding-bottom:8px;
                }
                Image_button::hover {
                background-color: grey;
            
                }
    """,




   'options': """
            OptionsContainer {
            padding-left: 50px;
            padding-top: 20px;
            border-bottom: 1px solid lightgrey;
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
            font-size: 38px;
            font-weight: bold; 
            color: white;
            padding-left: 30px;
            border: 2px solid grey;
            background-color: #695994; border-radius:12px;
       
             """,

    'options_container': """
font-size: 30px;
  color: white;
  
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

          #prompt_box {
          background-color:black;
          border: 1px solid lightgrey; border-radius: 12px;
          
          }
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

          #top_col_prompts {
          font-size: 24px; padding-left:10px; background-color:grey; 
          }

          #top_col_cont {
            padding-left: 10px; background-color:black;
          }

          
          #prompt_unit {
               border-bottom: 1px solid grey; background-color: black; font-size: 24px;
               padding-bottom: 5px; padding-top: 5px; 
                        
          }
        
          #prompts_col_names{
           font-size: 24px; padding-left: 10px;
          }

          #unit_type_label {
             font-size: 23px; background-color:#4a4a4a; padding-left:2px; padding-left: 10px;
          }
          #unit_content_label {
             font-size: 24px;  padding-left:2px; padding-left: 10px; padding-right:10px;
             background-color:black;
          }
          #unit_time_label {
            font-size: 24px; padding-right: 10px; padding-left:2px;border-left: 1px solid grey;
            background-color:black; padding-left: 10px;
          }

          #prompts_separator {
          font-size:24px; color: grey; padding-bottom:24px; border-bottom: 1px solid grey;
          background-color: black; padding-top:10px; 
          }
          
"""

,
     
       'keywords': """
                 Prompt_label {
                     font-size: 30px; border-bottom:2px solid black;
                  color: white;
                 }

                 KeywordsMenu {
              
                border: 2px solid grey;
                 background-color: #1f293b; border-radius:9px;
                }

                KeyWordsList {
                 font-size: 26px;
                  margin-top: 12px;
                  color: white;
                }
                #list_item {
                background-color:#5a3999; border-bottom: 2px solid black; margin-bottom: 2px;
                
                }
        
                #keyword_label{
                    font-size: 26px;
                }

            
          
                   
                #x_btn_keywords {
                font-size: 25px; background-color:grey; border: 1px solid black;
                border-radius: 7px;
                }
                #x_btn_keywords::hover {
                background-color: #ba4141;
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