"""
Analisador de Documentos com IA - Active BI Edition
Interface com design inspirado no site activebi.com.br
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import json
from datetime import datetime
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser
import os

from src.rag_engine import RAGEngine
from src.ia_client import IAClient
from src.response_controller import ResponseController, ResponseLevel
from src.cost_calculator import CostCalculator
from dotenv import load_dotenv

load_dotenv()

class ActiveBIStyle:
    """Configurações de estilo baseadas no site da Active BI"""
    
    # Cores principais do site
    PRIMARY_BLUE = "#0a2540"      # Azul escuro do header/fundo
    SECONDARY_BLUE = "#1a3a5c"    # Azul médio para elementos secundários
    LIGHT_BLUE = "#2a4a7c"        # Azul mais claro para hover
    ORANGE = "#ff6b00"            # Laranja do botão Contato e destaques
    ORANGE_HOVER = "#ff8533"      # Laranja mais claro para efeito de luminosidade
    WHITE = "#ffffff"             # Branco para textos
    GRAY_LIGHT = "#e0e0e0"        # Cinza claro para bordas
    BG_LIGHT = "#f5f7fa"          # Fundo claro para áreas de conteúdo
    
    # Fontes
    FONT_TITLE = ("Segoe UI", 16, "bold")
    FONT_SUBTITLE = ("Segoe UI", 12)
    FONT_BODY = ("Segoe UI", 10)
    FONT_BUTTON = ("Segoe UI", 10, "bold")
    FONT_HEADER = ("Segoe UI", 20, "bold")
    FONT_WELCOME = ("Segoe UI", 14)
    
    @classmethod
    def apply_styles(cls):
        """Aplica estilos aos widgets ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame padrão
        style.configure('TFrame', background=cls.WHITE)
        
        # Label padrão
        style.configure('TLabel', background=cls.WHITE, foreground=cls.PRIMARY_BLUE)
        
        # Botão primário (azul)
        style.configure('Primary.TButton',
                       background=cls.PRIMARY_BLUE,
                       foreground=cls.WHITE,
                       borderwidth=0,
                       focuscolor='none',
                       font=cls.FONT_BUTTON,
                       padding=(20, 8))
        style.map('Primary.TButton',
                 background=[('active', cls.LIGHT_BLUE),
                           ('pressed', cls.SECONDARY_BLUE)],
                 foreground=[('active', cls.WHITE)])
        
        # Botão laranja (Contato)
        style.configure('Contact.TButton',
                       background=cls.ORANGE,
                       foreground=cls.WHITE,
                       borderwidth=0,
                       focuscolor='none',
                       font=cls.FONT_BUTTON,
                       padding=(20, 8))
        style.map('Contact.TButton',
                 background=[('active', cls.ORANGE_HOVER)],
                 foreground=[('active', cls.WHITE)])
        
        # Botão padrão (outline azul)
        style.configure('Outline.TButton',
                       background=cls.WHITE,
                       foreground=cls.PRIMARY_BLUE,
                       borderwidth=1,
                       focusthickness=0,
                       font=cls.FONT_BUTTON,
                       padding=(15, 6))
        style.map('Outline.TButton',
                 background=[('active', cls.PRIMARY_BLUE)],
                 foreground=[('active', cls.WHITE)])
        
        # Botão de análise (laranja cheio)
        style.configure('Analyze.TButton',
                       background=cls.ORANGE,
                       foreground=cls.WHITE,
                       borderwidth=0,
                       focuscolor='none',
                       font=("Segoe UI", 12, "bold"),
                       padding=(30, 12))
        style.map('Analyze.TButton',
                 background=[('active', cls.ORANGE_HOVER)],
                 foreground=[('active', cls.WHITE)])


