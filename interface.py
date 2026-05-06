import pygame
import math

# =====================================================================
# CLASSE BOTAO
# =====================================================================
# Classe que representa um botao clicavel simples na interface
class Botao:
    def __init__(self, x, y, w, h, texto, cor, acao):
        # Cria um retangulo invisivel para tratar colisoes (cliques)
        self.rect = pygame.Rect(x, y, w, h)
        # Guarda o texto exibido, a cor de fundo e a string de acao (ID do botao)
        self.texto, self.cor, self.acao = texto, cor, acao

    def desenhar(self, tela, fonte):
        # Desenha o fundo do botao com bordas arredondadas (border_radius=6)
        pygame.draw.rect(tela, self.cor, self.rect, border_radius=6)
        
        # Renderiza o texto na cor branca
        surf = fonte.render(self.texto, True, (255, 255, 255))
        
        # Desenha o texto perfeitamente centralizado dentro do retangulo do botao
        tela.blit(surf, (self.rect.x + (self.rect.w - surf.get_width())//2,
                         self.rect.y + (self.rect.h - surf.get_height())//2))

# =====================================================================
# CLASSE CAIXA DE TEXTO (INPUT)
# =====================================================================
# Classe avancada para permitir digitacao e selecao de texto com o mouse
class CaixaTexto:
    PADDING = 5 # Espacamento interno (margem) entre o texto e a borda da caixa

    def __init__(self, x, y, w, h, prop, eixo):
        self.rect = pygame.Rect(x, y, w, h)
        
        # Define qual propriedade do objeto 3D essa caixa vai alterar ('pos', 'rot' ou 'escala')
        self.prop = prop
        # Define qual eixo sera alterado: 0 (X), 1 (Y) ou 2 (Z)
        self.eixo = eixo
        
        # Estados da caixa de texto
        self.ativo = False # Se True, a caixa esta focada e recebendo digitacao
        self.texto = ""
        self.cursor = 0 # Posicao atual do cursor (tracinho piscante) na string
        
        # Variaveis para controle de selecao de texto (como quando voce arrasta o mouse sobre uma palavra)
        self.sel_ini = 0
        self.sel_fim = 0
        self._arrastando = False # Indica se o usuario esta segurando e arrastando o clique

    # Metodo interno para verificar se existe algum texto selecionado
    def _tem_selecao(self):
        return self.sel_ini != self.sel_fim

    # Garante que o indice inicial da selecao seja sempre menor que o final
    def _sel_ordenada(self):
        return min(self.sel_ini, self.sel_fim), max(self.sel_ini, self.sel_fim)

    # Apaga apenas a parte do texto que o usuario selecionou
    def _deletar_selecao(self):
        a, b = self._sel_ordenada()
        self.texto = self.texto[:a] + self.texto[b:]
        self.cursor = self.sel_ini = self.sel_fim = a

    # Seleciona todo o conteudo digitado na caixa (Ctrl+A)
    def _selecionar_tudo(self):
        self.sel_ini = 0
        self.sel_fim = self.cursor = len(self.texto)

    # Converte a posicao X do mouse para o indice correto do texto
    # (Descobre entre quais letras o usuario clicou)
    def _mx_para_idx(self, fonte, mx):
        x_rel = mx - self.rect.x - self.PADDING
        for i in range(len(self.texto) + 1):
            if fonte.size(self.texto[:i])[0] >= x_rel:
                return i
        return len(self.texto)

    # Pega o texto digitado, converte para numero e aplica no objeto 3D selecionado
    def _aplicar(self, obj):
        try:
            val = float(self.texto)
            # Se a propriedade for rotacao, o usuario digita em graus, mas a matriz exige radianos
            if self.prop == 'rot': val = math.radians(val)
            # Usa getattr para acessar a propriedade correta (pos, rot, escala) dinamicamente
            getattr(obj, self.prop)[self.eixo] = val
        except ValueError:
            # Se o texto for invalido (ex: vazio ou com letras), ignora e nao faz nada
            pass

    def desenhar(self, tela, fonte, obj_selecionado):
        # Se a caixa nao estiver selecionada, ela deve mostrar o valor atual do objeto 3D
        if not self.ativo and obj_selecionado:
            val = getattr(obj_selecionado, self.prop)[self.eixo]
            # Se for rotacao, converte de radianos de volta para graus para ficar facil de ler
            if self.prop == 'rot': val = math.degrees(val)
            self.texto = f"{val:.2f}"

        # Define a cor da borda: Azul claro se ativo, Cinza escuro se inativo
        cor_borda = (137, 180, 250) if self.ativo else (88, 91, 112)
        
        # Desenha o fundo escuro da caixa
        pygame.draw.rect(tela, (30, 30, 46), self.rect, border_radius=4)
        # Desenha a borda (width=2 deixa oca por dentro)
        pygame.draw.rect(tela, cor_borda, self.rect, width=2, border_radius=4)

        PAD, TY = self.PADDING, self.rect.y + 6

        # Se houver texto selecionado, desenha um retangulo azul translucido por tras da selecao
        if self.ativo and self._tem_selecao():
            a, b = self._sel_ordenada()
            xa = PAD + fonte.size(self.texto[:a])[0]
            xb = PAD + fonte.size(self.texto[:b])[0]
            sel_surf = pygame.Surface((xb - xa, self.rect.h - 6), pygame.SRCALPHA)
            sel_surf.fill((137, 180, 250, 80)) # Azul com 80 de opacidade (Alpha)
            tela.blit(sel_surf, (self.rect.x + xa, self.rect.y + 3))

        # Renderiza e desenha o texto principal
        tela.blit(fonte.render(self.texto, True, (205, 214, 244)), (self.rect.x + PAD, TY))

        # Desenha o cursor (tracinho piscante) apenas se a caixa estiver ativa e nao houver selecao
        if self.ativo and not self._tem_selecao():
            # Usa o tempo do Pygame para fazer o cursor piscar a cada 500 milissegundos
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                cx = self.rect.x + PAD + fonte.size(self.texto[:self.cursor])[0]
                pygame.draw.line(tela, (205, 214, 244), (cx, self.rect.y + 4), (cx, self.rect.y + self.rect.h - 4), 1)

    def processar_evento(self, evento, obj_selecionado, fonte):
        # Trata o clique do mouse (Botao esquerdo = 1)
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if not self.ativo:
                    # Ao clicar pela primeira vez, ativa e seleciona todo o texto
                    self.ativo = True
                    self.texto = self.texto
                    self._selecionar_tudo()
                else:
                    # Se ja estava ativo, posiciona o cursor exatamente onde clicou
                    idx = self._mx_para_idx(fonte, evento.pos[0])
                    self.cursor = self.sel_ini = self.sel_fim = idx
                self._arrastando = True
            else:
                # Se clicou fora da caixa, aplica o valor no objeto 3D e desativa a edicao
                if self.ativo:
                    self._aplicar(obj_selecionado)
                    self.ativo = False
                self._arrastando = False

        # Se soltou o botao do mouse, para de arrastar a selecao
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self._arrastando = False

        # Se estiver movendo o mouse segurando o clique, expande a selecao do texto
        elif evento.type == pygame.MOUSEMOTION and self._arrastando and self.ativo:
            idx = self._mx_para_idx(fonte, evento.pos[0])
            self.sel_fim = self.cursor = idx

        # Trata as teclas pressionadas no teclado
        elif evento.type == pygame.KEYDOWN and self.ativo:
            mods = pygame.key.get_mods()

            # Tecla ENTER: aplica a transformacao e tira o foco
            if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._aplicar(obj_selecionado)
                self.ativo = False
                
            # Tecla ESC: cancela a edicao
            elif evento.key == pygame.K_ESCAPE:
                self.ativo = False
                
            # Atalho CTRL+A: seleciona tudo
            elif evento.key == pygame.K_a and (mods & pygame.KMOD_CTRL):
                self._selecionar_tudo()
                
            # Tecla BACKSPACE: apaga o caractere anterior ou a selecao inteira
            elif evento.key == pygame.K_BACKSPACE:
                if self._tem_selecao():
                    self._deletar_selecao()
                elif self.cursor > 0:
                    self.texto = self.texto[:self.cursor-1] + self.texto[self.cursor:]
                    self.cursor -= 1
                    self.sel_ini = self.sel_fim = self.cursor
                    
            # Tecla DELETE: apaga o caractere da frente
            elif evento.key == pygame.K_DELETE:
                if self._tem_selecao():
                    self._deletar_selecao()
                elif self.cursor < len(self.texto):
                    self.texto = self.texto[:self.cursor] + self.texto[self.cursor+1:]
                    self.sel_ini = self.sel_fim = self.cursor
                    
            # Setas DIRECIONAIS: movem o cursor para a esquerda ou direita
            elif evento.key == pygame.K_LEFT:
                self.cursor = max(0, self.cursor - 1)
                self.sel_ini = self.sel_fim = self.cursor
            elif evento.key == pygame.K_RIGHT:
                self.cursor = min(len(self.texto), self.cursor + 1)
                self.sel_ini = self.sel_fim = self.cursor
                
            # Tecla HOME: vai para o inicio do texto
            elif evento.key == pygame.K_HOME:
                self.cursor = self.sel_ini = self.sel_fim = 0
                
            # Tecla END: vai para o final do texto
            elif evento.key == pygame.K_END:
                self.cursor = self.sel_ini = self.sel_fim = len(self.texto)
                
            # Digitacao normal: aceita apenas numeros, ponto decimal e sinal negativo
            elif evento.unicode and evento.unicode in '0123456789.-':
                if self._tem_selecao():
                    self._deletar_selecao()
                self.texto = self.texto[:self.cursor] + evento.unicode + self.texto[self.cursor:]
                self.cursor += 1
                self.sel_ini = self.sel_fim = self.cursor

# =====================================================================
# FUNCOES AUXILIARES PARA DESENHO DO PAINEL LATERAL
# =====================================================================
# Definicao da paleta de cores (Tema Dark/Moderno)
COR_PAINEL      = (24, 24, 37)
COR_SEPARADOR   = (49, 50, 68)
COR_TEXTO_TITLE = (205, 214, 244)
COR_TEXTO_LABEL = (147, 153, 178)
COR_TEXTO_VALOR = (166, 227, 161)

# Desenha uma linha separadora horizontal no painel lateral
def desenhar_separador(tela, y):
    pygame.draw.line(tela, COR_SEPARADOR, (810, y), (1090, y), 1)

# Desenha o titulo de uma secao do menu e posiciona um separador logo abaixo
def desenhar_secao(tela, fonte_titulo, texto, y):
    tela.blit(fonte_titulo.render(texto, True, COR_TEXTO_TITLE), (820, y))
    desenhar_separador(tela, y + 26)