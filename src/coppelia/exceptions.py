class CoppeliaException(Exception):
    """Base exception for all Coppelia errors"""
    pass

class EntityEvaluationError(CoppeliaException):
    """Error during entity evaluation"""
    pass

class ConsensusError(CoppeliaException):
    """Error in consensus calculation"""
    pass

class SafetyVetoError(CoppeliaException):
    """Safety veto has blocked progression"""
    pass

class InvalidProposalError(CoppeliaException):
    """Proposal format or content is invalid"""
    pass

class ConfigurationError(CoppeliaException):
    """System configuration error"""
    pass
