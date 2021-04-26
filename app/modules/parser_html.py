import os

class ParserHTML:

    @staticmethod
    def open(filename, **kwargs):
        r"""
        Documentation here
        """
        with open(os.path.abspath(os.path.join(__file__, "../..", 'templates', filename)), "r") as f:
                
                msg = f.read().format(**kwargs)

        return msg