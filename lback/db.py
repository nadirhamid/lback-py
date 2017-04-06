class DBObject(object):
  FIELDS = []
  def __init__(self, obj):
	for field_idx in range( 0, len( self.FIELDS ) ):
		field_name = self.FIELDS[ field_idx ]
		setattr( self, field_name, obj[ field_idx ] )
	
