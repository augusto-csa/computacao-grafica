import numpy as np
import math

# Importa as funcoes de transformacao geometrica do modulo motor
from motor.transformacoes import matriz_translacao, matriz_escala, matriz_rotacao_x, matriz_rotacao_y, matriz_rotacao_z

# Classe que representa um objeto 3D na cena
class Malha3D:
    def __init__(self, verts, arestas, cor, nome):
        # Armazena os vertices originais do objeto como um array numpy
        self.vertices_originais = np.array(verts)
        # Lista de tuplas indicando quais vertices se conectam (arestas)
        self.conexoes = arestas
        # Cor das linhas do objeto no formato RGB
        self.cor_borda = cor
        # Nome identificador do objeto (ex: "Cubo", "Piramide")
        self.nome = nome
        
        # Vetores para armazenar as transformacoes individuais
        self.pos = np.array([0.0, 0.0, 0.0]) # Posicao atual nos eixos X, Y e Z
        self.rot = np.array([0.0, 0.0, 0.0]) # Rotacao atual (em radianos) nos eixos X, Y e Z
        self.escala = np.array([1.0, 1.0, 1.0]) # Fator de escala nos eixos X, Y e Z
        
        # Flags para permitir o controle via matrizes complexas (como quaternios)
        self.usar_matriz_forcada = False
        self.matriz_forcada = np.identity(4)

    def obter_matriz_modelo(self):
        # Se a flag estiver ativa, retorna a matriz customizada (usada na animacao)
        if self.usar_matriz_forcada: return self.matriz_forcada
        
        # Calcula e retorna a matriz modelo combinando Translacao * Rotacao * Escala
        return matriz_translacao(*self.pos) @ matriz_rotacao_z(self.rot[2]) @ matriz_rotacao_y(self.rot[1]) @ matriz_rotacao_x(self.rot[0]) @ matriz_escala(*self.escala)

# Funcao para gerar os vertices e arestas de um cubo
def gerar_cubo():
    # Retorna uma tupla contendo a lista de pontos 3D e a lista de ligacoes (linhas)
    return [[-1,-1,-1],[1,-1,-1],[1,-1,1],[-1,-1,1],[-1,1,-1],[1,1,-1],[1,1,1],[-1,1,1]], [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]

# Funcao para gerar os vertices e arestas de uma piramide
def gerar_piramide():
    # Retorna os vertices da base e do topo, junto com suas conexoes
    return [[-0.8,0,-0.8],[0.8,0,-0.8],[0.8,0,0.8],[-0.8,0,0.8],[0,1.5,0]], [(0,1),(1,2),(2,3),(3,0),(0,4),(1,4),(2,4),(3,4)]

# Funcao para gerar os vertices e arestas de uma esfera procedural
def gerar_esfera():
    verts, arestas = [], []
    
    # Loop para os meridianos (latitude)
    for i in range(11):
        lat = math.pi * i / 10 # Calcula o angulo da latitude
        
        # Loop para os paralelos (longitude)
        for j in range(10):
            lon = 2 * math.pi * j / 10 # Calcula o angulo da longitude
            
            # Calcula as coordenadas X, Y, Z usando equacoes esfericas e adiciona na lista
            verts.append([1.0 * math.sin(lat) * math.cos(lon), 1.0 * math.cos(lat), 1.0 * math.sin(lat) * math.sin(lon)])
            
            # Se nao estiver na ultima volta, cria as conexoes de arestas da malha
            if i < 10:
                at = i * 10 + j # Indice do vertice atual
                pr = at + 1 if j < 9 else i * 10 # Indice do proximo vertice na horizontal
                ab = at + 10 # Indice do vertice diretamente abaixo
                
                # Adiciona as linhas horizontais e verticais
                arestas.extend([(at, pr), (at, ab)])
                
    return verts, arestas