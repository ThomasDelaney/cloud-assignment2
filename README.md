# cloud-assignment2

So this RESTFUL API is a content management system for docker on a manager of known IP
It is ran by calling python3 app.py from the manager vm
and called by making requests to the api from another program

These are all the commands
GET /containers ----------- List all containers
GET /containers?state=running ----------- List running containers (only)
GET /containers/<id> ----------- Inspect a specific container
GET /containers/<id>/logs ----------- Dump specific container logs
GET /services ----------- List all service
GET /nodes ----------- List all nodes in the swarm
POST /containers ----------- Create a new container
PATCH /containers/<id> ----------- Change a container's state
DELTET /containers/<id>  ----------- Delete a specific container
DELETE /containers ----------- Delete all containers (including running)
GET /images ----------- List all images
POST /images ----------- Create a new image
PATCH /images/<id> ----------- Change a specific image's attributes
DELETE /images/<id> ----------- Delete a specific image
DELETE /images ----------- Delete all images
  
This api takes in parameters or json info which will be used to be put into docker commands that will be ran on the manager node

You can call this API by making a REST request using any language

e.g Python for GET /containers

def list_containers(ip):
    url = 'http://'+ip+':5000/containers'
    response = requests.get(url).json() 
    print(response)
    
Here I have a method which creates a URL to the VM with the correct path (running on port 5000) and sends a 'get' request to the API, then converts the output to JSON.
