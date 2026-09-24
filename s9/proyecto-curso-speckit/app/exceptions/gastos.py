"""Business logic exceptions for gasto operations.

These exceptions represent KNOWN business rule violations, not programming errors.
They are caught in routers and translated to 400 HTTP responses (not 500).
Per Artículo VIII (Compatibility Contract), exception names are FIXED and immutable.
"""


class CategoriaInvalidaError(Exception):
    """Raised when a gasto categoría is not in the valid enum.

    Valid categorías: ['comida', 'transporte', 'entretenimiento', 'otros']
    Caught by routers → 400 "categoría inválida" (business error, not validation)
    """
    pass


class LimiteExcedidoError(Exception):
    """Raised when adding a gasto would exceed the 500.0 cumulative limit for that categoría.

    Limit is per user, per categoría, cumulative forever (no reset per month).
    Caught by routers → 400 "límite excedido" (business error, not validation)
    """
    pass
