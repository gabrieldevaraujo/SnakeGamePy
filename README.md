# Snake (Jogo da Cobrinha)

Jogo da cobrinha clássico desenvolvido em **Python** com a biblioteca **Pygame**, como atividade prática de programação.

## Funcionalidades

- Movimentação da cobra pelas setas do teclado
- Geração aleatória de comida em posições livres do tabuleiro
- Crescimento da cobra ao coletar um alimento
- Sistema de pontuação exibido na tela, com recorde salvo entre execuções (`recorde.txt`)
- Aumento gradual de velocidade conforme a pontuação sobe
- Detecção de colisão com as paredes e com o próprio corpo
- Tela de Game Over com a pontuação final
- Reinício da partida sem precisar fechar o programa (basta pressionar Espaço)

## Requisitos

- Python 3.8 ou superior
- Biblioteca Pygame

## Como executar

1. Clone este repositório:
   ```bash
   git clone <URL-do-repositorio>
   cd <pasta-do-repositorio>
   ```

2. (Opcional, mas recomendado) crie um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux/Mac
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute o jogo:
   ```bash
   python snake.py
   ```

## Controles

| Tecla                | Ação                      |
|-----------------------|----------------------------|
| Setas do teclado       | Mover a cobra              |
| Espaço / Enter        | Iniciar / Reiniciar partida|
| Esc                   | Sair do jogo                |

## Estrutura do projeto

```
.
├── snake.py          # Código-fonte completo do jogo
├── requirements.txt  # Dependências do projeto
├── README.md          # Este arquivo
└── .gitignore
```

## Autor
Gabriel Neves Araujo - 230023026
Atividade desenvolvida para a disciplina de programação, utilizando Python e Pygame.
