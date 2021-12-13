# coding:utf-8

import click
from rdflib import URIRef
from .scripts.services.utils import get_type, i18n_t
from .scripts.services import index_owl, build_sbm_model
from .scripts.services.convert import convert2ttl
import i18n
from os import getenv, path


def init_i18n():
    FILE_DIR = path.dirname(path.abspath(__file__))
    LOCALE_DIR = path.join(FILE_DIR, 'locales')
    i18n.load_path.append(LOCALE_DIR)
    i18n.set('file_format', 'json')
    lang = getenv('LANG')

    locale = lang and lang.split('.')[0]
    locale = locale and locale.split('_')[0]
    i18n.set('locale', locale)
    i18n.set('fallback', 'en')
    i18n.set('skip_locale_root_data', True)


init_i18n()


@click.group()
def cmd():
    pass


@cmd.command(help=i18n_t('cmd.build_index.cmd_help'))
@click.argument('owl_data_ttl', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option('--dist', '-d',
              default='assets', type=click.Path(exists=False), help=i18n_t('cmd.build_index.opt_help_d'))
def build_index(owl_data_ttl, dist):
    if not owl_data_ttl:
        raise click.UsageError(i18n_t('cmd.build_index.error_not_specified'))

    for owl_data in owl_data_ttl:
        if get_type(owl_data) not in ('turtle', 'n3'):
            raise click.UsageError(i18n_t('cmd.build_index.error_invalid_type'))

    target_properties = {
        URIRef('http://www.w3.org/2002/07/owl#sameAs'): 'sameAs',
        URIRef('http://www.w3.org/2000/01/rdf-schema#label'): 'label',
        URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'): 'subClassOf',
        URIRef('http://www.w3.org/2000/01/rdf-schema#domain'): 'domain',
        URIRef('http://www.w3.org/2000/01/rdf-schema#range'): 'range',
    }
    output = index_owl(owl_data_ttl, target_properties, dist)
    click.echo('>>> {}'.format(output))


@cmd.command(help=i18n_t('cmd.convert.cmd_help'))
@click.argument('owl_data_files', nargs=-1, type=click.Path(exists=True, dir_okay=False))
def convert(owl_data_files):
    convert2ttl(owl_data_files)


@cmd.command(help=i18n_t('cmd.build.cmd_help'))
@click.argument('sbm_data_ttl', nargs=1, type=click.Path(exists=True))
@click.option('--assets', '-a', type=click.Path(exists=True), help=i18n_t('cmd.build.opt_help_a'))
@click.option('--dist', '-d', default='model.json', type=click.Path(exists=False, dir_okay=False), help=i18n_t('cmd.build.opt_help_d'))
def build(sbm_data_ttl, assets=None, dist=None):
    dist_file = build_sbm_model(sbm_data_ttl, assets, dist)
    if dist_file:
        click.echo('>>> {}'.format(dist_file))


if __name__ == '__main__':
    cmd()
