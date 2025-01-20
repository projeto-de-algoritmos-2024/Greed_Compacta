from flask import Flask, request, send_file
import os
import argparse
import heapq
import struct
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
                codigo_atual = ""  # Reseta o código atual quando encontra um caractere

        with open(arquivo_saida, "w") as arquivo_saida:
            arquivo_saida.write(texto_descompactado)


@app.route('/compactar', methods=['POST'])
def compactar_arquivo():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400

    arquivo = request.files['file']

    arquivo_path = "arquivo_temporario"
    arquivo.save(arquivo_path)
    arquivo_codificado = '/tmp/arquivo_codificado'

    compactar(arquivo_path)

    return send_file(arquivo_codificado, as_attachment=True, download_name="arquivo_compactado")

@app.route('/descompactar', methods=['POST'])
def descompactar_arquivo():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400

    arquivo = request.files['file']

    arquivo_path = "arquivo_restaurado"
    arquivo.save(arquivo_path)
    arquivo_restaurado = '/tmp/arquivo_restaurado'

    descompactar(arquivo_path, arquivo_restaurado)

    return send_file(arquivo_restaurado, as_attachment=True, download_name="arquivo_restaurado.txt")

if __name__ == '__main__':
    app.run(debug=True, port=3000)
