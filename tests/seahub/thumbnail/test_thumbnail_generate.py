# -*- coding: utf-8 -*-

from seahub.test_utils import BaseTestCase
from seahub.thumbnail.utils import generate_thumbnail
from seahub.utils import mkstemp
import os
from seaserv import seafile_api
from django.test import RequestFactory

class GenerateThumbnailTest(BaseTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        self.remove_repo(self.repo.id)

    def test_generate_thumbnail(self):
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

        file_path = '/thumbnail_test.png'
        repo_id = self.repo.id
        url = '/thumbnail/%s/create/' % repo_id
        request = self.factory.get(url)
        success, status_code = generate_thumbnail(request, repo_id, 48, file_path)
        assert success is True
        assert status_code == 200
