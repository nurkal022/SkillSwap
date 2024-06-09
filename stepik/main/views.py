from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from Register.decorators import *
from selenium import webdriver
from django.core.mail import send_mail, BadHeaderError
import smtplib
from email.mime.text import MIMEText

from .forms import MyModelForm
from django.http import JsonResponse
import requests
from django.db.models import Avg


def mainpage(request):
    
    menu = Course.objects.all()
    cats = Category.objects.all()
    context = {
        'title': 'Main Page',
        'menu': menu,
        'cats': cats,
    }
    return render(request,'main/base.html', context=context)

# @allowed_users(allowed_roles=['moderator'])
def catalogue(request): #, cat_id = 0
    
    menu = Course.objects.filter(is_published=True)
    cats = Category.objects.all()
    
    context = {
        'title': 'Catalogue',
        'menu': menu,
        'cats': cats,
        'cat_selected': 0,
    }
    return render(request, 'main/catalogue.html', context=context)

def category(request, cat_id):
    courses = Course.objects.filter(cat_id=cat_id, is_published=True)
    cats = Category.objects.all()

    context = {
        'courses': courses,
        'cats': cats,
        'cat_selected': cat_id,

    }
    return render(request, 'main/category.html', context)




@login_required
# @allowed_users(allowed_roles=['teacher'])
def create(request):
    id = request.user.pk
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES, initial={'idUser': id}) #2
        if form.is_valid():
            try:
                form.save()
                return redirect('mainpage')
            except:
                form.add_error(None, "Error at adding Course")
    else:
        form = AddPostForm(initial={'idUser': id})
    context = {
        'title': 'Create Course',
        'form': form,
    }
    return render(request, 'main/create.html', context=context)

# @login_required
# # @allowed_users(allowed_roles=['teacher'])
# def create_lesson(request, id):
#     if request.method == 'POST':
#         form = AddLessonForm(request.POST, request.FILES, initial={'idCourse': id})
#         if form.is_valid():
#             try:
#                 form.save()
#                 return redirect( f'/coursepage/{id}' )
#             except:
#                 form.add_error(None, "Error at adding Lesson")
#     else:
#         form = AddLessonForm(initial={'idCourse': id})
#     context = {
#         'title': 'Create lesson',
#         'form': form,
#         'id': id,
#     }
#     return render(request, 'main/create_lesson.html', context=context)
    

# @login_required
# def coursepage(request, id):
#     user = request.user.pk
#     videos = Video.objects.filter(idCourse=id)
#     menu = Course.objects.filter(id=id)
#     lesson = LessonContainer.objects.filter(idUser=user, idCourse=id)
#     author = User.objects.filter(pk = menu[0].idUser).first()
    
#     post = get_object_or_404(Course, id=id)
#     comments = post.comments.filter(active=True)
#     new_comment = None    # Comment posted
#     if request.method == 'POST':
#         comment_form = CommentForm(data=request.POST)
#         if comment_form.is_valid():
#             # Create Comment object but don't save to database yet
#             new_comment = comment_form.save(commit=False)
#             # Assign the current post to the comment
#             new_comment.post = post
#             # Save the comment to the database
#             new_comment.save()
#     else:
#         comment_form = CommentForm()
        
        
#     context = {
#         'title': "Coursepage",
#         'menu': menu,
#         'videos': videos,
#         'id': id,
#         'lesson': lesson,
#         'comments': comments,
#         'new_comment': new_comment,
#         'comment_form': comment_form,
#         'author': author,
#     }
#     return render(request, 'main/coursepage.html', context=context)

@login_required
def coursepage(request, id):
    user = request.user
    videos = Video.objects.filter(idCourse=id)
    menu = Course.objects.filter(id=id)
    lesson = LessonContainer.objects.filter(idUser=user.pk, idCourse=id)
    author = User.objects.filter(pk=menu[0].idUser).first()

    post = get_object_or_404(Course, id=id)
    comments = post.comments.filter(active=True)
    new_comment = None    # Comment posted

    # Check if the user has already commented by checking the cookie
    cookie_key = f'has_commented_before_{user.pk}_{id}'
    has_commented_before = request.COOKIES.get(cookie_key, False)

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            if not has_commented_before:
                # User is commenting for the first time
                # Add coins to the user's account
                user.learner.coins += 5
                user.learner.save()

                context = {
                    'title': "Coursepage",
                    'menu': menu,
                    'videos': videos,
                    'id': id,
                    'lesson': lesson,
                    'comments': comments,
                    'new_comment': new_comment,
                    'comment_form': comment_form,
                    'author': author,
                }

                # Set a cookie to remember that the user has commented
                response = render(request, 'main/coursepage.html', context=context)
                response.set_cookie(cookie_key, True)
                return response

            # User has commented before
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    context = {
        'title': "Coursepage",
        'menu': menu,
        'videos': videos,
        'id': id,
        'lesson': lesson,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'author': author,
    }
    return render(request, 'main/coursepage.html', context=context)



