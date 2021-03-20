import pytest
from handler import DownloadHanlder

def test_build_year_and_quarter():
    print('start test')
    yqs = DownloadHanlder.build_year_and_quarter(2019)
    print(yqs)
    assert len(yqs)==4