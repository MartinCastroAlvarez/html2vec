import sys
import typing

import spacy
import numpy as np
import lxml.etree
import requests

# python -m spacy download en_core_web_md
english: spacy.lang.en.English = spacy.load("en_core_web_md")


class Node:
    def __init__(self) -> None:
        self.xpath: str = '/'
        self.element: lxml.etree._Element = lxml.etree._Element()
        self.vector: typing.Optional[np.array] = None
        self.position: int = 0

    def __repr__(self) -> str:
        return "<Node: {}>".format(self.element)

    def get_parent(self) -> typing.Optional[lxml.etree._Element]:
        return self.element.getparent()

    def get_children(self) -> typing.Generator[lxml.etree._Element, None, None]:
        yield from self.element

    def __get_tag(self) -> str:
        return self.element.tag

    def __get_text(self) -> str:
        return ' '.join([
            self.element.text or '',
            self.element.tag or '',
        ]).strip()

    def __get_attributes(self) -> dict:
        return self.element.attrib

    def get_shape(self) -> tuple:
        return (5, 300)

    def get_vector(self) -> np.array:
        if self.vector is None:
            tag: str = self.__get_tag()
            text: str = self.__get_text()
            x1: np.array = english(tag).vector
            x2: np.array = english(text).vector
            x3: np.array = np.zeros(x1.shape)
            x4: np.array = np.array([self.position, ] * self.get_shape()[1])
            x5: np.array = english(' '.join([
                name.split('[')[0]
                for name in self.xpath.split('/')
            ])).vector
            for key, value in self.__get_attributes().items():
                x3 += english(tag).vector * english(value).vector
            self.vector: np.array = np.array([
                x1,  # Tag type.
                x2,  # Text vector.
                x3,  # Numeric representation of attributes.
                x4,  # Indicator of vertical position.
                x5,  # Numeric representation of xpath.
            ])
            assert self.vector.shape == self.get_shape()
        return self.vector

    def __add__(self, node: 'Node') -> 'Node':
        assert isinstance(node, self.__class__)
        self.vector = self.get_vector() + node.get_vector()
        return self


class Html2Vec:
    def __init__(self) -> None:
        self.relatives: int = 5

    def __repr__(self) -> str:
        return "<Model: {}>".format(self.__class__.__name__)

    def fit(self, text: str) -> typing.Generator[Node, None, None]:
        assert isinstance(text, str)
        assert text
        html: lxml.etree.HTML = lxml.etree.HTML(text)
        root: lxml.etree._ElementTree = html.getroottree()
        total_nodes: int = len(root.xpath(".//*"))
        index: dict = {}
        for i, element in enumerate(html.iter()):
            xpath: str = root.getpath(element)
            node: Node = Node()
            node.position = i / total_nodes
            node.element = element
            node.xpath = xpath
            index[xpath] = node
        for level in range(self.relatives):
            for node in index.values():
                if node.get_parent() is not None:
                    xpath: str = root.getpath(node.get_parent())
                    parent: Node = index[xpath]
                    node += parent
                for element in node.get_children():
                    xpath: str = root.getpath(element)
                    child: Node = index[xpath]
                    node += child
        yield from index.values()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url: str = sys.argv[1]
        response: requests.Response = requests.get(url)
        html: str = response.text
    else:
        html: str = """
            <html>
            <head>
            </head>
            <body>
                <div class='container'>
                    <div class='nav-bar'>
                        <img class="logo" src="https://sonar.com/logo.jpg"/>
                        <ul class="nav-list">
                            <li class="nav-link"">
                                <a href='https://sonar.com/'>Home</a>
                            </li>
                            <li class="nav-link"">
                                <a href='https://sonar.com/contact'>Contact</a>
                            </li>
                            <li class="nav-link"">
                                <a href='https://sonar.com/login'>Login</a>
                            </li>
                        </ul>
                    <div>
                    <div class='sidebar'>
                        <button class="share share-facebook">Facebook</button>
                        <button class="share share-instagram">Instagram</button>
                        <button class="share share-twitter">Twitter</button>
                    <div>
                    <div class='content'>
                        <h1 class='title'>Sonar</h1>
                        <h2 class='subtitle'>Natural Language Processing</h2>
                        <div id='article'>
                            <p>Lorem Ipsum Dolor Sit Amet</p>
                            <br/>
                            <p>Lorem Ipsum Dolor <b>Sit</b> Amet</p>
                            <p>Lorem Ipsum Dolor Sit Amet</p>
                            <br/>
                            <p>Lorem Ipsum <i>Dolor</i> Sit Amet</p>
                            <p>Lorem Ipsum Dolor Sit Amet</p>
                        </div>
                    </div>
                    <div class='footer'>
                        <a href="https://sonar.com/about">About Us</a>
                    </div>
                </div>
            </body>
            </html>
        """
    model: Html2Vec = Html2Vec()
    model.relatives = 5
    for node in model.fit(html):
        print(node)
        print(node.get_vector())
