import random
import sys
from collections import deque

import pygame

TAMANHO_CELULA = 20
COLUNAS = 32
LINHAS = 24
LARGURA_TELA = COLUNAS * TAMANHO_CELULA
ALTURA_TELA = LINHAS * TAMANHO_CELULA

VELOCIDADE_INICIAL = 8
VELOCIDADE_MAXIMA = 18
PONTOS_PARA_ACELERAR = 5  # a cada N pontos, o jogo fica um pouco mais rápido
FPS_TELA = 60

# paleta de cores (RGB)
COR_FUNDO = (18, 18, 24)
COR_COBRA_CABECA = (102, 217, 128)
COR_COBRA_CORPO = (60, 160, 90)
COR_COMIDA = (230, 70, 70)
COR_TEXTO = (240, 240, 240)
COR_TEXTO_DESTAQUE = (255, 210, 90)
COR_BORDA_MORTE = (200, 50, 50)

# Estados possíveis do jogo
ESTADO_MENU = "menu"
ESTADO_JOGANDO = "jogando"
ESTADO_GAME_OVER = "game_over"

# Direções representadas como vetores (delta_coluna, delta_linha). Guardamos também o "oposto" de cada direção para impedir que o jogador vire a cobra 180 graus instantaneamente, estabelendo uma fisica mínima de movimento.
CIMA = (0, -1)
BAIXO = (0, 1)
ESQUERDA = (-1, 0)
DIREITA = (1, 0)
OPOSTA = {CIMA: BAIXO, BAIXO: CIMA, ESQUERDA: DIREITA, DIREITA: ESQUERDA}

