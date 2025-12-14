#!/usr/bin/env python3
"""Simple example: Create a dashboard with a text panel"""
import os
import sys

from grafanarama import DashboardObject, Spec
from grafanarama.core.dashboard import Panel, GridPos
from grafanarama.apiclient import GrafanaClient


def main():
    # Create a simple text panel with markdown content
    text_panel = Panel(
        type="text",
        id=1,
        title="Hello from Python!",
        gridPos=GridPos(x=0, y=0, w=24, h=8),  # Full width (24 columns), 8 rows tall
        options={
            "mode": "markdown",  # Can be "markdown", "html", or "code"
            "content": "# Hello World!\n\nThis dashboard was created programmatically using Python!"
        }
    )
    
    # Create the dashboard with a UID (Grafana will generate one if not provided)
    import uuid
    dashboard_uid = str(uuid.uuid4())[:8]  # Generate a short UID
    
    dashboard = DashboardObject(
        title="Simple Dashboard",
        uid=dashboard_uid,
        schemaVersion=39,
        panels=[text_panel]
    )
    
    # Get authentication
    api_key = os.getenv("GRAFANA_API_KEY")
    auth_user = os.getenv("GRAFANA_USER", "admin")
    auth_pass = os.getenv("GRAFANA_PASSWORD", "admin")
    
    # Create client and send
    client = GrafanaClient(
        host=os.getenv("GRAFANA_HOST", "localhost"),
        port=int(os.getenv("GRAFANA_PORT", "3000")),
        apiKey=api_key,
        auth_user=auth_user,
        auth_pass=auth_pass,
    )
    
    print("Sending dashboard to Grafana...")
    result = client.send_dashboard(dashboard, overwrite=True)
    
    if result:
        print("✓ Dashboard created successfully!")
        print(f"  View at: http://localhost:3000")
    else:
        print("✗ Failed to create dashboard")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

