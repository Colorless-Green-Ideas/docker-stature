import logging

import toml
from docker import Client
from cachet import Cachet


def main(cli, cach, settings):
    docker_map = settings['containers']
    cs = cli.containers()
    for container in cs:
        cach_id = None
        name = container['Names'][0][1:]
        labels = container['Labels']
        if name in docker_map:
            cach_id = docker_map[name]

        elif filter(lambda k: "org.cachet" in k, labels.keys()):
            if "org.cachet.id" in container['Labels']:
                cach_id = labels['org.cachet.id']
            elif "org.cachet.name" in labels:
                args = {"name": labels["org.cachet.name"]}
                if "org.cachet.description" in labels:
                    args["description"] = labels["org.cachet.description"]
                if "org.cachet.link" in labels:
                    args["link"] = labels["org.cachet.link"]
                logging.info("Creating Component: %s", args['name'])
                ret = cach.postComponents(status=1, **args) #assume status is fine
                cach_id = ret.json()['data']['id']
                logging.info("Got component id: %d", cach_id)
                docker_map[name] = cach_id
        else:
            logging.info("Container: %s not found in your toml file, nor does it have a docker label metadata, see the docs for refrence.", name)
        status = container['Status'].split()[0]
        if status == "Up":
            cach.putComponentsByID(cach_id, status=1)
        elif status == "Exited":
            cach.putComponentsByID(cach_id, status=4)

if __name__ == '__main__':
    settings = toml.load("docker2cachet.toml")
    logging.basicConfig(level=logging.INFO)
    cli = Client(base_url='unix://var/run/docker.sock')
    cach = Cachet(settings['cachet']['url'], settings['cachet']['api_key'])
    main(cli, cach, settings)
