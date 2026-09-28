import sys

class CustomException(Exception):
    def __init__(self,message:str,get_detailed:Exception=None):
        self.error_message=self.get_detailed_error(message,get_detailed)
        super().__init__(self.error_message)
    @staticmethod   #without object we can call
    def get_detailed_error(message,get_detailed):
        _, _,tb=sys.exc_info()  #THIS 2 _ TAKEN 'FILE NAME' AND 'LINE NUMBER' AS INPUT SO
        file_name=tb.tb_frame.f_code.co_filename if tb else "Unknown File"                #tb=TRACE BACK 
        line_number=tb.tb_lineno if tb else "Unknown LineNumber"
        return(
            f"{message} | Error:{get_detailed}"
            f"File:{file_name} | Line:{line_number}"
        )
    def __str__(self):
        return self.error_message 