from datetime import datetime, timedelta
from blockchain.Document import Document
from blockchain.Proposal import Proposal
from copy import copy


class Bidding:
    trading_floor_count = 1

    def __init__(self, authority, deadline, bidder, bidder_unit, crier, bid_value, document_date,
                 documentation_address):
        self.trading_floor_number = str(self.__class__.trading_floor_count) + '/' + str(datetime.now().year),
        self.authority = authority,  # autoridade é quem assina o processo administrativo
        self.trading_floor_team = [],  # equipe de pregão escolhida pelo pregoeiro
        self.document = Document(bidder, bidder_unit, crier),  # edital
        self.created_at = datetime.now(),  # quando foi criada
        self.finish_at = datetime.now() + timedelta(days=int(deadline)),  # data limite para obter-se um proprietário
        self.owned_by = None,  # proprietário da licitação
        self.proposals = []  # propostas
        self.date_session = None,  # data da sessão
        self.time_session = None,  # horário da sessão
        self.bid_value = bid_value,  # valor da licitação
        self.document_date = document_date,  # data do edital
        self.documentation_address = documentation_address  # endereço para envio da documentação

        self.__class__.trading_floor_count += 1

    def __repr__(self):
        return "trading_floor_number: " + str(self.trading_floor_number) + ",\nauthority: " + self.authority[
            0] + ",\ntrading_floor_team: " + repr(self.trading_floor_team) + ",\ndocument: " + repr(
            self.document[0]) + ",\ncreated_at: " + str(self.created_at[0].timestamp()) + ",\nfinish_at: " + str(
            self.finish_at[
                0].timestamp()) + ",\nowned_by: " + str(self.owned_by[0]) + ",\nproposals: " + repr(self.proposals)

    def add_proposal(self, name, value):
        try:
            if datetime.now().timestamp() <= self.finish_at[0].timestamp():
                self.proposals.append(Proposal(name, value))
                return True
            return False
        except ValueError:
            return False

    def define_best_proposal(self):
        proposals = self.proposals
        min_value = proposals[0].proposal_value
        self.owned_by = proposals[0].company_name
        for proposal in proposals:
            if proposal.proposal_value < min_value:
                min_value = proposal.proposal_value
                self.owned_by = proposal.company_name

    def clone(self):
        authority = self.authority[0]
        bidder = "deafult"
        bidder_unit = "deafult"
        crier = "deafult"
        deadline = 0  # em dias
        bid_value = self.bid_value
        document_date = self.document_date
        documentation_address = self.documentation_address
        new_bidding = Bidding(authority, deadline, bidder, bidder_unit, crier, bid_value, document_date,
                              documentation_address)
        new_bidding.finish_at = self.finish_at
        new_bidding.document = self.document
        new_bidding.proposals = copy(self.proposals)
        return new_bidding

    def serialize(self):
        proposals = self.proposals
        new_proposals = []

        for proposal in proposals:
            new_proposals.append(proposal.serialize())

        return {
            "trading_floor_number": self.trading_floor_number,
            "authority": self.authority,
            "trading_floor_team": self.trading_floor_team,
            "document": self.document[0].serialize(),
            "created_at": str(self.created_at[0].timestamp()),
            "finish_at": str(self.finish_at[0].timestamp()),
            "owened_by": self.owned_by,
            "proposals": new_proposals
        }
