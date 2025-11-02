"""
Gerenciador do arquivo data.json

© 2025 Matheus Marcelino Lopes
Todos os direitos reservados.

Projeto: Sistema Militar Gerador de Cartões de Veículos
GitHub: https://github.com/Matheus-Marcelino/Cadastro-de-Veiculos.git

Este software é protegido pela Lei de Software Brasileira (Lei nº 9.609/1998).
É proibida a cópia, redistribuição ou uso comercial sem autorização expressa do autor.
O uso não autorizado para fins comerciais constitui violação de direitos autorais e está sujeito a penalidades legais.
"""
from json import load, dump
from json.decoder import JSONDecodeError
from os.path import join
from getpass import getuser

class JsonManager:
    def __init__(self) -> None:
        self.__DIR_INFO = join("C:\\Users", getuser(), "Documents", "SMGCV Informações", "data.json")  

    def load_file(self) -> dict:
        try:
            with open(self.__DIR_INFO, encoding="utf-8") as f:
                obj_json: dict = load(f)
        except (FileNotFoundError, JSONDecodeError):
            with open(self.__DIR_INFO, "w+",encoding="utf-8") as file_error_json:
                RECOVER: dict = {"first_run": True,
                                 "contagem_carro": 1,
                                 "contagem_moto": 1}
                dump(RECOVER, file_error_json, indent=4)

        with open(self.__DIR_INFO, encoding="utf-8") as file_json:
            obj_json = load(file_json)
        return obj_json

    def insert(self, data: dict) -> None:
        data["contagem_carro"] = data["contagem_carro"]
        data["contagem_moto"] = data["contagem_moto"]

        with open(self.__DIR_INFO, "w+", encoding="utf-8") as f:
           dump(data, f, indent=4)