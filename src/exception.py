import sys


# Creating function for error message detail
def error_message_detail(error, error_detail: sys):
    '''
    This function will return the error message with the file name and line number
    '''
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_no = exc_tb.tb_lineno
    error_message = "Error occured in python script name {0} line number [{1}] error message [{2}]".format(
        file_name, line_no, str(error))
    return error_message


class CustomException(Exception):
    '''
    This class is used to raise custom exception
    '''

    def __init__(self, error_message, error_detail: sys):
        '''
        This function will initialize the error message
        '''
        super().__init__(error_message)
        self.error_message = error_message_detail(
            error_message, error_detail=error_detail)

    def __str__(self):
        '''
        This function will return the error message
        '''
        return self.error_message
