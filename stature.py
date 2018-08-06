import sys
import logging
import time

import toml
import docker
import click

from cachet import Cachet


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def is_swarm(cli):
    "Is swarm mode enabled on this docker engine?"
    return not cli.swarm.attrs == {}


def is_healthy(container):
    container.reload() # causes a new request to daemon
    try:
        state = container.attrs['State']['Health']['Status']
        if state == "healthy":
            return True
        elif state == "starting":
            return False
        else:
            logging.error("unknown container state: %s", state)
    except KeyError:
        return False

def main(cli, cach, settings):
    cs = cli.containers.list()
    if not cs:
        logging.error("No containers running!")
        sys.exit(4)
    if 'containers' not in settings:
        logging.error("Write out your toml file! Try an empty containers section.")
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
                # print(ret.json())
                ret.raise_for_status()
                cach_id = ret.json()['data']['id']
                logging.info("Got component id: %s", cach_id)
                settings['containers'][name] = cach_id
        else:
            logging.info(
                "Container: %s not found in your toml file, nor does it have a docker label metadata, see the docs for refrence.", name)
            continue
        status = container.status
        logging.debug("Cachet ID: %s",cach_id)
        logging.debug("container: %s", container)
        if cach_id:
            if status == "running":
                ret = cach.putComponentsByID(cach_id, status=1)
                logging.debug(ret.text)
                ret.raise_for_status()
            elif status == "exited":
                ret = cach.putComponentsByID(cach_id, status=4)
                ret.raise_for_status()
    return settings


@click.command(context_settings=CONTEXT_SETTINGS)
# @click.option("--all", '-a', default=False, is_flag=True, help="Check exited containers too")
@click.option("--keep", "-k", default=False, is_flag=True, help="Keep cachet ids in your toml file")
@click.option('--debug', default=False, is_flag=True)
@click.option('--verbose/--silent', default=True)
@click.option("--conf-file", '-f', default="docker2cachet.toml", type=click.Path(exists=True))
def run(conf_file, verbose, debug, keep):
    settings = toml.load(conf_file)
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    if verbose:
        logging.basicConfig(level=logging.INFO)
    cli = docker.from_env()
    cach = Cachet(settings['cachet']['url'], settings['cachet']['api_key'])
    settings = main(cli, cach, settings)
    if keep:
        with open(conf_file, 'w') as f:
            toml.dump(settings, f)

if __name__ == '__main__':
    run()
