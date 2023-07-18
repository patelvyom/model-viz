import dash_bootstrap_components as dbc
from typing import List


class DashComponentFactory:
    """
    Base class for Dash component factories
    """

    component_id: str = None  # Almost all Dash components have an id

    def __init__(self, component_id: str):
        self.component_id = component_id

    def generate_component(self):
        raise NotImplementedError


class DashTab(DashComponentFactory):
    label: str = None

    def __init__(self, label: str, component_id: str = ""):
        super().__init__(component_id)
        self.label = label
        if self.component_id == "":
            self.component_id = self._generate_tab_id()

    def _generate_tab_id(self) -> str:
        return self.label.lower().replace(" ", "_")

    def generate_component(self):
        return dbc.Tab(label=self.label, tab_id=self.component_id)

    def __str__(self):
        return f"DashTab(label={self.label}, component_id={self.component_id})"


class DashTabs(DashComponentFactory):
    tabs: List[DashTab] = None

    def __init__(self, component_id, tabs: List[DashTab]):
        super().__init__(component_id)
        self.tabs = tabs

    def generate_component(self):
        return dbc.Tabs(
            [tab.generate_component() for tab in self.tabs],
            id=self.component_id,
            active_tab=self.tabs[0].component_id,
        )

    def __str__(self):
        return f"DashTabs(tabs={self.tabs}, id={self.component_id})"
