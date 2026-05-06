import numpy as np
import math

# Importa a funcao para criar a matriz de translacao do modulo motor
from motor.transformacoes import matriz_translacao

# Classe que controla a camera e como ela visualiza o cenario 3D
class CameraVisao:
    def __init__(self, pos, alvo, cima, fov, aspecto, d_min, d_max):
        # Vetor que representa a posicao exata da camera no mundo 3D
        self.posicao = np.array(pos, dtype=float)
        # Vetor que define para qual ponto a camera esta olhando
        self.direcao_alvo = np.array(alvo, dtype=float)
        # Vetor que indica qual direcao representa "para cima" na camera
        self.vetor_cima = np.array(cima, dtype=float)
        
        # Atributos para projecao: campo de visao (fov), proporcao da tela (aspecto) e limites de profundidade (d_min, d_max)
        self.fov, self.aspecto, self.p_prox, self.p_dist = fov, aspecto, d_min, d_max
        
        # Angulos iniciais de controle da orbita (mouse)
        self.ang_x, self.ang_y = 0.0, 0.0
        # Calcula a distancia inicial entre a camera e o alvo para servir como raio da orbita
        self.raio = np.linalg.norm(self.posicao - self.direcao_alvo)

    def orbitar(self, dx, dy):
        # Atualiza os angulos X e Y com base no movimento relativo do mouse (dx, dy) e uma sensibilidade de 0.01
        self.ang_x -= dx * 0.01
        self.ang_y += dy * 0.01
        
        # Limita a rotacao vertical para que a camera nao vire de cabeca para baixo
        self.ang_y = max(-math.pi/2.1, min(math.pi/2.1, self.ang_y))
        
        # Calcula as novas coordenadas da camera em um formato esferico (ao redor do alvo)
        cx = self.direcao_alvo[0] + self.raio * math.cos(self.ang_y) * math.sin(self.ang_x)
        cy = self.direcao_alvo[1] + self.raio * math.sin(self.ang_y)
        cz = self.direcao_alvo[2] + self.raio * math.cos(self.ang_y) * math.cos(self.ang_x)
        
        # Atualiza a posicao da camera com os novos valores calculados
        self.posicao = np.array([cx, cy, cz])

    def mover(self, frente, lado):
        # Calcula o vetor de distancia entre a camera e o alvo
        vz = self.posicao - self.direcao_alvo
        # Direcao "frente": normaliza o vetor Z invertido
        f_dir = -(vz / np.linalg.norm(vz))
        # Direcao "lado": produto vetorial entre a direcao frente e o vetor cima da camera
        l_dir = np.cross(f_dir, self.vetor_cima)
        
        # Combina o movimento para frente/tras e lateral em um unico vetor
        mov = (f_dir * frente) + (l_dir * lado)
        
        # Move tanto a camera quanto o alvo na mesma proporcao, simulando uma caminhada livre
        self.posicao += mov; self.direcao_alvo += mov

    def matriz_visualizacao(self):
        # Constroi o Sistema de Coordenadas da Camera (View Matrix)
        
        # Encontra o eixo Z da camera (apontando para o alvo) e o normaliza
        vz = self.posicao - self.direcao_alvo
        zn = vz / np.linalg.norm(vz)
        
        # Encontra o eixo X da camera fazendo produto vetorial entre o vetor Cima e Z
        vx = np.cross(self.vetor_cima, zn)
        xn = vx / np.linalg.norm(vx)
        
        # Encontra o eixo Y ortogonal fazendo o produto vetorial entre Z e X
        yn = np.cross(zn, xn)
        
        # Cria a matriz de rotacao com os eixos X, Y e Z calculados
        m_rot = np.array([[xn[0], xn[1], xn[2], 0], [yn[0], yn[1], yn[2], 0], [zn[0], zn[1], zn[2], 0], [0, 0, 0, 1]])
        # Cria a matriz de translacao com o inverso da posicao atual da camera
        m_trans = matriz_translacao(-self.posicao[0], -self.posicao[1], -self.posicao[2])
        
        # Retorna a Matriz View multiplicando a rotacao pela translacao
        return m_rot @ m_trans

    def matriz_projecao(self):
        # Calcula a Matriz de Projecao Perspectiva
        
        # Calcula o fator de escala (f) da perspectiva com base na metade do angulo do FOV
        f = 1.0 / math.tan(math.radians(self.fov) / 2.0)
        # Calcula o alcance da profundidade de visao
        prof = self.p_prox - self.p_dist
        
        # Retorna a matriz homogenea 4x4 que encolhe pontos distantes (perspectiva frustum)
        return np.array([[f / self.aspecto, 0, 0, 0], [0, f, 0, 0], [0, 0, (self.p_prox + self.p_dist) / prof, (2 * self.p_prox * self.p_dist) / prof], [0, 0, -1, 0]])