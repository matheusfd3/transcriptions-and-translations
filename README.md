# Transcriptions and Translations
## Descrição
Este projeto captura o áudio do microfone em tempo real, transcreve e traduz para português.

## Requisitos
**OBS: Este script foi desenvolvido e testado em sistema Linux**
1. Certifique-se de ter o Python 3.x instalado em seu sistema.
```bash
  pip install -r requirements.txt
```
Nota: Dependências adicionais podem ser necessárias. Caso apareça algum erro, tente instalá-las manualmente ou consulte a documentação das bibliotecas.
### PulseAudio (LINUX)
- Para capturar áudio do sistema (em vez do microfone) no Linux, você pode instalar o PulseAudio:
```bash
  sudo apt-get install pulseaudio
```
- Configurações adicionais podem ser necessárias para garantir que o PulseAudio capture o áudio corretamente.
## Como usar
1. Clone o repositório em sua máquina local:
```bash
  git clone https://github.com/matheusfd3/transcriptions-and-translations.git
```
2. Entre no diretório do projeto:
```bash
    cd transcriptions-and-translations
```
2. Execute o script:
```bash
  python main.py
```
3. Escolha o seu microfone.
4. Clique em "Começar" para ter o áudio transcrito e traduzido.

## Screenshots
- Transcrevendo e traduzindo um vídeo(em inglês) do YouTube em tempo real, usando PulseAudio para capturar áudio do sistema.
![App Screenshot](https://github.com/matheusfd3/transcriptions-and-translations/blob/main/.github/image01.png)

## Contribuição
Contribuições são bem-vindas! Se você encontrou um bug ou tem alguma sugestão para melhorar o projeto, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Autor
Este projeto foi desenvolvido por [matheusfd3](https://github.com/matheusfd3)
