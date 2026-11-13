class WBClient:
    """Заглушка клиента Wildberries API. Реальные вызовы — позже."""

    def __init__(self, token: str):
        self.token = token

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