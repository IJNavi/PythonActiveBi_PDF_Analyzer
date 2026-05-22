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
import webbrowser
import os
import subprocess

from src.rag_engine import RAGEngine
from src.ia_client import IAClient
from src.response_controller import ResponseController, ResponseLevel
from src.cost_calculator import CostCalculator
from dotenv import load_dotenv

load_dotenv()

class ActiveBIStyle:
    PRIMARY_BLUE = "#0c0d64"
    SECONDARY_BLUE = "#1a3a5c"
    LIGHT_BLUE = "#2a4a7c"
    ORANGE = "#ff6b00"
    ORANGE_HOVER = "#ff8533"
    WHITE = "#ffffff"
    GRAY_LIGHT = "#e0e0e0"
    BG_LIGHT = "#f5f7fa"
    
    FONT_TITLE = ("Segoe UI", 16, "bold")
    FONT_SUBTITLE = ("Segoe UI", 12)
    FONT_BODY = ("Segoe UI", 10)
    FONT_BUTTON = ("Segoe UI", 10, "bold")
    FONT_HEADER = ("Segoe UI", 20, "bold")
    FONT_WELCOME = ("Segoe UI", 14)
    
    @classmethod
    def apply_styles(cls):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=cls.WHITE)
        style.configure('TLabel', background=cls.WHITE, foreground=cls.PRIMARY_BLUE)
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


def apply_hover(widget, normal_color, hover_color):
    """Aplica efeito hover a um botão."""
    def on_enter(e):
        widget.config(bg=hover_color)
    def on_leave(e):
        widget.config(bg=normal_color)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


