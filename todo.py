import os

from sanic import Sanic
from sanic.response import json, text
from tinydb import TinyDB, Query


BASE_URL = 'http://todo-backend-sanic.herokuapp.com/todo'

app = Sanic('todo')
db = TinyDB('todos.json')

def make_todo(todo):
    return dict(
        id=todo.eid,
        url='{base_url}/{id}'.format(base_url=BASE_URL, id=todo.eid),
        **todo
    )

@app.route('/todo')
async def handle_collection(request):
    def handle_get():
        return json([make_todo(todo) for todo in db.all()])
    
    def handle_post(body=None):
        if not body or 'title' not in body:
            return text('POST request body must contain title', 400)
        eid = db.insert({
            'title': body['title'],
            'completed': body.get('completed', False),
            'order': body.get('order', 10)
        })
        return json(make_todo(db.get(eid=eid)))

    def handle_delete():
        eids = map(lambda t: t.eid, db.all())
        db.remove(eids=eids)
        return text('[]')

    if request.method == 'GET':
        return handle_get()
    elif request.method == 'POST':
        return handle_post(request.json)
    elif request.method == 'DELETE':
        return handle_delete()
    else:
        return text('GET/POST/DELETE', 405)

@app.route('/todo/<id:int>')
async def handle_single(request, id):
    def handle_get(id):
        todo = db.get(eid=id)
        if todo is None:
            return text('todo not found', 404)
        return json(make_todo(todo))
    
    def handle_patch(body, id):
        todo = db.get(eid=id)
        if todo is None:
            return text('todo not found', 404)
        todo.update(body)
        db.update(todo, eids=[id])
        return json(make_todo(todo))
    
    def handle_delete(id):
        todo = db.get(eid=id)
        if todo is None:
            return text('todo not found', 404)
        db.remove(eids=[id])
        return text('{}')

    if request.method == 'GET':
        return handle_get(id)
    elif request.method == 'PATCH':
        return handle_patch(request.json, id)
    elif request.method == 'DELETE':
        return handle_delete(id)
    else:
        return text('GET/PATCH/DELETE', 405)

app.run(host='0.0.0.0', port=int(os.environ['PORT']))