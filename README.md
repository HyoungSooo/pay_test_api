# pay_test_api

```
git clone <repositry>

docker-compose --env-file .env.dev up --build

```

요구사항


### login

schema => {  
  'phone_number': str  
  'password': str  
}  

endpoint => '/auth/api-jwt-auth/login/'

사용자의 핸드폰 번호와 비밀번호를 입력받아 jwt토큰을 제공해주는 api입니다. 입력받은 phone_number를 데이터베이스에서 확인해 일치하는 계정의 패스워드와 입력받은 password를 비교하여 인증합니다.
인증에 성공하면 사용자의 쿠키에 토큰을 저장합니다.

response
```
{
    "meta": {
        "code": 400,
        "message": "아이디/패스워드가 틀렸습니다."
    },
    "data": null
}

{
    "meta": {
        "code": 200,
        "message": "ok"
    },
    "data": {
        "access_token": <token>,
        "refresh_token": <token>
    }
}

```

### logout

schema => {}  

endpoint => '/auth/api-jwt-auth/logout/'

사용자의 쿠키에서 토큰을 지워주는 동작을 하는 api입니다.

response
```
{
    "meta": {
        "code": 202,
        "message": "ok"
    },
    "data": null
}
```

### registor

schema => {  
  'phone_number': str  
  'password': str  
}  
  
endpoint => '/auth/api-jwt-auth/register/'
  
휴대폰 번호와 비밀번호를 입력받아 회원가입을 진행합니다. 
휴대폰 번호의 입력 검증은 다음과 같습니다.

```
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
```
휴대폰 번호가 010,011등 국내 이동통신사의 번호인지, 각 자리수가 3~4인지를 확인합니다.

```
class UserManager(BaseUserManager):
    ...

    def create_user(self, phone_number, password, **extra_fields):

        if not phone_number:
            raise ValueError('휴대폰 번호를 입력해야합니다.')

        user = self.model(phone_number=phone_number ,**extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    ...
```

비밀번호는 django 내장함수인 set_password()를 활용해 hash함수가 적용된 값으로 저장합니다.

response
```
{
    "meta": {
        "code": 201,
        "message": "ok"
    },
    "data": null
}
```

### Product schma
```
class Product(models.Model):
    category = models.CharField(max_length=30)
    price = models.IntegerField()
    cost = models.IntegerField()
    name = models.CharField(max_length=20, unique=True)
    des = models.TextField()
    barcode = models.ImageField(upload_to='images/', blank=True)
    expiration_date = models.DateTimeField(validators=[validate_date])
    size = models.CharField(max_length=1, choices=SIZE)
    initial_set = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, make_barcode=True, *args, **kwargs):

        self.initial_set = ''.join(korean_to_be_initial(self.name))

        if make_barcode:

            korea_unicode = '-'.join([str(ord(i)) for i in self.name])
            code = barcode.get_barcode_class('code128')
            ean = code(f'{self.price}{self.expiration_date}{self.id}{korea_unicode}{self.size}',
                       writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            title = self.name.replace(' ', '')
            if os.path.isfile(f'/usr/src/app/images/{title}.png'):
                os.remove(f'/usr/src/app/images/{title}.png')
            self.barcode.save(f'{title}.png', File(buffer), save=False)
        return super().save(*args, **kwargs)

```

요구사항에 나와있는 필수 조건들과, 초성 검색에 활용하기 위한 initial_set필드로 구성했습니다.
save 함수를 오버라이딩해 자동으로 바코드 이미지와 이름의 초성을 생성하여 저장합니다.


### 상품 등록

schma => {  
    category : str  
    price : int  
    cost : int  
    name : str  
    des : str  
    barcode : str(url) not require  
    expiration_date : datetime.datetime  
    size : str  
}

endpoint => POST '/api/product/'  

response

```
{
    "meta": {
        "code": 201,
        "message": "objects create success"
    },
    "data": {
        "category": "asf",
        "name": "asdf",
        "size": "L",
        "cost": 1234,
        "price": 12345,
        "des": "asdfasdf",
        "expiration_date": "2023-04-25T17:39:00+09:00",
        "barcode": "/images/asdf.png"
    }
}
```


### 속성 부분수정

schma => {  
    category : str not require  
    price : int not require  
    cost : int not require  
    name : str not require  
    des : str not require   
    expiration_date : datetime.datetime not require  
    size : str not require  
}

endpoint => PATCH '/api/product/<int: pk>'

response

```
{
    "meta": {
        "code": 201,
        "message": "ok"
    },
    "data": {
        "category": "테스트용으로바꿈",
        "name": "테스트용으로바꿈",
        "size": "L",
        "cost": 1234,
        "price": 12345,
        "des": "asdfasdf",
        "expiration_date": "2023-04-25T17:39:00+09:00"
    }
}
```


### 상품 삭제

schma => {}  

endpoint => DELETE '/api/product/<int: pk>'

response
```
{
    "meta": {
        "code": 200,
        "message": "ok"
    },
    "data": null
}
```

### 리스트

schma => {}  

endpoint => GET '/api/product/'

cursor based pagination 기반으로 구현했습니다. django-rest-framework의 CursorPagination를 상속받아 구현했습니다.

response
```
{
    "meta": {
        "code": 200,
        "message": "cursor based list view"
    },
    "data": {
        "next": "http://127.0.0.1:8000/api/product/?cursor=cD0xMA%3D%3D",
        "previous": null,
        "results": [
            ...
            {
                "category": "음료",
                "name": "연유 라떼",
                "size": "S",
                "cost": 5000,
                "price": 10000,
                "des": "달달한 연유 라떼",
                "expiration_date": "2023-04-30T13:26:47+09:00",
                "barcode": "/images/%EC%97%B0%EC%9C%A0%EB%9D%BC%EB%96%BC.png"
            },
            ...
        ]
    }
}
```

### 상품 상세 내역

schma => {}  

endpoint => GET '/api/product/<int:pk>'

response 
```
{
    "meta": {
        "code": 200,
        "message": "ok"
    },
    "data": {
        "category": "음료",
        "name": "슈크림 라떼",
        "size": "S",
        "cost": 5000,
        "price": 10000,
        "des": "달달한 슈크림 라떼",
        "expiration_date": "2023-04-30T13:26:47+09:00"
    }
}

{
    "meta": {
        "code": 204,
        "message": "no content"
    },
    "data": null
}
```

### 이름 기반 검색

schma => {}  

endpoint => GET '/api/product/search/?q=<str:query>'

일반 검색, 초성 검색 모두 지원합니다.

```
class ProductSearchView(APIView):

    ...

    def get_queryset(self, condition: Q = None):
        if not condition:
            condition = Q()

        return Product.objects.filter(condition)

    def get(self, request):
        string = request.query_params.get('q')
        q = Q()
        q |= Q(name__icontains=string)
        q |= Q(initial_set__icontains=string)

        query_set = self.get_queryset(q)

        if query_set.count() == 0:
            return create_response_msg(status.HTTP_204_NO_CONTENT, 'no content')

        serializer = ProductSerializer(query_set, many=True)

        return create_response_msg(status.HTTP_200_OK, 'search result', data=serializer.data)

    ...

```

django orm을 활용해 LIKE 검색을 구현했습니다. 초성으로 미리 바꿔 저장한 덕분에 쉽게 할 수있었습니다.


### 접근제한

```
REST_FRAMEWORK = {
    ...

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

   ...
}

```

로그인, 로그아웃 회원가입을 제외한 모든 api는 접근제한이 설정되었습니다.

