from typing import Callable
from magicgui.tqdm import trange




class PrintToProgressBar:
    orig_print = __builtins__['print']

    def __init__(
        self, 
        start_filter: Callable[[str], bool], 
        to_find_fun: Callable[[str], int],
        end_filter: Callable[[str], bool] = lambda s: False,
    ) -> None:
        """
        Example
        -------
        
        >>> kmeans =  MiniBatchKMeans(verbose=1)
        ... with PrintToProgressBar(
        ...     start_filter=lambda s: "Minibatch" in s,  # start pbar when Minibatch is printed
        ...     to_find_fun=lambda s: int(s[s.index("/")+1 : s.index(": mean")]),  # Find total in "/243: mean"
        ...     end_filter=lambda s: "Converged" in s,  # stop pbar with "Converged" is printed
        ... ):
        ...     kmeans.fit(data)
        """
        self.start_filter = start_filter
        self.to_find_fun = to_find_fun
        self.end_filter = end_filter
        self.progbar = None
    
    def update_progressbar(self, text):
            if self.start_filter(text):
                if self.progbar is None:
                    to = self.to_find_fun(text)
                    self.progbar = iter(trange(1, to))
                next(self.progbar)
            elif self.end_filter(text):  # if something indicates it's over early
                list(self.progbar)  # finish out the progress bar


    def __enter__(self) -> None:
        __builtins__['print'] = self.update_progressbar


    def __exit__(self, type, value, tb):
        __builtins__['print'] = self.orig_print