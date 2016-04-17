# docker-stature
Docker container metadata as a Cachet component data!


# Configuration via toml (option 1)
You can manually assign containers by name to a cachet component in the `docker2cachet.toml` file. just make a new entry in the `[containers]` section.
[More on toml can be found here.](https://github.com/toml-lang/toml)

# Configuration via docker (option A)
You may apply labels to your containers via [compose](https://docs.docker.com/compose/overview/) in your [`docker-compose.yml`](https://docs.docker.com/compose/compose-file/#labels) or directly on the [docker commandline, or in your Dockerfile](https://docs.docker.com/engine/userguide/labels-custom-metadata/)

## Supported Labels
 * org.cachet.id
 * org.cachet.name
 * org.cachet.description
 * org.cachet.link

all labels are optional but id superceedes the rest.


#Connecting to docker over TLS
This is currently not exposed by the script but support could be added. `main()` takes a `docker.Client` instance that can be created with the [proper connection parameters.](https://docker-py.readthedocs.org/en/latest/tls/)
