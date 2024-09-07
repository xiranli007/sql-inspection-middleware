from .models import Product
import json
from django.http import JsonResponse
from django.core.serializers import serialize


# Create your views here.
def home(request):
    q = Product.objects.all()
    serialized_data = serialize('json', q) # where the query was performed (django "lazy query action")
    serialized_data = json.loads(serialized_data) # the json_load function take the json reponse and turn it into a python dictionary
    return JsonResponse(serialized_data, safe= False, status = 200)

