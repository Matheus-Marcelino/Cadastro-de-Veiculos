"""
Gerenciador do arquivo data.json

© 2025 Matheus Marcelino Lopes
Todos os direitos reservados.

Projeto: Sistema Militar Interno Gerador de Cartões de Veículos
GitHub: https://github.com/Matheus-Marcelino/Cadastro-de-Veiculos.git

Este software é protegido pela Lei de Software Brasileira (Lei nº 9.609/1998).
É proibida a cópia, redistribuição ou uso comercial sem autorização expressa do autor.
O uso não autorizado para fins comerciais constitui violação de direitos autorais e está sujeito a penalidades legais.
"""

from json import load, dump
from json.decoder import JSONDecodeError
from os.path import join, exists
from getpass import getuser

class JsonManager:
    def __init__(self) -> None:
        self.__DIR_INFO = join("C:\\Users", getuser(), "Documents", "SMGCV Informações", "data.json")
        self._data: dict | None = None

    def load_file(self, force_reload: bool = False) -> dict:
        """Carrega o JSON em memória. Se já carregado, retorna o mesmo objeto."""
        if self._data is not None and not force_reload:
            return self._data

        if not exists(self.__DIR_INFO):
            self._create_default_file()

        try:
            with open(self.__DIR_INFO, encoding="utf-8") as f:
                self._data = load(f)
        except JSONDecodeError:
            # Corrige arquivo corrompido
            self._create_default_file()
            with open(self.__DIR_INFO, encoding="utf-8") as f:
                self._data = load(f)

        return self._data

    def insert(self, data: dict) -> None:
        """Atualiza a memória e salva no disco."""
        if self._data is None:
            self.load_file()
        self._data.update(data)
        with open(self.__DIR_INFO, "w", encoding="utf-8") as f:
            dump(self._data, f, indent=4)

    def _create_default_file(self) -> None:
        """Cria um arquivo JSON com valores padrão."""
        default_data = {
            "ultima_exibicao_copyright": "",
            "first_run": True,
            "contagem_carro": 1,
            "contagem_moto": 1
        }
        with open(self.__DIR_INFO, "w", encoding="utf-8") as f:
            dump(default_data, f, indent=4)
        self._data = default_data