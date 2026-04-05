from email import message_from_bytes

def extract_mail(bytes):
    text_body = None
    html_body = None
    attachments = []

    msg = message_from_bytes(bytes)

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = part.get("Content-Disposition")

            if content_type == "text/plain" and disposition is None:
                text_body = (part.get_payload(decode=True).decode(part.get_content_charset() 
                                                               or "utf-8", errors="replace"))
                
            elif content_type == "text/html" and disposition is None:
                html_body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")

            # Attachments
            elif disposition and "attachment" in disposition.lower():
                filename = part.get_filename()
                data = part.get_payload(decode=True)
                attachments.append((filename, data))

    else:
        # Not multipart → simple email
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            text_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")
        elif content_type == "text/html":
            html_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")

    return {'text_body' :text_body, 'html_body': html_body, 'attachments': attachments}