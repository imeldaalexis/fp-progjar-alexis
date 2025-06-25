def encode_message(msg_type, sender, msg):
    return f"{msg_type}|{sender}|{msg}#"

def decode_message(raw):
    raw = raw.strip('#')
    parts = raw.split('|')
    if len(parts) != 3:
        return ("", "", "")
    return tuple(parts)