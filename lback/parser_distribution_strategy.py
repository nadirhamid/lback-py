
from parser import Parser
from parser_exception import ParserException

class ParserDistributionStrategy(Parser):
    def run(self):
        distribution_strategy = self.args.distribution_strategy
        if distribution_strategy!="shared" and distribution_strategy!="sharded":
            raise ParserException("Distribution Strategy value invalid")
