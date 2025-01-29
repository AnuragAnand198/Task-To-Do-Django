from sqlite3 import IntegrityError
from this import d
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.


def signupuser(req):
    if req.method == 'GET':
        return render(req, 'todo/signupuser.html', {'form': UserCreationForm()})
    if req.method == 'POST':
        if req.POST['password1'] == req.POST['password2']:
            try:
                user = User.objects.create_user(
                    req.POST['username'], password=req.POST['password1'])
                user.save()
                login(req, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(req, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Username already Exist.'})

        else:
            return render(req, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords did not match'})


def home(req):
    return render(req, 'todo/home.html')


@login_required
def currenttodos(req):
    todos = Todo.objects.filter(user=req.user, datecompleted__isnull=True)
    return render(req, 'todo/currenttodos.html', {'todos': todos})


@login_required
def completedtodos(req):
    todos = Todo.objects.filter(
        user=req.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(req, 'todo/completedtodos.html', {'todos': todos})


@login_required
def logoutuser(req):
    if req.method == 'POST':
        logout(req)
        return redirect('home')


def loginuser(req):
    if req.method == 'GET':
        return render(req, 'todo/loginuser.html', {'form': AuthenticationForm()})
    if req.method == 'POST':
        user = authenticate(
            req, username=req.POST['username'], password=req.POST['password'])
        if user is None:
            return render(req, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and Password did not match'})
        else:
            login(req, user)
            return redirect('currenttodos')


@login_required
def createtodo(req):
    if req.method == 'GET':
        return render(req, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(req.POST)
            newtodo = form.save(commit=False)
            newtodo.user = req.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(req, 'todo/createtodo.html', {'form': TodoForm(), 'error': 'Bad data enetered'})


@login_required
def viewtodo(req, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=req.user)
    if req.method == 'GET':
        form = TodoForm(instance=todo)
        return render(req, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(req.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(req, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad data entered'})


@login_required
def completetodo(req, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=req.user)
    if req.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(req, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=req.user)
    if req.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.delete()
        return redirect('currenttodos')
