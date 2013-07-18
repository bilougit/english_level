# -*- coding: utf-8 -*-
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from dydict.models import Dict, Internaute

@login_required
def removeWords(request):
  if request.method == 'POST':
    try:
      dict2_remove = Dict.objects.get(
          internaute=Internaute.objects.get(user=request.user),
          id=request.POST['word_id'])
    except Dict.DoesNotExist:
      pass
    else:
      dict2_remove.delete()
      return HttpResponse('<h1>{0} removed</h1>'.format(request.POST['word']))
