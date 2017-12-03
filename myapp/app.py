from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os
from tempfile import mkdtemp
from werkzeug import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
    return """
Available API endpoints:

GET /containers                     List all containers
GET /containers?state=running       List running containers (only)
GET /containers/<id>                Inspect a specific container
GET /containers/<id>/logs           Dump specific container logs
GET /images                         List all images
GET /services                       List all services
GET /nodes                          List all nodes

POST /images                        Create a new image
POST /containers                    Create a new container

PATCH /containers/<id>              Change a container's state
PATCH /images/<id>                  Change a specific image's attributes

DELETE /containers/<id>             Delete a specific container
DELETE /containers                  Delete all containers (including running)
DELETE /images/<id>                 Delete a specific image
DELETE /images                      Delete all images

"""

@app.route('/containers', methods=['GET'])
def containers_index():
    """
    List all containers

    curl -s -X GET -H 'Accept: application/json' http://localhost:5000/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json' http://localhost:5000/containers?state=running | python -mjson.tool

    """
    if request.args.get('state') == 'running':
        output = docker('ps')
        resp = json.dumps(docker_ps_to_array(output))

    else:
        output = docker('ps', '-a')
        resp = json.dumps(docker_ps_to_array(output))

    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['GET'])
def images_index():
    """
    List all images

    Complete the code below generating a valid response.
    """
    output = docker('image', 'ls')
    resp = json.dumps(docker_images_to_array(output))

    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['GET'])
def containers_show(id):
    """
    Inspect specific container

    """
    output = docker('container', 'inspect', id)
    resp = json.dumps(output.decode('utf-8'))

    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>/logs', methods=['GET'])
def containers_log(id):
    """
    Dump specific container logs

    """
    output = docker('logs', id)
    resp = json.dumps(docker_logs_to_object(id, output.decode('utf-8')))
    return Response(response=resp, mimetype="application/json")

@app.route('/services', methods=['GET'])
def services_index():
    """
    Display all running services
    """
    output = docker('service', 'ls')
    resp = json.dumps(docker_services_to_array(output))

    return Response(response=resp, mimetype="application/json")

@app.route('/nodes', methods=['GET'])
def nodes_index():
    """
    Display all nodes in the swarm
    """
    output = docker('node', 'ls')
    resp = json.dumps(docker_nodes_to_array(output))

    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['DELETE'])
def images_remove(id):
    """
    Delete a specific image

    curl -X DELETE 'Content-Type: application/json' http://localhost:5000/images/id
    """
    docker ('rmi', id)
    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['DELETE'])
def containers_remove(id):
    """
    Delete a specific container, must be stopped/killed
    """
    docker('container', 'rm', id)
    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['DELETE'])
def containers_remove_all():
    """
    Force remove all containers - dangrous!
    """
    psa = docker('ps', '-a', '-q')
    idList = []
    id = ''

    for c in psa.decode('utf-8'):
        if c == '\n':
            idList.append(id)
            id = ''
        else:
           id += c

    output = bytearray()
    for c in idList:
        output.extend(docker('container', 'rm', c))

    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['DELETE'])
def images_remove_all():
    """
    Force remove all images - dangrous!
    """

    images = docker('images', '-q')
    imgList = []
    id = ''

    for i in images.decode('utf-8'):
        if i == '\n':
            imgList.append(id)
            id = ''
        else:
           id += i

    output = bytearray()
    for i in imgList:
        output.extend(docker('rmi', i))

    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")


@app.route('/containers', methods=['POST'])
def containers_create():
    """
    Create container (from existing image using id or name)

    curl -X POST -H 'Content-Type: application/json' http://localhost:5000/containers -d '{"image": "my-app"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:5000/containers -d '{"image": "b14752a6590e"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:5000/containers -d '{"image": "b14752a6590e","publish":"8081:22"}'

    """
    body = request.get_json(force=True)
    image = body['image']
    args = ('run', '-d')
    id = docker(*(args + (image,)))[0:12]
    return Response(response='{"id": "%s"}' % id.decode('utf-8'), mimetype="application/json")


@app.route('/images/<tag>/<path:df>', methods=['POST'])
def images_create(tag, df):
    """
    Create image (from Dockerfile path)

    curl -X POST -H 'Accept: application/json'  http://localhost:5000/images/dockercms/home/c15300756/DockerCMS

    """

    path = '/'+df

    args = ('build', '-t', tag, '--file=', path)

    id = docker(*(args))
    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")


@app.route('/containers/<id>', methods=['PATCH'])
def containers_update(id):
    """
    Update container attributes (support: state=running|stopped)

    curl -X PATCH -H 'Content-Type: application/json' http://localhost:5000/containers/b6cd8ea512c8 -d '{"state": "running"}'
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:5000/containers/b6cd8ea512c8 -d '{"state": "stopped"}'

    """
    body = request.get_json(force=True)
    try:
        state = body['state']
        if state == 'running':
            docker('restart', id)
        elif state == 'stopped':
            docker('stop', id)
    except:
        pass

    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['PATCH'])
def images_update(id):
    """
    Update image attributes (support: name[:tag])  tag name should be lowercase only

    curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:5000/images/7f2619ed1768 -d '{"tag": "test:1.0"}'

    """

    body = request.get_json(force=True)
    tag = body['tag']
    docker('tag', id, tag)
    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")


def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    print(cmd)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr.startswith(b'Error'):
        print ('Error: {0} -> {1}'.format(' '.join(cmd), stderr))
    return stderr + stdout

#
# Docker output parsing helpers
#

#
# Parses the output of a Docker PS command to a python List
#
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode('utf-8')
        each['image'] = c[1].decode('utf-8')
        each['name'] = c[-1].decode('utf-8')
        each['ports'] = c[-2].decode('utf-8')
        all.append(each)
    return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = []
    for line in output.splitlines():
        all.append(line)
    logs['logs'] = all
    return logs
#
# Parses the output of a Docker image command to a python List
#
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2].decode('utf-8')
        each['tag'] = c[1].decode('utf-8')
        each['name'] = c[0].decode('utf-8')
        all.append(each)
    return all

def docker_services_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode('utf-8')
        each['name'] = c[1].decode('utf-8')
        each['image'] = c[4].decode('utf-8')
        all.append(each)
    return all

def docker_nodes_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode('utf-8')

        #if manager
        if c[1].decode('utf-8') == '*':
            each['hostname'] = 'manager'
        else:
            each['hostname'] = c[1].decode('utf-8')
        all.append(each)
    return all

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True)
