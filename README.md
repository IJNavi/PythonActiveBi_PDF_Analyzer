```markdown
# 📊 Active IA - Analisador de Documentos com Inteligência Artificial

Ferramenta desenvolvida para a **Active BI** que permite analistas de negócio fazerem perguntas sobre documentos PDF e obter respostas estruturadas automaticamente, com suporte a diversas línguas.

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
- **Idioma inteligente**: Detecta se a pergunta é em português ou inglês e responde no mesmo idioma
- **Três níveis de resposta**:
  - 📝 Conciso: 2 parágrafos para respostas rápidas
  - 📊 Padrão: 1 página A4 (500 palavras)
  - 🔬 Complexo: Análise aprofundada com múltiplas seções
- **Sugestões automáticas**: Sempre gera 3 perguntas de acompanhamento relevantes

## 📦 Como Obter o Projeto

### Opção 1: Baixar o Executável (Recomendado para usuários leigos em programação)
1. Acesse: https://github.com/IJNavi/PythonActiveBI_PDF_Analyzer/releases
2. Baixe o arquivo `ActiveIA.exe`
3. Coloque na Área de Trabalho, ou na pasta que preferir.
4. Pode criar um atalho: clique com o botão direito do mouse sobre o executável → "Criar atalho"

### Opção 2: Clonar o Repositório (Para desenvolvedores)
```bash
git clone https://github.com/[SEU-USUARIO]/analisador-pdf-ia.git
cd analisador-pdf-ia
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
 - O projeto já vai com um arquivo .env.exemple que é só copiar ou renomear! 
 - NÃO COLOQUE SUA CHAVE DE API NO ARQUIO .env.exemple!! O .gitignore só ignora o .env, 
   se der push para um repositório online com a chave no .env.exemple você irá expor ela!
## 🚀 Como Usar

1. Execute o programa (`ActiveIA.exe` ou `python gui.py`)
2. Clique em "ENTENDIDO" na tela de boas-vindas
3. Clique em "SELECIONAR" e escolha um arquivo PDF
4. Digite sua pergunta (ex: "Qual é o resumo deste documento?")
5. Escolha o nível de detalhamento da resposta
6. Clique em "ANALISAR DOCUMENTO"
7. Aguarde alguns segundos e veja a resposta formatada

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

- "Quais são as principais conclusões deste relatório?"
- "Faça uma análise SWOT da empresa"
- "Liste os 5 principais riscos mencionados"
- "Compare os resultados de 2023 com 2024"
- "What are the key recommendations?"

## 💰 Transparência de Custos

| Tipo de documento | Tokens | Custo estimado |
|------------------|--------|----------------|
| Relatório curto (10 páginas) | 5.000 | $0,0006 |
| Livro (300 páginas) | 75.000 | $0,015 |
| Mensal (100 documentos) | - | **~$15 USD** |

> 💡 **Dica**: O RAG local reduz em 95% os tokens enviados para a API!

## 💻 Recursos Computacionais

O sistema consome recursos locais principalmente durante o primeiro processamento de cada PDF. Para um documento de 300 páginas:

- **RAM**: até 1 GB temporariamente; com um índice ativo, cerca de 200 MB constantes
- **Processador**: uso intensivo por 1-3 minutos no primeiro acesso ao documento
- **Armazenamento**: 50-200 MB por documento em cache (pasta `rag_cache/`)

Consultas subsequentes são rápidas e leves, devido ao chache construído. Recomenda-se pelo menos 4 GB de RAM livre e 2 GB de espaço em disco.

## 🐛 Solução de Problemas Adicionais

| Problema | Solução |
|----------|---------|
| "OPENAI_API_KEY não encontrada" | Crie o arquivo `.env` com sua chave |
| "Falha ao extrair texto" | O PDF pode ser escaneado (imagem). Use OCR antes. |
| Programa abre e fecha rápido | Execute pelo terminal para ver a mensagem de erro |
| Tela branca ou congela | Aguarde o processamento do PDF (pode levar minutos em documentos grandes) |

## 📝 Licença

MIT License - Use à vontade para fins comerciais e pessoais.

---

**Desenvolvido para a Active BI | Consultoria Especializada em BI**
**Autor: Ivan Barbosa**
```
