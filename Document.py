class Document:

    def __init__(self, bidder, bidder_unit, crier):
        self.bidder = bidder  # licitador
        self.bidder_unit = bidder_unit  # unidade públic solicitante
        self.crier = crier  # pregoeiro

    def __repr__(self):
        return "bidder: " + self.bidder[0] + ",\nbidder_unit: " + self.bidder_unit[0] + ",\ncrier: " + self.crier[0]

    def serialize(self):
        return {
            "bidder": self.bidder,
            "bidder_unit": self.bidder_unit,
            "crier": self.crier
        }
