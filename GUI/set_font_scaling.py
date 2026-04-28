import re
import GUI.styles as styles
import config

scaling = None

pattern = r'font-size:\s*(\d+)\s*px;'

def repl(match):
    original = int(match.group(1))
    new_value = int(original * scaling)
    return f"font-size: {new_value}px;"

def set_scaling():
    global scaling
    scaling = float(config.OPTIONS['font_scaling'])
    for k, v in styles.styles.items():

        styles.styles[k] = re.sub(pattern, repl, styles.styles[k], flags=re.DOTALL)
