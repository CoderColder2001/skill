def build_buttons(context, request):
    return {
        "open": context.bind("open", {"type": "navigate", "url": request["url"]}),
        "dismiss": context.bind("dismiss", {"type": "close"}),
    }


def build_banner(context, request):
    if not request.get("banner_enabled", False):
        return None
    return {
        "tap": context.bind(
            "open", {"type": "navigate", "url": request["banner_url"]}
        )
    }
