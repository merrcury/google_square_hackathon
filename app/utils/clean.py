def cleaned(s: str) -> str:
    #JSON PARESED STRING TO JSON STRING
    return (s.strip().lower().replace("/", " ").replace("\\", " ").replace("\n", " ").replace("\t"," ", ).replace("\r", "").replace('"', "'").replace("```", "").replace("json",""))