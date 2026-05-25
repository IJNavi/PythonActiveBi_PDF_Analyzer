```markdown
# 📊 Active IA - Analisador de Documentos com Inteligência Artificial

Ferramenta desenvolvida para a **Active BI** que permite analistas de negócio fazerem perguntas sobre documentos PDF e obter respostas estruturadas automaticamente, com suporte a **7 idiomas** (português, inglês, espanhol, francês, mandarim, hindi e árabe).

## 🎯 Motivação da Escolha do Modelo

O projeto utiliza o modelo **GPT-4o Mini** da OpenAI pelos seguintes motivos:

| Critério | GPT-4o Mini | GPT-4o | Diferença |
|----------|-------------|--------|-----------|
| **Custo por análise** | $0,00165 | $0,0585 | 35x mais barato |
| **Qualidade** | Alta | Muito Alta | Diferença mínima para documentos |
| **Velocidade** | Rápido | Médio | Mais rápido |
| **Contexto** | 128K tokens | 128K tokens | Igual |

**Para 100 documentos de 300 páginas por mês:**
- GPT-4o Mini: **~$15 USD/mês**
- GPT-4o: **~$585 USD/mês**

✅ **Decisão:** O GPT-4o Mini oferece 98% da qualidade por 3% do custo, ideal para análise de documentos empresariais.

## 🧠 Como o Projeto Funciona

### Arquitetura
1. **Extração local**: O texto do PDF é extraído no seu computador
2. **RAG (Retrieval-Augmented Generation)**: O documento é dividido em blocos e indexado localmente
3. **Embeddings**: O modelo `all-MiniLM-L6-v2` transforma textos em vetores numéricos (roda offline e grátis)
4. **IA**: Apenas o contexto relevante é enviado para a OpenAI (economia de 95% dos tokens)

### Regras de Negócio
- **Idioma inteligente**: Detecta o idioma da pergunta (entre 7 opções) e responde no mesmo idioma, preservando jargões técnicos em inglês
- **Três níveis de resposta**:
  - 📝 Conciso: 2 parágrafos para respostas rápidas
  - 📊 Padrão: 1 página A4 (500 palavras)
  - 🔬 Complexo: Análise aprofundada com múltiplas seções
- **Sugestões automáticas**: Sempre gera 3 perguntas de acompanhamento no mesmo idioma da pergunta
- **Histórico de análises**: Visualize, copie ou delete resultados anteriores em uma tela dedicada

## 📦 Como Obter o Projeto

### Opção 1 (AINDA NÃO DISPONÍVEL): Baixar o Executável (Recomendado para usuários leigos em programação)
1. Acesse: https://github.com/IJNavi/PythonActiveBI_PDF_Analyzer/releases
2. Baixe o arquivo `ActiveIA.exe`
3. Coloque na Área de Trabalho, ou na pasta que preferir.
4. Pode criar um atalho: clique com o botão direito do mouse sobre o executável → "Criar atalho"

## 🔑 Configurando a chave da API (para o executável)

O programa precisa de um arquivo de configuração chamado `.env` (sem extensão) no mesmo diretório do executável. Siga os passos:

1. Abra o Bloco de Notas.
2. Cole as linhas abaixo, substituindo `sk-sua-chave-aqui` pela sua chave real:

  OPENAI_API_KEY=sk-sua-chave-aqui
  OPENAI_MODEL=gpt-4o-mini
  TIKTOKEN_CACHE_DIR=""

3. Salve o arquivo: clique em "Arquivo" → "Salvar como".
4. No campo "Salvar como tipo", selecione **"Todos os arquivos (*.*)"**.
5. No campo "Nome do arquivo", digite exatamente: `.env`
6. Escolha a mesma pasta onde está o `ActiveIA.exe` e clique em "Salvar".

Pronto. Na próxima execução, o programa usará sua chave. Se precisar trocar a chave, basta editar o arquivo `.env` com o Bloco de Notas novamente.

### Opção 2: Clonar o Repositório (Para desenvolvedores)
```bash
git clone https://github.com/IJNavi/PythonActiveBI_PDF_Analyzer.git
cd PythonActiveBI_PDF_Analyzer
python -m venv .venv
.venv\Scripts\activate  # No Windows
pip install -r requirements.txt
python gui.py
```

## 🔧 Configuração Necessária

1. **Obter uma chave da OpenAI**:
   - Acesse: https://platform.openai.com/api-keys
   - Crie uma chave (começa com `sk-...`)
   - Adicione créditos (mínimo $5 USD)

2. **Criar arquivo `.env`** na pasta do projeto:
```
OPENAI_API_KEY=sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
```
 - O projeto já vem com um arquivo `.env.example` que é só copiar ou renomear! 
 - **NÃO COLOQUE SUA CHAVE DE API NO ARQUIVO `.env.example`**!! O `.gitignore` só ignora o `.env`, se der push para um repositório online com a chave no `.env.example` você irá expor ela!

## 🚀 Como Usar

1. Execute o programa (`ActiveIA.exe` ou `python gui.py`)
2. Na tela de boas-vindas, leia as instruções e marque "Não mostrar esta tela novamente" se desejar pular nas próximas execuções
3. Clique em "ENTENDIDO" para acessar a tela principal
4. Clique em "SELECIONAR" e escolha um arquivo PDF
5. Digite sua pergunta em qualquer um dos 7 idiomas suportados
6. Escolha o nível de detalhamento da resposta
7. Clique em "ANALISAR DOCUMENTO"
8. Aguarde alguns segundos e veja a resposta formatada
9. Navegue entre as telas usando os botões do cabeçalho:
   - **ANALISAR**: Volta para a tela de análise
   - **CACHE**: Abre a pasta de cache do sistema (explorador de arquivos)
   - **ANÁLISES**: Abre o histórico de resultados para visualizar, copiar ou deletar JSONs anteriores
   - **CONTATO**: Abre o site da Active BI

## 📂 Organização de Arquivos

### Resultados (pasta `resultados/`)
Os arquivos JSON são salvos automaticamente na estrutura:
```
resultados/YYYY-MM-DD/HH/Nome_do_PDF/resultado_HHMMSS.json
```
Um arquivo `LEIA_ME.txt` na raiz explica a organização.

### Cache RAG (pasta `rag_cache/`)
Os índices são armazenados em:
```
rag_cache/Nome_do_PDF/hash_do_conteudo/chroma_db/
```
Apenas as 2 versões mais recentes de cada PDF são mantidas automaticamente. Um arquivo `LEIA_ME.txt` explica a estrutura e manutenção.

## ⚠️ Problemas de Compatibilidade e Soluções

Devido a mudanças frequentes nas bibliotecas (especialmente LangChain), você pode encontrar erros de importação ao executar o código-fonte. Siga as orientações abaixo.

### Erro: `ModuleNotFoundError: No module named 'langchain.text_splitter'` ou similar

Isso ocorre porque versões recentes do LangChain movem os submódulos para pacotes separados. Solução:

1. Instale os pacotes necessários:
```bash
pip install langchain-text-splitters langchain-huggingface langchain-chroma langchain-core
```

2. Edite o arquivo `src/rag_engine.py` e substitua as seguintes linhas:

- `from langchain.text_splitter import RecursiveCharacterTextSplitter` → `from langchain_text_splitters import RecursiveCharacterTextSplitter`
- `from langchain.embeddings import HuggingFaceEmbeddings` → `from langchain_huggingface import HuggingFaceEmbeddings`
- `from langchain.vectorstores import Chroma` → `from langchain_chroma import Chroma`
- `from langchain.schema import Document` → `from langchain_core.documents import Document`

### Erro: `ModuleNotFoundError: No module named 'PyPDF2'`

Instale o PyPDF2 separadamente:
```bash
pip install PyPDF2
```

### Erro: conflito de versões durante `pip install -r requirements.txt`

Remova as versões fixas e use versões flexíveis. Exemplo de `requirements.txt` modificado:
```
openai>=1.12.0
python-dotenv>=1.0.0
pypdf>=3.17.4
pdfplumber>=0.10.0
langchain>=0.1.0,<0.3.0
chromadb>=0.4.22
sentence-transformers>=2.2.2
faiss-cpu>=1.8.0
tiktoken>=0.5.2
Pillow>=10.1.0
requests>=2.31.0
```

Depois instale normalmente.

### Ambiente virtual não ativado

Sempre ative o ambiente virtual antes de executar ou instalar pacotes. No VSCode, pressione `Ctrl+Shift+P` e escolha o interpretador Python que está dentro da pasta `.venv`.

Se o problema persistir, exclua a pasta `.venv` e recrie-a:

```bash
rmdir /s .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 📊 Exemplo de Perguntas

