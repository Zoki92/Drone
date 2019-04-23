from django.utils.http import urlencode
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from drones.models import DroneCategory, Pilot
from drones import views
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class DroneCategoryTests(APITestCase):
    def post_drone_category(self, name):
        url = reverse(views.DroneCategoryList.name)
        data = {'name': name}
        response = self.client.post(url, data, format='json')
        return response

    def test_post_and_get_drone_category(self):
        """
        Ensure we can create a new DroneCategory
        and then retrieve it
        """
        new_drone_category_name = "Hexacopter"
        response = self.post_drone_category(new_drone_category_name)
        assert response.status_code == status.HTTP_201_CREATED
        assert DroneCategory.objects.count() == 1
        assert DroneCategory.objects.get().name == new_drone_category_name

    def test_post_existing_drone_category_name(self):
        """
        Ensure we cannot create a duplicate DroneCategory
        """
        new_drone_category_name = 'Duplicated Copter'
        response1 = self.post_drone_category(new_drone_category_name)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.post_drone_category(new_drone_category_name)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_drone_category_by_name(self):
        """
        Ensure we can filter a drone category by name
        """
        drone_category_name1 = "Hexacopter"
        self.post_drone_category(drone_category_name1)
        drone_category_name2 = "Octocopter"
        self.post_drone_category(drone_category_name2)
        filter_by_name = {'name': drone_category_name1}
        url = "{0}?{1}".format(
            reverse(views.DroneCategoryList.name),
            urlencode(filter_by_name))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results']
                         [0]['name'], drone_category_name1)

    def test_get_drone_categories_collection(self):
        """
        Ensure we can retrieve the drone categories collection
        """
        new_drone_category_name = 'Super Copter'
        self.post_drone_category(new_drone_category_name)
        url = reverse(views.DroneCategoryList.name)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results']
                         [0]['name'], new_drone_category_name)

    def test_update_drone_category(self):
        drone_category_name = 'Category initial Name'
        response = self.post_drone_category(drone_category_name)
        url = reverse(
            views.DroneCategoryDetail.name,
            None,
            {response.data['pk']}
        )
        updated_drone_category_name = 'Updated name'
        data = {'name': updated_drone_category_name}
        patch_response = self.client.patch(url, data, format='json')
        self.assertEqual(patch_response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'],
                         updated_drone_category_name)

    def test_get_drone_category(self):
        """
        Ensure we can get a single drone category by id
        """
        drone_category_name = 'Easy to retrieve'
        response = self.post_drone_category(drone_category_name)
        url = reverse(
            views.DroneCategoryDetail.name,
            None,
            {response.data['pk']}
        )
        get_response = self.client.get(url, format='json')
        self.assertEqual(get_response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(get_response.data['name'],
                         drone_category_name)


class PilotTests(APITestCase):
    def post_pilot(self, name, gender, races_count):
        url = reverse(views.PilotList.name)
        data = {
            'name': name,
            'gender': gender,
            'races_count': races_count
        }
        response = self.client.post(url, data, format='json')
        return response

    def create_user_and_set_token_credentials(self):
        user = User.objects.create_user(
            'test',
            'test@123.com',
            '123testing'
        )

        token = Token.objects.create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION='TOKEN {}'.format(token.key)
        )

    def test_post_and_get_pilot(self):
        """
        Ensure we can create a new Pilot and then retrieve it
        Ensure we cannot retrieve the persisted pilot without token
        """
        self.create_user_and_set_token_credentials()
        new_pilot_name = 'Gaston'
        response = self.post_pilot('Gaston', Pilot.MALE, 5)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pilot.objects.count(), 1)
        saved_pilot = Pilot.objects.get()
        self.assertEqual(saved_pilot.name, response.data['name'])
        self.assertEqual(saved_pilot.gender, response.data['gender'])
        self.assertEqual(saved_pilot.races_count, response.data['races_count'])
        url = reverse(
            views.PilotDetail.name,
            None,
            {saved_pilot.pk}
        )
        autorized_get_response = self.client.get(url, format='json')
        self.assertEqual(autorized_get_response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(autorized_get_response.data['name'], new_pilot_name)
        self.client.credentials()
        unauthorized_get_response = self.client.get(url, format='json')
        self.assertEqual(unauthorized_get_response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_try_to_post_pilot_without_token(self):
        """
        Ensure we cnanot create a pilot without a token
        """
        response = self.post_pilot(
            'Unauthorized Pilot',
            Pilot.MALE,
            5
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Pilot.objects.count(), 0)
