class Node:
    def __init__(self, valor, char):
        self.valor = valor  
        self.char = char  
        self.esquerda = None  
        self.direita = None

    def __lt__(self, other):
        return self.valor < other.valor