- "Quais são as principais conclusões deste relatório?" (português)
- "Faça uma análise SWOT da empresa" (português com termo inglês)
- "What are the key recommendations?" (inglês)
- "¿Cuáles son los riesgos identificados?" (espanhol)
- "请总结这份文档的主要内容" (mandarim)

## 💰 Transparência de Custos

| Tipo de documento | Tokens | Custo estimado |
|------------------|--------|----------------|
| Relatório curto (10 páginas) | 5.000 | $0,0006 |
| Livro (300 páginas) | 75.000 | $0,015 |
| Mensal (100 documentos) | - | **~$15 USD** |

> 💡 **Dica**: O RAG local reduz em 95% os tokens enviados para a API!

## 📈 Estimativa de Economia e Valor Agregado

Além da economia direta com o modelo GPT-4o Mini (já detalhada na seção de custos), o **Active IA** entrega benefícios que vão muito além da redução de tokens. A seguir, uma estimativa conservadora do valor gerado pelo sistema em um escritório de médio porte.

### Valor agregado exclusivo do Active IA

- **Extração automática de texto de PDF**: elimina o trabalho manual de abrir cada arquivo, selecionar e copiar trechos.
- **Organização dos resultados**: pastas estruturadas por data, hora e nome do documento (facilita auditoria, reuso e rastreabilidade).
- **Geração automática de perguntas de acompanhamento**: ajuda o analista a explorar o documento mais profundamente sem esforço adicional.
- **Interface gráfica integrada**: três telas (análise, histórico e cache) com botões de navegação que agilizam o fluxo de trabalho.

