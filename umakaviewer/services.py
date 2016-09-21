# coding:utf-8

import click
from rdflib import URIRef
from .scripts.services.utils import get_type
from .scripts.services import index_owl, build_sbm_model


@click.group()
def cmd():
    pass


@cmd.command(help=u'''
オントロジーのファイルから、モデルデータ作成のためのassetsを作成します。
''')
@click.argument('owl_data_ttl', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option('--dist', '-d', default='assets', type=click.Path(exists=False), help=u'出力先のディレクトリパス')
def build_index(owl_data_ttl, dist):
    if not owl_data_ttl:
        raise click.UsageError(u'オントロジーファイルを一つ以上指定してください。')

    for owl_data in owl_data_ttl:
        if get_type(owl_data) not in ('turtle', 'n3'):
            raise click.UsageError(u'オントロジーファイルはttlかn3のみ有効です。')

    target_properties = {
        URIRef('http://www.w3.org/2002/07/owl#sameAs'): 'sameAs',
        URIRef('http://www.w3.org/2000/01/rdf-schema#label'): 'label',
        URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'): 'subClassOf',
        URIRef('http://www.w3.org/2000/01/rdf-schema#domain'): 'domain',
        URIRef('http://www.w3.org/2000/01/rdf-schema#range'): 'range',
    }
    output = index_owl(owl_data_ttl, target_properties, dist)
    click.echo('>>> {}'.format(output))


"""
@cmd.command(help='''
build_indexに使えるファイルはturtleかn3形式のみのため、convertを行います。
''')
@click.argument('owl_data_files', nargs=-1, type=click.Path(exists=True, dir_okay=False))
def convert(owl_data_files):
    convert2ttl(owl_data_files)
"""


@cmd.command(help=u'''
SBMに従うメタデータからモデルデータを作成します。
''')
@click.argument('sbm_data_ttl', nargs=1, type=click.Path(exists=True))
@click.option('--assets', '-a', type=click.Path(exists=True), help=u'build_indexコマンドで吐き出されたディレクトリ')
@click.option('--dist', '-d', default='model.json', type=click.Path(exists=False), help=u'出力先のファイルパス')
def build(sbm_data_ttl, assets=None, dist=None):
    build_sbm_model(sbm_data_ttl, assets, dist)
    click.echo('>>> {}'.format(dist))


if __name__ == '__main__':
    cmd()
