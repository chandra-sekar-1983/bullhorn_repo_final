# **INTEGRATION FRAMEWORK**

## **Overview**

The main purpose of this project is to provide internal teams, external contractors, customers, and 3rd party companies with an easy and consistent way to implement Dialpad integrations with different platforms. For more information, please see our tech debt documentation: 
https://docs.google.com/document/d/1hInlcZpNSco4u5eNeZFJrzKdGcHWrHu-QWUq15Hvy1o/edit?usp=sharing

## **Setup**
Developers who want to take advantage of the framework need to fork out of this repo.
https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository

*How to pull from integration-framework*
```
cd integration-sample
git remote add integration-framework git@github.com:dialpad/integration-framework.git
git rebase integration-framework/main
OR
git pull integration-framework/main # Fetch and merge
git push main
```

## **Getting started**
Framework offers a foundtation to kick of production-ready microservice that's running Vue SPA backed by Sanic. It allows developers to gather group
of functionalites wrapped into modules/packages and re-use between projects. This smallest unit is called Feature. In other words;
a feature represents a micro vue app or blueprint depends on whether in the context of frontend or backend development. A feature can be injected to
any project running with the foundation of this framework. 

### **Local environment setup**
1. Copy .env.example file to .env
2. Update .env file for your local
3. Run below for building and creating containers in detached mode
   ```bash
   docker-compose -f docker-compose.yml -f datastore-compose.yml up --build -d
   ```

| Container | URL |
| --- | --- |
| server | http://localhost:8088 |
| client | http://localhost:8087 |


To create a user for development.
```
docker exec -it $(docker ps -qf "name=server") python shell.py
```
This would run an interactive shell that you can call application code or interact with ORM. Top level coroutines work.

```
from core.models import User
user = await User.create()
print(user.access_token)
```
Any request with access_token URL parameter should be authenticated.
i.e. http://localhost:8088?access_token=<user_access_token>

Various type of authentication methods can be injected as a default method.

