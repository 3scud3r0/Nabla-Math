"""Cifras clássicas apenas pedagógicas; não fornecem segurança moderna."""
import string
ALPHABET=string.ascii_uppercase

def caesar(text:str,shift:int)->str:
    shift%=26;result=[]
    for char in text:
        upper=char.upper()
        if upper in ALPHABET:
            transformed=ALPHABET[(ALPHABET.index(upper)+shift)%26]
            result.append(transformed if char.isupper() else transformed.lower())
        else:result.append(char)
    return "".join(result)

def vigenere(text:str,key:str,decrypt:bool=False)->str:
    shifts=[ALPHABET.index(char) for char in key.upper() if char in ALPHABET]
    if not shifts:raise ValueError("chave precisa conter letras ASCII")
    result=[];index=0
    for char in text:
        upper=char.upper()
        if upper in ALPHABET:
            shift=shifts[index%len(shifts)]*(-1 if decrypt else 1)
            transformed=ALPHABET[(ALPHABET.index(upper)+shift)%26]
            result.append(transformed if char.isupper() else transformed.lower());index+=1
        else:result.append(char)
    return "".join(result)

def frequency(text:str)->dict[str,int]:
    return {char:text.upper().count(char) for char in ALPHABET if char in text.upper()}

__all__=["caesar","frequency","vigenere"]
