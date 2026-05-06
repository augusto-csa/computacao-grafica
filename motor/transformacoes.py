import numpy as np

# =====================================================================
# MATRIZES DE TRANSFORMACAO HOMOGENEAS
# As matrizes 4x4 sao o padrao na computacao grafica para permitir 
# que translacao, rotacao e escala sejam combinadas por multiplicacao.
# =====================================================================

# Funcao que gera uma matriz de translacao (movimentar o objeto no espaco)
def matriz_translacao(dx, dy, dz):
    # Cria uma matriz identidade 4x4 (diagonal principal com 1, o resto com 0)
    matriz = np.identity(4)
    # Preenche a ultima coluna com os valores de deslocamento (X, Y, Z)
    matriz[0, 3] = dx; matriz[1, 3] = dy; matriz[2, 3] = dz
    return matriz

# Funcao que gera uma matriz de escala (aumentar ou diminuir o tamanho)
def matriz_escala(ex, ey, ez):
    # Cria uma matriz identidade 4x4
    matriz = np.identity(4)
    # Substitui os 3 primeiros valores da diagonal principal pelos multiplicadores de escala
    matriz[0, 0] = ex; matriz[1, 1] = ey; matriz[2, 2] = ez
    return matriz

# Funcao que gera uma matriz de rotacao ao redor do eixo X
def matriz_rotacao_x(radianos):
    # Calcula o cosseno e o seno do angulo desejado (fornecido em radianos)
    c, s = np.cos(radianos), np.sin(radianos)
    # Constroi e retorna a matriz matematica exata para girar um vertice em torno do eixo X
    return np.array([
        [1, 0,  0, 0], 
        [0, c, -s, 0], 
        [0, s,  c, 0], 
        [0, 0,  0, 1]
    ])

# Funcao que gera uma matriz de rotacao ao redor do eixo Y
def matriz_rotacao_y(radianos):
    c, s = np.cos(radianos), np.sin(radianos)
    # Constroi e retorna a matriz para girar um vertice em torno do eixo Y
    return np.array([
        [ c, 0, s, 0], 
        [ 0, 1, 0, 0], 
        [-s, 0, c, 0], 
        [ 0, 0, 0, 1]
    ])

# Funcao que gera uma matriz de rotacao ao redor do eixo Z
def matriz_rotacao_z(radianos):
    c, s = np.cos(radianos), np.sin(radianos)
    # Constroi e retorna a matriz para girar um vertice em torno do eixo Z (como um relogio)
    return np.array([
        [c, -s, 0, 0], 
        [s,  c, 0, 0], 
        [0,  0, 1, 0], 
        [0,  0, 0, 1]
    ])