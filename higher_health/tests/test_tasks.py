# import json
#
# import responses
# from django.contrib.auth.models import User
# from django.test import TestCase
#
# from higher_health.models import Campus, University
# from higher_health.tasks import submit_healthcheck_to_eventstore
# from higher_health.utils import get_risk_level, save_data
#
# from .utils_test import get_data
#
#
# class SubmitHealthCheckToEventStoreTests(TestCase):
#     @responses.activate
#     def test_all_fields(self):
#         """
#         Submits all fields to the eventstore
#         """
#         responses.add(
#             method=responses.POST,
#             url="https://eventstore-placeholder/api/v3/covid19triage/",
#         )
#         data = get_data()
#         data["risk_level"] = get_risk_level(data)
#         user = User.objects.create_user("27820001001")
#         healthcheck = save_data(data, user)
#         [call] = responses.calls
#         request_data = json.loads(call.request.body)
#         self.assertEqual(
#             request_data,
#             {
#                 "deduplication_id": str(healthcheck.id),
#                 "msisdn": healthcheck.msisdn,
#                 "first_name": healthcheck.first_name,
#                 "last_name": healthcheck.last_name,
#                 "source": healthcheck.source,
#                 "province": healthcheck.province,
#                 "city": "<None>",
#                 "age": healthcheck.age,
#                 "date_of_birth": None,
#                 "fever": healthcheck.fever,
#                 "cough": healthcheck.cough,
#                 "sore_throat": healthcheck.sore_throat,
#                 "difficulty_breathing": healthcheck.difficulty_breathing,
#                 "exposure": healthcheck.exposure,
#                 "tracing": healthcheck.confirm_accuracy,
#                 "risk": healthcheck.risk,
#                 "gender": healthcheck.gender,
#                 "city_location": healthcheck.location,
#                 "smell": healthcheck.smell,
#                 "preexisting_condition": healthcheck.preexisting_condition,
#                 "rooms_in_household": healthcheck.rooms_in_household,
#                 "persons_in_household": healthcheck.persons_in_household,
#                 "completed_timestamp": healthcheck.completed_timestamp.isoformat(),
#                 "data": {
#                     "confirm_accuracy": healthcheck.confirm_accuracy,
#                     "address": healthcheck.address,
#                     "city": healthcheck.city,
#                     "street_number": healthcheck.street_number,
#                     "route": healthcheck.route,
#                     "country": healthcheck.country,
#                     "destination": healthcheck.facility_destination,
#                     "university": None,
#                     "university_other": None,
#                     "campus": None,
#                     "campus_other": None,
#                     "reason": healthcheck.facility_destination_reason,
#                     "obesity": healthcheck.history_obesity,
#                     "diabetes": healthcheck.history_diabetes,
#                     "hypertension": healthcheck.history_hypertension,
#                     "cardiovascular": healthcheck.history_cardiovascular,
#                     "vaccine_uptake": healthcheck.vaccine_uptake,
#                 },
#             },
#         )
#
#     @responses.activate
#     def test_null_name_fields(self):
#         """
#         Submits a blank string for null name fields
#         """
#         responses.add(
#             method=responses.POST,
#             url="https://eventstore-placeholder/api/v3/covid19triage/",
#         )
#         data = get_data()
#         data["risk_level"] = get_risk_level(data)
#         user = User.objects.create_user("27820001001")
#
#         healthcheck = save_data(data, user)
#         healthcheck.first_name = None
#         healthcheck.last_name = None
#         healthcheck.save()
#         submit_healthcheck_to_eventstore(str(healthcheck.id))
#
#         call = responses.calls[-1]
#         request_data = json.loads(call.request.body)
#         self.assertEqual(request_data["first_name"], "")
#         self.assertEqual(request_data["last_name"], "")
#
#     @responses.activate
#     def test_tracing(self):
#         """
#         Submits tracing as False if null
#         """
#         responses.add(
#             method=responses.POST,
#             url="https://eventstore-placeholder/api/v3/covid19triage/",
#         )
#         data = get_data()
#         data["risk_level"] = get_risk_level(data)
#         user = User.objects.create_user("27820001001")
#
#         healthcheck = save_data(data, user)
#         healthcheck.confirm_accuracy = None
#         healthcheck.save()
#         submit_healthcheck_to_eventstore(str(healthcheck.id))
#
#         call = responses.calls[-1]
#         request_data = json.loads(call.request.body)
#         self.assertEqual(request_data["tracing"], False)
#
#     @responses.activate
#     def test_university(self):
#         """
#         Submits serialized university if present
#         """
#         responses.add(
#             method=responses.POST,
#             url="https://eventstore-placeholder/api/v3/covid19triage/",
#         )
#         data = get_data()
#         data["risk_level"] = get_risk_level(data)
#         user = User.objects.create_user("27820001001")
#
#         healthcheck = save_data(data, user)
#         university = (
#             healthcheck.facility_destination_university
#         ) = University.objects.create(name="Test university", province="ZA-WC")
#         healthcheck.save()
#         submit_healthcheck_to_eventstore(str(healthcheck.id))
#
#         call = responses.calls[-1]
#         request_data = json.loads(call.request.body)
#         self.assertEqual(
#             request_data["data"]["university"],
#             {"id": university.id, "name": "Test university", "province": "ZA-WC"},
#         )
#
#     @responses.activate
#     def test_campus(self):
#         """
#         Submits serialized campus if present
#         """
#         responses.add(
#             method=responses.POST,
#             url="https://eventstore-placeholder/api/v3/covid19triage/",
#         )
#         data = get_data()
#         data["risk_level"] = get_risk_level(data)
#         user = User.objects.create_user("27820001001")
#
#         healthcheck = save_data(data, user)
#         university = University.objects.create(name="Test university", province="ZA-WC")
#         campus = healthcheck.facility_destination_campus = Campus.objects.create(
#             name="Test campus", university=university
#         )
#         healthcheck.save()
#         submit_healthcheck_to_eventstore(str(healthcheck.id))
#
#         call = responses.calls[-1]
#         request_data = json.loads(call.request.body)
#         self.assertEqual(
#             request_data["data"]["campus"],
#             {
#                 "id": campus.id,
#                 "name": "Test campus",
#                 "university": {
#                     "id": university.id,
#                     "name": "Test university",
#                     "province": "ZA-WC",
#                 },
#             },
#         )
#
#     @responses.activate
#     def test_age(self):
#         """
#         Submits correct age value for 18-40
#         """
#         responses.add(
#             method=responses.POST,
#             url="https://eventstore-placeholder/api/v3/covid19triage/",
#         )
#         data = get_data()
#         data["risk_level"] = get_risk_level(data)
#         user = User.objects.create_user("27820001001")
#
#         healthcheck = save_data(data, user)
#         healthcheck.age = "18-39"
#         healthcheck.save()
#         submit_healthcheck_to_eventstore(str(healthcheck.id))
#
#         call = responses.calls[-1]
#         request_data = json.loads(call.request.body)
#         self.assertEqual(request_data["age"], "18-40")
#
#     @responses.activate
#     def test_city(self):
#         """
#         Submits the address value if present
#         """
#         responses.add(
#             method=responses.POST,
#             url="https://eventstore-placeholder/api/v3/covid19triage/",
#         )
#         data = get_data()
#         data["risk_level"] = get_risk_level(data)
#         user = User.objects.create_user("27820001001")
#
#         healthcheck = save_data(data, user)
#         healthcheck.address = "Test address"
#         healthcheck.save()
#         submit_healthcheck_to_eventstore(str(healthcheck.id))
#
#         call = responses.calls[-1]
#         request_data = json.loads(call.request.body)
#         self.assertEqual(request_data["city"], "Test address")
