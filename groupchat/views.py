from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED

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

    group_name = request.data.get('group')

    # Check if 'group' is provided and not empty
    if not group_name:
        return Response({"error": "Group name is required."}, status=HTTP_400_BAD_REQUEST)

    if chatGroup.objects.filter(roomName=group_name).exists():
        return Response({"error": "A group with this name already exists."}, status=HTTP_400_BAD_REQUEST)


    obj = chatGroup.objects.create(roomName=group_name)

    return Response({"message": "Group created successfully.", "group_id": obj.id}, status=HTTP_201_CREATED)
