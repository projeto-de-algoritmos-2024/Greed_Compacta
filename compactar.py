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

def gerar_codigos(node, codigo_atual="", codigos={}):
    if node is not None:
        if node.char is not None:
            codigos[node.char] = codigo_atual
        else:
            gerar_codigos(node.esquerda, codigo_atual + "0", codigos)
            gerar_codigos(node.direita, codigo_atual + "1", codigos)
    return codigos

def salvar_tabela_binaria(codigos, arquivo_saida):
    arquivo_saida.write(struct.pack("I", len(codigos)))  

    for char, codigo in codigos.items():
        if char == "":  
            arquivo_saida.write(struct.pack("B", 0))  
        else:
            arquivo_saida.write(struct.pack("B", ord(char)))

        arquivo_saida.write(struct.pack("B", len(codigo)))

        codigo_binario = int(codigo, 2)  

        for i in range(len(codigo)):
            bit = (codigo_binario >> (len(codigo) - i - 1)) & 1
            arquivo_saida.write(struct.pack("B", bit)) 

def compactar(arquivo_entrada):
    caracteres = {}

    with open(arquivo_entrada, "r") as arquivo:
        while True:
            caractere = arquivo.read(1)
            valor = caracteres.get(caractere, 0)
            caracteres[caractere] = valor + 1
            if not caractere:  
                break

    arvores = []
    for caractere, ocorrencias in caracteres.items():
        no = Node(ocorrencias, caractere)
        arvores.append(no)

    heapq.heapify(arvores)

    while len(arvores) > 1:
        esquerda = heapq.heappop(arvores)
        direita = heapq.heappop(arvores)

        n_arvore = Node(esquerda.valor + direita.valor, None)
        n_arvore.esquerda = esquerda
        n_arvore.direita = direita

        heapq.heappush(arvores, n_arvore)

    raiz = arvores[0]

    codigos = gerar_codigos(raiz)

    with open("arquivo_codificado", "wb") as arquivo_saida:
        salvar_tabela_binaria(codigos, arquivo_saida)

        with open(arquivo_entrada, "r") as arquivo:
            buffer = 0
            contagem_bits = 0

            while True:
                caractere = arquivo.read(1)
                if not caractere:  
                    break

                codigo = codigos.get(caractere, "")

                for bit in codigo:
                    buffer = (buffer << 1) | int(bit)
                    contagem_bits += 1

                    if contagem_bits == 8:
                        arquivo_saida.write(bytes([buffer])) 
                        buffer = 0
                        contagem_bits = 0

            if contagem_bits > 0:
                buffer = buffer << (8 - contagem_bits)
                arquivo_saida.write(bytes([buffer]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("entrada")
    args = parser.parse_args()

    compactar(args.entrada)
