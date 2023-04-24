from django.utils import timezone
import re
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from core.utils import create_response_msg


def validate_date(value):
    now = timezone.now()
    if now > value:
        raise ValidationError('현재시간 이전으론 설정할 수 없습니다.')

CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def korean_to_be_initial(korean_word):
    r_lst = []
    words = re.compile('[가-힣]+')
    for w in list(korean_word.strip().replace(' ', '')): 
        if words.match(w):
            ch1 = (ord(w) - ord('가'))//588

            r_lst.append(CHOSUNG_LIST[ch1])
        else:
            r_lst.append(w)
    return r_lst

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    """
    if isinstance(exc, ValidationError):

        messages = exc.detail
        
        return create_response_msg(status.HTTP_400_BAD_REQUEST, messages)

    response = exception_handler(exc, context)

    return response