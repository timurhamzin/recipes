class Purchase(View, LoginRequiredMixin):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        result = JsonResponse({'success': False})
        request_body = json.loads(request.body)
        recipe_id = request_body.get('id')
        if recipe_id is not None:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            cart_obj, created = ShoppingCart.objects.get_or_create(
                recipe=recipe, user=request.user)
            if created:
                result = JsonResponse({'success': True})
        else:
            result = JsonResponse({'success': False}, 400)
        return result

    def delete(self, request, recipe_id):
        cart_obj = get_object_or_None(ShoppingCart, recipe__id=recipe_id,
                                      user=request.user)
        if cart_obj is not None:
            cart_obj.delete()
        return JsonResponse({'success': True})

    @staticmethod
    def is_purchased(recipe, user):
        item = get_object_or_None(ShoppingCart, user=user, recipe=recipe)
        return item is not None
