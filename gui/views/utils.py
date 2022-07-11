
from typing import Any, Callable, Dict, TypeVar

from grpc import Call

A = TypeVar('A')

def match_items_to_kwargs(fun: Callable[..., A], **kwargs: str) -> Callable[[Dict[str, Any]], A]:
    """
    A Decorator, returns a function that calls a function on a single unpacked value of dict *input_dict*, specified by *key*.
    Useful in cases where a framework (e.g. Traitlets) passes a dict as a data structure on callback functions.
    
    Examples:

    >>> data = {'value': 5, 'name': 'Nick'}
    >>> add3 = lambda x: x + 3
    >>> add3_extract = match_items_to_kwargs(add3, x='value')
    >>> add3_extract(data)
    8

    >>> first_letter = lambda s: s[0]
    >>> first_letter_extract = match_items_to_kwargs(first_letter, s='name')
    >>> first_letter_extract(data)
    'N'


    """
    def wrapper(input_dict):
        inputs = {key: input_dict[value] for key, value in kwargs.items()}
        return fun(**inputs)
    return wrapper



def match_atttributes_to_kwargs(fun: Callable[..., A], **kwargs: str) -> Callable[[Any], A]:
    """
    A Decorator, returns a function that calls a function with kwargs on the extracted attributes of *obj*.
    Useful in cases where a framework passes an object as a data structure on callback functions.
    
    Examples:
    
    >>> from types import SimpleNamespace
    >>> data = SimpleNamespace(value=5, name='Nick')
    >>> add3 = lambda x: x + 3
    >>> add3_extract = match_atttributes_to_kwargs(add3, x='value')
    >>> add3_extract(data)
    8


    """
    def wrapper(obj):
        inputs = {key: getattr(obj, value) for key, value in kwargs.items()}
        return fun(**inputs)
    return wrapper    



def match_items_atttributes_to_kwargs(fun: Callable[..., A], key: str, **kwargs: str) -> Callable[[Dict[str, Any]], A]:
    """
    A Decorator, returns a function that calls a function with kwargs on the 'owner' key's attributes of a dictionary.
    Useful for Traitlets, which passes in the model inside a dictionary into a callback for observables.


    Examples:

    >>> from types import SimpleNamespace
    >>> model = SimpleNamespace(value=10, name='Nick')
    >>> change = {'new': 3, 'owner': model}
    >>> add3 = lambda x: x + 3
    >>> add3_callback = match_items_atttributes_to_kwargs(add3, 'owner', x='value')
    >>> add3_callback(change)
    13

    """


    call_on_model = match_atttributes_to_kwargs(fun, **kwargs)    
    def wrapper(inputs: Dict[str, Any]):
        model = inputs[key]
        return call_on_model(model)
    return wrapper
        

