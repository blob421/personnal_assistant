import re
import spacy
from utilities.db_calls import get_pending_events, save_event
from collections import defaultdict
nlp = spacy.load("en_core_web_sm")

async def are_keywords_in_messages(messages:list, keywords:list):
    occurences = {}
    found = []
  
    for m in messages:
        sender = m['sender']
        text = m['text']
       
        subject = m['subject']
    
        for k in keywords:
            if text:
                if k.lower() in text.lower() or k.lower() in subject.lower():
                    found.append({'keyword': k, 'sender': sender})
                    occurences[k] = occurences.get(k, 0) + 1
            else:
                if k.lower() in subject.lower():
                    found.append({'keyword': k, 'sender': sender})
                    occurences[k] = occurences.get(k, 0) + 1
                
    return found, occurences

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
    pending = await get_pending_events()
    if pending:       
        for o in pending:
         
            prompt_types[o['type']].append(o['message'])

  
    return {'result': prompt_types}


async def make_announcements(keywords:dict, notif_engine, GUI_link):
    announcements = []
    aggregated = {}
    for k in keywords:
        sender = k['sender']
        keyword = k['keyword']

        if not aggregated.get(keyword):
            aggregated[keyword] = []

        aggregated[keyword].append(sender)

    for idx, (k, senders) in enumerate(aggregated.items()):
            senders_string = ', '.join(senders)

            if idx == 0:
                full_string = f'The keyword {k} was found in messages sent by {senders_string}'
            else:
                full_string = f', the keyword {k} was found in mails coming from {senders_string}'

            notif_engine.notify('Keyword found', 
                                     f'the keyword {k} was found in mails coming from {senders_string}')
            
            announcements.append(full_string)
            await save_event('Keywords found', full_string)
            
    GUI_link.reload_requested.emit()

    return announcements