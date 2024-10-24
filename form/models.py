# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class DeliveryMethod(models.Model):
    delivery_method_no = models.AutoField(db_column='Delivery_Method_no', primary_key=True)  # Field name made lowercase.
    method_name = models.CharField(db_column='Method_name', max_length=50)  # Field name made lowercase.
    add_date_time = models.DateTimeField(db_column='Add_Date_Time', blank=True, default=timezone.now)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=8 , choices = [        
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ], default='active') # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'delivery_method'
    def __str__ (self):
        return self.method_name


class Frequency(models.Model):
    frequency_no = models.AutoField(primary_key=True)
    interval_type = models.CharField(max_length=10, choices =[   
        ('Hourly', 'Hourly'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),])
    interval_value = models.IntegerField()
    extended_frequency_boolean = models.BooleanField(db_column = 'Extended_Frequency_Boolean', default= False)
    extended_frequency_value = models.IntegerField(db_column= 'Extended_Frequency', blank = True, null= True)
    description = models.CharField(max_length=191)
    add_date_time = models.DateTimeField(db_column='Add_Date_Time', blank=True, default=timezone.now)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=8, choices = [        
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ], default='active')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'frequency'
    def __str__ (self):
        return self.description


class IssueTypes(models.Model):
    issue_type_no = models.AutoField(db_column='Issue_Type_no', primary_key=True)  # Field name made lowercase.
    issue_type = models.CharField(db_column='Issue_Type', max_length=50)  # Field name made lowercase.
    add_date_time = models.DateTimeField(db_column='Add_Date_Time', blank=True, default=timezone.now)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=8, choices = [        
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ], default='active')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'issue_types'
    def __str__ (self):
        return self.issue_type

class Task(models.Model):
    task_id = models.AutoField(db_column='Task_id', primary_key=True)  # Field name made lowercase.
    subject = models.CharField(db_column='Subject', max_length=191)  # Field name made lowercase.
    content = models.TextField(db_column='Content')  # Field name made lowercase.
    issue_type = models.ForeignKey(IssueTypes, on_delete= models.CASCADE, db_column= 'Issue_Type')  # Field name made lowercase.
    add_date_time = models.DateTimeField(db_column='Add_Date_Time', blank=True, default=timezone.now)  # Field name made lowercase.
    start_date = models.DateTimeField(db_column='Start_Date')  # Field name made lowercase.
    end_date = models.DateTimeField(db_column='End_Date', blank=True, null=True)  # Field name made lowercase.
    due_date = models.DateTimeField(db_column='Due_Date', blank=True, null=True)  # Field name made lowercase.
    frequency = models.ForeignKey(Frequency, on_delete= models.CASCADE, db_column= 'Frequency')  # Field name made lowercase.
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete= models.CASCADE, db_column= 'Delivery_Method')  # Field name made lowercase.
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(db_column='Status', max_length=8, choices = [        
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ], default='active')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'task'


class TaskLog(models.Model):
    tasklog_id = models.AutoField(primary_key=True, db_column='TaskLog_id') 
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)  # Field name made lowercase.
    subject = models.CharField(db_column='Subject', max_length=191)  # Field name made lowercase.
    content = models.TextField(db_column='Content')  # Field name made lowercase.
    issue_type = models.ForeignKey(IssueTypes, on_delete= models.CASCADE, db_column= 'Issue_Type')  # Field name made lowercase.
    due_date = models.DateTimeField(db_column='Due_Date', blank=True, null=True)  # Field name made lowercase.
    frequency = models.ForeignKey(Frequency, on_delete= models.CASCADE, db_column= 'Frequency')  # Field name made lowercase.
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete= models.CASCADE, db_column= 'Delivery_Method')  # Field name made lowercase.
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sent_date_time = models.DateTimeField(db_column='Sent_Date_Time', blank = True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'task_log'

class TaskDetails(models.Model):
    comment_id = models.AutoField(primary_key=True, db_column='comment_id') 
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_date = models.DateTimeField(db_column='Comment_Date', default=timezone.now)
    comments = models.TextField(db_column='Comments')
    status = models.CharField(db_column='Status', max_length=15)
    
    class Meta:
        managed =True
        db_table = 'task_details'