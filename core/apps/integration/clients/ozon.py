class OzonClient:
    """Заглушка клиента Ozon Seller API.

    Реальные HTTP-вызовы будут добавлены позже, когда появится токен.
    Пока все методы возвращают пустые списки и пишут в лог.
    """

    def __init__(self, client_id: str, api_key: str):
        self.client_id = client_id
        self.api_key = api_key

    def fetch_orders(self) -> list[dict]:
        return []

    def fetch_stocks(self) -> list[dict]:
        return []

    def fetch_prices(self) -> list[dict]:
        return []

    def fetch_promotions(self) -> list[dict]:
        return []

    def fetch_finances(self) -> list[dict]:
        return []