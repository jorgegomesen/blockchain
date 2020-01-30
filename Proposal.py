class Proposal:

    def __init__(self, name, value):
        self.company_name = name
        self.proposal_value = value

    def __repr__(self):
        return "company_name: " + self.company_name + ",\nvalue: " + str(self.proposal_value)

    def serialize(self):
        return {
            "company_name": self.company_name,
            "value": self.proposal_value
        }
