# 0513 Django Project4

> 2인 1조 팀플 영화 게시판 만들기. 팔로우, 좋아요 기능 추가



### 작성 과정

> 구현에 앞서서 먼저 대략적인 구상을 먼저 했음.
>
> Movie를 따로 모델로 만들어서 ,
>
> 1차적으로 메인 인덱스 화면에 보여주고 ,
>
> 각 영화에 따른 리뷰와 그 리뷰에 대한 댓글들을 작성.
>
> 로그인 기능은 따로 크게 기존 내용에서 달라지는 것이 없다. 

#### CURD 기능 구현, Comment, 좋아요

1. 기존 CRUD 기능을 구현하기에 앞서 Movie모델을 만든다.
   * Review모델에 movie 외래키를 추가했다. (movie : review = 1:N)
2. Movie 모델에 필드를 만들 때에는 포스터 url을 저장할 때 __이미지 주소복사__값을 넣어야 한다.
3. Movie모델은 관리자가 생성,수정,삭제를 관리하므로 따로 forms.py를 만들지 않았다!!
   * `python manage.py createsuperuser`로 관리자 설정 후 Movie정보 넣기.
4. 모든 CRUD기능에 url을 넣을 때, 앞서 제일 처음에 어떤 영화의 리뷰이며 그 리뷰의 댓글인지 구분해주기 위해서 url앞에 < int:movie_pk >으로 시작했다.

* urls.py

```python
from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.index, name= 'index'),
    path('<int:movie_pk>/review_list/', views.review_list, name= 'review_list'),
    path('<int:movie_pk>/create/', views.create, name= 'create'),
    path('<int:movie_pk>/<int:review_pk>/detail/', views.detail, name= 'detail'),
    path('<int:movie_pk>/<int:review_pk>/update/', views.update, name= 'update'),
    path('<int:movie_pk>/<int:review_pk>/delete/', views.delete, name= 'delete'),
    path('<int:movie_pk>/<int:review_pk>/comments/', views.comment_create, name= 'comment_create'),
    path('<int:movie_pk>/<int:review_pk>/comments/<int:comment_pk>/delete/', views.comment_delete, name= 'comment_delete'),
    path('<int:movie_pk>/<int:review_pk>/like/', views.like, name="like"),
]
```

5. views에서 함수를 구현할 때 모두 movie_pk를 가 필요한지 고려해서 코드짜기

* views.py

  `review.movie = movie` 처럼  왜래키 movie에 대한 값도 따로 넣어주기

```python
def create(request, movie_pk ):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            # 여기처럼 왜래키 movie에 대한 값도 따로 넣어주기
            review.movie = movie
            review.save()

            return redirect('community:review_list', movie.pk)
    else:
        review_form = ReviewForm()
    context = {
        'review_form' : review_form,
        'movie':movie,

    }
    return render(request,'community/form.html',context)

```

6. 좋아요는 Review에 좋아요를 표시하는 것이므로 Review에 like_users 필드를 만든다.
7. like함수에서도 마찬가지로 movie_pk를 고려해주고, 사용자가 좋아요한 사람들에 속해있으면 버튼을 눌렀을 때 쿼리셋에서 제거하고 그 반대도 하는 방식으로 구현

```python
def like(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user.is_authenticated :
        if review.like_users.filter(id=request.user.pk).exists():
            review.like_users.remove(request.user)
        else:
            review.like_users.add(request.user)

    else :
        return redirect('accounts:login')

    return redirect('community:detail', movie_pk, review_pk)
```



#### Login, Follow 기능

1. 먼저 커스텀된 유저를 사용하기 위해

settings 맨 끝에 `AUTH_USER_MODEL = 'accounts.User'`추가

```python
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    image = models.ImageField(blank=True)

    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='followings'
        )
```

2. 커스텀된 유저폼을 이용하기 위해 UserCreationForm을 상속받아 만듬

```python
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username','first_name','last_name','email', 'image']
```

3. migrate 후
4. url들은 movie를 따로 고려해줄 필요 없다.
5. 마찬가지로 views.py에서도 기존과 동일한 방식으로 로그인,로그아웃,회원가입 함수를 구현
6. profile을 만들어서 팔로우,팔로잉을 표시함

```python
@login_required
def profile(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username )

    context={
        'person':user,
    }
    return render(request, 'accounts/profile.html', context)

```

7. 팔로우 기능을 추가하기 위해

> 나.followers : '나'가 팔로우하는 사람

> 나.followings : '나'를 팔로우 하는 사람 

```python
@login_required
def follow(request, username ):
    you = get_object_or_404(get_user_model(), username=username )
    me = request.user

    if you != me :
        if you.followings.filter(pk=me.pk).exists():
            you.followings.remove(me)

        else:
            you.followings.add(me)

    return redirect('accounts:profile', you.username )
```





### 추가 구현 사항

* index.html

  카드를 사용하여 영화 게시판을 훨씬 보기 좋게 만들었다.

  

* profile.html

  1. 프로필 이미지를 기본 이미지로 넣어주었다.
  2. 팔로잉,팔로워를 따로 표시

```html
  <p>내가 팔로우 하고 있는 사람들 follower</p>
  {%for follower in person.followers.all %}
  <p>{{follower}}</p>
  {%endfor%}
  <hr/>
  <p>나를 팔로우 하고 있는 사람들 followings</p>
  {%for following in person.followings.all %}
  <p>{{following}}</p>
  {%endfor%}
```

을 추가하여 내가 팔로우하는 사람과, 나를 팔로우 하는 사람의 아이디를 표시하였다.



---

### 어려웠던 점

1. 처음에 Movie를 어떻게 구현해야 할지
2. 모든 url에서 movie.pk를 고려해줘야 할지
3. movie와 review의 관계 고려
4. review를 만들 때 movie 키값을 넣어줘야 했던 점
5. 인덱스에 카드형식을 사용하기 위해 이미지를 넣을 때 url을 가져올 때 고려
6. 전체적으로 중간마다 크고 작은 실수들
7. 사용자의 프로필 이미지를 넣고싶은데 static을 사용하는 법

---

### 페어프로그래밍에서 느낀 점

1. 협업은 소통이 정말 중요하다.

2. 실력차이가 나도 그런대로 서로 배울 점이 각각 있다.

3. 혼자 하는 것 보다 의지가 되고 좋다.

   