class WelcomeScreen:
    """Tela de boas-vindas com instruções para criar atalho"""
    
    def __init__(self, parent, on_complete):
        self.parent = parent
        self.on_complete = on_complete
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Cria widgets da tela de boas-vindas"""
        
        # Container principal com padding
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Logo (carregada da web)
        self.load_logo(main_container)
        
        # Título
        title_label = tk.Label(
            main_container,
            text="Bem-vindo ao Analisador de Documentos com IA",
            font=ActiveBIStyle.FONT_HEADER,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE
        )
        title_label.pack(pady=(20, 10))
        
        # Subtítulo
        subtitle_label = tk.Label(
            main_container,
            text="Active IA - Inteligência Adaptada ao seu Negócio",
            font=ActiveBIStyle.FONT_SUBTITLE,
            fg=ActiveBIStyle.SECONDARY_BLUE,
            bg=ActiveBIStyle.WHITE
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Frame para instruções
        instructions_frame = tk.Frame(
            main_container,
            bg=ActiveBIStyle.BG_LIGHT,
            relief=tk.RIDGE,
            bd=1
        )
        instructions_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Título das instruções
        inst_title = tk.Label(
            instructions_frame,
            text="📌 Como criar um atalho para facilitar o acesso:",
            font=ActiveBIStyle.FONT_TITLE,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.BG_LIGHT
        )
        inst_title.pack(pady=(20, 15), padx=20, anchor=tk.W)
        
        # Passo 1
        step1 = tk.Label(
            instructions_frame,
            text="1️⃣ Clique com o botão DIREITO do mouse no arquivo executável (.exe)",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.BG_LIGHT
        )
        step1.pack(pady=5, padx=30, anchor=tk.W)
        
        # Passo 2
        step2 = tk.Label(
            instructions_frame,
            text="2️⃣ No menu que abrir, selecione 'Criar atalho'",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.BG_LIGHT
        )
        step2.pack(pady=5, padx=30, anchor=tk.W)
        
        # Passo 3
        step3 = tk.Label(
            instructions_frame,
            text="3️⃣ Arraste o atalho criado para a Área de Trabalho ou Menu Iniciar",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.BG_LIGHT
        )
        step3.pack(pady=5, padx=30, anchor=tk.W)
        
        # Dica adicional
        tip_frame = tk.Frame(instructions_frame, bg=ActiveBIStyle.BG_LIGHT)
        tip_frame.pack(pady=(20, 20), padx=30, fill=tk.X)
        
        tip_icon = tk.Label(
            tip_frame,
            text="💡",
            font=("Segoe UI", 14),
            fg=ActiveBIStyle.ORANGE,
            bg=ActiveBIStyle.BG_LIGHT
        )
        tip_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        tip_text = tk.Label(
            tip_frame,
            text="Dica: Você pode renomear o atalho para 'Active IA' e alterar o ícone nas propriedades!",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.SECONDARY_BLUE,
            bg=ActiveBIStyle.BG_LIGHT
        )
        tip_text.pack(side=tk.LEFT)
        
        # Botão Entendido
        understood_btn = tk.Button(
            main_container,
            text="ENTENDIDO, VAMOS COMEÇAR →",
            font=ActiveBIStyle.FONT_BUTTON,
            bg=ActiveBIStyle.ORANGE,
            fg=ActiveBIStyle.WHITE,
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.on_complete
        )
        
        def on_enter(e):
            understood_btn.config(bg=ActiveBIStyle.ORANGE_HOVER)
        
        def on_leave(e):
            understood_btn.config(bg=ActiveBIStyle.ORANGE)
        
        understood_btn.bind("<Enter>", on_enter)
        understood_btn.bind("<Leave>", on_leave)
        understood_btn.pack(pady=30)
        
        # Rodapé com direitos
        footer = tk.Label(
            main_container,
            text="© 2024 Active BI - Consultoria Especializada em BI",
            font=("Segoe UI", 8),
            fg=ActiveBIStyle.GRAY_LIGHT,
            bg=ActiveBIStyle.WHITE
        )
        footer.pack(pady=(20, 0))
    
    def load_logo(self, container):
        """Carrega a logo da Active BI da web"""
        try:
            url = "https://www.activebi.com.br/midias/imagens/active-bi-branco.16782989371.webp"
            response = requests.get(url, timeout=10)
            img = Image.open(BytesIO(response.content))
            
            # Redimensiona mantendo proporção
            img.thumbnail((200, 80), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            
            logo_label = tk.Label(
                container,
                image=self.logo_img,
                bg=ActiveBIStyle.WHITE
            )
            logo_label.pack(pady=(0, 10))
        except Exception as e:
            # Fallback: texto se não conseguir carregar a imagem
            text_logo = tk.Label(
                container,
                text="ACTIVE BI",
                font=("Segoe UI", 24, "bold"),
                fg=ActiveBIStyle.PRIMARY_BLUE,
                bg=ActiveBIStyle.WHITE
            )
            text_logo.pack(pady=(0, 10))
            
            sub_logo = tk.Label(
                container,
                text="BUSINESS INTELLIGENCE",
                font=("Segoe UI", 10),
                fg=ActiveBIStyle.SECONDARY_BLUE,
                bg=ActiveBIStyle.WHITE
            )
            sub_logo.pack()


class HeaderFrame(tk.Frame):
    """Header com logo e botão de contato"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(height=80, bg=ActiveBIStyle.PRIMARY_BLUE)
        self.pack(fill=tk.X, pady=(0, 10))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Cria widgets do header"""
        
        # Container interno com padding
        container = tk.Frame(self, bg=ActiveBIStyle.PRIMARY_BLUE)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Logo (carregada da web)
        self.load_logo(container)
        
        # Botão Contato (laranja, lado direito)
        contact_btn = tk.Button(
            container,
            text="CONTATO",
            font=ActiveBIStyle.FONT_BUTTON,
            bg=ActiveBIStyle.ORANGE,
            fg=ActiveBIStyle.WHITE,
            bd=0,
            padx=25,
            pady=8,
            cursor="hand2",
            command=self.open_contact
        )
        
        # Efeito hover no botão Contato
        def on_enter(e):
            contact_btn.config(bg=ActiveBIStyle.ORANGE_HOVER)
        
        def on_leave(e):
            contact_btn.config(bg=ActiveBIStyle.ORANGE)
        
        contact_btn.bind("<Enter>", on_enter)
        contact_btn.bind("<Leave>", on_leave)
        
        contact_btn.pack(side=tk.RIGHT)
    
    def load_logo(self, container):
        """Carrega a logo da Active BI"""
        try:
            url = "https://www.activebi.com.br/midias/imagens/active-bi-branco.16782989371.webp"
            response = requests.get(url, timeout=10)
            img = Image.open(BytesIO(response.content))
            
            # Redimensiona mantendo proporção
            img.thumbnail((150, 50), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            
            logo_label = tk.Label(
                container,
                image=self.logo_img,
                bg=ActiveBIStyle.PRIMARY_BLUE
            )
            logo_label.pack(side=tk.LEFT)
        except:
            # Fallback: texto
            logo_text = tk.Label(
                container,
                text="ACTIVE BI",
                font=("Segoe UI", 16, "bold"),
                fg=ActiveBIStyle.WHITE,
                bg=ActiveBIStyle.PRIMARY_BLUE
            )
            logo_text.pack(side=tk.LEFT)
    
    def open_contact(self):
        """Abre o site da Active BI na página de contato (fale conosco)"""
        webbrowser.open("https://www.activebi.com.br/fale-conosco")


class DocumentAnalyzerGUI:
    """Interface gráfica principal"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Active IA - Analisador de Documentos")
        self.root.geometry("1000x750")
        self.root.configure(bg=ActiveBIStyle.WHITE)
        
        # Configurações
        self.current_pdf_path = None
        self.vectorstore = None
        self.rag_engine = None
        self.ia_client = None
        self.cost_calculator = None
        
        # Inicializa componentes
        self.init_components()
        
        # Mostra tela de boas-vindas primeiro
        self.show_welcome_screen()
    
    def init_components(self):
        """Inicializa os componentes do sistema"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                messagebox.showerror(
                    "Erro",
                    "OPENAI_API_KEY não encontrada!\n\n"
                    "Crie um arquivo .env na raiz do projeto com:\n"
                    "OPENAI_API_KEY=sua_chave_aqui"
                )
                self.root.quit()
                return
            
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            self.ia_client = IAClient(api_key, model)
            self.rag_engine = RAGEngine()
            self.response_controller = ResponseController()
            self.cost_calculator = CostCalculator(model)
            
            ActiveBIStyle.apply_styles()
            
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", str(e))
            self.root.quit()
    
    def show_welcome_screen(self):
        """Exibe a tela de boas-vindas"""
        self.welcome_screen = WelcomeScreen(self.root, self.on_welcome_complete)
    
    def on_welcome_complete(self):
        """Callback quando usuário clica em Entendido"""
        self.welcome_screen.frame.destroy()
        self.create_main_interface()
    
    def create_main_interface(self):
        """Cria a interface principal após o welcome screen"""
        
        # Header com logo e botão contato
        self.header = HeaderFrame(self.root)
        
        # Frame principal com scroll
        main_canvas = tk.Canvas(self.root, bg=ActiveBIStyle.WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Container principal
        main_frame = ttk.Frame(self.scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # ==================== SEÇÃO PDF ====================
        pdf_frame = tk.LabelFrame(
            main_frame,
            text=" 📄 Documento PDF ",
            font=ActiveBIStyle.FONT_TITLE,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE,
            bd=2,
            relief=tk.RIDGE
        )
        pdf_frame.pack(fill=tk.X, pady=(0, 20))
        
        pdf_inner = tk.Frame(pdf_frame, bg=ActiveBIStyle.WHITE)
        pdf_inner.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            pdf_inner,
            text="Arquivo:",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.pdf_path_var = tk.StringVar()
        pdf_entry = tk.Entry(
            pdf_inner,
            textvariable=self.pdf_path_var,
            font=ActiveBIStyle.FONT_BODY,
            bg=ActiveBIStyle.BG_LIGHT,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            relief=tk.SUNKEN,
            state='readonly',
            width=60
        )
        pdf_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        select_btn = tk.Button(
            pdf_inner,
            text="📂 SELECIONAR",
            font=ActiveBIStyle.FONT_BUTTON,
            bg=ActiveBIStyle.PRIMARY_BLUE,
            fg=ActiveBIStyle.WHITE,
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.select_pdf
        )
        
        def on_select_enter(e):
            select_btn.config(bg=ActiveBIStyle.LIGHT_BLUE)
        
        def on_select_leave(e):
            select_btn.config(bg=ActiveBIStyle.PRIMARY_BLUE)
        
        select_btn.bind("<Enter>", on_select_enter)
        select_btn.bind("<Leave>", on_select_leave)
        select_btn.pack(side=tk.RIGHT)
        
        # Status do PDF
        self.pdf_status_var = tk.StringVar(value="⚠️ Nenhum PDF carregado")
        status_label = tk.Label(
            pdf_frame,
            textvariable=self.pdf_status_var,
            font=("Segoe UI", 9),
            fg=ActiveBIStyle.SECONDARY_BLUE,
            bg=ActiveBIStyle.WHITE
        )
        status_label.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # ==================== SEÇÃO PERGUNTA ====================
        question_frame = tk.LabelFrame(
            main_frame,
            text=" ❓ Sua Pergunta ",
            font=ActiveBIStyle.FONT_TITLE,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE,
            bd=2,
            relief=tk.RIDGE
        )
        question_frame.pack(fill=tk.X, pady=(0, 20))
        
        question_inner = tk.Frame(question_frame, bg=ActiveBIStyle.WHITE)
        question_inner.pack(fill=tk.X, padx=15, pady=15)
        
        self.question_text = scrolledtext.ScrolledText(
            question_inner,
            height=5,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg=ActiveBIStyle.BG_LIGHT,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            relief=tk.SUNKEN,
            bd=1
        )
        self.question_text.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder
        self.question_text.insert("1.0", "Digite sua pergunta aqui...")
        self.question_text.bind("<FocusIn>", self.clear_placeholder)
        self.question_text.bind("<FocusOut>", self.add_placeholder)
        
        # ==================== SEÇÃO CONFIGURAÇÕES ====================
        config_frame = tk.LabelFrame(
            main_frame,
            text=" ⚙️ Configurações da Resposta ",
            font=ActiveBIStyle.FONT_TITLE,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE,
            bd=2,
            relief=tk.RIDGE
        )
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        config_inner = tk.Frame(config_frame, bg=ActiveBIStyle.WHITE)
        config_inner.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            config_inner,
            text="Nível de Detalhamento:",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        self.response_level = tk.StringVar(value="standard")
        
        # Radio buttons customizados
        concise_rb = tk.Radiobutton(
            config_inner,
            text="📝 Conciso (2 parágrafos)",
            variable=self.response_level,
            value="concise",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE,
            selectcolor=ActiveBIStyle.WHITE,
            activebackground=ActiveBIStyle.WHITE
        )
        concise_rb.pack(side=tk.LEFT, padx=(0, 20))
        
        standard_rb = tk.Radiobutton(
            config_inner,
            text="📊 Padrão (1 página A4)",
            variable=self.response_level,
            value="standard",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE,
            selectcolor=ActiveBIStyle.WHITE,
            activebackground=ActiveBIStyle.WHITE
        )
        standard_rb.pack(side=tk.LEFT, padx=(0, 20))
        
        complex_rb = tk.Radiobutton(
            config_inner,
            text="🔬 Complexo (Análise profunda)",
            variable=self.response_level,
            value="complex",
            font=ActiveBIStyle.FONT_BODY,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE,
            selectcolor=ActiveBIStyle.WHITE,
            activebackground=ActiveBIStyle.WHITE
        )
        complex_rb.pack(side=tk.LEFT)
        
        # ==================== BOTÃO ANALISAR ====================
        self.analyze_btn = tk.Button(
            main_frame,
            text="🔍 ANALISAR DOCUMENTO",
            font=("Segoe UI", 12, "bold"),
            bg=ActiveBIStyle.ORANGE,
            fg=ActiveBIStyle.WHITE,
            bd=0,
            padx=40,
            pady=12,
            cursor="hand2",
            state='disabled',
            command=self.analyze_document
        )
        
        def on_analyze_enter(e):
            if self.analyze_btn['state'] == 'normal':
                self.analyze_btn.config(bg=ActiveBIStyle.ORANGE_HOVER)
        
        def on_analyze_leave(e):
            if self.analyze_btn['state'] == 'normal':
                self.analyze_btn.config(bg=ActiveBIStyle.ORANGE)
        
        self.analyze_btn.bind("<Enter>", on_analyze_enter)
        self.analyze_btn.bind("<Leave>", on_analyze_leave)
        self.analyze_btn.pack(pady=(0, 20))
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=500)
        
        # ==================== SEÇÃO RESPOSTA ====================
        response_frame = tk.LabelFrame(
            main_frame,
            text=" 📊 Resposta da IA ",
            font=ActiveBIStyle.FONT_TITLE,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            bg=ActiveBIStyle.WHITE,
            bd=2,
            relief=tk.RIDGE
        )
        response_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        response_inner = tk.Frame(response_frame, bg=ActiveBIStyle.WHITE)
        response_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.response_text = scrolledtext.ScrolledText(
            response_inner,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=ActiveBIStyle.BG_LIGHT,
            fg=ActiveBIStyle.PRIMARY_BLUE,
            relief=tk.SUNKEN,
            bd=1,
            height=12
        )
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # Configura tags para formatação
        self.response_text.tag_config("heading", font=("Consolas", 12, "bold"), foreground=ActiveBIStyle.ORANGE)
        self.response_text.tag_config("bold", font=("Consolas", 10, "bold"))
        
        # ==================== INFORMAÇÕES RODAPÉ ====================
        info_frame = tk.Frame(main_frame, bg=ActiveBIStyle.WHITE)
        info_frame.pack(fill=tk.X)
        
        self.cost_label = tk.Label(
            info_frame,
            text="💰 Custo: -",
            font=("Segoe UI", 9),
            fg="green",
            bg=ActiveBIStyle.WHITE
        )
        self.cost_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.time_label = tk.Label(
            info_frame,
            text="⏱️ Tempo: -",
            font=("Segoe UI", 9),
            fg=ActiveBIStyle.ORANGE,
            bg=ActiveBIStyle.WHITE
        )
        self.time_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.tokens_label = tk.Label(
            info_frame,
            text="🔢 Tokens: -",
            font=("Segoe UI", 9),
            fg=ActiveBIStyle.SECONDARY_BLUE,
            bg=ActiveBIStyle.WHITE
        )
        self.tokens_label.pack(side=tk.LEFT)
        
        copy_btn = tk.Button(
            info_frame,
            text="📋 Copiar Resposta",
            font=ActiveBIStyle.FONT_BUTTON,
            bg=ActiveBIStyle.PRIMARY_BLUE,
            fg=ActiveBIStyle.WHITE,
            bd=0,
            padx=15,
            pady=3,
            cursor="hand2",
            command=self.copy_response
        )
        
        def on_copy_enter(e):
            copy_btn.config(bg=ActiveBIStyle.LIGHT_BLUE)
        
        def on_copy_leave(e):
            copy_btn.config(bg=ActiveBIStyle.PRIMARY_BLUE)
        
        copy_btn.bind("<Enter>", on_copy_enter)
        copy_btn.bind("<Leave>", on_copy_leave)
        copy_btn.pack(side=tk.RIGHT)
    
    def clear_placeholder(self, event):
        """Limpa placeholder da pergunta"""
        if self.question_text.get("1.0", tk.END).strip() == "Digite sua pergunta aqui...":
            self.question_text.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        """Adiciona placeholder se vazio"""
        if not self.question_text.get("1.0", tk.END).strip():
            self.question_text.insert("1.0", "Digite sua pergunta aqui...")
    
    def select_pdf(self):
        """Seleciona arquivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_pdf_path = file_path
            self.pdf_path_var.set(file_path)
            self.process_pdf_background()
    
    def process_pdf_background(self):
        """Processa PDF em thread separada"""
        self.analyze_btn.config(state='disabled')
        self.progress.pack(pady=(0, 20))
        self.progress.start()
        
        self.pdf_status_var.set("🔄 Processando PDF e criando índices...")
        
        def process():
            try:
                self.vectorstore = self.rag_engine.process_pdf(self.current_pdf_path)
                self.root.after(0, self.on_pdf_processed)
            except Exception as e:
                self.root.after(0, lambda err=e: self.on_pdf_error(str(err)))
        
        threading.Thread(target=process, daemon=True).start()
    
    def on_pdf_processed(self):
        """Callback quando PDF é processado"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        self.pdf_status_var.set("✅ PDF processado e pronto para análise!")
    
    def on_pdf_error(self, error_msg):
        """Callback quando erro no processamento do PDF"""
        self.progress.stop()
        self.progress.pack_forget()
        self.pdf_status_var.set(f"❌ Erro: {error_msg[:50]}...")
        messagebox.showerror("Erro no PDF", error_msg)
    
    def analyze_document(self):
        """Executa análise do documento"""
        if not self.current_pdf_path or not self.vectorstore:
            messagebox.showwarning("Aviso", "Selecione um PDF válido primeiro!")
            return
        
        question = self.question_text.get("1.0", tk.END).strip()
        if not question or question == "Digite sua pergunta aqui...":
            messagebox.showwarning("Aviso", "Digite uma pergunta!")
            return
        
        # Limpa resposta anterior
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", "🔄 Processando sua pergunta...\n\nIsso pode levar alguns segundos...")
        
        # Desabilita botões durante análise
        self.analyze_btn.config(state='disabled')
        self.progress.pack(pady=(0, 20))
        self.progress.start()
        
        # Executa análise em thread
        def analyze():
            import time
            start_time = time.time()
            
            try:
                # 1. Define nível de resposta
                level_map = {
                    "concise": ResponseLevel.CONCISE,
                    "standard": ResponseLevel.STANDARD,
                    "complex": ResponseLevel.COMPLEX
                }
                level = level_map[self.response_level.get()]
                
                # 2. Detecta idioma e obtém prompt
                language, system_prompt = self.response_controller.process_question(question, level)
                
                # 3. Recupera contexto relevante via RAG
                context, metadata_list = self.rag_engine.retrieve_context(
                    self.vectorstore, question, k=5
                )
                
                # 4. Envia para IA
                response_text, token_info = self.ia_client.ask_question_with_context(
                    context=context,
                    question=question,
                    system_prompt=system_prompt,
                    metadata={'filename': Path(self.current_pdf_path).name}
                )
                
                # 5. Gera sugestões
                suggestions = self.ia_client.get_suggestions(
                    context=context,
                    metadata={'filename': Path(self.current_pdf_path).name},
                    language=language
                )
                
                # 6. Calcula custo
                cost = self.cost_calculator.calculate_cost(
                    token_info['input_tokens'],
                    token_info['output_tokens']
                )
                
                # 7. Formata resposta final
                result = {
                    "type": "text",
                    "text": response_text,
                    "source": Path(self.current_pdf_path).name,
                    "suggestions": suggestions,
                    "_metadata": {
                        "model": os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                        "input_tokens": token_info['input_tokens'],
                        "output_tokens": token_info['output_tokens'],
                        "cost_usd": cost,
                        "response_level": self.response_level.get(),
                        "language": language,
                        "chunks_used": len(metadata_list),
                        "time_seconds": round(time.time() - start_time, 2)
                    }
                }
                
                self.root.after(0, lambda: self.display_result(result, time.time() - start_time))
                
            except Exception as e:
                self.root.after(0, lambda: self.on_analysis_error(str(e)))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def display_result(self, result, elapsed_time):
        """Exibe resultado na interface"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        
        # Exibe texto formatado
        self.response_text.delete("1.0", tk.END)
        
        # Formatação básica de Markdown
        text = result['text']
        
        lines = text.split('\n')
        for line in lines:
            if line.startswith('## '):
                self.response_text.insert(tk.END, line[3:] + '\n', "heading")
            elif line.startswith('**') and line.endswith('**'):
                self.response_text.insert(tk.END, line[2:-2] + '\n', "bold")
            else:
                self.response_text.insert(tk.END, line + '\n')
        
        # Adiciona sugestões
        self.response_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.response_text.insert(tk.END, "💡 PERGUNTAS SUGERIDAS:\n\n", "bold")
        for i, suggestion in enumerate(result['suggestions'], 1):
            self.response_text.insert(tk.END, f"{i}. {suggestion}\n")
        
        # Atualiza informações
        metadata = result.get('_metadata', {})
        self.cost_label.config(text=f"💰 Custo: ${metadata.get('cost_usd', 0):.6f}")
        self.time_label.config(text=f"⏱️ Tempo: {elapsed_time:.1f}s")
        self.tokens_label.config(
            text=f"🔢 Tokens: {metadata.get('input_tokens', 0)} in / {metadata.get('output_tokens', 0)} out"
        )
        
        # Salva resultado em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"resultado_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        self.response_text.insert(tk.END, f"\n\n📁 Resultado salvo em: {output_file}")
    
    def on_analysis_error(self, error_msg):
        """Callback para erro na análise"""
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", f"❌ ERRO NA ANÁLISE:\n\n{error_msg}")
        messagebox.showerror("Erro", f"Falha na análise:\n{error_msg}")
    
    def copy_response(self):
        """Copia resposta para clipboard"""
        response = self.response_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(response)
        messagebox.showinfo("Sucesso", "Resposta copiada para a área de transferência!")


def main():
    """Ponto de entrada principal"""
    root = tk.Tk()
    app = DocumentAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()