class WelcomeScreen:
    def __init__(self, parent, on_complete):
        self.parent = parent
        self.on_complete = on_complete
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        top_bar = tk.Frame(self.frame, bg=ActiveBIStyle.PRIMARY_BLUE, height=80)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        logo_container = tk.Frame(top_bar, bg=ActiveBIStyle.PRIMARY_BLUE)
        logo_container.pack(expand=True, pady=10)
        self.load_logo(logo_container)

        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = tk.Label(main_container, text="Bem-vindo ao Analisador de Documentos com IA",
                               font=ActiveBIStyle.FONT_HEADER, fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.WHITE)
        title_label.pack(pady=(10, 5))
        subtitle_label = tk.Label(main_container, text="Active IA - Inteligência Adaptada ao seu Negócio",
                                  font=ActiveBIStyle.FONT_SUBTITLE, fg=ActiveBIStyle.SECONDARY_BLUE, bg=ActiveBIStyle.WHITE)
        subtitle_label.pack(pady=(0, 20))

        instructions_frame = tk.Frame(main_container, bg=ActiveBIStyle.BG_LIGHT, relief=tk.RIDGE, bd=1)
        instructions_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        inst_title = tk.Label(instructions_frame, text="📌 Como criar um atalho para facilitar o acesso:",
                              font=ActiveBIStyle.FONT_TITLE, fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.BG_LIGHT)
        inst_title.pack(pady=(15, 10), padx=20, anchor=tk.W)

        step1 = tk.Label(instructions_frame, text="1 Clique com o botão DIREITO do mouse no arquivo Iniciar.bat",
                         font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.BG_LIGHT)
        step1.pack(pady=3, padx=30, anchor=tk.W)
        step2 = tk.Label(instructions_frame, text="2 No menu que abrir, selecione 'Criar atalho'",
                         font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.BG_LIGHT)
        step2.pack(pady=3, padx=30, anchor=tk.W)
        step3 = tk.Label(instructions_frame, text="3 Arraste o atalho criado para a Área de Trabalho ou Menu Iniciar",
                         font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.BG_LIGHT)
        step3.pack(pady=3, padx=30, anchor=tk.W)

        tip_frame = tk.Frame(instructions_frame, bg=ActiveBIStyle.BG_LIGHT)
        tip_frame.pack(pady=(15, 15), padx=30, fill=tk.X)
        tip_icon = tk.Label(tip_frame, text="💡", font=("Segoe UI", 14), fg=ActiveBIStyle.ORANGE, bg=ActiveBIStyle.BG_LIGHT)
        tip_icon.pack(side=tk.LEFT, padx=(0, 10))
        tip_text = tk.Label(tip_frame, text="Dica: Você pode renomear o atalho para 'Active IA' e alterar o ícone nas propriedades!",
                            font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.SECONDARY_BLUE, bg=ActiveBIStyle.BG_LIGHT)
        tip_text.pack(side=tk.LEFT)

        self.skip_var = tk.BooleanVar(value=False)
        skip_check = tk.Checkbutton(main_container, text="Não mostrar esta tela novamente", variable=self.skip_var,
                                    font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.WHITE,
                                    selectcolor=ActiveBIStyle.WHITE, activebackground=ActiveBIStyle.WHITE)
        skip_check.pack(pady=(10, 5))

        understood_btn = tk.Button(main_container, text="ENTENDIDO, VAMOS COMEÇAR →",
                                   font=ActiveBIStyle.FONT_BUTTON, bg=ActiveBIStyle.ORANGE, fg=ActiveBIStyle.WHITE,
                                   bd=0, padx=25, pady=10, cursor="hand2", command=self.on_complete)
        apply_hover(understood_btn, ActiveBIStyle.ORANGE, ActiveBIStyle.ORANGE_HOVER)
        understood_btn.pack(pady=15)

        footer = tk.Label(main_container, text="© 2024 Active BI - Consultoria Especializada em BI",
                          font=("Segoe UI", 8), fg=ActiveBIStyle.GRAY_LIGHT, bg=ActiveBIStyle.WHITE)
        footer.pack(pady=(10, 0))

    def load_logo(self, container):
        try:
            local_path = Path(__file__).parent / "src" / "LogoActiveBI.PNG"
            if local_path.exists():
                img = Image.open(local_path)
                img.thumbnail((200, 80), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                logo_label = tk.Label(container, image=self.logo_img, bg=ActiveBIStyle.PRIMARY_BLUE)
                logo_label.pack(pady=(5, 5))
            else:
                raise FileNotFoundError
        except Exception:
            text_logo = tk.Label(container, text="ACTIVE BI", font=("Segoe UI", 24, "bold"),
                                 fg=ActiveBIStyle.WHITE, bg=ActiveBIStyle.PRIMARY_BLUE)
            text_logo.pack(pady=(5, 0))
            sub_logo = tk.Label(container, text="BUSINESS INTELLIGENCE", font=("Segoe UI", 10),
                                fg=ActiveBIStyle.WHITE, bg=ActiveBIStyle.PRIMARY_BLUE)
            sub_logo.pack(pady=(0, 5))


class HeaderFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(height=80, bg=ActiveBIStyle.PRIMARY_BLUE)
        self.pack(fill=tk.X, pady=(0, 10))
        self.create_widgets()

    def create_widgets(self):
        container = tk.Frame(self, bg=ActiveBIStyle.PRIMARY_BLUE)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.load_logo(container)

        analyze_btn = self._create_nav_button(container, "ANALISAR", self.controller.show_analysis_screen)
        analyze_btn.pack(side=tk.LEFT, padx=(10, 5))

        cache_btn = self._create_nav_button(container, "CACHE", self.controller.open_cache_folder)
        cache_btn.pack(side=tk.LEFT, padx=5)

        history_btn = self._create_nav_button(container, "ANÁLISES", self.controller.show_history_screen)
        history_btn.pack(side=tk.LEFT, padx=5)

        contact_btn = self._create_nav_button(container, "CONTATO", self.open_contact, is_contact=True)
        contact_btn.pack(side=tk.RIGHT)

    def _create_nav_button(self, parent, text, command, is_contact=False):
        bg_color = ActiveBIStyle.ORANGE if is_contact else ActiveBIStyle.PRIMARY_BLUE
        hover_color = ActiveBIStyle.ORANGE_HOVER if is_contact else ActiveBIStyle.LIGHT_BLUE
        btn = tk.Button(parent, text=text, font=ActiveBIStyle.FONT_BUTTON,
                        bg=bg_color, fg=ActiveBIStyle.WHITE, bd=0, padx=15, pady=8,
                        cursor="hand2", command=command)
        apply_hover(btn, bg_color, hover_color)
        return btn

    def load_logo(self, container):
        try:
            local_path = Path(__file__).parent / "src" / "LogoActiveBI.PNG"
            if local_path.exists():
                img = Image.open(local_path)
                img.thumbnail((150, 50), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                logo_label = tk.Label(container, image=self.logo_img, bg=ActiveBIStyle.PRIMARY_BLUE)
                logo_label.pack(side=tk.LEFT)
            else:
                raise FileNotFoundError
        except Exception:
            logo_text = tk.Label(container, text="ACTIVE BI", font=("Segoe UI", 16, "bold"),
                                 fg=ActiveBIStyle.WHITE, bg=ActiveBIStyle.PRIMARY_BLUE)
            logo_text.pack(side=tk.LEFT)

    def open_contact(self):
        webbrowser.open("https://www.activebi.com.br/fale-conosco")


class AnalysisScreen(tk.Frame):
    def __init__(self, controller, parent):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.current_pdf_path = None
        self.vectorstore = None
        self.processing = False  # Evita múltiplas análises simultâneas
        self.create_widgets()

    def create_widgets(self):
        container = tk.Frame(self, bg=ActiveBIStyle.WHITE)
        container.pack(fill=tk.BOTH, expand=True)

        main_canvas = tk.Canvas(container, bg=ActiveBIStyle.WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=main_canvas.yview)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollable_frame = ttk.Frame(main_canvas)
        canvas_window = main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def resize_content(event):
            canvas_width = event.width
            content_width = min(900, canvas_width - 40)
            x_position = max((canvas_width - content_width) // 2, 0)
            main_canvas.coords(canvas_window, x_position, 0)
            main_canvas.itemconfig(canvas_window, width=content_width)
        main_canvas.bind("<Configure>", resize_content)

        self.scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

        # MouseWheel apenas no canvas (não global)
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        main_canvas.bind("<MouseWheel>", on_mousewheel)

        main_frame = ttk.Frame(self.scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=60, pady=20)

        # Seção PDF
        pdf_frame = tk.LabelFrame(main_frame, text=" 📄 Documento PDF ",
                                  font=ActiveBIStyle.FONT_TITLE, fg=ActiveBIStyle.PRIMARY_BLUE,
                                  bg=ActiveBIStyle.WHITE, bd=2, relief=tk.RIDGE)
        pdf_frame.pack(fill=tk.X, pady=(0, 20))

        pdf_inner = tk.Frame(pdf_frame, bg=ActiveBIStyle.WHITE)
        pdf_inner.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(pdf_inner, text="Arquivo:", font=ActiveBIStyle.FONT_BODY,
                 fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.WHITE).pack(side=tk.LEFT, padx=(0, 10))
        self.pdf_path_var = tk.StringVar()
        pdf_entry = tk.Entry(pdf_inner, textvariable=self.pdf_path_var, font=ActiveBIStyle.FONT_BODY,
                             bg=ActiveBIStyle.BG_LIGHT, fg=ActiveBIStyle.PRIMARY_BLUE, relief=tk.SUNKEN,
                             state='readonly', width=60)
        pdf_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        select_btn = tk.Button(pdf_inner, text="📂 SELECIONAR", font=ActiveBIStyle.FONT_BUTTON,
                               bg=ActiveBIStyle.PRIMARY_BLUE, fg=ActiveBIStyle.WHITE, bd=0,
                               padx=15, pady=5, cursor="hand2", command=self.select_pdf)
        apply_hover(select_btn, ActiveBIStyle.PRIMARY_BLUE, ActiveBIStyle.LIGHT_BLUE)
        select_btn.pack(side=tk.RIGHT)

        self.pdf_status_var = tk.StringVar(value="⚠️ Nenhum PDF carregado")
        status_label = tk.Label(pdf_frame, textvariable=self.pdf_status_var, font=("Segoe UI", 9),
                                fg=ActiveBIStyle.SECONDARY_BLUE, bg=ActiveBIStyle.WHITE)
        status_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Seção Pergunta
        question_frame = tk.LabelFrame(main_frame, text=" ❓ Sua Pergunta ",
                                       font=ActiveBIStyle.FONT_TITLE, fg=ActiveBIStyle.PRIMARY_BLUE,
                                       bg=ActiveBIStyle.WHITE, bd=2, relief=tk.RIDGE)
        question_frame.pack(fill=tk.X, pady=(0, 20))
        question_inner = tk.Frame(question_frame, bg=ActiveBIStyle.WHITE)
        question_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.question_text = scrolledtext.ScrolledText(question_inner, height=5, wrap=tk.WORD,
                                                       font=("Segoe UI", 10), bg=ActiveBIStyle.BG_LIGHT,
                                                       fg=ActiveBIStyle.PRIMARY_BLUE, relief=tk.SUNKEN, bd=1)
        self.question_text.pack(fill=tk.BOTH, expand=True)
        self.question_text.insert("1.0", "Digite sua pergunta aqui...")
        self.question_text.bind("<FocusIn>", self.clear_placeholder)
        self.question_text.bind("<FocusOut>", self.add_placeholder)

        # Configurações
        config_frame = tk.LabelFrame(main_frame, text=" ⚙️ Configurações da Resposta ",
                                     font=ActiveBIStyle.FONT_TITLE, fg=ActiveBIStyle.PRIMARY_BLUE,
                                     bg=ActiveBIStyle.WHITE, bd=2, relief=tk.RIDGE)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        config_inner = tk.Frame(config_frame, bg=ActiveBIStyle.WHITE)
        config_inner.pack(fill=tk.X, padx=15, pady=15)
        tk.Label(config_inner, text="Nível de Detalhamento:", font=ActiveBIStyle.FONT_BODY,
                 fg=ActiveBIStyle.PRIMARY_BLUE, bg=ActiveBIStyle.WHITE).pack(side=tk.LEFT, padx=(0, 20))
        self.response_level = tk.StringVar(value="standard")
        concise_rb = tk.Radiobutton(config_inner, text="📝 Conciso (2 parágrafos)", variable=self.response_level,
                                    value="concise", font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.PRIMARY_BLUE,
                                    bg=ActiveBIStyle.WHITE, selectcolor=ActiveBIStyle.WHITE, activebackground=ActiveBIStyle.WHITE)
        concise_rb.pack(side=tk.LEFT, padx=(0, 20))
        standard_rb = tk.Radiobutton(config_inner, text="📊 Padrão (1 página A4)", variable=self.response_level,
                                     value="standard", font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.PRIMARY_BLUE,
                                     bg=ActiveBIStyle.WHITE, selectcolor=ActiveBIStyle.WHITE, activebackground=ActiveBIStyle.WHITE)
        standard_rb.pack(side=tk.LEFT, padx=(0, 20))
        complex_rb = tk.Radiobutton(config_inner, text="🔬 Complexo (Análise profunda)", variable=self.response_level,
                                    value="complex", font=ActiveBIStyle.FONT_BODY, fg=ActiveBIStyle.PRIMARY_BLUE,
                                    bg=ActiveBIStyle.WHITE, selectcolor=ActiveBIStyle.WHITE, activebackground=ActiveBIStyle.WHITE)
        complex_rb.pack(side=tk.LEFT)

        # Botão Analisar
        self.analyze_btn = tk.Button(main_frame, text="🔍 ANALISAR DOCUMENTO", font=("Segoe UI", 12, "bold"),
                                     bg=ActiveBIStyle.ORANGE, fg=ActiveBIStyle.WHITE, bd=0, padx=40, pady=12,
                                     cursor="hand2", state='disabled', command=self.analyze_document)
        apply_hover(self.analyze_btn, ActiveBIStyle.ORANGE, ActiveBIStyle.ORANGE_HOVER)
        self.analyze_btn.pack(pady=(0, 20))

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=500)

        # Resposta
        response_frame = tk.LabelFrame(main_frame, text=" 📊 Resposta da IA ",
                                       font=ActiveBIStyle.FONT_TITLE, fg=ActiveBIStyle.PRIMARY_BLUE,
                                       bg=ActiveBIStyle.WHITE, bd=2, relief=tk.RIDGE)
        response_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        response_inner = tk.Frame(response_frame, bg=ActiveBIStyle.WHITE)
        response_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.response_text = scrolledtext.ScrolledText(response_inner, wrap=tk.WORD, font=("Consolas", 10),
                                                       bg=ActiveBIStyle.BG_LIGHT, fg=ActiveBIStyle.PRIMARY_BLUE,
                                                       relief=tk.SUNKEN, bd=1, height=12)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        self.response_text.tag_config("heading", font=("Consolas", 12, "bold"), foreground=ActiveBIStyle.ORANGE)
        self.response_text.tag_config("bold", font=("Consolas", 10, "bold"))

        # Rodapé
        info_frame = tk.Frame(main_frame, bg=ActiveBIStyle.WHITE)
        info_frame.pack(fill=tk.X)
        self.cost_label = tk.Label(info_frame, text="💰 Custo: -", font=("Segoe UI", 9),
                                   fg="green", bg=ActiveBIStyle.WHITE)
        self.cost_label.pack(side=tk.LEFT, padx=(0, 20))
        self.time_label = tk.Label(info_frame, text="⏱️ Tempo: -", font=("Segoe UI", 9),
                                   fg=ActiveBIStyle.ORANGE, bg=ActiveBIStyle.WHITE)
        self.time_label.pack(side=tk.LEFT, padx=(0, 20))
        self.tokens_label = tk.Label(info_frame, text="🔢 Tokens: -", font=("Segoe UI", 9),
                                     fg=ActiveBIStyle.SECONDARY_BLUE, bg=ActiveBIStyle.WHITE)
        self.tokens_label.pack(side=tk.LEFT)
        copy_btn = tk.Button(info_frame, text="📋 Copiar Resposta", font=ActiveBIStyle.FONT_BUTTON,
                             bg=ActiveBIStyle.PRIMARY_BLUE, fg=ActiveBIStyle.WHITE, bd=0, padx=15, pady=3,
                             cursor="hand2", command=self.copy_response)
        apply_hover(copy_btn, ActiveBIStyle.PRIMARY_BLUE, ActiveBIStyle.LIGHT_BLUE)
        copy_btn.pack(side=tk.RIGHT)

    def clear_placeholder(self, event):
        if self.question_text.get("1.0", tk.END).strip() == "Digite sua pergunta aqui...":
            self.question_text.delete("1.0", tk.END)
    def add_placeholder(self, event):
        if not self.question_text.get("1.0", tk.END).strip():
            self.question_text.insert("1.0", "Digite sua pergunta aqui...")

    def select_pdf(self):
        file_path = filedialog.askopenfilename(title="Selecione um arquivo PDF",
                                               filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if file_path:
            self.current_pdf_path = file_path
            self.pdf_path_var.set(file_path)
            self.process_pdf_background()

    def process_pdf_background(self):
        if self.controller.rag_engine is None:
            self.on_pdf_error("Motor RAG não inicializado. Verifique a configuração.")
            return
        self.analyze_btn.config(state='disabled')
        self.progress.pack(pady=(0, 20))
        self.progress.start()
        self.pdf_status_var.set("🔄 Processando PDF e criando índices...")
        def process():
            try:
                self.vectorstore = self.controller.rag_engine.process_pdf(self.current_pdf_path)
                if self.winfo_exists():
                    self.controller.root.after(0, self.on_pdf_processed)
            except Exception as e:
                if self.winfo_exists():
                    self.controller.root.after(0, lambda err=e: self.on_pdf_error(str(err)))
        threading.Thread(target=process, daemon=True).start()

    def on_pdf_processed(self):
        if not self.winfo_exists():
            return
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        self.pdf_status_var.set("✅ PDF processado e pronto para análise!")

    def on_pdf_error(self, error_msg):
        if not self.winfo_exists():
            return
        self.progress.stop()
        self.progress.pack_forget()
        self.pdf_status_var.set(f"❌ Erro: {error_msg[:50]}...")
        messagebox.showerror("Erro no PDF", error_msg)

    def analyze_document(self):
        if self.processing:
            messagebox.showinfo("Aguarde", "Uma análise já está em andamento.")
            return
        if not self.current_pdf_path or not self.vectorstore:
            messagebox.showwarning("Aviso", "Selecione um PDF válido primeiro!")
            return
        question = self.question_text.get("1.0", tk.END).strip()
        if not question or question == "Digite sua pergunta aqui...":
            messagebox.showwarning("Aviso", "Digite uma pergunta!")
            return
        self.processing = True
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", "🔄 Processando sua pergunta...\n\nIsso pode levar alguns segundos...")
        self.analyze_btn.config(state='disabled')
        self.progress.pack(pady=(0, 20))
        self.progress.start()
        def analyze():
            import time
            start_time = time.time()
            try:
                level_map = {"concise": ResponseLevel.CONCISE, "standard": ResponseLevel.STANDARD, "complex": ResponseLevel.COMPLEX}
                level = level_map[self.response_level.get()]
                language, system_prompt = self.controller.response_controller.process_question(question, level)
                context, metadata_list = self.controller.rag_engine.retrieve_context(self.vectorstore, question, k=5)
                response_text, token_info = self.controller.ia_client.ask_question_with_context(
                    context=context, question=question, system_prompt=system_prompt,
                    metadata={'filename': Path(self.current_pdf_path).name}
                )
                suggestions = self.controller.ia_client.get_suggestions(
                    context=context, metadata={'filename': Path(self.current_pdf_path).name}, language=language
                )
                cost = self.controller.cost_calculator.calculate_cost(token_info['input_tokens'], token_info['output_tokens'])
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
                if self.winfo_exists():
                    self.controller.root.after(0, lambda: self.display_result(result, time.time() - start_time))
            except Exception as e:
                if self.winfo_exists():
                    self.controller.root.after(0, lambda: self.on_analysis_error(str(e)))
            finally:
                self.processing = False
        threading.Thread(target=analyze, daemon=True).start()

    def display_result(self, result, elapsed_time):
        if not self.winfo_exists():
            return
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        self.response_text.delete("1.0", tk.END)
        text = result['text']
        for line in text.split('\n'):
            if line.startswith('## '):
                self.response_text.insert(tk.END, line[3:] + '\n', "heading")
            elif line.startswith('**') and line.endswith('**'):
                self.response_text.insert(tk.END, line[2:-2] + '\n', "bold")
            else:
                self.response_text.insert(tk.END, line + '\n')
        self.response_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.response_text.insert(tk.END, "💡 PERGUNTAS SUGERIDAS:\n\n", "bold")
        for i, sug in enumerate(result['suggestions'], 1):
            self.response_text.insert(tk.END, f"{i}. {sug}\n")
        metadata = result.get('_metadata', {})
        self.cost_label.config(text=f"💰 Custo: ${metadata.get('cost_usd', 0):.6f}")
        self.time_label.config(text=f"⏱️ Tempo: {elapsed_time:.1f}s")
        self.tokens_label.config(text=f"🔢 Tokens: {metadata.get('input_tokens', 0)} in / {metadata.get('output_tokens', 0)} out")

        # Salvar JSON e criar LEIA_ME.txt
        pdf_filename = result['source']
        import re
        safe_pdf_name = re.sub(r'[<>:"/\\|?*]', '_', pdf_filename).strip().replace(' ', '_')
        if len(safe_pdf_name) > 80:
            safe_pdf_name = safe_pdf_name[:80]
        base_dir = Path(__file__).parent / "resultados"
        data_str = datetime.now().strftime("%Y-%m-%d")
        hora_str = datetime.now().strftime("%H")
        resultados_dir = base_dir / data_str / hora_str / safe_pdf_name
        resultados_dir.mkdir(parents=True, exist_ok=True)

        readme_file = base_dir / "LEIA_ME.txt"
        if not readme_file.exists():
            readme_content = """ESTRUTURA DA PASTA DE RESULTADOS

Esta pasta armazena os arquivos JSON gerados pelas análises de documentos.

Organização:
- resultados/YYYY-MM-DD/HH/Nome_Do_PDF/resultado_HHMMSS.json

Exemplo:
- resultados/2025-05-21/22/relatorio_financeiro.pdf/resultado_223045.json

Onde:
- YYYY-MM-DD: ano-mês-dia da consulta
- HH: hora da consulta (00 a 23)
- Nome_Do_PDF: nome do arquivo original (caracteres especiais e espaços substituídos por _)
- resultado_HHMMSS.json: arquivo com a resposta da IA no formato JSON

Você pode copiar, editar ou deletar esses arquivos manualmente.
Deletar um arquivo não afeta o funcionamento do programa, apenas remove o histórico.
"""
            with open(readme_file, "w", encoding="utf-8-sig") as f:
                f.write(readme_content)

        timestamp = datetime.now().strftime("%H%M%S")
        output_file = resultados_dir / f"resultado_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        self.response_text.insert(tk.END, f"\n\n📁 Resultado salvo em: {output_file}")

    def on_analysis_error(self, error_msg):
        if not self.winfo_exists():
            return
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state='normal')
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", f"❌ ERRO NA ANÁLISE:\n\n{error_msg}")
        messagebox.showerror("Erro", f"Falha na análise:\n{error_msg}")

    def copy_response(self):
        # Copia apenas o texto da resposta (sem sugestões, sem cabeçalho, sem caminho de arquivo)
        full_text = self.response_text.get("1.0", tk.END)
        # Tentar extrair apenas a parte antes do separador "="
        if "💡 PERGUNTAS SUGERIDAS" in full_text:
            answer_part = full_text.split("💡 PERGUNTAS SUGERIDAS")[0].strip()
        else:
            answer_part = full_text
        # Remover cabeçalho extra se existir (ex: "📁 Resultado salvo em")
        if "📁 Resultado salvo em:" in answer_part:
            answer_part = answer_part.split("📁 Resultado salvo em:")[0].strip()
        self.controller.root.clipboard_clear()
        self.controller.root.clipboard_append(answer_part)
        messagebox.showinfo("Sucesso", "Resposta copiada para a área de transferência (apenas o conteúdo da IA).")


class HistoryScreen(tk.Frame):
    def __init__(self, controller, parent):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.current_json_path = None
        self.create_widgets()
        self.load_results_tree()

    def create_widgets(self):
        top_frame = tk.Frame(self, bg=ActiveBIStyle.WHITE)
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        self.copy_btn = tk.Button(top_frame, text="COPIAR", command=self.copy_json,
                                  font=ActiveBIStyle.FONT_BUTTON, bg=ActiveBIStyle.PRIMARY_BLUE,
                                  fg=ActiveBIStyle.WHITE, padx=15, pady=5, state='disabled')
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 20))
        self.delete_btn = tk.Button(top_frame, text="DELETAR", command=self.confirm_delete,
                                    font=ActiveBIStyle.FONT_BUTTON, bg=ActiveBIStyle.ORANGE,
                                    fg=ActiveBIStyle.WHITE, padx=15, pady=5, state='disabled')
        self.delete_btn.pack(side=tk.LEFT)

        tree_frame = tk.Frame(self, bg=ActiveBIStyle.WHITE)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20,10), pady=10)
        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        content_frame = tk.Frame(self, bg=ActiveBIStyle.WHITE)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10,20), pady=10)
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, font=("Consolas", 10),
                                                      bg=ActiveBIStyle.BG_LIGHT, fg=ActiveBIStyle.PRIMARY_BLUE,
                                                      relief=tk.SUNKEN, bd=1)
        self.content_text.pack(fill=tk.BOTH, expand=True)

    def load_results_tree(self):
        base_dir = Path(__file__).parent / "resultados"
        self.tree.delete(*self.tree.get_children())
        if not base_dir.exists():
            self.tree.insert("", "end", text="Nenhum resultado encontrado", values=("",))
            return
        root_node = self.tree.insert("", "end", text="Resultados", open=True)
        for year_dir in sorted(base_dir.iterdir()):
            if year_dir.is_dir():
                year_node = self.tree.insert(root_node, "end", text=year_dir.name, open=True)
                for hour_dir in sorted(year_dir.iterdir()):
                    if hour_dir.is_dir():
                        hour_node = self.tree.insert(year_node, "end", text=hour_dir.name, open=True)
                        for pdf_dir in sorted(hour_dir.iterdir()):
                            if pdf_dir.is_dir():
                                pdf_node = self.tree.insert(hour_node, "end", text=pdf_dir.name, open=False)
                                for json_file in sorted(pdf_dir.glob("*.json")):
                                    self.tree.insert(pdf_node, "end", text=json_file.name, values=(str(json_file),))
        self.tree.column("#0", width=300)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, 'values')
        if values:
            self.current_json_path = Path(values[0])
            try:
                with open(self.current_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, json.dumps(data, indent=2, ensure_ascii=False))
                self.copy_btn.config(state='normal')
                self.delete_btn.config(state='normal')
            except Exception:
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, "Erro ao ler arquivo JSON")
                self.copy_btn.config(state='disabled')
                self.delete_btn.config(state='disabled')
        else:
            self.current_json_path = None
            self.content_text.delete(1.0, tk.END)
            self.copy_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')

    def copy_json(self):
        if self.current_json_path:
            try:
                with open(self.current_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.parent.clipboard_clear()
                self.parent.clipboard_append(json.dumps(data, indent=2, ensure_ascii=False))
                messagebox.showinfo("Copiado", "Conteúdo JSON copiado para a área de transferência.")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível copiar: {str(e)}")

    def confirm_delete(self):
        if not self.current_json_path:
            return
        pdf_folder = self.current_json_path.parent.name
        json_name = self.current_json_path.name
        msg = f"Quer mesmo deletar o arquivo {json_name} da pasta {pdf_folder}?"
        popup = tk.Toplevel(self)
        popup.title("Confirmar exclusão")
        popup.geometry("400x150")
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 75
        popup.geometry(f"+{x}+{y}")
        popup.transient(self.parent)
        popup.grab_set()
        tk.Label(popup, text=msg, wraplength=350).pack(pady=20)
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)
        sim_btn = tk.Button(btn_frame, text="SIM", command=lambda: self.delete_file(popup), bg="red", fg="white", padx=20)
        sim_btn.pack(side=tk.LEFT, padx=20)
        nao_btn = tk.Button(btn_frame, text="NÃO", command=popup.destroy, padx=20)
        nao_btn.pack(side=tk.LEFT, padx=20)

    def delete_file(self, popup):
        try:
            self.current_json_path.unlink()
            pdf_folder = self.current_json_path.parent
            if not any(pdf_folder.iterdir()):
                pdf_folder.rmdir()
            hour_folder = pdf_folder.parent
            if not any(hour_folder.iterdir()):
                hour_folder.rmdir()
            data_folder = hour_folder.parent
            if not any(data_folder.iterdir()):
                data_folder.rmdir()
            popup.destroy()
            self.load_results_tree()
            self.content_text.delete(1.0, tk.END)
            self.copy_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível deletar: {str(e)}")
            popup.destroy()


class DocumentAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Active IA - Analisador de Documentos")
        self.root.geometry("1000x750")
        self.root.configure(bg=ActiveBIStyle.WHITE)

        self.rag_engine = None
        self.ia_client = None
        self.response_controller = None
        self.cost_calculator = None
        self.header = None
        self.current_frame = None

        self.init_components()

        skip_file = Path(__file__).parent / ".skip_welcome"
        if skip_file.exists():
            self.show_analysis_screen()
        else:
            self.show_welcome_screen()

    def init_components(self):
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                messagebox.showerror("Erro", "OPENAI_API_KEY não encontrada!\n\nCrie um arquivo .env na raiz do projeto com:\nOPENAI_API_KEY=sua_chave_aqui")
                self.root.quit()
                return
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            self.ia_client = IAClient(api_key, model)  # IAClient deve ter timeout configurado
            self.rag_engine = RAGEngine()
            self.response_controller = ResponseController()
            self.cost_calculator = CostCalculator(model)
            ActiveBIStyle.apply_styles()
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", str(e))
            self.root.quit()

    def show_welcome_screen(self):
        self.clear_main_area()
        self.welcome_screen = WelcomeScreen(self.root, self.on_welcome_complete)

    def on_welcome_complete(self):
        if hasattr(self.welcome_screen, 'skip_var') and self.welcome_screen.skip_var.get():
            skip_file = Path(__file__).parent / ".skip_welcome"
            skip_file.touch()
        self.welcome_screen.frame.destroy()
        self.show_analysis_screen()

    def clear_main_area(self):
        if hasattr(self, 'header') and self.header is not None:
            self.header.destroy()
            self.header = None
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None
        # Remove quaisquer outros frames órfãos
        for child in list(self.root.winfo_children()):
            if isinstance(child, (tk.Frame, ttk.Frame)) and child not in (self.header, self.current_frame):
                child.destroy()

    def show_analysis_screen(self):
        self.clear_main_area()
        self.header = HeaderFrame(self.root, self)
        self.current_frame = AnalysisScreen(self, self.root)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_history_screen(self):
        self.clear_main_area()
        self.header = HeaderFrame(self.root, self)
        self.current_frame = HistoryScreen(self, self.root)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def open_cache_folder(self):
        cache_path = Path(__file__).parent / "rag_cache"
        if cache_path.exists():
            subprocess.Popen(["explorer", str(cache_path)])  # safer
        else:
            messagebox.showinfo("Info", "A pasta de cache ainda não existe. Processe um PDF primeiro.")


def main():
    root = tk.Tk()
    app = DocumentAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()