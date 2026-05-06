import pygame
import math
import sys

# Importacoes dos modulos separados do nosso motor 3D
from motor.transformacoes import matriz_translacao, matriz_rotacao_x, matriz_rotacao_y
from motor.quaternio import QuaternioCalc
from motor.camera import CameraVisao
from motor.renderizador import MotorRenderizacao
from modelos.objeto_3d import Malha3D, gerar_cubo, gerar_piramide, gerar_esfera

# Importacoes da interface de usuario (botoes, caixas de texto e paleta de cores)
from interface import Botao, CaixaTexto, desenhar_secao, COR_PAINEL, COR_SEPARADOR, COR_TEXTO_LABEL, COR_TEXTO_VALOR

# Funcao principal que inicializa o jogo e contem o loop principal
def iniciar_aplicacao():
    # Inicializa todos os modulos do Pygame
    pygame.init()
    
    # Cria a janela principal com 1100 pixels de largura (800 pro 3D + 300 pro menu) e 600 de altura
    tela = pygame.display.set_mode((1100, 600))
    pygame.display.set_caption("Motor 3D - Modularizado")
    
    # Cria o relogio para controlar os quadros por segundo (FPS) e inicializa as fontes
    relogio = pygame.time.Clock()
    fonte        = pygame.font.SysFont("Segoe UI", 18)
    fonte_titulo = pygame.font.SysFont("Segoe UI", 20, bold=True)
    fonte_hud    = pygame.font.SysFont("Segoe UI", 22, bold=True)

    # Instancia a camera na posicao Z=12, olhando para a origem (0,0,0)
    cam   = CameraVisao([0, 3, 12], [0, 0, 0], [0, 1, 0], 60, 800/600, 0.1, 100.0)
    # Instancia o motor de renderizacao para desenhar na area de 800x600 da tela
    motor = MotorRenderizacao(800, 600, tela)

    # Variaveis para a cena de animacao do PDF
    t_rot, o_pira = 0.0, 0.0
    q_ini = QuaternioCalc.criar_de_eixo_angulo([0, 1, 0], 0)
    # Cria as malhas que serao usadas apenas na animacao
    obj_cubo_anim = Malha3D(*gerar_cubo(),     (0, 200, 255),   "Cubo")
    obj_pira_anim = Malha3D(*gerar_piramide(), (255, 150, 0),   "Piramide")

    # Variaveis de estado para o Modo Editor
    objetos      = [] # Lista que vai guardar os objetos criados pelo usuario
    idx_sel      = -1 # Indice do objeto atualmente selecionado (-1 significa nenhum)
    cena_animada = True # Comeca na cena da animacao do professor

    # Posicao X inicial do painel lateral
    PAINEL_X = 808

    # Lista de botoes da interface
    botoes = [
        Botao(PAINEL_X,       48, 82, 34, "+ Cubo",   (137, 180, 250), "add_cubo"),
        Botao(PAINEL_X + 88,  48, 82, 34, "+ Piram",  (249, 226, 175), "add_pira"),
        Botao(PAINEL_X + 176, 48, 84, 34, "+ Esfera", (166, 227, 161), "add_esfe"),
        Botao(PAINEL_X,       168, 40, 28, "<",       (88, 91, 112),   "prev"),
        Botao(PAINEL_X + 46,  168, 40, 28, ">",       (88, 91, 112),   "next"),
        Botao(PAINEL_X + 100, 168, 172, 28, "Excluir", (243, 139, 168), "del"),
    ]

    # Posicoes Y e X para alinhar as caixas de texto perfeitamente como uma tabela
    INPUT_Y = [285, 355, 425]
    INPUT_X = [PAINEL_X + 44, PAINEL_X + 124, PAINEL_X + 204]

    # Lista com as 9 caixas de texto (3 eixos para Posicao, Rotacao e Escala)
    inputs = [
        CaixaTexto(INPUT_X[0], INPUT_Y[0], 68, 28, 'pos',    0),
        CaixaTexto(INPUT_X[1], INPUT_Y[0], 68, 28, 'pos',    1),
        CaixaTexto(INPUT_X[2], INPUT_Y[0], 68, 28, 'pos',    2),
        CaixaTexto(INPUT_X[0], INPUT_Y[1], 68, 28, 'rot',    0),
        CaixaTexto(INPUT_X[1], INPUT_Y[1], 68, 28, 'rot',    1),
        CaixaTexto(INPUT_X[2], INPUT_Y[1], 68, 28, 'rot',    2),
        CaixaTexto(INPUT_X[0], INPUT_Y[2], 68, 28, 'escala', 0),
        CaixaTexto(INPUT_X[1], INPUT_Y[2], 68, 28, 'escala', 1),
        CaixaTexto(INPUT_X[2], INPUT_Y[2], 68, 28, 'escala', 2),
    ]

    # Flags de controle do loop e do mouse
    rodando, mouse_press = True, False

    # Inicia o loop principal que mantem a janela aberta
    while rodando:
        # Controla o tempo e pega os segundos passados desde o ultimo frame
        dt = relogio.tick(60) / 1000.0
        
        # Atalho para pegar o objeto atualmente selecionado, se existir
        obj_atual = objetos[idx_sel] if objetos and idx_sel != -1 else None

        # Processa todos os eventos (teclado, mouse, fechar janela)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            
            # Se apertou ESPACO e nao esta digitando em nenhuma caixa, troca de cena
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE and not any(i.ativo for i in inputs):
                cena_animada = not cena_animada

            # Repassa os eventos para as caixas de texto
            if not cena_animada and obj_atual:
                for inp in inputs: inp.processar_evento(evento, obj_atual, fonte)

            # Eventos de clique do mouse
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Clique do botao esquerdo
                    mouse_press = True
                    
                    # Se clicou na area do menu (X > 800)
                    if not cena_animada and evento.pos[0] > 800:
                        for btn in botoes:
                            if btn.rect.collidepoint(evento.pos):
                                # Lida com os cliques nos botoes de adicionar objetos
                                if btn.acao == "add_cubo":
                                    objetos.append(Malha3D(*gerar_cubo(),     (0, 200, 255),   "Cubo"));    idx_sel = len(objetos)-1
                                elif btn.acao == "add_pira":
                                    objetos.append(Malha3D(*gerar_piramide(), (249, 226, 175), "Piramide")); idx_sel = len(objetos)-1
                                elif btn.acao == "add_esfe":
                                    objetos.append(Malha3D(*gerar_esfera(),   (166, 227, 161), "Esfera")); idx_sel = len(objetos)-1
                                
                                # Lida com os botoes de navegacao e exclusao
                                elif objetos:
                                    if btn.acao == "prev": idx_sel = (idx_sel - 1) % len(objetos)
                                    elif btn.acao == "next": idx_sel = (idx_sel + 1) % len(objetos)
                                    elif btn.acao == "del":
                                        objetos.pop(idx_sel)
                                        idx_sel = len(objetos)-1 if objetos else -1
                                        
                # Roda o scroll do mouse para aplicar Zoom (FOV)
                elif evento.button == 4: cam.fov = max(10, cam.fov - 5)
                elif evento.button == 5: cam.fov = min(120, cam.fov + 5)
                
            # Soltou o clique do mouse
            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                mouse_press = False
                
            # Movel o mouse segurando o clique na area 3D -> Orbita a camera
            elif evento.type == pygame.MOUSEMOTION and mouse_press and evento.pos[0] < 800:
                cam.orbitar(evento.rel[0], evento.rel[1])

        # Controle de movimento da camera pelas teclas WASD
        # So funciona se nao houver nenhuma caixa de texto ativa sendo digitada
        if not any(i.ativo for i in inputs):
            teclas, v_cam = pygame.key.get_pressed(), 6.0 * dt
            if teclas[pygame.K_w]: cam.mover( v_cam, 0)
            if teclas[pygame.K_s]: cam.mover(-v_cam, 0)
            if teclas[pygame.K_a]: cam.mover(0, -v_cam)
            if teclas[pygame.K_d]: cam.mover(0,  v_cam)

        # Limpa a tela com uma cor cinza escuro
        tela.fill((30, 30, 46))

        if cena_animada:
            # ===============================================
            # CENA DE ANIMACAO DO PDF (CUBO E PIRAMIDE)
            # ===============================================
            t_rot += 1.2 * dt
            if t_rot > math.pi * 2: t_rot -= math.pi * 2

            # Interpolacao Esferica (SLERP) no Cubo
            q_alvo = QuaternioCalc.criar_de_eixo_angulo([1, 0.5, 0], t_rot)
            obj_cubo_anim.usar_matriz_forcada = True
            obj_cubo_anim.matriz_forcada = QuaternioCalc.interpolacao_esferica(q_ini, q_alvo, 1.0).para_matriz4x4()

            # Orbita na Piramide
            o_pira += 2.5 * dt
            obj_pira_anim.usar_matriz_forcada = True
            obj_pira_anim.matriz_forcada = matriz_rotacao_y(o_pira) @ matriz_translacao(3.5, 0, 0) @ matriz_rotacao_x(o_pira * 1.5)

            # Desenha tudo
            motor.desenhar_cena([obj_cubo_anim, obj_pira_anim], cam)
            tela.blit(fonte_hud.render("ANIMACAO  [ESPACO = Editor]", True, (255, 255, 255)), (16, 16))

            # Esconde o menu durante a animacao
            pygame.draw.rect(tela, COR_PAINEL, (800, 0, 300, 600))
            pygame.draw.line(tela, COR_SEPARADOR, (800, 0), (800, 600), 2)
            msg = fonte_titulo.render("Modo Editor Desativado", True, COR_TEXTO_LABEL)
            tela.blit(msg, (800 + (300 - msg.get_width())//2, 290))

        else:
            # ===============================================
            # MODO EDITOR (TRANSFORMACOES MANUAIS)
            # ===============================================
            motor.desenhar_cena(objetos, cam)
            tela.blit(fonte_hud.render("MODO EDITOR  [ESPACO = Animacao]", True, (255, 255, 255)), (16, 16))

            # Desenha o fundo e a borda do menu lateral
            pygame.draw.rect(tela, COR_PAINEL, (800, 0, 300, 600))
            pygame.draw.line(tela, COR_SEPARADOR, (800, 0), (800, 600), 2)

            # Secao 1: Criar
            desenhar_secao(tela, fonte_titulo, "Criar Objeto", 18)
            for btn in botoes[:3]: btn.desenhar(tela, fonte)

            # Secao 2: Selecionar e Excluir
            desenhar_secao(tela, fonte_titulo, "Selecionar Objeto", 100)
            if obj_atual:
                nome_txt = f"{obj_atual.nome}  ({idx_sel+1} / {len(objetos)})"
                surf_nome = fonte.render(nome_txt, True, COR_TEXTO_VALOR)
                tela.blit(surf_nome, (PAINEL_X, 136))
                for btn in botoes[3:]: btn.desenhar(tela, fonte)
            else:
                tela.blit(fonte.render("Nenhum objeto na cena", True, COR_TEXTO_LABEL), (PAINEL_X, 136))
                for btn in botoes[3:]: btn.desenhar(tela, fonte)

            # Secao 3: Transformacoes
            desenhar_secao(tela, fonte_titulo, "Transformacoes", 210)
            tela.blit(fonte.render("(Aperte ENTER para aplicar)", True, COR_TEXTO_LABEL), (PAINEL_X, 240))

            # Se tem um objeto ativo, desenha os campos de texto
            if obj_atual:
                # Desenha as letras X, Y, Z no topo
                for ci, label in enumerate(["X", "Y", "Z"]):
                    tela.blit(fonte.render(label, True, COR_TEXTO_LABEL), (INPUT_X[ci] + 26, 265))

                # Desenha as etiquetas Pos, Rot e Esc ao lado das linhas
                for ri, label in enumerate(["Pos", "Rot", "Esc"]):
                    tela.blit(fonte.render(label, True, COR_TEXTO_LABEL), (PAINEL_X, INPUT_Y[ri] + 5))

                # Processa o visual das 9 caixas
                for inp in inputs: inp.desenhar(tela, fonte, obj_atual)
            else:
                # Avisa o usuario caso a tela esteja vazia
                tela.blit(fonte.render("Adicione um objeto para editar", True, COR_TEXTO_LABEL), (PAINEL_X, 280))

            # Dica de atalhos no rodape
            dica = fonte.render("WASD = camera   Scroll = zoom", True, COR_TEXTO_LABEL)
            tela.blit(dica, (800 + (300 - dica.get_width())//2, 572))

        # Manda o Pygame atualizar o frame na tela
        pygame.display.flip()

# Executa o programa se o script for rodado diretamente
if __name__ == "__main__":
    iniciar_aplicacao()