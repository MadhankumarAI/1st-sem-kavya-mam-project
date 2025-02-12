from django.shortcuts import render
from djcelery.views import JsonResponse
from openid.server.server import HTTP_OK
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import *
from django.contrib.auth.decorators import login_required

@login_required
def public_chat(request):

    rooms = chatGroup.objects.all()
    messages = Messages.objects.all().order_by('createdAt')

    return render(request, 'groupchat/gc.html', {
        'messages': messages,
        'rooms': rooms,  # Pass the list of usernames
    })

def createGroup(request):
    data = request.data
    if not data['group']:
        return Response(status=HTTP_400_BAD_REQUEST)
    else:
        obj = chatGroup.objects.filter(roomName=data['group'])
        if obj is not None:
            return Response(status=HTTP_400_BAD_REQUEST)
        obj = chatGroup.objects.create(roomName=data['group'])
        obj.save()
        return Response(status=HTTP_OK)
