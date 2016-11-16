class StreamSizeLimitError(Exception):
    pass
class StreamTimeoutError(Exception):
    pass
class ParsingError(Exception):
    pass
class MultipleMoleculesinSDF(Exception):
    def __init__(self,*args,file_name='',**kwrags):
        msg="Parsing Error: SD files with more than 1 molecule are not accepted."
        super(MultipleMoleculesinSDF, self).__init__(msg,*args, **kwrags)
class InvalidMoleculeFileExtension(Exception):
    def __init__(self,*args,ext=None,**kwrags):
        self.ext = ext
        msg = "Molecule file with invalid extension: '"+ext+"' ."
        super(InvalidMoleculeFileExtension, self).__init__(msg,*args, **kwrags)