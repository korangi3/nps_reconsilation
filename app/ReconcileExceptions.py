"""                                                                                               
                                                                                                     
               /                           \                                                     
    \         /                             \   /                                   
     \       /                               \ /                                              
      \     /                         / _-_-_::-_-_/                                                     
  {....\.../....... |\..             /  /     /\
 {    /-:-/         |=== ``=========/__/     /  \ 
  {../....\.........|/..``                  /
    /      \        |
   /        \                                                                                   
  /

"""

class FatalError(Exception):
    def __init__(self, message="Fatal error occoured, bot need to shut down"):
        self.message = message
        super().__init__(self.message)

"""sqlite"""
class TableCreationError(Exception):
     def __init__(self, message="Could Not Create Table"):
        self.message = message
        super().__init__(self.message)

class MultipleValueReturn(Exception):
    def __init__(self, message="Query Returned multiple value"):
        self.message = message
        super().__init__(self.message)



"""FILTER"""
class IndexingError(Exception):
    def __init__(self, message="Error Occoured while indexing"):
        self.message = message
        super().__init__(self.message)

class FilterRuleError(Exception):
    def __init__(self, message="Error Occoured while applying filter rule"):
        self.message = message
        super().__init__(self.message)

"""LOAD VARIABLES"""
class VariableLoadError(Exception):
    def __init__(self, message="Error Occoured while initializing the variables"):
        self.message = message
        super().__init__(self.message)