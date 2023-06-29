import re
import base64

def remove_colors(string):

    color_pattern =  re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    color_pattern2 = re.compile(r'\x1b[^m]*m')

    result = color_pattern.sub('', string)
    result = color_pattern2.sub('', result)

    return result

def get_query(string):
    pattern = re.compile('[\s\S]*Action Input: (\\"[\s\S]*\\")')
    match = pattern.search(string)
    if match:
        result = match.group(1)
    else:
        result = None

    return result

def process_string(string):
    lines = string.split('\n')
    processed_lines = []
    for line in lines:
        line = line.strip()
        if line:
            processed_lines.append(line.replace('\t', '    '))
    return '\n'.join(processed_lines)


def save_file(encoded_string):
    filePath = "service-account-key.json"

    json = _decode_base64(encoded_string)
    file = open(filePath, "w")
    file.write(json)
    file.close()

    return filePath
    
def _decode_base64(encoded_string):
    try:
        decoded_bytes = base64.b64decode(encoded_string)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except base64.binascii.Error:
        file = open(encoded_string, "r")
        return file.read()