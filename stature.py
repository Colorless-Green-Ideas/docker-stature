import logging

import toml
from docker import Client
from cachet import Cachet


def main(cli, cach, settings):
    docker_map = settings['containers']
    cs = cli.containers()
    for container in cs:
        name = container['Names'][0][1:]
        if name in docker_map:
            cach_id = docker_map[name]
            status = container['Status'].split()[0]
            if status == "Up":
                cach.putComponentsByID(cach_id, status=1)
        else:
            logging.info("Container: %s not found in your toml file", name)


if __name__ == '__main__':
    settings = toml.load("docker2cachet.toml")
    logging.basicConfig(level=logging.INFO)
    cli = Client(base_url='unix://var/run/docker.sock')
    cach = Cachet(settings['cachet']['url'], settings['cachet']['api_key'])
    main(cli, cach, settings)
