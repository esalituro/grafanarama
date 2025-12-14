from typing import Any

from pydantic import model_serializer, field_validator, model_validator

from .core.dashboard import Dashboard, Metadata, Spec, Status


class DashboardObject(Dashboard):
    metadata: Any
    spec: Any
    status: Any

    @model_validator(mode="before")
    @classmethod
    def gather_fields_into_spec(cls, values) -> dict:
        # Handle case where values is not a dict (e.g., already validated)
        if not isinstance(values, dict):
            return values
        
        # Copy all fields into 'spec', excluding fields that are already
        # defined or supposed to be outside 'spec'.
        spec_content = {k: v for k, v in values.items() if k not in ["spec", "metadata", "status"]}
        
        # Ensure schemaVersion is set
        if "schemaVersion" not in spec_content:
            spec_content["schemaVersion"] = 39
        
        # If 'spec' is provided, merge its contents
        if "spec" in values:
            spec_value = values["spec"]
            # If spec is already a Spec object, convert to dict
            if isinstance(spec_value, Spec):
                spec_dict = spec_value.model_dump(exclude_unset=True)
            # If spec is a dict, use it directly
            elif isinstance(spec_value, dict):
                spec_dict = spec_value
            else:
                spec_dict = {}
            
            # Merge spec dict into spec_content (spec_content takes precedence)
            spec_content = {**spec_dict, **spec_content}
        
        # Build the return dict with proper structure
        # Handle metadata - if provided as dict, try to create Metadata object, otherwise use as-is
        metadata_value = values.get("metadata")
        if metadata_value is None:
            metadata_value = {}
        elif isinstance(metadata_value, dict) and metadata_value:
            # Only try to create Metadata if dict is not empty
            try:
                metadata_value = Metadata(**metadata_value)
            except Exception:
                # If Metadata creation fails, keep as dict (will fail validation later)
                pass
        
        # Handle status - if provided as dict, create Status object, otherwise use as-is
        status_value = values.get("status")
        if status_value is None:
            status_value = Status()
        elif isinstance(status_value, dict):
            status_value = Status(**status_value)
        
        result = {
            "spec": Spec(**spec_content),
            "metadata": metadata_value,
            "status": status_value
        }
        
        return result

    @model_serializer()
    def serialize_model(self) -> Spec:
        return self.spec
