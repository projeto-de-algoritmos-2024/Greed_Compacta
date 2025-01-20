import os
import argparse
import heapq
import struct

class Node:
    def __init__(self, valor, char):
        self.valor = valor  
        self.char = char  
        self.esquerda = None  
        self.direita = None

    def __lt__(self, other):
        return self.valor < other.valor

def ler_tabela_binaria(arquivo_entrada):
    num_caracteres = struct.unpack("I", arquivo_entrada.read(4))[0]
    
    codigos = {}
    
    for _ in range(num_caracteres):
        char = struct.unpack("B", arquivo_entrada.read(1))[0]
        char = chr(char)

        comprimento_codigo = struct.unpack("B", arquivo_entrada.read(1))[0]
        
        codigo = 0
        for _ in range(comprimento_codigo):
            bit = struct.unpack("B", arquivo_entrada.read(1))[0]
            codigo = (codigo << 1) | bit
        
        codigo_binario = format(codigo, '0' + str(comprimento_codigo) + 'b')
        
        codigos[char] = codigo_binario

    return codigos

def descompactar(arquivo_entrada, arquivo_saida):
    with open(arquivo_entrada, "rb") as arquivo_entrada:
        codigos = ler_tabela_binaria(arquivo_entrada)
        
        tabela_reversa = {v: k for k, v in codigos.items()}

        dados = arquivo_entrada.read()
        
        bits = ''.join(f"{byte:08b}" for byte in dados)
        
        codigo_atual = ""
        texto_descompactado = ""
        for bit in bits:
            codigo_atual += bit
            if codigo_atual in tabela_reversa:
                texto_descompactado += tabela_reversa[codigo_atual]
                codigo_atual = ""  

        with open(arquivo_saida, "w") as arquivo_saida:
            arquivo_saida.write(texto_descompactado)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("entrada", help="Arquivo de entrada (compactado)")
    parser.add_argument("saida", help="Arquivo de saída (descompactado)")
    args = parser.parse_args()

    descompactar(args.entrada, args.saida)
