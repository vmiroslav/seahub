# -*- coding: utf-8 -*-

from seahub.test_utils import BaseTestCase
from seaserv import seafile_api
import os
import json
from seahub.utils import mkstemp

from django.core.urlresolvers import reverse

class ThumbnailCreateTest(BaseTestCase):
    def setUp(self):
        self.login_as(self.user)

    def tearDown(self):
        self.remove_repo(self.repo.id)

    def test_repo_not_exist(self):
        url = reverse('thumbnail_create', kwargs={
            'repo_id': '349f89d3-ea03-4bbe-bb3a-e3b3b8032fad'
        })
        resp = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, resp.status_code)

    def test_path_not_exit(self):
        url = reverse('thumbnail_create', kwargs={
            'repo_id': self.repo.id
        })
        resp = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, resp.status_code)

    def test_thumbnail_create(self):
        seafile_api.post_empty_file(self.repo.id,
                                    '/',
                                    filename='thumbnail_test.png',
                                    username=self.user.username)

        with open('tests/seahub/thumbnail/thumbnail_origin.png', 'rb') as f:
            f = f.read()
        fd, tmp_file = mkstemp()
        try:
            bytesWritten = os.write(fd, f)
        except:
            bytesWritten = -1
        finally:
            os.close(fd)
        assert bytesWritten > 0
        seafile_api.put_file(self.repo.id, tmp_file, '/', 'thumbnail_test.png',
                             self.user.username, None)

        url = reverse('thumbnail_create', kwargs={
            'repo_id': self.repo.id
        })
        url = url + '?path=/' + 'thumbnail_test.png' + '&size=60'
        resp = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        json_resp = json.loads(resp.content)
        assert json_resp['encoded_thumbnail_src'] == 'thumbnail/%s/60/thumbnail_test.png' %self.repo.id
        self.assertEqual(200, resp.status_code)

