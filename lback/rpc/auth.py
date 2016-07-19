
from lback.utils import lback_token_alg, lback_token_key, lback_redis
class Auth(object):
   def  __init__(self):
	self.client = lback_redis()
   def getAuthenticationToken( self, username, password ):
	 token = lback_token_alg( username, password )
	 return token 
   def setAuthenticationToken( self, username, password, token ):
	 key = lback_token_key( username, password )
	 return self.client.set(token, key)
   def isAuthenticated( self, token ):
	 return self.client.get( token )
   

