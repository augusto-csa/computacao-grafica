import numpy as np
import pygame

# Classe responsavel por pegar os dados 3D matematicos e transforma-los em pixels na tela (Pipeline Grafico)
class MotorRenderizacao:
    def __init__(self, larg, alt, tela):
        # Armazena as dimensoes da janela (largura e altura) e a superficie do Pygame onde o desenho sera feito
        self.l, self.a, self.tela = larg, alt, tela

    def desenhar_cena(self, malhas, cam):
        # Obtem a matriz de visualizacao, que muda a perspectiva do mundo para a visao da camera
        m_view = cam.matriz_visualizacao()
        # Obtem a matriz de projecao, responsavel por aplicar a distorcao de profundidade (perspectiva)
        m_proj = cam.matriz_projecao()

        # Passa por todos os objetos (malhas) que precisam ser desenhados na tela
        for malha in malhas:
            # Calcula a matriz MVP (Model-View-Projection)
            # Ela une a posicao do objeto (Model), a posicao da camera (View) e a lente da camera (Projection)
            m_mvp = m_proj @ m_view @ malha.obter_matriz_modelo()
            
            # Lista para guardar as posicoes 2D finais de cada vertice apos as contas
            pts_2d = []
            
            # Processa cada vertice (ponto 3D) do objeto atual
            for v in malha.vertices_originais:
                # Converte o vertice 3D para coordenada homogenea adicionando o w=1.0 no final
                # Em seguida, multiplica pela matriz MVP para projetar o ponto
                vh = m_mvp @ np.array([v[0], v[1], v[2], 1.0])
                
                # Divisao Perspectiva: divide os valores x, y, z pelo componente w
                # E isso que faz os objetos mais distantes parecerem menores na tela
                if vh[3] != 0: vh = vh / vh[3]
                
                # Clipping (Recorte) basico no eixo Z
                # Verifica se o vertice esta dentro da regiao visivel (entre o plano proximo e o distante)
                if -1.0 <= vh[2] <= 1.0:
                    # Viewport Transform: Converte as coordenadas normalizadas (que vao de -1 a 1)
                    # para as coordenadas reais de pixels da tela do seu monitor
                    px = int((vh[0] + 1) * self.l / 2)
                    py = int((1 - vh[1]) * self.a / 2)
                    pts_2d.append((px, py))
                else:
                    # Se o vertice estiver atras da camera ou muito longe, marca como None para descartar
                    pts_2d.append(None)

            # Depois de projetar todos os pontos, hora de ligar os pontos com as linhas (arestas)
            for ia, ib in malha.conexoes:
                p1, p2 = pts_2d[ia], pts_2d[ib]
                
                # A linha so sera desenhada se AMBOS os pontos estiverem dentro do campo de visao da tela
                if p1 and p2: 
                    # Usa a funcao do Pygame para traçar uma reta entre o Ponto 1 e o Ponto 2 com a cor do objeto
                    pygame.draw.line(self.tela, malha.cor_borda, p1, p2, 1)