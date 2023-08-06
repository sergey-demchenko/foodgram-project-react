from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .models import Recipe


def add_del_recipe(request, pk, serializer, model):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user

    if request.method == 'POST':
        serializer = serializer(
            recipe, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        model.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        model.objects.filter(
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)
