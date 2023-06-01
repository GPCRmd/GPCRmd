import csv

class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
class CsvDictWriterNoFile(csv.DictWriter):
  def __init__(self,*args, **kwds):
    echo = Echo()
    super(CsvDictWriterNoFile, self).__init__(echo,*args,**kwds)
      
      
class CsvDictWriterRowQuerySetIterator:
    def __init__(self, csvwriter, iterator,headers=True,comment_block=''):
        self.csvwriter = csvwriter
        self.iterator = iterator
        self.headers = headers
        self.comment_block = comment_block
        self.__commentprinted = False
        self.__headersprinted = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__commentprinted:
          self.__commentprinted = True
          return self.comment_block
        elif self.headers and not self.__headersprinted:
          self.__headersprinted = True
          header = dict(zip(self.csvwriter.fieldnames, self.csvwriter.fieldnames))
          return self.csvwriter.writerow(header)
          
        row = next(self.iterator).__dict__
        return self.csvwriter.writerow(row)