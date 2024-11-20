class Logger:
    def __init__(self, simulation):
        """
        Initialize the logger.

        Args:
            simulation (object): Reference to the simulation infrastructure.
        """
        self.simulation = simulation
        self.log_values = []  # List of log entries
        self.expression_to_unit = {}  # Mapping of expressions to units

    def add_value_to_log(self, log_prop):
        """
        Adds a value to the log.

        Args:
            log_prop (dict): Properties of the log item.

        Returns:
            int: Index of the log entry.
        """
        # Validate object path and retrieve the object
        object_path = self.convert_shorthand_to_full_path(log_prop.get("object_path"))
        try:
            obj = eval(f"self.simulation.{object_path}")
            log_prop["obj_uuid"] = obj.uuid
        except AttributeError as e:
            raise ValueError(f"Object does not exist: {object_path}") from e

        # Check if the entry already exists
        for idx, entry in enumerate(self.log_values):
            if entry["obj_uuid"] == log_prop["obj_uuid"] and entry["expression"] == log_prop["expression"]:
                # Update label or name if new values are provided
                if log_prop.get("label") and log_prop["label"] != entry.get("label"):
                    print(f"Warning: Overwriting log label from '{entry.get('label')}' to '{log_prop['label']}'")
                    entry["label"] = log_prop["label"]
                if log_prop.get("name") and log_prop["name"] != entry.get("name"):
                    print(f"Warning: Overwriting log name from '{entry.get('name')}' to '{log_prop['name']}'")
                    entry["name"] = log_prop["name"]
                return idx

        # Generate missing metadata
        log_prop.setdefault("name", self.generate_name(log_prop["expression"], obj.uuid))
        log_prop.setdefault("unit", self.expression_to_unit.get(log_prop["expression"], "-"))
        log_prop.setdefault("label", self.generate_label(log_prop, obj))

        # Add new entry
        log_prop["index"] = len(self.log_values)
        self.log_values.append(log_prop)
        return log_prop["index"]

    def convert_shorthand_to_full_path(self, path):
        """Convert shorthand path to full path."""
        return path.replace(":s:", ".toStores.")  # Example conversion

    def generate_name(self, expression, uuid):
        """Generate a name for the log item."""
        sanitized = "".join(c if c.isalnum() else "_" for c in expression)
        if len(sanitized) > 30:
            sanitized = sanitized[:30]
        return f"{sanitized}_{uuid}"

    def generate_label(self, log_prop, obj):
        """Generate a label for the log item."""
        label = getattr(obj, "name", log_prop["object_path"])
        unit = log_prop.get("unit")
        if unit in self.expression_to_unit:
            return f"{label} - {self.expression_to_unit[unit]}"
        return log_prop["expression"]
