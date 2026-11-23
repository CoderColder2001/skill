from dataclasses import dataclass


@dataclass
class SessionState:
    tenant: str
    theme: str


class Session:
    def __init__(self, tenant, theme):
        self.state = SessionState(tenant, theme)

    def open_page(self):
        from activity_tab import HostPage

        page = HostPage(self.state)
        page.attach()
        return page

    def update_theme(self, theme):
        self.state.theme = theme
