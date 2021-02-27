
import os
import sys
import argparse
import glob

import yaml

from textwrap import dedent
from flask import Flask, Markup, redirect, url_for
from bs4 import BeautifulSoup

import bootwrap as bw

app = Flask(__name__, static_folder='docs', static_url_path='')

with open('main.yaml', 'r') as file:
    demo = yaml.load(file)


QUOTES_AUTHORS = [
    'N.Mandela',
    'W.Disney',
    'S.Jobs',
]

QUOTES_TEXT = [
    '"The greatest glory in living lies not in never falling, but in rising every time we fall."',
    '"The way to get started is to quit talking and begin doing."',
    '"Your time is limited, so don\'t waste it living someone else\'s life. Don\'t be trapped by dogma – which is living with the results of other people\'s thinking."'
]


class DocArguments(bw.Panel):
    def __init__(self, content):

        body = []
        for row in content:
            body.append([
                bw.Text(f'<i style="white-space: nowrap">{row[0]}</i>'),
                bw.Text(f'<code style="white-space: nowrap">{row[1]}</code>'),
                bw.Text(row[2]).as_secondary()
            ])
        super().__init__(
            bw.Table(
                head=['Name', 'Type', 'Description'],
                body=body
            ).add_classes('table-sm table-bordered')
        )


class DocSection(bw.Panel):
    def __init__(self, content):
        title = None
        if 'title' in content:
            title = bw.Text(content['title']).as_heading(1)

        subtitle = None
        if 'subtitle' in content:
            subtitle = bw.Text(content['subtitle']).as_heading(2).add_classes('text-muted')

        image = None
        if 'image' in content:
            image = bw.Image(content['image'], width=500)

        code_left = None
        code_right = None
        if 'code' in content:
            c = content['code']
            if '@right' in c:
                c = c.replace('@right', '').strip()
                code_right = bw.Text(c).as_code()
            else:
                c = c.replace('@left', '').strip()
                code_left = bw.Text(c).as_code()

        constructor = None
        if 'constructor' in content:
            constructor = f'''
                <p><strong>Constructor:</strong> <code>{content['constructor']}</code></p>
            '''

        arguments = None
        if 'arguments' in content:
            arguments = DocArguments(content['arguments'])

        evaluation = None
        if 'evaluation' in content:
            loc = {}
            exec(content['evaluation'], {}, loc)
            evaluation = loc['output']

        description = []
        if 'description' in content:
            for fragment in content['description']:
                if isinstance(fragment, str):
                    description.append(bw.Text(fragment).as_paragraph())
                elif isinstance(fragment, dict):
                    try:
                        description.append(
                            bw.Table(
                                head=fragment['head'],
                                body=fragment['body']
                            )
                        )
                    except KeyError as err:
                        raise AssertionError(
                            f'Invalid fragment format for a table;'
                        ) from err
                else:
                    raise AssertionError(
                        f'Unsupported fragment type {type(fragment)};'
                    )

        if not isinstance(description, list):
            description = [description]

        super().__init__(
            bw.Panel(
                bw.Panel(title, subtitle, constructor),
                bw.Panel()
            ).horizontal(),
            bw.Panel(
                bw.Panel(arguments, *description,  code_left),
                bw.Panel(code_right, image, evaluation)
            ).horizontal()
        )
        self.add_classes('mt-5')












class GenericPage(bw.Page):
    """Generic web-pages for demoing web-components.
    
    Args:
        content (WebComponent): The web-page content to show
    """
    def __init__(self, content):

        def docgen(content):
            if isinstance(content, dict):
                items = []
                for name, tab in content.items():
                    items.append(
                            bw.Navigation.Item(
                            name, 
                            bw.Panel(*list(map(DocSection, tab))),
                            len(items)==0
                        )
                    )
                return [bw.Navigation(*items).as_tabs()]
            else:
                return list(map(DocSection, content))

        super().__init__(
            favicon = 'favicon.ico',
            menu=bw.Menu(
                logo = bw.Image(
                    'logo.png',
                    width=32,
                    alt='Bootwrap Logo'
                ),
                brand=bw.Text('Bootwrap').as_strong().as_light(),
                anchors=[
                    bw.Anchor('Home').link('/'),
                    bw.Anchor('Introduction').link('/introduction'),
                    bw.Anchor('Components').link('/components')
                ], 
                actions=[
                    bw.Button('GitHub').\
                        as_outline().\
                        as_light().\
                        link('https://github.com/mmgalushka/python-bootwrap')
                ]
            ),
            content=docgen(content)
        )


@app.route('/')
def home():
    with open('main.yaml', 'r') as file:
        content = yaml.load(file, Loader=yaml.FullLoader)
    return Markup(GenericPage(content['home']))


@app.route('/introduction')
def introduction():
    with open('main.yaml', 'r') as file:
        content = yaml.load(file, Loader=yaml.FullLoader)
    return Markup(GenericPage(content['introduction']))


@app.route('/components')
def components():
    with open('main.yaml', 'r') as file:
        content = yaml.load(file, Loader=yaml.FullLoader)
    return Markup(GenericPage(content['components']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action', 
        choices=['demo', 'docs'],
        help='action to run'
    )

    args = parser.parse_args(sys.argv[1:])

    if args.action == 'docs':
 
        for path in glob.glob('docs/*.html'):
            os.remove(path)

        def save_page(filename, page):
            page = str(page).\
                replace('href="/"', 'href="index.html"').\
                replace('href="/introduction"', 'href="introduction.html"').\
                replace('href="/components"', 'href="components.html"')
            with open(f'docs/{filename}', 'w') as file:
                soup = BeautifulSoup(page)
                file.write(soup.prettify())

        save_page('index.html', home())
        save_page('introduction.html', introduction())
        save_page('components.html', components())

    else:
        app.run(debug=True)
