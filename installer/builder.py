
if __name__ == '__main__':
   import os
   import shutil 
   print "Building Linux Distributable"
   if os.path.exists("build"):
      shutil.rmtree("build")
   if os.path.exists("dist"):
      shutil.rmtree("dist")
   if os.path.exists("../build/linux-x64"):
      shutil.rmtree("../build/linux-x64")
   os.system("pyinstaller ./lback")
   os.system("pyinstaller ../lback_grpc/bin/lback-server")
   os.system("pyinstaller ../lback_grpc/bin/lback-agent")

   build_path = "./build/lback"
   dist_path = "./dist/lback"
   bin_build_path = "../build/linux-x64"

   def make_build_path(path):
      return "%s%s"%( build_path, path )
   def make_dist_path(path):
      return "%s%s"%( dist_path, path )
   def make_bin_build_path(prefix, path):
      return "%s%s%s"%( bin_build_path,prefix, path )

   shutil.copy(make_build_path("/mysqlclient-1.3.10-py2.7-linux-x86_64.egg/_mysql.so"), make_dist_path("/_mysql.so"))
   shutil.copytree(make_build_path("/grpcio-1.0.0-py2.7-linux-x86_64.egg/grpc"), make_dist_path("/grpc"))
   shutil.copytree(make_build_path("/pycrypto-2.6.1-py2.7-linux-x86_64.egg/Crypto"), make_dist_path("/Crypto"))
   shutil.copytree(make_dist_path(""),make_bin_build_path("/bin", ""))
   shutil.copy("./dist/lback-server/lback-server", make_bin_build_path("/bin", "/lback-server"))
   shutil.copy("./dist/lback-agent/lback-agent", make_bin_build_path("/bin", "/lback-agent"))
   os.makedirs(make_bin_build_path("/conf", ""))
   shutil.copy("../settings.json", make_bin_build_path("/conf", "/settings.json"))


