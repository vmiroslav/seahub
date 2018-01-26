import json
import os

from django.core.urlresolvers import reverse

from seahub.test_utils import BaseTestCase
from seahub.tags.models import FileTag
from seaserv import seafile_api

class ListLibDirTest(BaseTestCase):
    def setUp(self):
        self.login_as(self.user)
        self.endpoint = reverse('list_lib_dir', args=[self.repo.id])
        self.folder_name = os.path.basename(self.folder)

    def tearDown(self):
        self.remove_repo()

    def test_can_list(self):
        resp = self.client.get(self.endpoint, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        assert self.folder_name == json_resp['dirent_list'][0]['obj_name']
        assert self.repo.name == json_resp['repo_name']

    def test_can_list_file_tags(self):
        seafile_api.post_empty_file(self.repo.id,
                                    '/',
                                    filename='test_tags1.txt',
                                    username=self.user.username)
        seafile_api.post_empty_file(self.repo.id,
                                    '/',
                                    filename='test_tags2.txt',
                                    username=self.user.username)
        FileTag.objects.get_or_create_file_tag(self.repo.id,
                                               '/', 'test_tags2.txt',
                                               False, 'tag1',
                                               self.user.username)
        FileTag.objects.get_or_create_file_tag(self.repo.id,
                                               '/', 'test_tags2.txt',
                                               False, 'tag2',
                                               self.user.username)

        resp = self.client.get(self.endpoint, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_resp = json.loads(resp.content)

        for file in json_resp['dirent_list']:
            if file['obj_name'] == 'test_tag1.txt':
                self.assertEqual([], file['tags'])
            if file['obj_name'] == 'test_tags2.txt':
                self.assertEqual(['tag1', 'tag2'], file['tags'])
