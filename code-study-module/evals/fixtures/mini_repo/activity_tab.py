class ActivityTab:
    def __init__(self, provider):
        self.provider = provider

    def render(self):
        if self.provider is None:
            return None
        return self.provider()

    def detach(self):
        self.provider = None


class HostPage:
    def __init__(self, session_state):
        self.state = session_state
        self.tab = None

    def attach(self):
        tenant_at_attach = self.state.tenant
        self.tab = ActivityTab(
            lambda: {"tenant": tenant_at_attach, "theme": self.state.theme}
        )

    def close(self):
        if self.tab is not None:
            self.tab.detach()
            self.tab = None