### **How to run tests**
1. Copy .env.example file to .env
2. Update .env file for your local
3. Run below code for building and creating containers. This will run the python unittests in discovery mode. Default configuration 
  (Please see https://docs.python.org/3/library/unittest.html#unittest-test-discovery)
  ```bash
  docker-compose -f test-compose.yml -f test-redis-compose.yml up --build # Against Redis
  docker-compose -f test-compose.yml -f test-datastore-compose.yml up --build # Against Datastore
  ```
At the end of running all tests, interactive python shell.
The interactive python shell works similar to your Python REPL. Moreover, it provides quick access to the database.
Here, you can import your Database models and start interacting with them right away. To access interactive shell run below.
```
docker attach $(docker ps -qf "name=test-server")
```

### **Why you should use integration framework**


Framework offers built-in support for;
- Production-ready foundation
- Consistent feature(micro-app) structure
- Reusability through injection
- Easy colloboration between different teams

**server side**

- Re-usable project independent features injections.
- Enable/disable features on application start
Disabling a feature will prevent feature module and all of its sub-module and sub-packages to be read and
executed by interpreter. The feature module only gets injected if it's enabled. Sibling features must
not be tight-coupled. A feature should only be tight coupled with its parent if it's necessary.

- Lifecycle hooks


| Name | Description |
| --- | --- |
| init.py | Runs before feature gets read and executed by the interpreter |
| pre_create.py | Runs after all features are initialized and before Sanic app created |
| post_create.py | Runs after all features are initialized and Sanic app is injected with middlewares, routes, context  |

- Class based customizable routes and middlewares 

- ORM that can interact both relational and non-relational through dynamic client injection.  [README](./server/core/orm/README.md)

- Simple template engine 

- Logger with formatter injection

- Feature context

**client side**

- Re-usable project independent features injections.
- Enable/disable feature on compile time.
Disabling a feature will prevent feature package and all of its sub-packages to be *served to* or read and executed by
browsers. The feature module only gets imported if it's injected and enabled. If feature is splitted in its own package
on the time of compiling, the chunk contains the feature won't be served to the browser. Code-spliting will
try to optimize to create chunks to be served if a feature is enabled 

- Lifecycle hooks

| Name | Description |
| --- | --- |
| init.js | Runs before feature gets read and executed by the browser |
| preCreate.js | Runs after all features are initialized before Vue app, store, router created |
| postCreate.js | Runs after all features are initialized after Vue app, store, router created |

- *Feature* based nested routes

- *Feature* based store module tree

- *Feature* based code splitting (depends on feature size)

- Tree shaking

- Simple template engine

- Logger [README](./server/core/logging/README.md)
   
- Http request client

- Dialtone & Handset support

- GCP Remote environment testing with local static files served by webpack dev server


**devops**

- Terraform IaC to provision and create automated CI/CD pipeline on Google Cloud Platform
```bash
./devops/admin/manual_run.sh --help
```
This script can be used to manually trigger a deploy or infrastructure change.

- Helper script to add secret to Google Secret Manager
```bash
./devops/admin/add_secret.sh
```
- Private version automation including CI/CD listenning to developers' version branch
- Testing with local static files (REMOTE_LOCALHOST)

## Server
Integration Framework has a wrapper around Sanic to be able to dynamically enable/disable feature on the application initial run
on the server via environment variables or configuration file. Due to its architectu

A feature is a specially wrapped package, that has capable of building its and recursively all its childrens' store modules, route definitions,
default enable setting using pre-defined files and pass it to the on runtime. 

Integration Framework creates and initialized root feature which triggers all its children features gets created and initialized recursively
A feature is a group of endpoints served under a blueprint. There can be nested features under a feature group. 

![Application Lifecycle 2](https://user-images.githubusercontent.com/6083754/184377844-7919ebb6-1a2b-482d-a256-ad68ccfb8d44.png)



```
example-feature
│   README.md
│   __init__.py    
│   config.py
|   children.py
│   middlewares.py
|   routes.py
└───lifehooks
| └─── init.py
| └─── pre_create.py
| └─── post_create.py
 
```
  
*__init__.py*
------
  Contains docstring for all information about the feature

*config.py*
------
  Contains configuration of the feature.


*children.py*
------
  Contains information about any children feature defined.
  ```python
  from core.sanic import Feature


  class Dialpad(Feature):
    module_name = 'core.features.dialpad'


  class Zoho(Feature):
    inject_to = 'dialpad_iframe_external'
  ```
 
*middlewares.py*
------
  Contains middlewares that intercept all HTTP calls handled by this feature. 
  Any middleware implemented under this file will be automatically injected in the order of they are defined.
  A Middleware must implement *```middleware```* function.
  
  Example middleware definitions:
  ./example_feature/middlewares.py
  ```python
  from core.sanic import OnRequest
  from core.sanic import OnResponse
  
  
  class MiddlewareForRequest(OnRequest):
    
    def middleware(request):
      print("I run when a request is received by the server")  
  
  
  class MiddlewareForResponse(OnResponse):
    
    def middleware(request, response):
      print("I run when a response is returned by the server")
  
  class MiddlewareForDev(OnResponse):
    ACTIVE = config.is_dev()
  
    def middleware(request, response):
      print("I run only if server is running dev mode")
  ```
  
 *routes.py*
 ------
  Contains routes that would define url mapping between URL path and a handler. 
  Any route implemented under this file will be automatically injected in the order of they are defined. 
  A Route must implement *```handler```* function. Routes will be injected  
  Anything you add to context dictionary with a key prefixed with 'ctx_' will be loaded into
  route instance on request. request.route.ctx
  if you would like to allow unauthenticated request to this particular route, please add 
  'ctx_allow_unauthenticated': True to the context dictionary.
  
  
  Example route definitions:
  ./example_feature/routes.py
  
  ```python
  class ExampleRoute(Route):
    PATH = '/example-route'
    context = {}
	
    @templated_response(template_path=f'{config.TEMPLATES_FOLDER}/index.html')
    async def handler(request):
      pass
  
  class ExampleRoutePostMethod(Route):
    PATH = '/example-route-post'
    METHODS = ['POST']

    async def handler(request):
      pass

  class ExampleDevRoute(Route):
    PATH = '/example-dev-route'
    ACTIVE = config.is_dev()
    context = {}
	
    async def handler(request):
      pass
  ```
  
  **LIFEHOOKS**
  
  *init.py*
  ------
  This is a lifecycle hook. Contains a script that would run before a feature gets initialized.
  Place the custom scripts that you'd like to be run before importing and initialization happens for the feature.
  
  *pre_create.py*
  ------
  This is a lifecycle hook. It gets executed before sanic app created 
  Pre create of parent features gets executed first. (Inorder traversal)
  i.e. ./server/core/features/dialpad/lifehooks/pre_create.py
  ```python
  from core.sanic import Application
  from core.sanic import OnRequest
  
  class AuthenticateDialpad(Middleware):
    ...
    
  dpi = Application.get_feature('dpi')
  dpi.inject_middleware(AuthenticateDialpad)
  ```  

  *post_create.py*
  ------
  This is a lifecycle hook. It gets executed after sanic app is created and injected with middlewares
  , routes, context.
  Post create of leaf features gets executed first. (Postorder traversal)
  i.e. ./server/dpi/external/lifehooks/post_create.py
  ```python
  from core.sanic import Application
  dpi = Application.get_feature('dpi')
  dpi.context.something = 'extra'

  ```  

## Client
Integration Framework has a wrapper around Vue to be able to dynamically inject features and enable/disable on compile and run time
via configuration files. A feature has capable of building its and recursively all its childrens store modules, route definitions, etc., 
(Pre-order travers) and passing it to the Vue app on runtime.

Example feature folder structure


	```
	example-feature
	│   README.md
	│   config.js
	│   Feature.vue    
	│   store.js
	|   routes.js
	|.  children.js
	└───lifehooks/
	| |-- init.js 
	│ |-- postCreate.js
	| |-- preCreate.js
	|
	└───components/
	| |-- ...
	|    
	└───pages/
	  |-- ...
	      
	```

![Client Class Diagram](https://user-images.githubusercontent.com/6083754/180499277-7db67910-846c-4e72-83e9-de0d1bf09719.png)

![Application Lifecycle Client (6)](https://user-images.githubusercontent.com/6083754/180479018-8f8e5127-2ada-4dbd-afe2-5bf7aa6cf08a.png)



*config.js*
------
 
Exports all the configurations for the feature.


*Feature.vue*
------

Home page for the feature. When feature URL is requested, vue-router will route to this Vue component (page). It could work like a 
single component or contains *```<router-view>```* component and route to child pages.
 
 
*store.js*
------
 
Exports feature's store module definition. If feature has any child feature, Integration Framework will include its store file into feature's store as a module.
i.e.
```js
 export default {
  state () {
    return {}
  },

  getters: {},

  mutations: {},

  actions: {},
}

```
*./routes.js*
------
A package to export list of routes that if any extra page is wanted to be served for this feature.
```js
export default [
  {
    name: 'sample-page',
    path: 'sample-page',
    component: () => import('./pages/SamplePage.vue')
  }
]
```

*children.js*
------
A package to export children of this feature. There are various way to inject children feature. Here are some examples
```js

const dialpad = new Feature({
  packageName: 'core/features/dialpad',
})

const zoho = new Feature({
  name: 'zoho',
  injectTo: 'dialpad/iframe/external',
})

const analytics = new Feature({
  name: 'analytics'
})

```

- dialpad feature: Lives under core/features/dialpad and to be injected as a child to this feature.
- external feature: Lives under 'core/features/dialpad/iframe/external' and to be injected as a child to 'dialpad/iframe' feature
- zoho feature: Lives under './<this-feature>/sample' and to be injected as a child to dialpad/iframe/children
- analytics feature: Lives under ./<this-feature>/analytics and to be injected as a child to this feature
	
Example Feature Tree (Zoho Project)
![Feature tree (1)](https://user-images.githubusercontent.com/6083754/180481476-42a5d78e-d090-4f86-815e-530527e2da68.png)

	- Dialpad Feature: Built-in. Implemented for creating application integrated with Dialpad.
	- Api Feature: Built-in. Implemented for integrating with Dialpad Public API.
	- Iframe Feature: Built-in. Implemented for creating sidebar iframe apps in Dialpad.
	- External Feature: Built-in. Implemented for integrating with external services for sidebar iframe apps implemented in Dialpad
	- Zoho Feature: Implemented for integrating Zoho with Dialpad.
	

*lifehooks/init.js*
------
A package to run before a feature gets initialized if it's enabled. Include any code you'd like to run before the feature is initialized.

*lifehooks/preCreate.js*
------
This is a lifecycle hook. Exports default async function that takes *```application```* as arguments.

This file gets executed after all features are initialized before Vue app, Vuex store, and Vue router is created.
Pre create of parent features get executed first. (Inorder traversal)
i.e. ./client/src/dialpad/lifehooks/preCreate.js
```js
export default async function ({ feature, application }) {
  // Code
};
```

*lifehooks/postCreate.js*
------
This is a lifecycle hook. Exports default async function that takes;
*```app```*, *```store```*, *```router```*, *```application```* as arguments.

This file gets executed after the Vue app, Vuex store, and Vue router is created.
Post create of leaf features get executed first. (Preorder traversal)
i.e. ./client/src/dialpad/lifehooks/postCreate.js
```js
export default async function ({ app, store, router, feature, application }) {
  await store.dispatch('dialpad/initialize')
};
```
 
*./components*
------
 Contains components wrapped inside this feature. The feature's *```Feature.vue```* component
 or any defined page components will use these to shape themselves.

*./pages*
------
 Contains components that are rendered by the router on a request to a URL. 
 If any page is defined under here, to make them routable, there needs to be *```Feature.vue```*  defined and
 has to contain *```<router-view>```* component to be able
 to serve the pages by the help of vue-router. 
 
 Also,  *```routes.js```* has to contain route information for this page.
  ```js
  export default [
    {
      name: 'sample-page',
      path: 'sample-page',
      component: () => import('./pages/Error404.vue')
    }
  ]
  ```

   
## Database configuration
You can govern which client to use depending on the DB backend you have through implementing proper
client to integrate with DB backend for Dialpad Integration Framework ORM
```bash
ORM_CLIENT=core.orm.clients.datastore.DatastoreClient
ORM_CLIENT=core.orm.clients.redis.RedisClient # For testing
```

Please see [ORM](./server/core/orm/README.md) for more details.

## Configuration

### Common configuration
Below configurations can be modified by; 
- .env file for local development
- ./devops/terraform/vars/"${ENV}".tfvars

<table>
  <tr>
    <th>Variable</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
  <tr>
    <td>NAME</td>
    <td>The Dialpad integration's name (App name)</td>
    <td>dpi</td>
  </tr>
  <tr>
    <td>ENV</td>
    <td>Environment of the server intented to be interacted</td>
    <td>dev</td>
  </tr>
  <tr>
    <td>PORT</td>
    <td>The port where this app will be served</td>
    <td>8088</td>
  </tr>
  <tr>
    <td>BASE_URL</td>
    <td>The url of this app</td>
    <td>http://localhost:8088</td>
  </tr>
  <tr>
    <td>SANIC_FAST</td>
    <td>Automatically run the maximum number of workers given the system constraints</td>
    <td>0</td>
  </tr>
  <tr>
    <td>ORM_CLIENT</td>
    <td>Name of the database client to be injected</td>
    <td>DatastoreClient</td>
  </tr>
</table>

### GCP specific configuration
Below configurations can be modified in; 
- ./devops/terraform/vars/"${ENV}".tfvars

<table>
  <tr>
    <th>Variable</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
  <tr>
    <td>DESCRIPTION</td>
    <td>Description of the app</td>
    <td>None</td>
  </tr>
  <tr>
    <td>REGIONS</td>
    <td>List of regions where the app will be deployed</td>
    <td>None</td>
  </tr>
  <tr>
    <td>PROJECT</td>
    <td>The GCP project's information</td>
    <td>None</td>
  </tr>
  <tr>
    <td>DOMAIN</td>
    <td>Complete domain address. Leave undefined to use global LB ip address</td>
    <td>None</td>
  </tr>
  <tr>
    <td>HTTPS_REDIRECT</td>
    <td>Redirect calls from HTTP to HTTPS</td>
    <td>false</td>
  </tr>
  <tr>
    <td>SSL</td>
    <td>Enables SSL</td>
    <td>false</td>
  </tr>
  <tr>
    <td>ENV_VARS</td>
    <td>Environment variables to be defined</td>
    <td>None</td>
  </tr>
</table>

## Devops
![Integration Framework (12)](https://user-images.githubusercontent.com/6083754/164491063-a5491439-7dab-4457-a21c-bd423a074b58.png)
Please see [Devops](./devops/README.md)

