try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface


class CVSSExplainAction(actionInterface):
    """Explain CVSS v3.x and v4.0 vectors in a human-readable format.

    Example:

    - `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
    - `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:P`
    """

    METRICS = {
        "AV": {
            "N": "Network",
            "A": "Adjacent",
            "L": "Local",
            "P": "Physical",
        },
        "AC": {
            "L": "Low attack complexity",
            "H": "High attack complexity",
        },
        "AT": {
            "N": "No attack requirements",
            "P": "Attack requirements present",
        },
        "PR": {
            "N": "No privileges required",
            "L": "Low privileges required",
            "H": "High privileges required",
        },
        "UI": {
            "N": "No user interaction",
            "P": "Passive user interaction",
            "A": "Active user interaction",
            "R": "User interaction required",  # CVSS v3
        },
        "S": {
            "U": "Unchanged scope",
            "C": "Changed scope",
            "N": "No subsequent impact",
            "P": "Subsequent system impacted",
            "X": "Not defined",
        },
        "C": {
            "N": "No confidentiality impact",
            "L": "Low confidentiality impact",
            "H": "High confidentiality impact",
        },
        "I": {
            "N": "No integrity impact",
            "L": "Low integrity impact",
            "H": "High integrity impact",
        },
        "A": {
            "N": "No availability impact",
            "L": "Low availability impact",
            "H": "High availability impact",
        },
        "VC": {
            "N": "No vulnerability confidentiality impact",
            "L": "Low vulnerability confidentiality impact",
            "H": "High vulnerability confidentiality impact",
        },
        "VI": {
            "N": "No vulnerability integrity impact",
            "L": "Low vulnerability integrity impact",
            "H": "High vulnerability integrity impact",
        },
        "VA": {
            "N": "No vulnerability availability impact",
            "L": "Low vulnerability availability impact",
            "H": "High vulnerability availability impact",
        },
        "SC": {
            "N": "No subsequent confidentiality impact",
            "L": "Low subsequent confidentiality impact",
            "H": "High subsequent confidentiality impact",
        },
        "SI": {
            "N": "No subsequent integrity impact",
            "L": "Low subsequent integrity impact",
            "H": "High subsequent integrity impact",
        },
        "SA": {
            "N": "No subsequent availability impact",
            "L": "Low subsequent availability impact",
            "H": "High subsequent availability impact",
        },
    }

    def __init__(self, parsers={}, supportedType={"cvss"}):
        super().__init__(parsers=parsers, supportedType=supportedType)
        self.description = "CVSS: Explain"
        self.explanations = {}

    def explain(self, vector):
        parts = vector.split("/")
        version = parts[0]

        explanation = [version]

        for part in parts[1:]:
            if ":" not in part:
                continue

            metric, value = part.split(":", 1)

            if metric in self.METRICS:
                text = self.METRICS[metric].get(value, value)
                explanation.append(f"- {metric}: {text}")
            else:
                explanation.append(f"- {metric}: {value}")

        return "\n".join(explanation)

    def execute(self):
        self.observables = self.get_observables()

        if self.observables.get("cvss"):
            self.explanations = {
                vector: self.explain(vector)
                for vector in self.observables["cvss"]
            }

        return self.explanations

    def __str__(self):
        self.execute()
        return "\n\n".join(self.explanations.values())