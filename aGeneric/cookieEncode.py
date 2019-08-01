cookie = {
    'install_id': '80292226089',
    'odin_tt': 'b72496984c553c010af4a8b26e4e3dd744be9bc1f4ffee6adc69dcc59cd84e2a20e5a392f0e7401d9cb4dac0f79cfe99',
    'qh[360]': '1',
    'sessionid': 'b22d38d0985601d2d21a33536cd3eb84',
    'sid_guard': 'b22d38d0985601d2d21a33536cd3eb84|1564109403|5184000|Tue, 24-Sep-2019 02:50:03 GMT',
    'sid_tt': 'b22d38d0985601d2d21a33536cd3eb84',
    'ttreq': '1$377a07aa313271b703ae1e4d37fb29e12763edc4',
    'uid_tt': '35255105dd0e98bbd02af619fc292c8b'
}

a = ''
for k, v in cookie.items():
    a = a + '%s=%s; ' % (k, v)
print(a)
