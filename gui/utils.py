from traitlets import HasTraits
import numpy as np

class PrintableTraits:
    """Makes HasTrait instances pretty-print the trait values, to help with debugging."""

    def __repr__(self):
        if not hasattr(self, 'trait_values'):
            raise TypeError("PrintableTraits needs a .trait_values() method to work, make sure you're inheriting from traitlets.HasTraits")
        return f"{self.__class__.__name__}({', '.join(f'{key}={val if not isinstance(val, np.ndarray) else val.shape}' for key, val in self.trait_values().items())})"


