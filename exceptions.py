class EngineError(Exception):
    pass

class DataError(EngineError):
    pass

class TimeframeError(EngineError):
    pass

class PatternError(EngineError):
    pass
