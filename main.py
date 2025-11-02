"""
Gera a interface do sistema de cadastro de veículos

© 2025 Matheus Marcelino Lopes
Todos os direitos reservados.

Projeto: Sistema Militar Gerador de Cartões de Veículos
GitHub: https://github.com/Matheus-Marcelino/Cadastro-de-Veiculos.git

Este software é protegido pela Lei de Software Brasileira (Lei nº 9.609/1998).
É proibida a cópia, redistribuição ou uso comercial sem autorização expressa do autor.
O uso não autorizado para fins comerciais constitui violação de direitos autorais e está sujeito a penalidades legais.
"""

from kivymd.app import MDApp
from kivymd.app import Builder
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import SlideTransition
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6, A7, landscape
from os import makedirs, remove
from os.path import dirname, abspath, join
from getpass import getuser
from shutil import move
from generator_qr import Creat_Qr
from json_manager import JsonManager
import sys


class Application(MDApp):
    title = "Sistema Militar Gerador de Cartões de Veículos"
    icon = "images\\15rcmecicon.png"

    def build(self):
        # Define o tamanho mínimo da janela e o tema
        Window.minimum_width, Window.minimum_height = 700, 600
        self.theme_cls.theme_style = 'Dark'

        self.__FILE_PROPERTIES = Builder.load_file('properties.kv')
        self.__ID = self.__FILE_PROPERTIES.ids

        # Define diretório principal dependendo se está rodando como exe ou script
        if getattr(sys, 'frozen', False): 
            self.__DIR_MAIN = sys._MEIPASS if hasattr(sys, '_MEIPASS') else dirname(sys.executable)
        else:
            self.__DIR_MAIN = dirname(abspath(__file__))

        # Define diretório de armazenamento dos dados do usuário
        self.__DIR_INFO = join("C:\\Users", getuser(), "Documents", "SMGCV Informações")

        self.__JSON = JsonManager()

        # --- Menu Posto/Graduação ---
        menu_items_pg = [
            {"text": "Soldado", "on_release": lambda x="Soldado": self.set_item_pg(x)},
            {"text": "Cabo", "on_release": lambda x="Cabo": self.set_item_pg(x)},
            {"text": "3° Sargento", "on_release": lambda x="3° Sargento": self.set_item_pg(x)},
            {"text": "2° Sargento", "on_release": lambda x="2° Sargento": self.set_item_pg(x)},
            {"text": "1° Sargento", "on_release": lambda x="1° Sargento": self.set_item_pg(x)},
            {"text": "Sub Tenente", "on_release": lambda x="Sub Tenente": self.set_item_pg(x)},
            {"text": "Aspirante", "on_release": lambda x="Aspirante": self.set_item_pg(x)},
            {"text": "2° Tenente", "on_release": lambda x="2° Tenente": self.set_item_pg(x)},
            {"text": "1° Tenente", "on_release": lambda x="1° Tenente": self.set_item_pg(x)},
            {"text": "Capitão", "on_release": lambda x="Capitão": self.set_item_pg(x)},
            {"text": "Major", "on_release": lambda x="Major": self.set_item_pg(x)},
            {"text": "Tenente Coronel", "on_release": lambda x="Tenente Coronel": self.set_item_pg(x)},
            {"text": "Coronel", "on_release": lambda x="Coronel": self.set_item_pg(x)},
            {"text": "General de Brigada", "on_release": lambda x="General de Brigada": self.set_item_pg(x)},
            {"text": "General de Divisão", "on_release": lambda x="General de Divisão": self.set_item_pg(x)},
            {"text": "General de Exército", "on_release": lambda x="General de Exército": self.set_item_pg(x)},
        ]
        # Criação do dropdown menu para PG
        self.menu_pg = MDDropdownMenu(
            caller=self.__ID.PG,
            items=menu_items_pg,
            width_mult=3,
        )

        # --- Menu Subunidade ---
        menu_items_su = [
            {"text": "1° Esqd", "on_release": lambda x="1° Esqd": self.set_item_su(x)},
            {"text": "3° Esqd", "on_release": lambda x="3° Esqd": self.set_item_su(x)},    
            {"text": "C/Ap", "on_release": lambda x="C/Ap": self.set_item_su(x)},
            {"text": "Base Adm", "on_release": lambda x="Base Adm": self.set_item_su(x)}
        ]
        # Criação do dropdown menu para SU
        self.menu_su = MDDropdownMenu(
            caller=self.__ID.SU,
            items=menu_items_su,
            width_mult=3,
        )

        # --- Menu Tipo de Veículo ---
        menu_items_veiculo = [
            {"text": "Carro", "on_release": lambda x="Carro": self.set_item_veiculo(x)},
            {"text": "Moto", "on_release": lambda x="Moto": self.set_item_veiculo(x)},    
        ]
        # Criação do dropdown menu para Veículo
        self.menu_veiculo = MDDropdownMenu(
            caller=self.__ID.veiculo,
            items=menu_items_veiculo,
            width_mult=3,
        )

        return self.__FILE_PROPERTIES

    def on_start(self):
        """
        Função chamada no início da execução do app.
        Configura telas, cria pastas e checa primeira execução para copyright 
        """
        # Define transição entre telas
        self.root.transition = SlideTransition(duration=0.3, direction="left")

        # Cria diretórios necessários
        makedirs(self.__DIR_INFO, exist_ok=True)
        makedirs(f"{self.__DIR_INFO}\\pdfs", exist_ok=True)
        for sub in ["carro", "moto"]:
            makedirs(f"{self.__DIR_INFO}\\cartoes\\{sub}", exist_ok=True)

        # Carrega dados do JSON para checar se é primeira execução para o copyright
        self._data = self.__JSON.load_file()
        if self._data["first_run"]:
            self._data["first_run"] = False
            self.__FILE_PROPERTIES.current = "copyright"
            Clock.schedule_once(self._go_to_main_screen, 10)  # 3 segundos de copyright
            self.__JSON.insert(self._data)
        else:
            self.__FILE_PROPERTIES.current = "cadastro"

    def _go_to_main_screen(self, *args):
        """Função para trocar para tela de cadastro"""
        self.__FILE_PROPERTIES.current = "cadastro"

    # --- Funções dos menus ---
    def set_item_su(self, text_item):
        """Seleciona subunidade no dropdown"""
        self.__ID.SU.text = text_item
        self.menu_su.dismiss()

    def set_item_pg(self, text_item):
        """Seleciona PG no dropdown"""
        self.__ID.PG.text = text_item
        self.menu_pg.dismiss()

    def set_item_veiculo(self, text_item):
        """Seleciona tipo de veículo no dropdown"""
        self.__ID.veiculo.text = text_item
        self.menu_veiculo.dismiss()

    # --- Função para criar PDF com informações do cadastro ---
    def creat_pdf(self):
        """Cria PDF com dados da pessoa e veículo"""
        campos = [
            self.__ID.PG,
            self.__ID.nomeCompleto,
            self.__ID.nomeGuerra,
            self.__ID.marca,
            self.__ID.placa,
            self.__ID.cor,
            self.__ID.SU
        ]

        # Validação dos campos para não permitir vazios
        validation = True 
        for campo in campos:
            if not str(campo.text).strip():
                campo.error = True
                campo.helper_text = "A caixa de texto não pode estar vazia"
                validation = False
            else:
                campo.error = False
                campo.helper_text = ""
                
        if validation:
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
            c.drawImage(f'{self.__DIR_MAIN}\\images\\15rcmec.jpg', 73, altura - 150, width=150, height=135)
            c.drawString(10, altura - 190, f"P/G: {pg}")
            c.drawString(10, altura - 220, f"Nome Completo: {nome.strip().title()}")
            c.drawString(10, altura - 250, f"Nome de Guerra: {nome_de_guerra.strip().title()}")
            c.drawString(10, altura - 280, f"Modelo: {modelo.strip()}")
            c.drawString(10, altura - 310, f"placa: {placa.strip().upper()}")
            c.drawString(10, altura - 340, f"Cor: {cor.strip().capitalize()}")
            c.drawString(10, altura - 370, f"SU: {su}")

            c.showPage()
            c.save()
            move(f"{self.__DIR_MAIN}\\{pdf_nome}",f"{self.__DIR_INFO}\\pdfs\\{pdf_nome}" )

    # --- Função para gerar cartão com QR code ---
    def generate_card(self) -> None:
        """Cria cartão de veículo com QR code e número de controle"""

        campos = [
            self.__ID.nomeArquivo,
            self.__ID.veiculo,
            self.__ID.textQr
        ]

        # Validação dos campos para não permitir vazios
        validation = True 
        for campo in campos:
            if not str(campo.text).strip():
                campo.error = True
                campo.helper_text = "A caixa de texto não pode estar vazia"
                validation = False
            else:
                campo.error = False
                campo.helper_text = ""

        if validation:
            self._data =  self.__JSON.load_file()

            # Cria QR code temporário
            Creat_Qr(self.__ID.textQr.text, False, f"{self.__ID.nomeArquivo.text}") # -- Cria um Qr code --

            # Nome do aquivo PDF
            pdf_nome = f"cartao do(a) {str(self.__ID.nomeArquivo.text).capitalize()}.pdf"
            pdf_temp = join(self.__DIR_INFO, pdf_nome)

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
                c.drawImage(f"{self.__DIR_MAIN}\\images\\15rcmec.jpg", 75, altura - 150, width=150, height=130)
                c.drawImage(f"{self.__DIR_INFO}\\{self.__ID.nomeArquivo.text}.png.", 80, altura - 330, width=140, height=140)
                c.drawString(115, altura - 370, f"{str(self._data['contagem_carro']).zfill(3)}")

                c.showPage()
                c.save()
                move(f"{pdf_temp}", f"{self.__DIR_INFO}\\cartoes\\carro\\{pdf_nome}" )

                # Atualiza contador de carros
                self._data["contagem_carro"] += 1
                self.__JSON.insert(self._data)

            # --- Cartão para Moto ---
            else:
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
                c.drawImage(f"{self.__DIR_MAIN}\\images\\15rcmec.jpg", -7, altura - 180, width=100, height=90)
                c.drawImage(f"{self.__DIR_INFO}\\{self.__ID.nomeArquivo.text}.png.", 80, altura - 280 , width=140, height=120)
                c.drawString(200, altura - 150, f"{str(self._data['contagem_moto']).zfill(3)}")

                c.showPage()
                c.save()
                move(f"{pdf_temp}", f"{self.__DIR_INFO}\\cartoes\\moto\\{pdf_nome}" )

                # Atualiza contador de motos
                self._data["contagem_moto"] += 1
                self.__JSON.insert(self._data)

            # Remove o Qrcode
            remove(f"{self.__DIR_INFO}\\{self.__ID.nomeArquivo.text}.png")


if __name__ == "__main__":
    Application().run()
