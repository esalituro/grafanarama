#!/usr/bin/env python3
"""Example: Create a dashboard with a text panel"""
import os
import sys

from grafanarama import DashboardObject, Spec
from grafanarama.core.dashboard import Panel, GridPos
from grafanarama.apiclient import GrafanaClient, print_grafana


def main():
    # Create a text panel
    text_panel = Panel(
        type="text",
        id=1,
        title="Welcome Panel",
        gridPos=GridPos(x=0, y=0, w=24, h=8),  # Full width, 8 rows high
        options={
            "mode": "markdown",  # Can be "markdown", "html", or "code"
            "content": """
# Welcome to Grafana!

This dashboard was created using the **grafanarama** Python API.

## Features:
- ✅ Programmatic dashboard creation
- ✅ Type-safe panel configuration
- ✅ Easy integration with Grafana

You can add more panels, configure data sources, and customize everything!
            """.strip()
        }
    )
    
    # Create dashboard with the text panel
    dashboard = DashboardObject(
        spec=Spec(
            title="My First Dashboard with Text Panel",
            schemaVersion=39,
            panels=[text_panel]
        )
    )
    
    print("Dashboard JSON:")
    print_grafana(dashboard)
    print()
    
    # Get authentication from environment variables
    api_key = os.getenv("GRAFANA_API_KEY")
    auth_user = os.getenv("GRAFANA_USER")
    auth_pass = os.getenv("GRAFANA_PASSWORD")
    
    if not api_key and not (auth_user and auth_pass):
        print("Error: Either GRAFANA_API_KEY or GRAFANA_USER/GRAFANA_PASSWORD must be set")
        print("  export GRAFANA_API_KEY='your_api_key'")
        print("  OR")
        print("  export GRAFANA_USER='admin'")
        print("  export GRAFANA_PASSWORD='admin'")
        return 1
    
    # Create client and send dashboard
    client = GrafanaClient(
        host=os.getenv("GRAFANA_HOST", "localhost"),
        port=int(os.getenv("GRAFANA_PORT", "3000")),
        apiKey=api_key,
        auth_user=auth_user,
        auth_pass=auth_pass,
    )
    
    result = client.send_dashboard(dashboard)
    if result:
        print(f"✓ Dashboard sent successfully!")
        print(f"  View it at: http://{client.server}/d/{dashboard.spec.uid or 'dashboard'}")
    else:
        print(f"✗ Failed to send dashboard. Check the error above.")
        if client.results:
            print(f"Status code: {client.results.status_code}")
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())