@login_required
def lesson(request, id):
    user = request.user.pk

    videos = Video.objects.filter(idCourse=id)
    menu = Course.objects.filter(id=id)
    lesson = LessonContainer.objects.filter(idUser=user, idCourse=id)
    
    
    context = {
        'title': "Coursepage",
        'menu': menu,
        'videos': videos,
        'id': id,
        'lesson': lesson,
    }
    return render(request, 'main/lessonpage.html', context=context)



@login_required
def profile(request):
    user = request.user.pk
    course = Course.objects.filter(idUser=user)
    container = LessonContainer.objects.filter(idUser=user)
    UserChoice = Course.objects.all()
    # group = request.user.groups.all()[0].name
    context = {
        'title': "Profile page",
        'course': course,
        'container': container,
        'UserChoice': UserChoice,
        'group': "",
    }
    return render(request, 'main/profile.html', context=context)




# def searchbar(request):
#     if request.method == 'GET':
#         search = request.GET.get('search')
#         post = Course.objects.all().filter(title__contains=search, is_published=True)
#         return render(request, 'main/searchbar.html', {'post': post})

def searchbar(request):
    cats = Category.objects.all()
    if request.method == 'GET':
        search = request.GET.get('search')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        min_rating = request.GET.get('min_rating')
        category = request.GET.get('category')
        
        # Base queryset
        queryset = Course.objects.all().filter(title__contains=search, is_published=True)

        
        if category:
            queryset = queryset.filter(cat=category)
        print('CATEGORY: ', category)    
                                           
        # Apply price filter
        if min_price is not None and min_price.isdigit():
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price is not None and max_price.isdigit():
            queryset = queryset.filter(price__lte=float(max_price))

        # Apply average rating filter
        if min_rating is not None and min_rating.isdigit():
            queryset = queryset.annotate(avg_rating=Avg("comments__rate")).filter(avg_rating__gte=float(min_rating))

        return render(request, 'main/searchbar.html', {'post': queryset,  'cats': cats})




# def accountSettings(request):
#     post = Learner.objects.all().filter(user_id=request.user.pk)
#     if post:
#         print(post)
#         user = request.user.learner
#     else:
#         Learner.objects.create(user_id=request.user.pk, name=request.user.username, coins=100)
#         user = request.user.learner

#     form = UpdateUserForm(instance=user)

#     if request.method == "POST":
#         form = UpdateUserForm(request.POST, request.FILES, instance=user)
#         if form.is_valid():
#             form.save()
#             return redirect('profile')
#         else:
#             print(form.errors)
            
#     context = {
#         'title': "Edit Profile page",
#         'form': form,

#     }
#     return render(request, 'main/accountSettings.html', context=context)
def accountSettings(request):
    try:
        user = request.user.learner
    except:
        user = Learner.objects.create(user=request.user, coins=100)    

    form = UpdateUserForm(request=request, instance=user)

    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=user, request=request)
        if form.is_valid():
            form.save()

            # Check if Instagram and TikTok cookies are already set for the user
            instagram_cookie_set = request.COOKIES.get(f'instagram_added_coins_{request.user.pk}', False)
            tiktok_cookie_set = request.COOKIES.get(f'tiktok_added_coins_{request.user.pk}', False)

            if form.cleaned_data.get('instagram') and not instagram_cookie_set:
                user.coins += 50
                user.save()
                response = redirect('profile')
                response.set_cookie(f'instagram_added_coins_{request.user.pk}', True)
                return response

            if form.cleaned_data.get('tiktok') and not tiktok_cookie_set:
                user.coins += 50
                user.save()
                response = redirect('profile')
                response.set_cookie(f'tiktok_added_coins_{request.user.pk}', True)
                return response
            return redirect('profile')
    context = {
        'title': "Edit Profile page",
        'form': form,
    }
    return render(request, 'main/accountSettings.html', context=context)


def add_course_to_user(request, id):
    
    course = Course.objects.filter(pk = id).first()
    usera = User.objects.filter(id = course.idUser).first()
    if request.user.learner.coins >= course.price:
        # request.user.learner.coins -= course.price
        # usera.learner.coins += course.price
        # request.user.learner.save() 
        # usera.learner.save()
        pass
    else:
        return redirect('profile')      
    if course.price > 0:
        context = {'cost': course.price, 'id': id}
        return render(request, 'main/payment.html', context) 
    else:  
        user = request.user.pk
        lesson = LessonContainer.objects.create(idUser=user, idCourse=id)
        return redirect('profile')    
        
        
        
