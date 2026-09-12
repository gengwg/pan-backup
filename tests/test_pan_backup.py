import http.server
import threading

import pytest

import pan_backup

CONFIG_XML = (
    '<?xml version="1.0"?>'
    '<response status="success"><result><config><devices/></config></result></response>'
)
EMPTY_RESULT_XML = '<?xml version="1.0"?><response><result/></response>'


class Handler(http.server.BaseHTTPRequestHandler):
    body = CONFIG_XML
    status = 200

    def do_GET(self):
        payload = self.body.encode()
        self.send_response(self.status)
        self.send_header('Content-Type', 'application/xml')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    httpd = http.server.HTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield httpd
    httpd.shutdown()


def make_config(tmp_path, httpd, **overrides):
    config = {
        'myurl': f'http://127.0.0.1:{httpd.server_port}/',
        'ssl_certificate': True,
        'timeout': 5,
        'tmp_file': str(tmp_path / 'data.xml'),
        'backup_file': str(tmp_path / 'backups' / 'pan-backup.xml'),
    }
    config.update(overrides)
    return config


def test_load_config(tmp_path):
    conf = tmp_path / 'pan.conf'
    conf.write_text("myurl = 'http://example.com/'\n")
    assert pan_backup.load_config(conf)['myurl'] == 'http://example.com/'


def test_backup_writes_config(server, tmp_path):
    Handler.body, Handler.status = CONFIG_XML, 200
    assert pan_backup.pan_backup(make_config(tmp_path, server)) == 0
    assert '<config>' in (tmp_path / 'backups' / 'pan-backup.xml').read_text()


def test_backup_without_result_fails(server, tmp_path):
    Handler.body, Handler.status = EMPTY_RESULT_XML, 200
    assert pan_backup.pan_backup(make_config(tmp_path, server)) == 1


def test_backup_http_error_fails(server, tmp_path):
    Handler.body, Handler.status = 'nope', 500
    assert pan_backup.pan_backup(make_config(tmp_path, server)) == 1