### Impacto financeiro estimado (valores aproximados)

A análise considerou um cenário típico:  
- 50 documentos por mês, cada um com 20 páginas.  
- 3 perguntas por documento → 150 consultas mensais.  
- Uso do modelo GPT-4o Mini já é muito barato, mas o RAG local reduz ainda mais os tokens de entrada (de ~14 mil para ~5 mil por pergunta).  

**Redução de custo de API**: cerca de **R$ 1,00 por mês** (ganho marginal, pois o modelo base já é de baixo custo).  

**Economia de tempo do analista**: cerca de **R$ 840 por mês**.  
- Sem o sistema, cada pergunta demandaria cerca de 10 minutos (ler, selecionar trechos, colar no chat, formatar resposta).  
- Com o Active IA, a tarefa cai para 1 minuto.  
- 150 perguntas × 9 minutos economizados = 1.350 minutos (22,5 horas) por mês.  
- Salário médio de analista (com encargos): R$ 6.000/mês (160h) → R$ 37,50/hora.  
- Economia: 22,5h × R$ 37,50 = **R$ 843,75/mês**.  

**Produtividade extra**: o analista pode realizar **10 vezes mais análises** no mesmo período, ou liberar horas para outras atividades estratégicas.  

> ⚠️ **Observação**: Os valores são estimativas. O retorno real depende do volume de documentos, da complexidade das perguntas e da eficiência do analista. No entanto, o ROI do projeto é altamente positivo em qualquer cenário realista.

## 💻 Recursos Computacionais

O sistema consome recursos locais principalmente durante o primeiro processamento de cada PDF. Para um documento de 300 páginas:

- **RAM**: até 1 GB temporariamente; com um índice ativo, cerca de 200 MB constantes
- **Processador**: uso intensivo por 1-3 minutos no primeiro acesso ao documento
- **Armazenamento**: 50-200 MB por documento em cache (pasta `rag_cache/`)

Consultas subsequentes são rápidas e leves, devido ao cache construído. Recomenda-se pelo menos 4 GB de RAM livre e 2 GB de espaço em disco.

## 🐛 Solução de Problemas Adicionais

| Problema | Solução |
|----------|---------|
| "OPENAI_API_KEY não encontrada" | Crie o arquivo `.env` com sua chave |
| "Falha ao extrair texto" | O PDF pode ser escaneado (imagem). Use OCR antes. |
| Programa abre e fecha rápido | Execute pelo terminal para ver a mensagem de erro |
| Tela branca ou congela | Aguarde o processamento do PDF (pode levar minutos em documentos grandes) |
| Sugestões vêm em inglês mesmo com pergunta em português | Verifique se o detector de idioma está funcionando (o sistema tenta detectar pela pergunta) |

## 📝 Licença

MIT License - Use à vontade para fins comerciais e pessoais.

---

**Desenvolvido para a Active BI | Consultoria Especializada em BI**
**Autor: Ivan Barbosa**
```