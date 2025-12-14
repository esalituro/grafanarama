from datetime import datetime, timezone

import json
import pytest


from grafanarama.core.dashboard import (
    AnnotationContainer,
    AnnotationPanelFilter,
    AnnotationQuery, Dashboard, DataSourceRef, Metadata, Spec, Status
)

from grafanarama import DashboardObject


@pytest.fixture
def sample_datetime():
    return datetime(2024, 3, 20, 22, 00, 00, 0000, tzinfo=timezone.utc)


@pytest.fixture
def annotation_query(datasource_ref):
    return AnnotationQuery(
        name="Annotations & Alerts",
        datasource=datasource_ref,
        enable=True,
        iconColor="rgba(0, 211, 255, 1)",
    )


@pytest.fixture
def dashboard_serialized(dashboard):
    serial = """
{
    "metadata": {
        "uid": "fdgaok30vxmo0b",
        "creationTimestamp": "2024-03-20T22:00:00Z",
        "deletionTimestamp": null,
        "finalizers": [
            "finalizer"
        ],
        "resourceVersion": "1",
        "labels": {},
        "updateTimestamp": "2024-03-20T22:00:00Z",
        "createdBy": "me",
        "updatedBy": "me",
        "extraFields": {}
    },
    "spec": {
        "id": null,
        "uid": null,
        "title": null,
        "description": null,
        "revision": null,
        "gnetId": null,
        "tags": null,
        "timezone": "browser",
        "editable": true,
        "graphTooltip": 0,
        "time": null,
        "timepicker": null,
        "fiscalYearStartMonth": 0,
        "liveNow": null,
        "weekStart": null,
        "refresh": null,
        "schemaVersion":39,
        "version": null,
        "panels": null,
        "templating": null,
        "annotations": null,
        "links": null,
        "snapshot": null
    },
    "status": {
        "operatorStates": null,
        "additionalFields": null
    }
}
"""
    return json.loads(serial)


@pytest.fixture
def dashboard_empty():
    serial = """
{
  "annotations": {
    "list": [
      {
        "builtIn": 1.0,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [],
  "schemaVersion": 39,
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "browser",
  "title": "New dashboard",
  "uid": "fdgaok30vxmo0b",
  "version": 1,
  "weekStart": ""
}
"""
    return json.loads(serial)


@pytest.fixture
def dashboard(metadata, spec, status):
    return Dashboard(metadata=metadata, spec=spec, status=status)


@pytest.fixture
def dashboard_object(metadata, spec, status):
    return DashboardObject(metadata=metadata, spec=spec, status=status)


@pytest.fixture
def spec():
    return Spec(schemaVersion=39)


@pytest.fixture
def status():
    return Status()


@pytest.fixture
def metadata(sample_datetime):
    return Metadata(
        uid="fdgaok30vxmo0b",
        creationTimestamp=sample_datetime,
        updateTimestamp=sample_datetime,
        finalizers=["finalizer"],
        labels={},
        resourceVersion="1",
        createdBy="me",
        updatedBy="me",
        extraFields={},
    )


@pytest.fixture
def annotation_panel_filter():
    return AnnotationPanelFilter(ids=[1])


@pytest.fixture
def datasource_ref():
    return DataSourceRef(type="grafana", uid="-- Grafana --")


def test_AnnotationContainer():
    assert type(AnnotationContainer()) == AnnotationContainer


def test_AnnotationPanelFilter(annotation_panel_filter):
    assert type(annotation_panel_filter) == AnnotationPanelFilter


def test_AnnotationQuery(annotation_query):
    assert type(annotation_query) == AnnotationQuery


def test_Dashboard(dashboard):
    assert type(dashboard) == Dashboard


def test_Dashboard_serialized(dashboard, dashboard_serialized):
    assert dashboard.model_dump_json() == json.dumps(
        dashboard_serialized, separators=(",", ":")
    )


def test_DashboardObject_serialized(dashboard_object, dashboard_serialized):
    assert dashboard_object.model_dump_json() == json.dumps(
        dashboard_serialized["spec"], separators=(",", ":")
    )


def test_DashboardObject_parse_raw(dashboard_object, dashboard_empty):
    new_dashboard_object = dashboard_object.model_validate_json(
        json.dumps(dashboard_empty)
    )
    assert (
        json.loads(
            new_dashboard_object.model_dump_json(exclude_unset=True, by_alias=True)
        )
        == dashboard_empty
    )


def test_DashboardObject_with_spec_only():
    """Test creating DashboardObject with just spec=Spec(...) - this was the bug we fixed"""
    from grafanarama import DashboardObject, Spec
    
    # This should work without errors (the bug was in the validator)
    dashboard = DashboardObject(spec=Spec(title="My Dashboard", schemaVersion=39))
    assert dashboard.spec.title == "My Dashboard"
    assert dashboard.spec.schemaVersion == 39
    # Should serialize to just the spec
    serialized = dashboard.model_dump_json()
    data = json.loads(serialized)
    assert data["title"] == "My Dashboard"
    assert data["schemaVersion"] == 39


def test_DashboardObject_with_top_level_fields():
    """Test creating DashboardObject with top-level fields that should go into spec"""
    from grafanarama import DashboardObject
    
    # This should merge top-level fields into spec
    dashboard = DashboardObject(title="Test Dashboard", schemaVersion=39)
    assert dashboard.spec.title == "Test Dashboard"
    assert dashboard.spec.schemaVersion == 39
