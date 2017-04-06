from .utils import lback_db, lback_validate_id

class DBObject(object):
  FIELDS = []
  TABLE = ""
  def __init__(self, obj):
	for field_idx in range( 0, len( self.FIELDS ) ):
		field_name = self.FIELDS[ field_idx ]
		setattr( self, field_name, obj[ field_idx ] )

  @classmethod
  def find_by_id( cls, id ):
       lback_validate_id( id ) 
       db = lback_db()
       select_cursor= db.cursor()
       select_cursor.execute("SELECT * FROM " + cls.TABLE + " WHERE id LIKE %s",("%"+id+"%",))
       db_obj = select_cursor.fetchone()
       return cls( db_obj )

  @classmethod
  def delete_by_id( cls, id ):
       lback_validate_id( id )
       db = lback_db()
       select_cursor = db.cursor()
       select_cursor.execute("DELETE FROM " + cls.TABLE + " WHERE id LIKE %s",("%"+id+"%",))
       db_obj = select_cursor.fetchone()
       db.commit()
	
