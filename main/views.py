from django.shortcuts import render, redirect
from main.models import Datapoint, Dataset
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from main.forms import UserForm, DatasetForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
import json

#This annotation requires the request.user to be the same as the dataset.owner
def owner_required(function):
    def new_f(request, dataset_id):
        dataset = Dataset.objects.get(pk=dataset_id)
        if dataset.owner == request.user:
            return function(request, dataset_id)
        else:
            return redirect(index)
    return new_f

def viewer_required(function):
    def new_f(request, dataset_id):
        dataset = Dataset.objects.get(pk=dataset_id)
        if dataset.owner == request.user or request.user in dataset.viewers.all():
            return function(request, dataset_id)
        else:
            return redirect(index)
    return new_f

def index(request):
    own_datasets = []
    viewing_datasets = []
    if request.user.is_authenticated():
        own_datasets = Dataset.objects.filter(owner = request.user)
        viewing_datasets =  Dataset.objects.filter(viewers = request.user)
    return render(request,"main/index.html", {'own_datasets': own_datasets,'viewing_datasets' : viewing_datasets })

@login_required
def add_dataset(request):
    if request.method == 'POST':
        dataset_form = DatasetForm(data = request.POST)
        if dataset_form.is_valid():
            ds = dataset_form.save(commit=False)
            ds.owner = request.user
            ds.save()
            return redirect(index)
        else:
            return render(request,'main/add_dataset.html',{'dataset_form' : dataset_form})
    else:
        dataset_form = DatasetForm()
        return render(request,'main/add_dataset.html',{'dataset_form' : dataset_form})

@owner_required
def update_dataset(request, dataset_id):
    #update old dataposts
    for key in request.POST:
        if key.startswith('pk_'):
            pk = int(key[3:])
            dp = Datapoint.objects.get(pk=pk)
            if request.POST[key] == '-1':
                dp.delete()
            else:
                dp.value = request.POST[key]
                dp.save()
    #Get all new datapoints(all in the same field) and zip then in pairs of 2
    new_dps = request.POST.getlist('new_dp')
    dp_pairs = zip(*(iter(new_dps),) * 2)
    dataset = Dataset.objects.get(pk=dataset_id)
    for pair in dp_pairs:
        try:
            new_dp, created = Datapoint.objects.get_or_create(dataset=dataset,date=pair[0], defaults={'value': pair[1]})
            new_dp.value = pair[1]
            new_dp.save()
        except ValueError:
            pass
    return redirect(table,dataset_id)

@owner_required
def delete_dataset(request, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    dataset.delete()
    return HttpResponse("Dataset deleted")

@viewer_required
def dataset_overview(request, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    is_owner = False
    if dataset.owner == request.user:
        is_owner = True
    return render(request,'main/dataset_overview.html',{'is_owner':is_owner,'dataset':dataset})

@owner_required
def share(request, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    if request.method == "GET":
        viewers = dataset.viewers.all()
        return render(request, 'main/share.html',{'dataset': dataset, 'viewers':viewers})
    elif request.method == "POST":
        username = request.POST['username']
        user = User.objects.get(username=username)
        dataset.viewers.add(user)
        return redirect(share, dataset_id)

def suggest_user(request, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    viewers = dataset.viewers.all()
    query = request.GET['suggestion']
    user_names = get_user_names(max_result=8, starts_with=query,viewers=viewers)
    user_names = json.dumps(user_names)
    return HttpResponse(user_names)

@viewer_required
def remove_viewer(request, dataset_id):
    viewer_id = request.POST['viewer_id']
    viewer = User.objects.get(pk=viewer_id)
    dataset = Dataset.objects.get(pk=dataset_id)
    dataset.viewers.remove(viewer)
    return HttpResponse("Viewer removed")

@viewer_required
def table(request, dataset_id):
    dataset = Dataset.objects.get(pk = dataset_id)
    data = Datapoint.objects.filter(dataset = dataset)
    
    is_owner = False
    if dataset.owner == request.user:
        is_owner = True   
    return render(request,"main/table.html",{'is_owner':is_owner,'dataset':dataset, 'data': data})

def graph(request):
    if request.method == "GET":
        set_ids = [int(x) for x in request.GET['sets'].split(',')]
        labels = []

        for set_id in set_ids:
            ds = Dataset.objects.get(pk=set_id)
            datapoints = Datapoint.objects.filter(dataset=ds)
            for dp in datapoints:
                if not dp.date in labels:
                    labels.append(dp.date)

        all_values = []
        for set_id in set_ids:
            set_values = []
            ds = Dataset.objects.get(pk=set_id)
            datapoints = Datapoint.objects.filter(dataset=ds)
            for l in labels:
                found = False
                for dp in datapoints:
                    if l == dp.date:
                        found = True
                        set_values.append(dp.value)
                if not found:
                    set_values.append(0)
            all_values.append(set_values)

        
        labels =  map(str,labels)
        print all_values
        print labels

        return render(request,'main/graph.html',{'labels':labels, 'values':all_values})

@viewer_required
def return_json(request, dataset_id):
    if request.method == 'GET':
        dataset = Dataset.objects.get(pk=dataset_id)
        datapoints = Datapoint.objects.filter(dataset=dataset)
        data = serializers.serialize("json",datapoints)
        return HttpResponse(data, mimetype="application/json")

def get_user_names(max_result=0, starts_with='',viewers=[]):
    user_list = []
    names_list = []
    if starts_with:
        user_list = User.objects.filter(username__startswith=starts_with)
    else:
        user_list = User.objects.all()
    if max_result > 0:
        if len(user_list) > max_result:
            user_list = user_list[:max_result]
    for user in user_list:
        print user
        if not user in viewers:
            print user
            names_list.append(user.username)
    return names_list

#User functions 
def register(request):
    registered = False
    
    if request.method == "POST":
        user_form = UserForm(data = request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
    else:
        user_form = UserForm()

    context_dict = {'user_form' : user_form,'registered' : registered}
    return render(request, 'main/register.html', context_dict)

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if not user is None:
            login(request,user)
            return HttpResponseRedirect("/main")
        else:
            return render(request,'main/login.html',{'bad_details':True})

    else:
        return render(request,"main/login.html")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/main")
