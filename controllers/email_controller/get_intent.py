from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
from controllers.email_controller.intent_words import GOOD_WORDS, BAD_WORDS, URGENT_WORDS, HOSTILE_WORDS
import json

async def get_intent(emails, controller):
    intent_emails = []
    reload = False
    for e in emails:
        if not e['sender'] in controller.watchlist:
            intent_emails.append({**e, 'tags': None})
            continue

        reload = True
        score, tags = await score_message(e['text'])
        if score < 0 :
            tags.add('bad')
        elif score > 0 :
            tags.add('good')

        intent_emails.append({**e, 'tags': json.dumps(list(tags))})

    return intent_emails, reload

async def score_message(text):
    blob = TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
    polarity = blob.sentiment[0]   # -1 to +1
    tags = set()
    score = polarity * 2  # Basic +2 or -2 as fallback

    text_lower = text.lower()
    
    if any(w in text_lower for w in GOOD_WORDS):
        tags.add('good')
        score += 1

    if any(w in text_lower for w in BAD_WORDS):
        tags.add('bad')
        score -= 1

    if any(w in text_lower for w in URGENT_WORDS):
        tags.add('urgent')
        score -= 2

    if any(w in text_lower for w in HOSTILE_WORDS):
        tags.add('hostile')
        score -= 3

    return score, tags

    
