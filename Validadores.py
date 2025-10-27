import re

def limpar_numero(valor: str) -> str:
    """Remove tudo que não for dígito"""
    return re.sub(r'\D', '', valor or "")

def validar_email(email: str) -> bool:
    """Valida formato de email simples"""
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email or "") is not None

def validar_cpf(cpf: str) -> bool:
    """Valida CPF com 11 dígitos numéricos"""
    cpf_limpo = limpar_numero(cpf)
    return re.match(r'^\d{11}$', cpf_limpo) is not None

def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ com 14 dígitos numéricos"""
    cnpj_limpo = limpar_numero(cnpj)
    return re.match(r'^\d{14}$', cnpj_limpo) is not None

def validar_cep(cep: str) -> bool:
    """Valida CEP com 8 dígitos"""
    cep_limpo = limpar_numero(cep)
    return re.match(r'^\d{8}$', cep_limpo) is not None

def validar_contato(contato: str) -> bool:
    """Valida telefone/whatsapp com 10 ou 11 dígitos"""
    contato_limpo = limpar_numero(contato)
    return re.match(r'^\d{10,11}$', contato_limpo) is not None
