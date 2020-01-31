class Proposal:

    def __init__(self, name, value):
        self.company_name = name  # empresa concorrente a licitação
        self.proposal_value = value  # valor dos serviços prestados

    def __repr__(self):
        return "company_name: " + self.company_name + ",\nvalue: " + str(self.proposal_value)

    def serialize(self):
        return {
            "company_name": self.company_name,
            "value": self.proposal_value
        }
