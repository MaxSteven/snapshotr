import re

def check_script(name):
    re1='((?:[a-z][a-z]*[0-9]+[a-z0-9]*))'  # Shot
    re2='(\\.)'                             # .
    re3='((?:[a-z][a-z]+))'                 # Task
    re4='(\\.)'                             # .
    re5='((?:[a-z][a-z]+))'                 # Artist
    re6='(\\.)'                             # .
    re7='(v)'                               # v
    re8='(\\d+)'                            # Major version number
    re9='(\\.)'                             # .
    re10='(\\d+)'                           # Minor version number
    re11='(\\.)'                            # .
    re12='(nk)'                             # nk
    rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12,re.IGNORECASE|re.DOTALL)
    result = rg.match(name)
    return result