def pay(request, id):  
    course = Course.objects.filter(pk = id).first()
    usera = User.objects.filter(id = course.idUser).first()
    if request.user.learner.coins >= course.price:
        request.user.learner.coins -= course.price
        usera.learner.coins += course.price
        request.user.learner.save() 
        usera.learner.save() 
    user = request.user.pk
    lesson = LessonContainer.objects.create(idUser=user, idCourse=id)
    name = Course.objects.filter(pk = id)
       
    return redirect('profile')
    


def remove_course(request, id):
    context = {
        'id': id,
    }
    return render(request, 'main/remove_course.html', context)
    


def delete_course_from_user(request, id):
    user = request.user.pk
    lesson = LessonContainer.objects.filter(idUser=user, idCourse=id).delete()
    return redirect('profile')
    
    
    
    
    
    
    
    
def delete_course(request, id):
    user = request.user.pk
    course = Course.objects.filter(pk=id).delete()
    return redirect('profile')



@allowed_users(allowed_roles=['moderator'])
def accept_course(request, id):
    
    course = get_object_or_404(Course, pk=id)
    if course.is_published == True:
        course.is_published = False
    else:
        course.is_published = True      
    course.save()
    return redirect('moderator')



@allowed_users(allowed_roles=['moderator'])
def moderator(request):
    group = request.user.groups.all()[0].name
    course = Course.objects.filter(is_published=False)

    context = {
        'title': 'Moderator page',
        'group': group,
        'course': course,
    }

    return render(request, 'main/moderator.html', context)



@login_required
def send_message(request):
    u_name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    message = request.POST.get('message', '')
   
    message = "Name: " + u_name + "\nEmail: " + email + "\nPhone: " + phone + "\nMessage: " + message
    telegram_bot_id = "5970994672:AAHR5Mux2ikEkRm5VmHK-s--LBSsCK_1x6k"
    chat_id = -1001821458102
    data = {
        "chat_id": chat_id,
        "text": message
    }

    
    url = "https://api.telegram.org/bot" + telegram_bot_id + "/sendMessage"
    response = requests.post(url, json=data)
    # return JsonResponse({'status': response.status_code})    
    return render(request, 'main/base.html')



def my_view(request, id):
    my_model_instance = Cart(idUser = request.user.pk, idCourse = id)
    my_model_instance.save()
        
    user = request.user.pk
    videos = Video.objects.filter(idCourse=id)
    menu = Course.objects.filter(id=id)
    lesson = LessonContainer.objects.filter(idUser=user, idCourse=id)
    context = {
        'title': "Coursepage",
        'menu': menu,
        'videos': videos,
        'id': id,
        'lesson': lesson,
    }    
    return render(request, 'main/coursepage.html', context)



def top_page(request):
    courses_list = Course.objects.annotate(avg_rating=Avg('comments__rate')).order_by('-avg_rating')
    return render(request, 'main/top_page.html', {'courses_list': courses_list})

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from datetime import datetime, timedelta
import random
# @login_required
# def game(request):
#     score = request.POST.get('score', 0)  # Assuming you send the score as a POST parameter
#     request.user.learner.coins += int(score)
#     request.user.learner.save()

#     return render(request, 'main/game.html', {'score': score})
@login_required
def game(request):
    # Check the number of times the user has played today
    user_key = f"game_access_{request.user.id}"
    access_count = cache.get(user_key, 0)

    questions = Question.objects.all()
    random_question = random.choice(questions) if questions else None
    
    # Allow access only twice a day
    if access_count < 2:
        # Increment the access count and set it to expire at the end of the day
        cache.set(user_key, access_count + 1, timeout=timedelta(days=1).total_seconds())
        
        return render(request, 'main/game.html', {'question': random_question})
    else:
        # Calculate the remaining time until the next try
        current_time = datetime.now()
        end_of_day = datetime(current_time.year, current_time.month, current_time.day, 23, 59, 59)
        remaining_time = end_of_day - current_time
        return render(request, 'main/game_limit_exceeded.html', {'remaining_time': remaining_time})


def check_answers(request, id):
    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        correct_answer = Question.objects.get(pk = id).correct_answer

        print('user: ', user_answer)
        print('correct: ', correct_answer)
        
        if user_answer == correct_answer:
            # Update user's coins if the answer is correct
            request.user.learner.coins += 30
            request.user.learner.save()

    return redirect('game')


def notifications(request):
    
    latest_courses = Course.objects.filter(is_published=True).order_by('-created_at')[:5]

    context = {
        'latest_courses': latest_courses,
    }
    
    return render(request, 'main/notifications.html', context)