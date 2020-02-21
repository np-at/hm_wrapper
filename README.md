# hm_wrapper
built on top of https://github.com/SLiX69/Sonarr-API-Python-Wrapper, provides a python(3) wrapper for interacting with Sonarr and Radarr APIs


## To Install

Using pip:
> pip3 install -U hm_wrapper

## Using
    >>> from hm_wrapper.sonarr import Sonarr
        
    >>> s = Sonarr("[Sonarr URL here]", "[Your Sonarr API Key here]")   
    >>> brady_bunch = s.lookup_series("Brady Bunch")
    >>> for b in brady_bunch:
    >>>     print(b["title"])
    
    The Brady Bunch
    The Brady Bunch Hour
    Becca's Bunch
    Brady's Beasts
    The Wild Bunch
    The Brady Brides
    The Brady Kids
    The Jungle Bunch
    A Bunch of Munsch
    A Bunch Of Fives
    The Bradys
    Matilda and the Ramsay Bunch
    Building Brady
    A Very Brady Renovation
    The Wayne Brady Show
    Bunch Of Five
    My Fair Brady
    Wheelie and the Chopper Bunch
    What Was Carol Brady Thinking?
    Back Home with the Bradys