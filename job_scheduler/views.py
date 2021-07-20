from django.http import Http404
from django.shortcuts import render

from .models import Job
import datetime


def index(request):
    job_list = Job.objects.order_by('-start_date')
    return render(request, 'job_scheduler/index.html', {'job_list': job_list})


def list_jobs(request):
    job_list = Job.objects.order_by('-start_date')
    return render(request, 'job_scheduler/list.html', {'job_list': job_list})


def detail(request, job_id):
    # return HttpResponse("You're looking at job %s." % job_id)
    try:
        job = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:  # noqa
        raise Http404("Job does not exist")
    return render(request, 'job_scheduler/detail.html', {'job': job})
