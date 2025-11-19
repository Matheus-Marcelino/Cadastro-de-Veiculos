"""
Criador do Qr Code

© 2025 Matheus Marcelino Lopes
Todos os direitos reservados.

Projeto: Sistema Militar Interno Gerador de Cartões de Veículos
GitHub: https://github.com/Matheus-Marcelino/Cadastro-de-Veiculos.git

Este software é protegido pela Lei de Software Brasileira (Lei nº 9.609/1998).
É proibida a cópia, redistribuição ou uso comercial sem autorização expressa do autor.
O uso não autorizado para fins comerciais constitui violação de direitos autorais e está sujeito a penalidades legais.
"""

from qrcode.main import QRCode
from os.path import join
from getpass import getuser


def Creat_Qr(text, name):
    """Cria o Qr Code

    Args:
        text (str): Texto que será inserido do Qr Code
        view (bool): True -> mostra a imagem na tela
                     False -> Não mostra a imagem na tela

    Returns:
        str: Caminho do arquivo
    """
    treated_text = name.replace('/', ' ')
    treated_text = treated_text.replace('\\', ' ') + '.png'

    qr = QRCode()
    qr.add_data(text)

    FILE: str = join("C:\\Users", getuser(), "Documents", "SMGCV Informações")

    qr_img = qr.make_image()

    qr_img.save(f'{FILE}\\{treated_text}')