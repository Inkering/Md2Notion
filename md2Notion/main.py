from notion.client import NotionClient
import notion.block
from mistletoe import Document
from md2Notion.secret import get_secret

# Notion helpers


def return_notion_client(secret_string):
    """returns notion client object.
    secret_string: string with notion web token from a valid cookie
    returns: notion client reference
    """

    return NotionClient(token_v2=secret_string)


def return_test_page(client):
    """return notion page given a valid notion client object
    client: valid notion client reference
    returns: notion page block for hardcoded testing ground
    """

    url = "https://www.notion.so/Test-block-8b59ffcf77bd4816b1fb54f2157cf500"
    return client.get_block(url)


def create_page(root_page, child_title):
    """
    create a new notion page
    root_page: notion page block
    child_title: string for the title of the new page
    returns: object referencing new child
    """

    child = root_page.children.add_new(notion.block.PageBlock,
                                       title=child_title)
    return child


# markdown parsing system


def parse_file(file_name):
    """"parse file into mistletoe document"""
    with open(file_name, 'r') as f:
        all_lines = f.readlines()

    raw_markdown = ''.join(all_lines)

    mistle_doc = Document(raw_markdown)

    return mistle_doc


def tree_former(doc, page_items):
    """pretty print a mistletoe markdown document
    doc: mistletoe parsed markdown document object
    returns: linear list of items in markdown doc """

    # handle element at level
    element = {
        "type": "",
        "content": ""
    }

    try:
        # if doc.__class__.__name__ != "Heading":
        #     print(doc.content)

        name = doc.__class__.__name__
        # Headings don't have content attributes
        if name == "Heading":
            # mistletoe parses headers by adding a
            # level attribute, we need to parse that
            # into separate elements
            if doc.level == 1:
                element["type"] = "h1"
            elif doc.level == 2:
                element["type"] = "h2"
            elif doc.level == 3:
                element["type"] = "h3"
            else:
                print("found unknown level", doc.level)
        elif name == "ThematicBreak":
            element["type"] = "divider"
        elif name == "Paragraph":
            # paragraphs can contain different object types,
            # but notion doesn't have a concept of a line break
            # TODO: can paragraphs have lists inside them?
            element["type"] = "text"
        elif name == "RawText":
            # RawText's are the leaves in our tree
            # and should always have a content attribute
            element["content"] = doc.content

            # at this level, add the finished object to the
            # total list of items.
            page_items.append(element)
    except AttributeError():
        pass

    # begin recurse
    try:
        for child in doc.children:
            try:
                tree_former(child, page_items)
            except AttributeError():
                pass
    except AttributeError():
        pass


def doc_to_notion_scheme(root_page, doc):
    """transforms mistletoe parsed markdown document
    into dictionary defining structure of new notion page.
    root_page: root notion page for new page to go under
    doc: mistletoe parsed markdown document object
    """

    new_page = root_page.children.add_new(notion.block.PageBlock,
                                          title="imported notes")

    page_items = []
    tree_former(doc, page_items)

    # loop through page_items

    # -> make notion block for each time according to block_sticher

    # done!


def block_switcher(arg):
    """define notion blocks in use
    arg: string for type of block needed
    returns: notion block object
    """
    switcher = {
        "quote": notion.block.QuoteBlock,
        "divider": notion.block.DividerBlock,
        "text": notion.block.TextBlock,
        "code": notion.block.CodeBlock,
        "h1": notion.block.HeaderBlock,
        "h2": notion.block.SubheaderBlock,
        "h3": notion.block.SubsubheaderBlock,
        "todo": notion.block.TodoBlock,
        "bullet": notion.block.BulletedListBlock,
        "number": notion.block.BulletedListBlock
    }
    return switcher.get(arg, "invalid")


def run_test():
    """Main execution"""
    client = return_notion_client(get_secret())
    page = return_test_page(client)
    create_page(page, "new page")
