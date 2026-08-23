class EvidenceLinker:

    def build(
        self,
        strategy,
        evidence_states,
        failures=None,
    ):

        failures = failures or []

        confidence = (
            len(evidence_states)
            /
            max(
                len(evidence_states)
                + len(failures),
                1,
            )
        )

        return {
            "strategy": strategy,
            "supporting_states": evidence_states,
            "counter_examples": failures,
            "confidence": round(
                confidence,
                3,
            ),
        }
