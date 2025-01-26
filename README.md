# Simulação de Campos Elétricos

Este projeto permite a simulação de campos elétricos gerados por cargas pontuais e de linha. Ele utiliza a biblioteca `pygame` para a interface gráfica e visualização do campo elétrico e potencial gerado pelas cargas.

## Funcionalidades

- Visualização do campo elétrico e do potencial gerado por diferentes disposições de cargas.
- Interface interativa para adicionar, mover e remover cargas.
- Exibição de linhas de campo elétrico ou potencial gerado pelas cargas.
- Suporte a exemplos pré-definidos de configuração de cargas, como dipolos e quadrupolos.
- Capacidade de alternar entre visualização de campo elétrico e potencial.

## Instalação

### Pré-requisitos

- Python 3.x instalado em seu sistema.
- `pygame` e `numpy` devem ser instalados.

### Passos de Instalação

1. Clone este repositório:

    ```bash
    git clone https://github.com/Getulio-Mendes/Eletric-Charge-Simulation.git
    ```

2. Navegue até o diretório do projeto:

    ```bash
    cd Eletric-Charge-Simulation
    ```

3. Instale as dependências necessárias:

    ```bash
    pip install pygame numpy
    ```

4. Agora, você pode rodar o programa. Para iniciar o menu principal, execute o arquivo `menu.py`:

    ```bash
    python src/menu.py
    ```

## Como Usar

### Menu Principal

- **Projeto em Branco**: Cria um novo projeto vazio.
- **Exemplo: Dipolo**: Simula um dipolo com duas cargas de sinais opostos.
- **Exemplo: Monopolo Falso**: Exemplo de configuração com múltiplas cargas dispostas de forma a simular um monopolo falso.
- **Exemplo: Linha e Ponto**: Exemplo com uma carga de linha e uma carga pontual.
- **Exemplo: Duas Linhas**: Exemplo com duas cargas de linha de sinais opostos.
- **Exemplo: Quadrupolo**: Exemplo com quatro cargas dispostas como um quadrupolo.
- **Sair**: Fecha o programa.

### Interação com a Simulação

- **Adicionar Carga**: No menu lateral, você pode adicionar cargas pontuais (positivas ou negativas) ou cargas de linha (positivas ou negativas).
- **Mover Cargas**: Clique e arraste as cargas para movê-las pela tela.
- **Remover Cargas**: Ative o modo de remoção para apagar as cargas clicando nelas.
- **Alternar entre Campo Elétrico e Potencial**: Altere o modo de visualização entre campo elétrico e potencial utilizando o botão no menu lateral.

## Colaboradores

- Getúlio Santos Mendes
- Leandro Sousa Costa
- Felipe Parreiras Dias
- Regiane Pereira
