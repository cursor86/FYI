# **RapidClip**

**RapidClip** é um projeto que automatiza a criação de vídeos curtos, ideais para plataformas como YouTube Shorts, Instagram Reels, TikTok e Kwai. Permite gerar vídeos completos a partir de um tema fornecido, combinando narração, imagens dinâmicas, efeitos visuais, legendas sincronizadas, registro detalhado do processo, integração de músicas de fundo, balanceamento automático do volume da música de fundo em harmonia com a narração, e montagem final e renderização do vídeo com transições animadas. Ao usar os novos modelos de TTS da OpenAI (Recomendado), a aplicação consegue definir dinamicamente o tom utilizado na narração, entonação, entre outras características da voz.

🇺🇸 Para a versão em inglês deste README, veja [README.md](README.md).

---

## **Vídeos de Demonstração gerados pelo RapidClip:**
_Observação: Os vídeos de demonstração foram convertidos de mp4 para mov._

<table>
  <thead>
    <tr>
      <th align="center"><g-emoji alias="arrow_forward">▶️</g-emoji> Demonstração 1</th>
      <th align="center"><g-emoji alias="arrow_forward">▶️</g-emoji> Demonstração 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">
        <video controls width="480">
          <source src="https://raw.githubusercontent.com/itallonardi/rapidclip-generator/main/demos/pt-br/vida_animal.mov" type="video/quicktime">
          Seu navegador não suporta o elemento de vídeo. Faça o download.
        </video>
        <br>
        <a href="https://raw.githubusercontent.com/itallonardi/rapidclip-generator/main/demos/pt-br/vida_animal.mov" download>Baixar Demonstração 1</a>
      </td>
      <td align="center">
        <video controls width="480">
          <source src="https://raw.githubusercontent.com/itallonardi/rapidclip-generator/main/demos/pt-br/historia.mov" type="video/quicktime">
          Seu navegador não suporta o elemento de vídeo. Faça o download.
        </video>
        <br>
        <a href="https://raw.githubusercontent.com/itallonardi/rapidclip-generator/main/demos/pt-br/historia.mov" download>Baixar Demonstração 2</a>
      </td>
    </tr>
  </tbody>
</table>

---

## **Funcionalidades Implementadas**

- **Criação Automática de Conteúdo**: Geração de roteiros personalizados com base no tema fornecido.
- **Narração de Áudio**: Transformação do roteiro em narração de alta qualidade, com suporte tanto ao ElevenLabs quanto ao OpenAI TTS.
- **Reprocessamento de Áudio**: Ajuste da duração do áudio para compatibilidade com plataformas.
- **Geração de Legendas**: Criação de legendas aprimoradas com alinhamento e segmentação:
  - Tokenização do texto transcrito, preservando a pontuação.
  - Alinhamento das palavras com seus respectivos timestamps e pontuações.
  - Criação de legendas legíveis e sincronizadas, respeitando limites de caracteres e palavras por linha.
- **Geração Aprimorada de Imagens**:
  - Geração diversificada de prompts para criação de imagens, utilizando o contexto das legendas e os prompts já gerados para garantir variação e criatividade.
  - Suporte à configuração da versão do modelo SANA via variável de ambiente.
- **Montagem Final do Vídeo**: Composição do vídeo final utilizando áudio, imagens, legendas e transições animadas (incluindo efeito de zoom in), mantendo a resolução de 1080x1920.
- **Integração de Músicas de Fundo**:
  - Seleção de trilha sonora a partir de uma biblioteca local de músicas de uso livre (configurada em `songs/songs.json` e armazenada em `songs/mp3`).
  - Escolha automática da música por um modelo de IA, com base no roteiro e nas imagens geradas.
- **Marca d'Água no Vídeo**: Marca d'água opcional em nível de vídeo, com texto personalizado através do argumento `--watermark`.
- **Imagens Relevantes**: Melhoria na seleção de imagens para ilustrar melhor o conteúdo.
- **Efeitos Visuais e Transições**: Aplicação de zoom, animações e cortes suaves adicionais.
- **Renderização Completa**: Criação do vídeo final pronto para publicação.
- **Suporte a Múltiplos Idiomas**: Possibilidade de criação de conteúdo, narração e legendas em diversos idiomas.
- **Registro de Processo**: Armazenamento de logs detalhados do andamento do processo – incluindo os prompts gerados para cada intervalo de imagem – na pasta de saída de cada vídeo.
- **Novos modelos de TTS da OpenAI suportados**: Ao usar os novos modelos de TTS da OpenAI, a aplicação consegue definir dinamicamente o tom utilizado na narração, entonação, entre outras características da voz.

---

## **Como Usar o RapidClip**

Antes de utilizar o RapidClip, é necessário configurar as variáveis de ambiente. Utilize o arquivo `.env.example` como modelo para criar seu próprio arquivo `.env`, contendo as seguintes variáveis:

```plaintext
OPENAI_API_KEY=sua-chave-api-openai
ELEVENLABS_API_KEY=sua-chave-api-elevenlabs
REPLICATE_API_TOKEN=sua-chave-api-replicate
SANA_MODEL_VERSION=versao-do-modelo-sana
```

---

## **Execução do RapidClip**

### **Usando Docker**

Você pode executar o RapidClip via Docker, facilitando o uso em um ambiente isolado com todas as dependências pré-instaladas. Para mais detalhes, consulte o [README.DOCKER.md](README.DOCKER.md).

### **Execução local (sem Docker)**

Se preferir rodar o projeto diretamente na sua máquina, siga os passos abaixo:

**1. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**2. Gere o vídeo:**

**Usando OpenAI TTS (Recomendado!):**
```bash
python src/main.py --theme "Curiosidades da Tecnologia (uma única curiosidade)" \
  --language "pt-BR" \
  --max_duration 60 \
  --tts_service openai \
  --openai_tts_model "gpt-4o-mini-tts" \
  --openai_tts_voice "ash" \
  --watermark "Nome do seu canal ou texto personalizado"
```

**Usando ElevenLabs TTS:**
```bash
python src/main.py --theme "Curiosidades do Espaço (uma única curiosidade)" \
  --language "pt-BR" \
  --voice_id "CstacWqMhJQlnfLPxRG4" \
  --max_duration 60 \
  --tts_service elevenlabs \
  --watermark "Nome do seu canal ou texto personalizado"
```

---

## **Licença**

Este projeto está licenciado sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.