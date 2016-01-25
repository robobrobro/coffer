"""
[(En)|(De)]crypts files
"""


from .coffer import Coffer
from .main import main, get_program_name, get_description
from .version import __version__

__all__ = ['main', 'get_program_name', 'get_description', 'Coffer']
__version__ = __version__
