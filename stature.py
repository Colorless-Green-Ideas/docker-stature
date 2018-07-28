import sys
import logging
import time

import baker
import toml
import docker

from cachet import Cachet


def main(cli, cach, settings):
    cs = cli.containers.list()
    if not cs:
        logging.error("No containers running!")
        sys.exit(4)
    for container in cs:
        cach_id = None
        name = container.name
        labels = container.labels
        if name in settings['containers']:
            cach_id = settings['containers'][name]

        elif filter(lambda k: "org.cachet" in k, labels.keys()):
            if "org.cachet.id" in labels:
                cach_id = labels['org.cachet.id']
            elif "org.cachet.name" in labels:
                args = {"name": labels["org.cachet.name"]}
                if "org.cachet.description" in labels:
                    args["description"] = labels["org.cachet.description"]
                if "org.cachet.link" in labels:
                    args["link"] = labels["org.cachet.link"]
                logging.info("Creating Component: %s", args['name'])
                # assume status is fine
                ret = cach.postComponents(status=1, **args)
                ret.raise_for_status()
                cach_id = ret.json()['data']['id']
                logging.info("Got component id: %d", cach_id)
                settings['containers'][name] = cach_id
        else:
            logging.info(
                "Container: %s not found in your toml file, nor does it have a docker label metadata, see the docs for refrence.", name)
            continue
        status = container.status
        time.sleep(2)
        logging.debug("Cachet ID: %d",cach_id)
        if status == "up":
            ret = cach.putComponentsByID(cach_id, status=1)
            logging.debug(ret.text)
            ret.raise_for_status()
        elif status == "exited":
            ret = cach.putComponentsByID(cach_id, status=4)
            ret.raise_for_status()
    return settings


@baker.command(default=True, shortopts={"conf_file": "f", })
def run(conf_file="docker2cachet.toml"):
    settings = toml.load(conf_file)
    logging.basicConfig(level=logging.INFO)
    cli = docker.from_env()
    cach = Cachet(settings['cachet']['url'], settings['cachet']['api_key'])
    settings = main(cli, cach, settings)
    with open(conf_file, 'w') as f:
        toml.dump(settings, f)

if __name__ == '__main__':
    baker.run()
