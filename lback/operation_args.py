class OperationArgs( object ):
  def __init__( self, *args, **kwargs ):
      for k, v in kwargs.iteritems():
         setattr( self, k, v )
