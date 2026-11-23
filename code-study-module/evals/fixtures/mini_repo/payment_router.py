"""A local routing example; providers are identifiers, not real integrations."""


def route_payment(country, wallet_enabled, forced_provider=None):
    if forced_provider is not None:
        if forced_provider not in {"card", "wallet"}:
            raise ValueError("unknown provider")
        return forced_provider
    if country == "CN" and wallet_enabled:
        return "wallet"
    return "card"


def checkout(request):
    if request["amount"] <= 0:
        raise ValueError("amount must be positive")
    provider = route_payment(
        request["country"],
        request.get("wallet_enabled", False),
        request.get("forced_provider"),
    )
    return {"provider": provider, "amount": request["amount"]}
