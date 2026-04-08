
import spacy
nlp = spacy.load("en_core_web_sm")

async def are_keywords_in_messages(messages:list, keywords:set):
    found = []
     
    for m in messages:
        sender = m['sender']
        text = m['text']
       
        subject = m['subject']
    
        for k in keywords:
            if text:
                if k.lower() in text.lower() or k.lower() in subject.lower():
                    found.append({'keyword': k, 'sender': sender})
            else:
                if k.lower() in subject.lower():
                    found.append({'keyword': k, 'sender': sender})
                
    return found

def extract_nouns(text):
    doc = nlp(text)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]