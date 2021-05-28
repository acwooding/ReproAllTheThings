class EasydataError(Exception):
    """General Easydata Error. Further error types are subclassed from this Exception"""
    pass

class ParameterError(EasydataError):
    """Paramater(s) to a function or method are invalid"""
    pass

class ValidationError(EasydataError):
    """Hash check failed"""
    pass

class ObjectCollision(EasydataError):
    """Object already exists in object store"""
    pass

class NotFoundError(EasydataError):
    """Named object not found in object store"""
    pass
