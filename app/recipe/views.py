""" Views for Recipe API """
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient
)
from recipe import serializers
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient ids to filter'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """ View for manager recipe APIs """
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_into_ints(self, qs):
        """ Convert a list of strings into ints"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve recipers for authenticated user """
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_into_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_into_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        
        return queryset.filter(
            user= self.request.user,
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """ Return serializer class for the request """
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        
        return serializers.RecipeDetailSerializer

    def perform_create(self, serializer):
        """ create a new recipe """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ Upload an image to recipe """
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0,1],
                description='Integer value to filter the assigned tags/ ingredients to recipe',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    """ Base Recipe attributes viewset """
    authentication_classes = [TokenAuthentication]
    permission_classes =  [IsAuthenticated]

    def get_queryset(self):
        """ Filter queryset to authenticated user """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        
        if assigned_only:
            queryset.filter(recipe__isnull=False)
        
        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

class TagViewSet(BaseRecipeAttrViewSet):
    """ Manage tags in the viewsets """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    

class IngredientViewSet(BaseRecipeAttrViewSet):
    """ View for Ingredients API """
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()