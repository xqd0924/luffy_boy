class MyResponse():
    def __init__(self):
        self.status = 100
        self.msg = None

    @property
    def get_dic(self):
        return self.__dict__
#     自定义异常
class CommonException(Exception):
    def __init__(self,status,msg):
        self.status=status
        self.msg=msg
