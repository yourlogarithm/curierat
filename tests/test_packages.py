from classes.category import Category
from classes.contact import Contact
from classes.form import Form
from classes.package_status import PackageStatus
from constants import TEST_DEFAULT_PASSWORD
from tests.test_client import TestClient


class FormSubmissionTest(TestClient):
    TEST_FORM = Form(
        sender_contact=Contact(
            first_name='Sender First Name',
            last_name='Sender Last Name',
            email='sender@gmail.com',
            phone='0751234567'
        ),
        receiver_contact=Contact(
            first_name='Receiver First Name',
            last_name='Receiver Last Name',
            email='receiver@gmail.com',
            phone='0785123456'
        ),
        office='Timisoara',
        destination='Bucuresti',
        weight=1.5,
        category=Category.Fragile
    )

    def get_package(self, origin: str = None, destination: str = None):
        dict_val = self.TEST_FORM.to_dict()
        if origin is not None and destination is not None:
            dict_val.update({'office': origin, 'destination': destination})
        elif origin is not None:
            dict_val.update({'office': origin})
        elif destination is not None:
            dict_val.update({'destination': destination})
        dict_val.update({'status': 'transit'})
        return dict_val

    def test_calculate_price(self):
        response = self.client.post('/packages/calculate_price', headers=self.authorize('office', TEST_DEFAULT_PASSWORD), json=self.TEST_FORM.to_dict())
        self.assertAlmostEqual(185.408925, float(response.text), delta=5)

    def test_add_package(self):
        package = self.get_package()
        headers = self.authorize('office', TEST_DEFAULT_PASSWORD)
        data = self.client.post('/packages/add', headers=headers, json=package).json()
        route = self.client.get(f'/routes/package/{data["package_code"]}', headers=headers).json()
        self.assertEqual(route['packages'][0]['sender_contact']['first_name'], package['sender_contact']['first_name'])

    def test_change_status(self):
        headers = self.authorize('office', TEST_DEFAULT_PASSWORD)
        data0 = self.client.post('/packages/add', headers=headers, json=self.get_package('Iasi', 'Brasov')).json()
        code0, id0 = data0['package_code'], data0['route_id']
        self.client.post(f'/packages/change_status/{code0}', headers=self.authorize('courier', TEST_DEFAULT_PASSWORD),
                         params={'status': PackageStatus.WaitingReceiver.value}).json()
        entry = self.client.get(f'/routes/package/{code0}', headers=headers).json()
        package_entry = next(filter(lambda x: x['code'] == code0, entry['packages']))
        self.assertEqual(PackageStatus.WaitingReceiver, package_entry['status'])

    def test_get_package(self):
        headers = self.authorize('moderator', TEST_DEFAULT_PASSWORD)
        package = self.get_package('Iasi', 'Brasov')
        self.client.post('/packages/add', headers=headers, json=package).json()
        new_package = self.get_package('Iasi', 'Brasov')
        new_package.update({'sender_contact': Contact(
            first_name='Second Sender First Name',
            last_name='Second Sender Last Name',
            email='second_sender@gmail.com',
            phone='075111111'
        ).dict()})
        self.client.post('/packages/add', headers=headers, json=new_package).json()
        result = self.client.post(f'/packages/get_by_contact', headers=headers, json=package['sender_contact']).json()
        self.assertGreaterEqual(len(result), 1)
        for entry in result:
            self.assertEqual(package['sender_contact']['first_name'], entry['sender_contact']['first_name'])
            self.assertEqual(package['sender_contact']['last_name'], entry['sender_contact']['last_name'])
            self.assertEqual(package['sender_contact']['email'], entry['sender_contact']['email'])
            self.assertEqual(package['sender_contact']['phone'], entry['sender_contact']['phone'])
