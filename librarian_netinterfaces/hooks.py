from .dashboard_plugin import NetInterfacesDashboardPlugin


def initialize(supervisor):
    supervisor.exts.dashboard.register(NetInterfacesDashboardPlugin)
