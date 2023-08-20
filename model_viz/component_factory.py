import dash_bootstrap_components as dbc
from typing import List
from abc import ABC, abstractmethod


class DashComponentFactory(ABC):
    """
    Base class for Dash component factories
    """

    component_id: str = None  # Almost all Dash components have an id

    def __init__(self, component_id: str):
        self.component_id = component_id

    @abstractmethod
    def generate_component(self):
        raise NotImplementedError


class DashTab(DashComponentFactory):
    label: str = None

    def __init__(self, label: str, component_id: str):
        super().__init__(component_id)
        self.label = label

    def generate_component(self) -> dbc.Tab:
        return dbc.Tab(label=self.label, tab_id=self.component_id)

    def __str__(self):
        return f"DashTab(label={self.label}, component_id={self.component_id})"


class DashTabs(DashComponentFactory):
    tabs: List[DashTab] = None
    tab_ids: List[str] = None

    def __init__(self, component_id: str, tabs: List[DashTab]):
        super().__init__(component_id)
        self.tabs = tabs
        self.tab_ids = [tab.component_id for tab in tabs]

    def generate_component(self) -> dbc.Tabs:
        return dbc.Tabs(
            [tab.generate_component() for tab in self.tabs],
            id=self.component_id,
            active_tab=self.tab_ids[0],
        )

    def __str__(self):
        return f"DashTabs(tabs={self.tabs}, id={self.component_id})"
