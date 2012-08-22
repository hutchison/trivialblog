# -*- coding: utf-8 -*-
# FIXME: hier müssen wir die User aus der Datenbank ziehen
USERS = {
        'editor': 'editor',
        'viewer': 'viewer',
        }

GROUPS = {
        'editor': ['editors']
        }

def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
