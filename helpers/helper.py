import re

def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts", session_str)

    if match:
        extracted_session = match.group(1)
        return extracted_session
    
    return ""

def getFoodList(foods_dict: dict):

    foods = ", ".join([f"{int(value)} plat(s) de {key}" for key, value in foods_dict.items()])
    return foods

if __name__ == "__main__":
    print(getFoodList({"samusa":2,"pap":1}))
    print(extract_session_id('projects/mila-sentibot-sl9t/agent/sessions/62f0d575-f363-e741-898e-c268649b75ca/contexts/ongoing-order'))
  