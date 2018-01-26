import os
import json

from django.core.urlresolvers import reverse

from seaserv import seafile_api
from seahub.test_utils import BaseTestCase

from tests.common.utils import randstring

class RepoTrashTest(BaseTestCase):

    def setUp(self):

        self.user_name = self.user.username
        self.admin_name = self.admin.username

        self.repo_id = self.repo.id
        self.repo_name = self.repo.repo_name

        self.file_path = self.file
        self.file_name = os.path.basename(self.file_path)

        self.folder_path = self.folder
        self.folder_name = os.path.basename(self.folder.rstrip('/'))

        self.url = reverse('api-v2.1-repo-trash', args=[self.repo_id])

    def tearDown(self):
        self.remove_repo()
        self.remove_group()

    def test_can_get(self):

        # delete a file first
        seafile_api.del_file(self.repo_id, '/',
                self.file_name, self.user_name)

        self.login_as(self.user)

        resp = self.client.get(self.url)
        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp['data'][0]['obj_name'] == self.file_name
        assert json_resp['data'][0]['is_dir'] == False

    def test_can_not_get_with_invalid_repo_permission(self):

        self.login_as(self.admin)

        resp = self.client.get(self.url)
        self.assertEqual(403, resp.status_code)

    def test_can_not_get_with_invalid_path_parameter(self):

        invalid_path = randstring(6)

        self.login_as(self.admin)

        resp = self.client.get(self.url + '?path=%s' % invalid_path)
        self.assertEqual(404, resp.status_code)

    def test_can_delete(self):

        # delete a file first
        seafile_api.del_file(self.repo_id, '/',
                self.file_name, self.user_name)

        self.login_as(self.user)

        # get trash item count
        resp = self.client.get(self.url)
        json_resp = json.loads(resp.content)
        init_num = len(json_resp['data'])

        # delete this file from library trash
        data = {'path': self.file_path}
        resp = self.client.delete(self.url,
                json.dumps(data), 'application/json')

        # get trash item count again
        resp = self.client.get(self.url)
        json_resp = json.loads(resp.content)
        assert len(json_resp['data']) == init_num - 1

    def test_can_not_delete_with_invalid_repo_permission(self):

        self.login_as(self.admin)

        data = {'path': self.file_path}
        resp = self.client.delete(self.url,
                json.dumps(data), 'application/json')

        self.assertEqual(403, resp.status_code)

    def test_can_not_delete_without_path_parameter(self):

        self.login_as(self.admin)

        # delete this file from library trash
        data = {}
        resp = self.client.delete(self.url,
                json.dumps(data), 'application/json')

        self.assertEqual(400, resp.status_code)
