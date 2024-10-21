from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, TemplateView
from .models import Task, IssueTypes, DeliveryMethod, TaskLog, Frequency, TaskDetails
from datetime import datetime
from django.core.paginator import  Paginator
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Success Page To Test Out Pages

class SuccessView(TemplateView):
    template_name = 'form/success.html'

# Details of an Specific Task 

class IssueDetailView(DetailView):
    model = Task
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()  # The task being viewed
        context['cmts'] = TaskDetails.objects.filter(task_id=task)  # Add comments to the context
        return context
    def post(self, request, *args, **kwargs):
        task = self.get_object()
        commentContent = request.POST.get('commentContent')
        commentStatus = request.POST.get('commentStatus')
        TaskDetails.objects.create(
            task_id = task,
            user = request.user,
            comments = commentContent,
            status = commentStatus
        )
        task.status = commentStatus
        task.save()

        messages.success(request, 'Comment  Successfully Created!')
        return redirect('task_detail', pk=task.pk)

# Searching For Content 
@login_required
def searchContent(request):
    message = ''
    query = request.GET.get('query')
    results = []
    if query:
        results = Task.objects.filter(content__icontains = query)
  #  paginator = Paginator(results, 10)  # Show 10 results per page
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    if len(results) == 0:
        message = 'Error: Data Requested Is Not Found!'
    paginator = Paginator(results, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'results': results , 
        'query': query,
        'message': message,
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
    }
    return render(request, 'form/search.html',  context)

