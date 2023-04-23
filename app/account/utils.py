import re
from django.core.exceptions import ValidationError

def validate_phone(phone_num):
    # 입력된 번호에서 공백 제거
    phone_number = phone_num.replace(" ", "")

    # 입력된 번호가 "XXX-XXXX-XXXX" 형식을 따르는지 확인
    pattern = re.compile(r"\d{3}-\d{3,4}-\d{4}")
    match = pattern.fullmatch(phone_number)

    if not match:
        raise ValidationError('잘못된 휴대폰 번호입니다.')
    
    # 입력된 번호가 국내 이동통신사의 번호인지 확인
    mobile_pattern = re.compile(r"^01[016789]-\d{3,4}-\d{4}$")
    mobile_match = mobile_pattern.fullmatch(phone_number)

    if not mobile_match:
        raise ValidationError('잘못된 휴대폰 번호입니다.')

    return True
