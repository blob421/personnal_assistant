import re
import spacy
from utilities.db_calls import get_pending_events
from collections import defaultdict
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




def extract_gmail_msgid(msg_data):

    for part in msg_data:
        if isinstance(part, (bytes, bytearray)):
            header = part.decode(errors='ignore')

            match = re.search(r'X-GM-MSGID\s+(\d+)', header, re.IGNORECASE)
            if match:
                return match.group(1)
    return None

async def extract_pending_prompts():
    prompt_types = defaultdict(list)
    prompt_missed = False
    pending = await get_pending_events()
    if pending:
               
        for o in pending:
            if not prompt_missed and o['type'] == 'Daily prompt':
                prompt_missed = True
            else:
                prompt_types[o['type']].append([o['message']])

  
    return {'prompt_pending': prompt_missed, 'result': prompt_types}

