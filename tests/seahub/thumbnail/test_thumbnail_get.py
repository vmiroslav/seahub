# -*- coding: utf-8 -*-

from seahub.test_utils import BaseTestCase
from seaserv import seafile_api
import os
import json
from seahub.utils import mkstemp
from django.core.urlresolvers import reverse

class ThumbnailGetTest(BaseTestCase):
    def test_thumbnail_get(self):
        self.login_as(self.user)
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

        url = reverse('thumbnail_get', kwargs={
            'repo_id': self.repo.id,
            'size': 77,
            'path': 'thumbnail_test.png'
        })
        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code)