ARQUIVO_RECORDE = "recorde.txt"
class Cobra:
    """Representa a cobra: sua posição, direção e regras de movimento."""

    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        centro = (COLUNAS // 2, LINHAS // 2)
        # O corpo é guardado como uma deque decoordenadas (coluna, linha), da cabeça (índice 0) até a cauda. Uma deque é usada porque inserir na cabeça e remover da cauda a cada movimento é O(1), diferente de uma lista comum onde remover do início é O(n). (tudo em prol do bom processamento!! viva a complexidade de algoritmos!)
        self.corpo = deque([centro, (centro[0] - 1, centro[1]), (centro[0] - 2, centro[1])])
        self.direcao = DIREITA
        self.proxima_direcao = DIREITA
        self.deve_crescer = False

    def definir_direcao(self, nova_direcao):
        """Atualiza a direção pretendida, ignorando inversões de 180 graus."""
        if nova_direcao == OPOSTA.get(self.direcao):
            return
        self.proxima_direcao = nova_direcao

    def mover(self):
        # A direção só é processada aqui (e não em definir_direcao) para que a cobra não vire 2 movimentos em 1 passo (evita colisão nelamesma)
        self.direcao = self.proxima_direcao
        coluna_cabeca, linha_cabeca = self.corpo[0]
        delta_coluna, delta_linha = self.direcao
        nova_cabeca = (coluna_cabeca + delta_coluna, linha_cabeca + delta_linha)

        self.corpo.appendleft(nova_cabeca)
        if self.deve_crescer:
            # Quando crescer, ela não tira da cauda, apenas aumenta o corpo na cauda.
            self.deve_crescer = False
        else:
            self.corpo.pop()

    def crescer(self):
        self.deve_crescer = True

    def colidiu_com_parede(self):
        coluna_cabeca, linha_cabeca = self.corpo[0]
        return not (0 <= coluna_cabeca < COLUNAS and 0 <= linha_cabeca < LINHAS)

    def colidiu_com_propio_corpo(self):
        cabeca = self.corpo[0]
        # A cabeça é comparada com o restante do corpo (sem contar ela mesma).
        return cabeca in list(self.corpo)[1:]

    def ocupa(self, posicao):
        return posicao in self.corpo

    def desenhar(self, tela):
        for indice, (coluna, linha) in enumerate(self.corpo):
            retangulo = pygame.Rect(
                coluna * TAMANHO_CELULA, linha * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA
            )
            cor = COR_COBRA_CABECA if indice == 0 else COR_COBRA_CORPO
            pygame.draw.rect(tela, cor, retangulo)


class Comida:
    """Representa o alimento que a cobra deve coletar para crescer e pontuar."""

    def __init__(self):
        self.posicao = (0, 0)

    def reposicionar(self, celulas_ocupadas):
        """Sorteia uma nova posição livre (fora do corpo da cobra)."""
        # Gerar todas as posições livres e escolher uma delas garante que a comida nunca apareça em cima da cobra.
        todas_as_posicoes = {(c, l) for c in range(COLUNAS) for l in range(LINHAS)}
        posicoes_livres = list(todas_as_posicoes - set(celulas_ocupadas))
        self.posicao = random.choice(posicoes_livres)

    def desenhar(self, tela):
        coluna, linha = self.posicao
        retangulo = pygame.Rect(
            coluna * TAMANHO_CELULA, linha * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA
        )
        pygame.draw.rect(tela, COR_COMIDA, retangulo)


class Jogo:
    """Controla o laço principal, os estados do jogo e a pontuação."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake - Atividade Pygame")
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        self.relogio = pygame.time.Clock()

        self.fonte_normal = pygame.font.SysFont("consolas", 22)
        self.fonte_titulo = pygame.font.SysFont("consolas", 48, bold=True)

        self.recorde = self._carregar_recorde()
        self.estado = ESTADO_MENU
        self._preparar_nova_partida()

        # Temporizador em milissegundos usado para controlar a velocidade de movimento da cobra independentemente do FPS de renderização (assim o desenho na tela permanece fluido mesmo em velocidades baixas).
        self.tempo_acumulado = 0

    def _carregar_recorde(self):
        try:
            with open(ARQUIVO_RECORDE, "r", encoding="utf-8") as arquivo:
                return int(arquivo.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _salvar_recorde(self):
        with open(ARQUIVO_RECORDE, "w", encoding="utf-8") as arquivo:
            arquivo.write(str(self.recorde))

    def _preparar_nova_partida(self):
        self.cobra = Cobra()
        self.comida = Comida()
        self.comida.reposicionar(self.cobra.corpo)
        self.pontuacao = 0
        self.velocidade_atual = VELOCIDADE_INICIAL

    # --------------------------------------------------------

    def executar(self):
        while True:
            delta_tempo_ms = self.relogio.tick(FPS_TELA)
            self._processar_eventos()

            if self.estado == ESTADO_JOGANDO:
                self._atualizar_logica(delta_tempo_ms)

            self._desenhar_tela()

    def _processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                self._processar_tecla(evento.key)

    def _processar_tecla(self, tecla):
        if self.estado == ESTADO_MENU:
            if tecla in (pygame.K_SPACE, pygame.K_RETURN):
                self.estado = ESTADO_JOGANDO
            return

        if self.estado == ESTADO_GAME_OVER:
            if tecla in (pygame.K_SPACE, pygame.K_RETURN):
                self._preparar_nova_partida()
                self.estado = ESTADO_JOGANDO
            elif tecla == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            return

        mapa_teclas = {
            pygame.K_UP: CIMA,
            pygame.K_DOWN: BAIXO,
            pygame.K_LEFT: ESQUERDA,
            pygame.K_RIGHT: DIREITA,
        }
        if tecla in mapa_teclas:
            self.cobra.definir_direcao(mapa_teclas[tecla])
        elif tecla == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    def _atualizar_logica(self, delta_tempo_ms):
        # Só move a cobra quando o tempo acumulado ultrapassa o intervalo correspondente à velocidade atual. Isso faz com que a velocidade do jogo do FPS de renderização, permitindo aumentar a dificuldade sem deixar o jogo "travado" a 60 quadros por segundo.
        self.tempo_acumulado += delta_tempo_ms
        intervalo_movimento_ms = 1000 // self.velocidade_atual

        if self.tempo_acumulado < intervalo_movimento_ms:
            return
        self.tempo_acumulado = 0

        self.cobra.mover()

        if self.cobra.colidiu_com_parede() or self.cobra.colidiu_com_propio_corpo():
            self._finalizar_partida()
            return

        if self.cobra.corpo[0] == self.comida.posicao:
            self.cobra.crescer()
            self.pontuacao += 1
            self.comida.reposicionar(self.cobra.corpo)

            # A cada PONTOS_PARA_ACELERAR, a velocidade sobe um passo, até o VELOCIDADE_MAXIMA para o jogo continuar jogável
            if self.pontuacao % PONTOS_PARA_ACELERAR == 0:
                self.velocidade_atual = min(self.velocidade_atual + 1, VELOCIDADE_MAXIMA)

    def _finalizar_partida(self):
        self.estado = ESTADO_GAME_OVER
        if self.pontuacao > self.recorde:
            self.recorde = self.pontuacao
            self._salvar_recorde()

    # -- Desenho --------------------------------------------------------------

    def _desenhar_tela(self):
        self.tela.fill(COR_FUNDO)

        if self.estado == ESTADO_MENU:
            self._desenhar_menu()
        elif self.estado == ESTADO_JOGANDO:
            self.comida.desenhar(self.tela)
            self.cobra.desenhar(self.tela)
            self._desenhar_hud()
        elif self.estado == ESTADO_GAME_OVER:
            self._desenhar_game_over()

        pygame.display.flip()

    def _desenhar_hud(self):
        texto_pontuacao = self.fonte_normal.render(f"Pontos: {self.pontuacao}", True, COR_TEXTO)
        texto_recorde = self.fonte_normal.render(
            f"Recorde: {self.recorde}", True, COR_TEXTO_DESTAQUE
        )
        self.tela.blit(texto_pontuacao, (10, 8))
        self.tela.blit(texto_recorde, (10, 32))

    def _desenhar_menu(self):
        self._desenhar_texto_centralizado("SNAKE", self.fonte_titulo, COR_COBRA_CABECA, -60)
        self._desenhar_texto_centralizado(
            "Use as setas do teclado para mover", self.fonte_normal, COR_TEXTO, 10
        )
        self._desenhar_texto_centralizado(
            "Pressione ESPACO para comecar", self.fonte_normal, COR_TEXTO_DESTAQUE, 45
        )
        self._desenhar_texto_centralizado(
            f"Recorde atual: {self.recorde}", self.fonte_normal, COR_TEXTO, 80
        )

    def _desenhar_game_over(self):
        self.tela.fill(COR_FUNDO)

        self._desenhar_texto_centralizado("GAME OVER", self.fonte_titulo, COR_BORDA_MORTE, -60)
        self._desenhar_texto_centralizado(
            f"Pontuacao final: {self.pontuacao}", self.fonte_normal, COR_TEXTO, 0
        )
        self._desenhar_texto_centralizado(
            "Pressione ESPACO para jogar novamente", self.fonte_normal, COR_TEXTO_DESTAQUE, 45
        )
        self._desenhar_texto_centralizado(
            "Pressione ESC para sair", self.fonte_normal, COR_TEXTO, 75
        )

    def _desenhar_texto_centralizado(self, texto, fonte, cor, deslocamento_vertical):
        superficie_texto = fonte.render(texto, True, cor)
        retangulo = superficie_texto.get_rect(
            center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + deslocamento_vertical)
        )
        self.tela.blit(superficie_texto, retangulo)


def main():
    jogo = Jogo()
    jogo.executar()


if __name__ == "__main__":
    main()
