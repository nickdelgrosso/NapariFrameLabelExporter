from typing import List, Union, Tuple
import numpy as np

class PrintableTraits:
    """Makes HasTrait instances pretty-print the trait values, to help with debugging."""

    def __repr__(self):
        if not hasattr(self, 'trait_values'):
            raise TypeError("PrintableTraits needs a .trait_values() method to work, make sure you're inheriting from traitlets.HasTraits")
        return f"{self.__class__.__name__}({', '.join(f'{key}={val if not isinstance(val, np.ndarray) else val.shape}' for key, val in self.trait_values().items())})"






def cycle_next_item(items: Union[List, Tuple], item):
    """Returns the next item in a sequence from the one asked for, cycling back to the first if necessary."""
    next_index = items.index(item) + 1
    if next_index == len(items):
        next_index = 0
    next_item = items[next_index]
    return next_item



def cycle_prev_item(items: Union[List, Tuple], item):
    """Returns the previous item in a sequence from the one asked for, cycling back to the last if necessary."""
    prev_index = items.index(item) - 1
    prev_item = items[prev_index]
    return prev_item
