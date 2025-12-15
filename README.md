# Grafanarama

A Python library for programmatically creating and managing Grafana dashboards with type-safe, schema-driven models.

## Features

- 🎯 **Type-Safe**: Pydantic models generated from Grafana's JSON schemas ensure type safety
- 🔄 **Schema-Driven**: Automatically adapts to schema changes - no hardcoded field lists
- 🚀 **Easy to Use**: Simple Python API for creating dashboards and panels
- 🔐 **Secure**: Environment variable support for credentials
- 📦 **Comprehensive**: Supports dashboards, panels, datasources, and more

## Installation

```bash
pip install grafanarama
```

Or using Poetry:

```bash
poetry add grafanarama
```

## Quick Start

### 1. Start Grafana

```bash
docker compose up -d
```

This starts Grafana on `http://localhost:3000` (default credentials: `admin`/`admin`).

### 2. Set Up Authentication

Create a `.env` file or export environment variables:

```bash
# Option 1: Use API Key
export GRAFANA_API_KEY="your_api_key_here"

# Option 2: Use Basic Auth (simpler for testing)
export GRAFANA_USER="admin"
export GRAFANA_PASSWORD="admin"
```

### 3. Create Your First Dashboard

```python
from grafanarama import DashboardObject, Spec
from grafanarama.core.dashboard import Panel, GridPos
from grafanarama.apiclient import GrafanaClient
import os

# Create a text panel
text_panel = Panel(
    type="text",
    id=1,
    title="Hello World!",
    gridPos=GridPos(x=0, y=0, w=24, h=8),
    options={
        "mode": "markdown",
        "content": "# My First Dashboard\n\nCreated with Grafanarama!"
    }
)

# Create the dashboard
dashboard = DashboardObject(
    title="My Dashboard",
    schemaVersion=39,
    panels=[text_panel]
)

# Send to Grafana
client = GrafanaClient(
    host=os.getenv("GRAFANA_HOST", "localhost"),
    port=int(os.getenv("GRAFANA_PORT", "3000")),
    auth_user=os.getenv("GRAFANA_USER", "admin"),
    auth_pass=os.getenv("GRAFANA_PASSWORD", "admin"),
)

client.send_dashboard(dashboard)
```

## Examples

See the `examples/` directory for more examples:

- **`simple_dashboard.py`** - Basic dashboard with a text panel
- **`dashboard_with_text_panel.py`** - More detailed text panel example
- **`test_auth.py`** - Test your Grafana authentication

Run an example:

```bash
export GRAFANA_USER="admin"
export GRAFANA_PASSWORD="admin"
python examples/simple_dashboard.py
```

## Architecture

### Schema-Based Approach

Grafanarama uses Pydantic models generated from Grafana's JSON schemas. This means:

- ✅ **Maintainable**: When Grafana schemas change, regenerate models - no manual updates needed
- ✅ **Type-Safe**: Full type checking and validation
- ✅ **Auto-Detection**: Array fields and nested structures are automatically detected from schemas
- ✅ **Future-Proof**: Works with any Grafana resource type (dashboards, datasources, etc.)

### How It Works

1. **Model Generation**: Pydantic models are generated from Grafana JSON schemas using `datamodel-codegen`
2. **Schema Introspection**: The library uses `model_json_schema()` to introspect field types
3. **Smart Defaults**: Array fields automatically convert `null` to `[]` based on schema information
4. **Serialization**: Dashboards are serialized to Grafana-compatible JSON with all required fields

## API Reference

### DashboardObject

The main class for creating dashboards:

```python
from grafanarama import DashboardObject, Spec

dashboard = DashboardObject(
    title="My Dashboard",
    schemaVersion=39,
    panels=[...],
    # All Spec fields are supported
)
```

### Panel

Create panels for your dashboard:

```python
from grafanarama.core.dashboard import Panel, GridPos

panel = Panel(
    type="text",  # Panel type (text, timeseries, stat, etc.)
    id=1,
    title="My Panel",
    gridPos=GridPos(x=0, y=0, w=24, h=8),  # Position and size
    options={...}  # Panel-specific options
)
```

### GrafanaClient

API client for interacting with Grafana:

```python
from grafanarama.apiclient import GrafanaClient

client = GrafanaClient(
    host="localhost",
    port=3000,
    apiKey="your_key",  # or use auth_user/auth_pass
    use_https=False
)

# Send dashboard
client.send_dashboard(dashboard, overwrite=True)

# Get dashboard
dashboard_data = client.get_dashboard("dashboard-slug")

# Send datasource
client.send_datasource(datasource)
```

## Supported Resources

Currently supported Grafana resources:

- ✅ **Dashboards** - Full support
- ✅ **Panels** - All panel types
- ✅ **Datasources** - Basic support
- 🔄 **Access Policies** - Models available
- 🔄 **Teams** - Models available
- 🔄 **Roles** - Models available
- 🔄 **Library Panels** - Models available

More resources can be added by generating models from Grafana schemas.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/esalituro/grafanarama.git
cd grafanarama

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running Tests

```bash
pytest
```

### Generating Models

Models are generated from Grafana JSON schemas. See `Taskfile.yml` for generation tasks.

### Project Structure

```
grafanarama/
├── core/           # Core Grafana resource models (dashboards, teams, etc.)
├── composable/     # Composable elements (panels, data queries)
├── apiclient.py    # HTTP client for Grafana API
├── schema_utils.py # Schema introspection utilities
└── __init__.py     # DashboardObject and main exports

examples/
├── simple_dashboard.py
├── dashboard_with_text_panel.py
└── test_auth.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GRAFANA_API_KEY` | Grafana API key | None |
| `GRAFANA_USER` | Basic auth username | None |
| `GRAFANA_PASSWORD` | Basic auth password | None |
| `GRAFANA_HOST` | Grafana host | `localhost` |
| `GRAFANA_PORT` | Grafana port | `3000` |
| `GRAFANA_USE_HTTPS` | Use HTTPS | `false` |

## Troubleshooting

### Authentication Issues

If you get a 401 error, test your authentication:

```bash
python examples/test_auth.py
```

This will help diagnose authentication problems.

### Dashboard Import Errors

If you see "tags expected array" or similar errors:
- Make sure you're using the latest version
- The library automatically handles array field defaults
- Check that all required fields are present

### Service Account Tokens

Service account tokens (starting with `glsa_`) may not work with all Grafana versions. Use regular API keys or basic auth instead.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Pydantic](https://pydantic.dev/) for type-safe data validation
- Models generated from [Grafana](https://grafana.com/) JSON schemas
- Inspired by the need for programmatic Grafana dashboard management
