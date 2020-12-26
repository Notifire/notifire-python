try:
    import aiohttp  # NOQA, pylint: disable=W0611
except ImportError:
    collect_ignore = ['transport/test_aiohttp']
