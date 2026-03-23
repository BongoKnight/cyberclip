from cyberclip.userAction.UrlScanAction import QueryUrlScanAction


def test_extract_scan_ids():

    action = QueryUrlScanAction()

    fake_json = {
        "results": [
            {"result": "https://urlscan.io/api/v1/result/abc123/"},
            {"result": "https://urlscan.io/api/v1/result/xyz456/"},
        ]
    }

    scan_ids = action._extract_scan_ids(fake_json)

    assert scan_ids == ["abc123", "xyz456"]