#Filtering the reports -------------------------
@login_required
def filterContent(request):
    filtResults = []
    filterValue = request.GET.get('filters')
    filterSearchValue = request.GET.get('filterInput')
    filterTime = request.GET.get('filterDate')
    message =""
    current_date = timezone.now().date()
    filtResults = Task.objects.none() 
    foreign_key_fields = {
        'issue_type': 'issue_type__issue_type',
        'delivery_method': 'delivery_method__method_name',
        'recipient':'recipient__recipient',
        'frequency': 'frequency__description'
    }

    if filterValue:
        # If a filterValue is provided, check if filterSearchValue is empty
        if not filterSearchValue:
            message = "Error: Please enter a value for the selected filter!"
        else:
            if filterValue == "add_date_time":
                try:
                    range1 = datetime.strptime(filterSearchValue, "%Y-%m-%d %H:%M:%S")
                    range2 = datetime.strptime(filterTime, "%Y-%m-%d %H:%M:%S")
                    filtResults = Task.objects.filter(add_date_time__range= (range1, range2 ))
                except ValueError:
                    message = "Invalid date format. Please use YYYY-MM-DD HH:MM:SS ."
            else:
                if filterValue in foreign_key_fields:
                    filter_kwargs = {f"{foreign_key_fields[filterValue]}__icontains": filterSearchValue}
                    filtResults = Task.objects.filter(**filter_kwargs)
                else:
                    filter_kwargs={f"{filterValue}__icontains":filterSearchValue}
                    filtResults = Task.objects.filter(**filter_kwargs)  

            if not filtResults.exists():
                message = "Error: No tasks found matching the criteria!"

    elif not filterValue and not filterSearchValue:
        message = "Error: Please enter both filter type and value!"


    paginator = Paginator(filtResults, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {
        'filtResults': filtResults, 
        'filterSearchValue': filterSearchValue , 
        'filterValue':filterValue,
        'message': message,
        'page_obj': page_obj,
        'filterTime': filterTime,
        'total_pages': paginator.num_pages,
    }
    return render(request, 'form/filter.html', context)






#Reports on the first page --------------------
@login_required
def home(request):
    tasks = Task.objects.all()  
    paginator = Paginator(tasks, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {            
    'tasks': tasks,
    'page_obj': page_obj,
    'total_pages': paginator.num_pages,
    }
    return render(request, 'form/home.html', context)


#To Crate an Issue ---------------------------

@login_required
def create_issue(request):
    users = User.objects.all()
    if request.method == 'POST':
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        issue_type_value = request.POST.get('issue_type')
        start_date_value = request.POST.get('start_date')
        end_date_value = request.POST.get('end_date', None)
        due_date_value = request.POST.get('due_date', None)
        delivery_method_value = request.POST.get('delivery_method')
        interval_value_value = request.POST.get('interval_value')
        interval_type_value = request.POST.get('interval_type')
        extended_frequency_boolean = 1 if request.POST.get('addFreq') else 0
        if extended_frequency_boolean == 1:
            extended_frequency_value =  request.POST.get('changeOnce') 
        else:
            extended_frequency_value = None
        recipient_name = request.POST.get('recipient')
        recipient_value = User.objects.get(username=recipient_name)  # Fetch the User instance
        status = request.POST.get('status')
        
        try:
            start_date = datetime.strptime(start_date_value, '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(end_date_value, '%Y-%m-%dT%H:%M') if end_date_value else None
            due_date = datetime.strptime(due_date_value, '%Y-%m-%dT%H:%M') if due_date_value else None
        except ValueError:
            return render(request, 'form/task_form.html', {'error': 'Invalid date format', 'form_data': request.POST})
        
        # Create new records
        issue_type = IssueTypes.objects.create(
            issue_type=issue_type_value,
            add_date_time = timezone.now()
        )
        delivery_method = DeliveryMethod.objects.create(
            method_name=delivery_method_value,
            add_date_time = timezone.now()    
        )
        frequency = Frequency.objects.create(
            interval_value=interval_value_value,
            interval_type=interval_type_value,
            add_date_time = timezone.now(),
            extended_frequency_boolean = extended_frequency_boolean,
            extended_frequency_value = extended_frequency_value,
            description= 'Once Every ' + interval_value_value + ' ' + interval_type_value
        )
        
        # Create new Task record
        task = Task.objects.create(
            subject=subject,
            content=content,
            start_date=start_date,
            end_date=end_date,
            due_date=due_date,
            add_date_time = timezone.now(),
            frequency=frequency,
            issue_type=issue_type,
            delivery_method=delivery_method,
            recipient=recipient_value,
            status=status,
        )
        TaskLog.objects.create(
            task_id = task,
            subject = subject,
            content = content,
            issue_type = issue_type,
            frequency = frequency,
            delivery_method = delivery_method,
            recipient = recipient_value,
            sent_date_time = timezone.now()
        )
        messages.success(request, 'Task  Successfully Created!')
        return redirect('task_list')
    
    return render(request, 'form/task_form.html', {'users':users})

@login_required
def update_issue(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    users = User.objects.all()
    if request.method == 'POST':
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        issue_type_value = request.POST.get('issue_type')
        start_date_value = request.POST.get('start_date')
        end_date_value = request.POST.get('end_date', None)
        due_date_value = request.POST.get('due_date', None)
        delivery_method_value = request.POST.get('delivery_method')
        interval_value_value = request.POST.get('interval_value')
        interval_type_value = request.POST.get('interval_type')
        extended_frequency_boolean = 1 if request.POST.get('addFreq') else 0
        if extended_frequency_boolean == 1:
            extended_frequency_value =  request.POST.get('changeOnce') 
        else:
            extended_frequency_value = None
        recipient_name = request.POST.get('recipient')
        recipient_value = User.objects.get(username=recipient_name)  # Fetch the User instance
        status = request.POST.get('status')
        

        # Parse dates
        try:
            start_date = parse_datetime(start_date_value)
            end_date = parse_datetime(end_date_value) if end_date_value else None
            due_date = parse_datetime(due_date_value) if due_date_value else None
        except ValueError:
            return render(request, 'task_form.html', {'error': 'Invalid date format', 'task': task})




        # Update IssueType
        issue_type = get_object_or_404(IssueTypes, issue_type_no=task.issue_type.issue_type_no)
        issue_type.issue_type = issue_type_value
        issue_type.save()

        # Update DeliveryMethod
        delivery_method = get_object_or_404(DeliveryMethod, delivery_method_no=task.delivery_method.delivery_method_no)
        delivery_method.method_name = delivery_method_value
        delivery_method.save()

        # Update Frequency
        frequency = get_object_or_404(Frequency, frequency_no=task.frequency.frequency_no)
        frequency.interval_value = interval_value_value
        frequency.interval_type = interval_type_value
        frequency.extended_frequency_boolean = extended_frequency_boolean
        frequency.extended_frequency_value = extended_frequency_value
        frequency.description = f"Once Every {interval_value_value} {interval_type_value}"
        frequency.save()
    
        # Update the fields
        task.subject = subject
        task.content = content
        task.start_date = start_date
        task.end_date = end_date
        task.due_date = due_date
        task.recipient = recipient_value
        task.status = status

        # Save changes to the database
        task.save()
        last_log = TaskLog.objects.filter(task_id_id=task_id).order_by('-tasklog_id').first()
        sent_date_time = last_log.sent_date_time

        

        TaskLog.objects.create(
            task_id=task,
            subject=subject,
            content=content,
            issue_type=task.issue_type,
            frequency=task.frequency,
            delivery_method=task.delivery_method,
            sent_date_time = sent_date_time,
            recipient=recipient_value,
        )
        messages.success(request, 'Task  Successfully Updated!')
        return redirect('task_detail', pk=task.task_id)
    context = {
        'task':task,
        'users':users,
    }
    # If not POST, render the form with current data
    return render(request, 'form/update.html', context)

