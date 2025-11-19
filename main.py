"""
Gera a interface do sistema de cadastro de veículos

© 2025 Matheus Marcelino Lopes
Todos os direitos reservados.

Projeto: Sistema Militar Interno Gerador de Cartões de Veículos
GitHub: https://github.com/Matheus-Marcelino/Cadastro-de-Veiculos.git

Este software é protegido pela Lei de Software Brasileira (Lei nº 9.609/1998).
É proibida a cópia, redistribuição ou uso comercial sem autorização expressa do autor.
O uso não autorizado para fins comerciais constitui violação de direitos autorais e está sujeito a penalidades legais.
"""

import sys
from os import makedirs, remove, environ
from os.path import dirname, abspath, join, basename, exists, splitext
from platform import system
if system() == "Windows":
    environ["KIVY_GL_BACKEND"] = "angle_sdl2"

from getpass import getuser
from shutil import move
from datetime import datetime, timedelta
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'window_icon', '')
Config.set('modules', 'winfiledrop', '')

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.screenmanager import SlideTransition
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6, A7, landscape
from pypdf import PdfReader, PdfWriter
from json_manager import JsonManager
from generator_qr import Creat_Qr


class Application(MDApp):
    title = "Sistema Militar Interno Gerador de Cartões de Veículos"
    icon = StringProperty("")
    wallpaper = StringProperty("")
    current_file = StringProperty("")  # caminho do arquivo atualmente anexado do anexo de arquivos (na memória fisica)

    def build(self):
        __FILE_PROPERTIES = Builder.load_file('properties.kv')
        self.__ID = __FILE_PROPERTIES.ids
        self.__data = JsonManager()

        self._setup_window()
        self._executable_assistant()
        self._setup_bindings()
        self._setup_menus()

        return __FILE_PROPERTIES

    # -=-=-=-=-=-=- Funções Principais do Programa -=-=-=-=-=-=-
    # -- Ao iniciar --
    def on_start(self) -> None:
        """
        Função chamada no início da execução do app.
        Configura telas, cria pastas e checa primeira execução para copyright 
        """

        # Define transição entre telas
        self.root.transition = SlideTransition(duration=0.3, direction="left")

        # Cria diretórios necessários
        makedirs(self.__DIR_DOC, exist_ok=True)
        makedirs(join(self.__DIR_DOC,"pdfs"), exist_ok=True)
        for sub in ["carro", "moto"]:
            makedirs(join(self.__DIR_DOC,"cartoes", sub), exist_ok=True)

        # -------------------------------------------------------------------------------
        archive = self.__data.load_file(True)
        ultima_exibicao = "" if archive["ultima_exibicao_copyright"] == "" else datetime.fromisoformat(archive['ultima_exibicao_copyright'])
        # Carrega dados do JSON para checar se é primeira execução para o copyright
        if archive["first_run"]:
            archive["first_run"] = False
            archive["ultima_exibicao_copyright"] = datetime.now().isoformat()
            self.__ID.screen_manager.current = "copyright"
            Clock.schedule_once(self._go_to_main_screen, 10)  # 10 segundos de copyright
            self.__data.insert(archive)

        # Mostra o copyright uma vez por mês
        elif datetime.now() - ultima_exibicao >= timedelta(days=30):
            archive["ultima_exibicao_copyright"] = datetime.now().isoformat()
            self.__ID.screen_manager.current = "copyright"
            Clock.schedule_once(self._go_to_main_screen, 10)
            self.__data.insert(archive)

    # --- Função para criar PDF com informações do cadastro ---
    def create_pdf(self) -> None:
        """Cria PDF com dados da pessoa e veículo"""
        valid_pdf = self._validate_pdf_attachment()
        valid_text = self._validate_text_fields(1)

        if valid_pdf and valid_text:
            # Nome do arquivo PDF
            pdf_nome = f"Documento do(a) {self.__ID.PG.text} {self.__ID.nomeGuerra.text}.pdf"
            c = canvas.Canvas(pdf_nome, pagesize=A6)
            _, altura = A6
            c.setFont("Times-Bold", 9)

            # Captura informações para inserir no PDF
            pg = str(self.__ID.PG.text)
            nome = str(self.__ID.nomeCompleto.text)
            nome_de_guerra = str(self.__ID.nomeGuerra.text)
            modelo = str(self.__ID.marca.text)
            placa = str(self.__ID.placa.text)
            cor = str(self.__ID.cor.text)
            su = str(self.__ID.SU.text)

            # Inserção de imagens e textos no PDF
            c.drawImage(join(self.__DIR_MAIN,"images","Imagem do documento de informações da empresa.png"), 73, altura - 150, width=150, height=135)
            c.drawString(10, altura - 190, f"P/G: {pg}")
            c.drawString(10, altura - 220, f"Nome Completo: {nome.strip().title()}")
            c.drawString(10, altura - 250, f"Nome de Guerra: {nome_de_guerra.strip().title()}")
            c.drawString(10, altura - 280, f"Modelo: {modelo.strip()}")
            c.drawString(10, altura - 310, f"placa: {placa.strip().upper()}")
            c.drawString(10, altura - 340, f"Cor: {cor.strip().capitalize()}")
            c.drawString(10, altura - 370, f"SU: {su}")

            c.showPage()
            c.save()
            move(join(self.__DIR_MAIN, pdf_nome),join(self.__DIR_DOC,"pdfs", pdf_nome))

            # -- Adiciona um pdf em anexo no pdf que será criado acima -- 
            try:
                # Abre o PDF principal e o PDF anexado
                main_pdf = PdfReader(join(self.__DIR_DOC,"pdfs",pdf_nome))
                anexado_pdf = PdfReader(self.current_file)

                # Novo escritor para o PDF combinado
                writer = PdfWriter()

                # Adiciona as páginas do PDF principal
                for page in main_pdf.pages:
                    writer.add_page(page)

                # Adiciona as páginas do PDF anexado (dropzone)
                for page in anexado_pdf.pages:
                    writer.add_page(page)

                # Sobrescreve o arquivo final com o combinado
                with open(join(self.__DIR_DOC,"pdfs",pdf_nome), "wb") as f:
                    writer.write(f)
                self.__ID.create_pdf_btn.md_bg_color = "green"
                self.__ID.create_pdf_btn.text = "Criar PDF\n(Sucesso)"
                self._restore_button(self.__ID.create_pdf_btn, "Criar PDF", "#2196f3", 4)
            except Exception as e:
                print(f"[ERRO] Falha ao combinar PDFs: {e}")
                self.__ID.dropzone_card.md_bg_color = (0.5, 0, 0, 1)
                self.__ID.drop_label.text = "Houve algum problema ao combinar os PDFs"
                self.__ID.create_pdf_btn.md_bg_color = "red"
                self.__ID.create_pdf_btn.text = "Criar PDF\n(Falha)"
            self._clear_field((self.__ID.PG, self.__ID.nomeCompleto, self.__ID.nomeGuerra,self.__ID.marca,
                                self.__ID.placa, self.__ID.cor, self.__ID.SU))
        else:
            self.__ID.create_pdf_btn.md_bg_color = (0.5, 0, 0, 1)
            self.__ID.create_pdf_btn.text = "Criar PDF\n(Falha)"

    # --- Função para gerar cartão com QR code ---
    def generate_card(self) -> None:
        """Cria cartão de veículo com QR code e número de controle"""

        if self._validate_text_fields(2):
            self.__ID.btn_card_creator.md_bg_color = "green"
            self.__ID.btn_card_creator.text = "Gerar cartão\n(Sucesso)"
            archive = self.__data.load_file(True)

            # Cria QR code temporário
            Creat_Qr(self.__ID.textQr.text, f"{self.__ID.nomeArquivo.text}") # -- Cria um Qr code --

            # Nome do aquivo PDF
            pdf_nome = f"cartao do(a) {str(self.__ID.nomeArquivo.text).capitalize()}.pdf"
            pdf_temp = join(self.__DIR_DOC, pdf_nome)

            # -- Criação do cartão de carro --
            if self.__ID.veiculo.text == "Carro":
                c = canvas.Canvas(pdf_temp, pagesize=A6)

                largura, altura = A6
                c.setFont("Times-Bold", 50)

                # Retângulo vermelho de rodapé
                altura_rodape = 20
                c.setFillColor(colors.red)
                c.setStrokeColor(colors.red)
                c.rect(x=0, y=0, width=largura, height=altura_rodape, fill=1, stroke=0)

                # Linha vermelha acima do rodapé
                c.setLineWidth(5)
                c.line(0, 28, largura, 28)

                c.setFillColor(colors.black)
                # Inserção de imagens e número de controle
                c.drawImage(join(self.__DIR_MAIN,"images","logo da empresa no cartão.jpg"), 75, altura - 150, width=150, height=130)
                c.drawImage(join(self.__DIR_DOC,f"{self.__ID.nomeArquivo.text}.png."), 80, altura - 330, width=140, height=140)
                c.drawString(115, altura - 370, f"{str(archive['contagem_carro']).zfill(3)}")

                c.showPage()
                c.save()
                move(f"{pdf_temp}", join(self.__DIR_DOC,"cartoes","carro",pdf_nome))

                # Atualiza contador de carros
                archive["contagem_carro"] += 1
                self.__data.insert(archive)
                
            # --- Cartão para Moto ---
            elif self.__ID.veiculo.text == "Moto":
                c = canvas.Canvas(pdf_temp, pagesize=landscape(A7))

                largura, altura = A7
                c.setFont("Times-Bold", 60) 

                # Retângulo vermelho de rodapé
                altura_rodape = 20
                c.setFillColor(colors.red)
                c.setStrokeColor(colors.red)
                c.rect(0, 0, landscape(A7)[0], 10, fill=1, stroke=0)

                # Linha vermelha acima do rodapé
                c.setLineWidth(3)
                c.line(0, 15, landscape(A7)[0], 15)

                c.setFillColor(colors.black)
                # Inserção de imagens e número de controle
                c.drawImage(join(self.__DIR_MAIN,"images","logo da empresa no cartão.jpg"), -7, altura - 180, width=100, height=90)
                c.drawImage(join(self.__DIR_DOC,f"{self.__ID.nomeArquivo.text}.png."), 80, altura - 280 , width=140, height=120)
                c.drawString(200, altura - 150, f"{str(archive['contagem_moto']).zfill(3)}")

                c.showPage()
                c.save()
                move(f"{pdf_temp}", join(self.__DIR_DOC,"cartoes","moto",pdf_nome))

                # Atualiza contador de motos
                archive["contagem_moto"] += 1
                self.__data.insert(archive)

            self._restore_button(self.__ID.btn_card_creator, "Gerar cartão", "#2196f3", 4)

            try:
                # Remove o Qrcode
                remove(join(self.__DIR_DOC,f"{self.__ID.nomeArquivo.text}.png"))
            except FileNotFoundError:
                self.__data.load_file()
            except PermissionError:
                print(f"[ERRO] Não foi possível remover o arquivo {join(self.__DIR_DOC, self.__ID.nomeArquivo.text + '.png')}")
            except Exception as e:
                print(f"[ERRO inesperado] {e}")

            self._clear_field((self.__ID.veiculo, self.__ID.nomeArquivo, self.__ID.textQr))

        else:
            self.__ID.btn_card_creator.md_bg_color = (0.5, 0, 0, 1)
            self.__ID.btn_card_creator.text = "Gerar cartão\n(Falha)"

    # -=-=-=-=-=-=- FUNÇÕES AUXILIARES E CONFIGURAÇÕES PRINCIPAIS DA TELA -=-=-=-=-=-=-
    # -- Configurações que são feitas dentro do Build e funções auxiliares --

    # -- Configurações do Window --
    def _setup_window(self) -> None:
        """Configurações da tela"""        
        Window.size = (800, 700)
        Window.minimum_width, Window.minimum_height = 700, 600
        self.theme_cls.theme_style = 'Dark'

        # Definindo o caminho absoluto do icone e wallpaper
        self.icon = self._resource_path(join("images","ICONE DO WINDOW"))
        self.wallpaper = self._resource_path(join("images", "camuflado.png"))

    def _executable_assistant(self) -> None: 
        """Definições de arquivos/pastas importantes
        """
        # Define diretório principal dependendo se está rodando como exe ou script
        if getattr(sys, 'frozen', False): 
            self.__DIR_MAIN = sys._MEIPASS if hasattr(sys, '_MEIPASS') else dirname(sys.executable)
        else:
            self.__DIR_MAIN = dirname(abspath(__file__))
        # Define diretório de armazenamento dos dados do usuário
        self.__DIR_DOC = join("C:\\Users", getuser(), "Documents", "SMGCV Informações")

    def _setup_bindings(self) -> None:
        # Bind do evento de redimensionamento
        Window.bind(on_resize=self._limit_window_size)

        # faz o bind do evento on_dropfile para aceitar arquivos arrastados do sistema operacional e soltos dentro da janela
        Window.bind(on_dropfile=self._on_file_drop)


        # Pega todos os campos e adiciona o evento de foco
        for campo in reversed(self.__ID.fields_box.children):
            if hasattr(campo, "focus"):
                campo.bind(focus=self.scroll_ate_campo)

        # --- Faz o bind de foco de cada campo ao respectivo menu ---
        self.__ID.PG.bind(focus=lambda campo, focus: self._close_menu_when_lose_focus(focus, self.menu_pg))
        self.__ID.SU.bind(focus=lambda campo, focus: self._close_menu_when_lose_focus(focus, self.menu_su))
        self.__ID.veiculo.bind(focus=lambda campo, focus: self._close_menu_when_lose_focus(focus, self.menu_veiculo))

    def _resource_path(self, relative) -> str:
        """
        Resolve path absoluto seguro para recursos internos da aplicação, funcionando tanto em
        desenvolvimento (.py) quanto em versões empacotadas (.exe) via cx_Freeze. Garante que 
        arquivos como imagens, ícones e KV sejam acessados corretamente independente do local 
        onde o programa esteja instalado.
        """

        if getattr(sys, "frozen", False):
            base_path = dirname(sys.executable)
        else:
            base_path = dirname(abspath(__file__))
        return join(base_path, relative)

    def _limit_window_size(self, window, width, height) -> None:
        """Define tamanho máximo da janela"""
        MAX_WIDTH = 882
        MAX_HEIGHT = 829
        if width > MAX_WIDTH:
            width = MAX_WIDTH
        if height > MAX_HEIGHT:
            height = MAX_HEIGHT
        Window.size = (width, height)

    # -- Decodifica o arquivo para uma string --
    def _decode_path(self, file_path_bytes: bytes) -> str:
        """Decodifica com segurança bytes de um arquivo solto em um caminho de string."""
        if isinstance(file_path_bytes, bytes):
            for enc in ("utf-8", "latin-1"):
                try:
                    return file_path_bytes.decode(enc)
                except Exception:
                    continue
            # fallback repr
            return str(file_path_bytes)
        return str(file_path_bytes)

    def _on_file_drop(self, window, file_path_bytes) -> None:
        """
        Chamado pelo Kivy quando um arquivo é colocado na janela.
        Aceita o arquivo somente se o mouse estiver sobre o widget da zona de lançamento.
        Comportamento: mantém apenas o arquivo mais recente (substitui o anterior).
        """
        print("cheguei1")
        path = self._decode_path(file_path_bytes)
        # obter a posição atual do mouse (x, y) nas coordenadas da janela (origem canto inferior esquerdo)
        x, y = Window.mouse_pos

        # tenta encontrar o widget dropzone
        dz = None
        try:
            dz = self.__ID.get("dropzone_card")
        except Exception:
            dz = None

        if not dz:
            return

        # collide_point espera coordenadas relativas às coordenadas pai do widget, 
        # mas Window.mouse_pos está nas coordenadas da janela. collide_point funciona com coordenadas de janela.
        if dz.collide_point(x, y):
            self.current_file = path
            try:
                self.filename = basename(path)
                # A label está dentro do cartão; pode estar acessível como rótulo dz.ids.drop
                if hasattr(dz, "ids") and "drop_label" in dz.ids:
                    dz.ids.drop_label.text = f"Anexo:\n{self.filename}"
                else:
                    # fallback: tenta pelo root.ids
                    if "drop_label" in self.__ID:
                        self.__ID.drop_label.text = f"Anexo:\n{self.filename}"
            except Exception:
                print("Erro ao atualizar label do dropzone")
                return
        else:
            print("arquivo foi arrastado para fora")
            return

    # -- Validadores -- 
    def _validate_text_fields(self, Window: int) -> bool:
        match Window:
            case 1:
                campos = [
                    self.__ID.PG,
                    self.__ID.nomeCompleto,
                    self.__ID.nomeGuerra,
                    self.__ID.marca,
                    self.__ID.placa,
                    self.__ID.cor,
                    self.__ID.SU,
                ]

                # Validação dos campos para não permitir vazios
                valid = True

                for campo in campos:
                    if not str(campo.text).strip():
                        campo.error = True
                        campo.helper_text = "A caixa de texto não pode estar vazia"
                        valid = False
                        continue

                    campo.error = False
                    campo.helper_text = ""
                return valid

            case  2:
                campos = [
                self.__ID.nomeArquivo,
                self.__ID.veiculo,
                self.__ID.textQr
                ]

                # Validação dos campos para não permitir vazios
                valid = True 
                for campo in campos:
                    if not str(campo.text).strip():
                        campo.error = True
                        campo.helper_text = "A caixa de texto não pode estar vazia"
                        valid = False
                    else:
                        campo.error = False
                        campo.helper_text = ""
                return valid

    def _validate_pdf_attachment(self) -> bool:
        if not (hasattr(self, "current_file") and self.current_file and exists(self.current_file)):
            self.__ID.dropzone_card.md_bg_color = (1, 0, 0, 0.3)
            self.__ID.drop_label.text = "Nenhum arquivo PDF anexado"
            return False

        if not str(splitext(self.filename)[-1].lower()) == ".pdf":
            self.__ID.dropzone_card.md_bg_color = (1, 0, 0, 0.3)
            self.__ID.drop_label.text = "O arquivo inserido precisa ser um PDF"
            return False

        self.__ID.dropzone_card.md_bg_color = (0,0,0,0.5)
        self.__ID.drop_label.text = f"Anexo:\n{self.filename}"
        return True

    # --  Função do MDScrollView-- 
    def scroll_ate_campo(self, campo, focus) -> None:
        """Faz o scroll descer quando o campo ganha foco."""
        if focus:
            scroll = self.__ID.Scroll_field
            # método interno do ScrollView que rola até o widget
            scroll.scroll_to(campo, padding=20, animate=True)

    # -- Função para sair do copyright
    def _go_to_main_screen(self, *args) -> None:
        """Função para trocar para tela de cadastro"""
        self.__ID.screen_manager.current = "cadastro"

    # -- Função para restaura o botão --
    def _restore_button(self, buttonId, text, color, time) -> None:
        def restore(*args):
            buttonId.md_bg_color = color
            buttonId.text = text

        # agenda a restauração
        Clock.schedule_once(restore, time)

    # -- função para limpar os Fields --
    def _clear_field(self, fields_id: tuple) -> None:
        for field in fields_id:
            field.text = ""

    # -- Funções dos Menus -- 
    def _setup_menus(self) -> None:
        # --- Menu Posto/Graduação ---
        menu_items_pg = [
            {"text": "Soldado", "on_release": lambda x="Soldado": self._set_item_pg(x)},
            {"text": "Cabo", "on_release": lambda x="Cabo": self._set_item_pg(x)},
            {"text": "3° Sargento", "on_release": lambda x="3° Sargento": self._set_item_pg(x)},
            {"text": "2° Sargento", "on_release": lambda x="2° Sargento": self._set_item_pg(x)},
            {"text": "1° Sargento", "on_release": lambda x="1° Sargento": self._set_item_pg(x)},
            {"text": "Sub Tenente", "on_release": lambda x="Sub Tenente": self._set_item_pg(x)},
            {"text": "Aspirante", "on_release": lambda x="Aspirante": self._set_item_pg(x)},
            {"text": "2° Tenente", "on_release": lambda x="2° Tenente": self._set_item_pg(x)},
            {"text": "1° Tenente", "on_release": lambda x="1° Tenente": self._set_item_pg(x)},
            {"text": "Capitão", "on_release": lambda x="Capitão": self._set_item_pg(x)},
            {"text": "Major", "on_release": lambda x="Major": self._set_item_pg(x)},
            {"text": "Tenente Coronel", "on_release": lambda x="Tenente Coronel": self._set_item_pg(x)},
            {"text": "Coronel", "on_release": lambda x="Coronel": self._set_item_pg(x)},
            {"text": "General de Brigada", "on_release": lambda x="General de Brigada": self._set_item_pg(x)},
            {"text": "General de Divisão", "on_release": lambda x="General de Divisão": self._set_item_pg(x)},
            {"text": "General de Exército", "on_release": lambda x="General de Exército": self._set_item_pg(x)},
        ]
        # Criação do dropdown menu para PG
        self.menu_pg = MDDropdownMenu(
            caller=self.__ID.PG,
            items=menu_items_pg,
            width_mult=3,
        )

        # --- Menu Subunidade ---
        menu_items_su = [
            {"text": "1° Esqd", "on_release": lambda x="1° Esqd": self._set_item_su(x)},
            {"text": "3° Esqd", "on_release": lambda x="3° Esqd": self._set_item_su(x)},    
            {"text": "C/Ap", "on_release": lambda x="C/Ap": self._set_item_su(x)},
            {"text": "Base Adm", "on_release": lambda x="Base Adm": self._set_item_su(x)}
        ]
        # Criação do dropdown menu para SU
        self.menu_su = MDDropdownMenu(
            caller=self.__ID.SU,
            items=menu_items_su,
            width_mult=3,
        )

        # --- Menu Tipo de Veículo ---
        menu_items_veiculo = [
            {"text": "Carro", "on_release": lambda x="Carro": self._set_item_veiculo(x)},
            {"text": "Moto", "on_release": lambda x="Moto": self._set_item_veiculo(x)},    
        ]
        # Criação do dropdown menu para Veículo
        self.menu_veiculo = MDDropdownMenu(
            caller=self.__ID.veiculo,
            items=menu_items_veiculo,
            width_mult=3,
        )

    def _set_item_su(self, text_item) -> None:
        """Seleciona subunidade no dropdown"""
        self.__ID.SU.text = text_item
        self.menu_su.dismiss()

    def _set_item_pg(self, text_item) -> None:
        """Seleciona PG no dropdown"""
        self.__ID.PG.text = text_item
        self.menu_pg.dismiss()

    def _set_item_veiculo(self, text_item) -> None:
        """Seleciona tipo de veículo no dropdown"""
        self.__ID.veiculo.text = text_item
        self.menu_veiculo.dismiss()

    def _close_menu_when_lose_focus(self, focus, menu) -> None:
        """Fecha o menu quando o campo perde o foco (Tab ou clique fora)."""
        if not focus and menu:
            menu.dismiss()


def Main():
    Application().run()


# permite que o módulo exporte main()
__all__ = ["Main"]

if __name__ == "__main__":
    Main()
