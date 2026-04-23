from email import message_from_bytes
from email.utils import parseaddr

def extract_mail(raw_bytes):
    msg = message_from_bytes(raw_bytes)

    headers = dict(msg.items())
    try:
        _, sender_address = parseaddr(headers['From'])

    except (IndexError, AttributeError):
        print(headers['From'])
        sender_address = headers['From']
    
    subject = headers['Subject']
    
    text_body = None
    html_body = None
    attachments = []

    # Walk through MIME parts
    for part in msg.walk():
        ctype = part.get_content_type()
        disp = part.get("Content-Disposition")

        # Only accept the FIRST clean text/plain part
        if text_body is None and ctype == "text/plain" and disp is None:
            payload = part.get_payload(decode=True)
            if payload:
                text_body = payload.decode(
                    part.get_content_charset() or "utf-8",
                    errors="replace"
                )
            continue

        # HTML (optional)
        if html_body is None and ctype == "text/html" and disp is None:
            payload = part.get_payload(decode=True)
            if payload:
                html_body = payload.decode(
                    part.get_content_charset() or "utf-8",
                    errors="replace"
                )
            continue

        # Attachments
        if disp and "attachment" in disp.lower():
            filename = part.get_filename()
            data = part.get_payload(decode=True)
            attachments.append((filename, data))
  
    return {
        "text_body": text_body,
        "html_body": html_body,
        "attachments": attachments,
        "sender": sender_address,
        "subject": subject 
    }
