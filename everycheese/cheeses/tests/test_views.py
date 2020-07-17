import pytest

from pytest_django.asserts import assertContains


from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from everycheese.users.tests.factories import UserFactory
from everycheese.users.models import User
from ..models import Cheese
from ..views import CheeseCreateView, CheeseDetailView, CheeseListView
from .factories import CheeseFactory

pytestmark = pytest.mark.django_db


def test_good_cheese_list_view_expanded(rf):
    url = reverse("cheeses:list")

    request = rf.get(url)
    callable_obj = CheeseListView.as_view()
    response = callable_obj(request)

    assertContains(response, "Cheese List")


def test_good_cheese_list(rf):
    request = rf.get(reverse("cheeses:list"))
    response = CheeseListView.as_view()(request)
    assertContains(response, "Cheese List")


def test_good_cheese_detail_view(rf):
    cheese = CheeseFactory()
    # NOTE THE KWARGS
    url = reverse("cheeses:detail", kwargs={"slug": cheese.slug})

    request = rf.get(url)

    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)

    assertContains(response, cheese.name)


@pytest.fixture
def user():
    return UserFactory()


def test_good_cheese_create_view(client, user):
    # Login the user to the request factory
    client.force_login(user)
    # Generate the url
    url = reverse("cheeses:add")
    # Get the response from Django
    response = client.get(url)
    # Confirm that we have a valid response
    assert response.status_code == 200


def test_cheese_list_contains_2_cheese(rf):
    cheese1 = CheeseFactory()
    cheese2 = CheeseFactory()

    request = rf.get(reverse("cheeses:list"))
    response = CheeseListView.as_view()(request)

    assertContains(response, cheese1.name)
    assertContains(response, cheese2.name)


def test_detail_contains_cheese_data(rf):
    cheese = CheeseFactory()
    url = reverse("cheeses:detail", kwargs={"slug": cheese.slug})
    request = rf.get(url)

    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)

    assertContains(response, cheese.name)
    assertContains(response, cheese.get_firmness_display())
    assertContains(response, cheese.country_of_origin.name)


def test_cheese_create_form_valid(client, user):
    client.force_login(user)
    form_data = {
        "name": "Paski Sir",
        "description": "A salty hard cheese",
        "firmness": Cheese.Firmness.HARD,
    }
    url = reverse("cheeses:add")
    response = client.post(url, form_data)

    cheese = Cheese.objects.get(name="Paski Sir")

    assert cheese.description == "A salty hard cheese"
    assert cheese.firmness == Cheese.Firmness.HARD
    assert cheese.creator == user

