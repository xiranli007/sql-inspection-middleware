import factory
from factory.faker import faker
from .models import Product

# set up faker
FAKE = faker.Faker

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.Faker("sentence", nb_word=5)
    slug = factory.Faker("slug")
    # is_digital has a default value, no need to specify