from .utils import lback_db, lback_validate_id

class DBObject(object):
  FIELDS = []
  TABLE = ""
  def __init__(self, obj):
	for field_idx in range( 0, len( self.FIELDS ) ):
		field_name = self.FIELDS[ field_idx ]
		setattr( self, field_name, obj[ field_idx ] )

  def update_field(self, field_name, field_value):
       db = lback_db()
       cursor = db.cursor()
       cursor.execute("UPDATE "  + self.TABLE + " SET " + field_name + " = %s  WHERE ID = %s", ( field_value, self.id, ) )
       db.commit()
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
  @classmethod
  def eval_and_return(cls, db_obj):
      if not db_obj:
         return None
      return cls( db_obj )
	
