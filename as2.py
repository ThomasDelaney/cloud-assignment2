import requests
import json

def index(ip):
    url = 'http://'+ip+':5000/'
    response = requests.get(url).text
    print(response)

def list_containers(ip):
    url = 'http://'+ip+':5000/containers'
    response = requests.get(url).json()
    print(response)

def list_containers_running(ip):
    url = 'http://'+ip+':5000/containers'
    response = requests.get(url, params='state=running').json()
    print(response)

def list_images(ip):
    url = 'http://'+ip+':5000/images'
    response = requests.get(url).json()
    print(response)

def container_id(ip, id):
    url = 'http://'+ip+':5000/containers/'+id
    response = requests.get(url).json()
    print(response)

def container_logs(ip, id):
    url = 'http://'+ip+':5000/containers/'+id+'/logs'
    response = requests.get(url).json()
    print(response)

def services(ip):
    url = 'http://'+ip+':5000/services'
    response = requests.get(url).json()
    print(response)

def nodes(ip):
    url = 'http://'+ip+':5000/nodes'
    response = requests.get(url).json()
    print(response)

def image_delete(ip, id):
    url = 'http://'+ip+':5000/images/'+id
    response = requests.delete(url).json()
    print(response)

def container_delete(ip, id):
    url = 'http://'+ip+':5000/containers/'+id
    response = requests.delete(url).json()
    print(response)

def container_delete_all(ip):
    url = 'http://'+ip+':5000/containers'
    response = requests.delete(url).json()
    print(response)

def image_delete_all(ip):
    url = 'http://'+ip+':5000/images'
    response = requests.delete(url).json()
    print(response)

def image_create(ip, tag, path):
    url = 'http://'+ip+':5000/images/'+tag+"/"+path
    response = requests.post(url)
    print(response.text)

def container_create(ip, id):
    url = 'http://'+ip+':5000/containers'
    data = {"image": id}
    header = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=header)
    print(response.json())

def container_update(ip, id, state):
    url = 'http://'+ip+':5000/containers/'+id
    data ={"state": state}
    header = {"Content-Type": "application/json"}
    response = requests.patch(url, data=json.dumps(data), headers=header).json()
    print(response)

def image_update(ip, id, tag):
    url = 'http://'+ip+':5000/images/'+id
    data ={"tag": tag}
    header = {"Content-Type": "application/json"}
    response = requests.patch(url, data=json.dumps(data), headers=header).json()
    print(response)

if __name__ == "__main__":
    ip = '35.195.5.26'
    index(ip)
    list_containers(ip)
    #list_images(ip)
    #container_id(ip, '1da240f0ee54')
    #container_logs(ip, '1da240f0ee54')
    #list_containers_running(ip)
    #services(ip)
    #nodes(ip)
    #container_delete(ip, 'd2227a51993a')
    #image_delete(ip, '343824eb2425')
    #container_create(ip, 'fa9f23efb4f5')
    #image_create(ip, 'ca2', 'home/c15300756/DockerCMS')
    #image_update(ip, 'fa9f23efb4f5', 'test:3.0')
    #container_delete_all(ip)
    #image_delete_all(ip)
    #container_update(ip, 'b4f53ad874e7', 'running')
