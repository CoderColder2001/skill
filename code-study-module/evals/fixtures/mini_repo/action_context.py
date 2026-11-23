from dataclasses import dataclass, field


@dataclass
class ActionContext:
    storage_enabled: bool
    actions: dict = field(default_factory=dict)

    def bind(self, key, action):
        if not self.storage_enabled:
            return action
        self.actions[key] = action
        return {"action_ref": key}

    def materialize(self):
        return [
            {"id": key, "action": action}
            for key, action in sorted(self.actions.items())
        ]
