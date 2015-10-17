from functools import wraps
from time import time

def timeit(f):
  @wraps(f)
  def wrapper(*args, **kwds):
    start = time()
    result = f(*args, **kwds)
    elapsed = time() - start
    if elapsed > 0.05:
        print(f.__name__+" took "+str(elapsed))
    return result
  return wrapper
