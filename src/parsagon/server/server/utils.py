from collections import defaultdict
from enum import Enum
import itertools
from lxml import etree


NODE_ID_ATTR = 'data-psgn-id'


class ElemDataType(Enum):
    TEXT = 'TEXT'
    URL = 'URL'
    IMAGE = 'IMAGE'
    HTML = 'HTML'
    ACTION = 'ACTION'


def get_elem_data(elem, data_type):
    if data_type == ElemDataType.TEXT.value:
        return elem.xpath('normalize-space()')
    elif data_type == ElemDataType.URL.value:
        if elem.tag == 'a' and 'href' in elem.attrib:
            return elem.get('href')
        else:
            inner_matches = elem.findall('.//a[@href]')
            if len(inner_matches) == 1:
                return inner_matches[0].get('href')
            else:
                return ''
    elif data_type == ElemDataType.IMAGE.value:
        if elem.tag == 'img' and 'src' in elem.attrib:
            return elem.get('src')
        else:
            inner_matches = elem.findall('.//img[@src]')
            if len(inner_matches) == 1:
                return inner_matches[0].get('src')
            else:
                return ''
    elif data_type == ElemDataType.HTML.value:
        return etree.tostring(elem, method='html', encoding=str)
    elif data_type == ElemDataType.ACTION.value:
        return elem
    else:
        raise ValueError('Invalid data type')


class Grouping:
    def __init__(self, sub_groups, elem, types, location, column=None):
        self.sub_groups = sub_groups
        self.elem = elem
        if len(types) == 1 and isinstance(next(iter(types)), frozenset):
            self.types = next(iter(types))
        else:
            self.types = frozenset(types)
        self.pointer = location
        self.column = column


def combine_columns(leaves):
    merged = True
    while merged:
        merged = False
        object_to_groups = defaultdict(set)
        column_to_groups = defaultdict(set)
        next_leaves = []
        for leaf in leaves:
            if leaf.column['object']:
                object_to_groups[leaf.column['object']['name']].add(leaf)
            column_to_groups[leaf.column['name']].add(leaf)
        for leaf in leaves:
            if not leaf.column['object'] or object_to_groups[leaf.column['name']]:
                next_leaves.append(leaf)
                continue
            for parent in column_to_groups[leaf.column['object']['name']]:
                if not leaf.column['is_list'] and leaf.column['name'] in parent.types:
                    break
                else:
                    parent.sub_groups.append(leaf)
                    parent.elem = leaf.pointer
                    parent.types |= frozenset([leaf.column['name']])
                    merged = True
                    break
            else:
                clone = Grouping(leaf.sub_groups, leaf.elem, leaf.types, leaf.pointer, leaf.column)
                leaf.sub_groups = [clone]
                leaf.elem = leaf.pointer
                leaf.types = frozenset([leaf.column['name']])
                object_to_groups[leaf.column['object']['name']].discard(leaf)
                column_to_groups[leaf.column['name']].discard(leaf)
                if leaf.column['object']['object']:
                    object_to_groups[leaf.column['object']['object']['name']].add(leaf)
                column_to_groups[leaf.column['object']['name']].add(leaf)
                leaf.column = leaf.column['object']
                next_leaves.append(leaf)
        leaves = next_leaves
    column_to_leaves = defaultdict(list)
    final_leaves = []
    for leaf in leaves:
        if leaf.column['object'] is None:
            if leaf.column['name'] not in column_to_leaves:
                column_to_leaves[leaf.column['name']].append(leaf)
                final_leaves.append(leaf)
            else:
                base_leaf = column_to_leaves[leaf.column['name']][-1]
                for child in leaf.sub_groups:
                    if not child.column['is_list'] and child.column['name'] in base_leaf.types:
                        final_leaves.append(leaf)
                        break
                else:
                    base_leaf.sub_groups.extend(leaf.sub_groups)
                    base_leaf.elem = leaf.pointer
                    base_leaf.types |= leaf.types
        else:
            final_leaves.append(leaf)
    return final_leaves


def create_data(trees):
    result = {}
    for tree in trees:
        column = tree.column
        name = tree.column['name']
        is_list = tree.column['is_list']
        if name not in result and is_list:
            result[name] = []

        if column['user_created']:
            value = get_elem_data(tree.elem, column['type'])
        else:
            tree.sub_groups.sort(key=lambda grouping: grouping.pointer.orig_node_id if hasattr(grouping.pointer, 'orig_node_id') else grouping.pointer.get(NODE_ID_ATTR))
            value = create_data(tree.sub_groups)

        if is_list:
            result[name].append(value)
        else:
            result[name] = value
    return result


def build_structure(columns, target_data):
    name_to_column = {column['name']: column for column in columns}
    leaves = []
    descendants = defaultdict(set)
    for column_name, elems in target_data.items():
        column = name_to_column[column_name]
        for elem in elems:
            leaf = Grouping([], elem, [column['name']], elem, column=column)
            leaves.append(leaf)

            head = leaf.pointer
            while head is not None:
                descendants[head].add(leaf)
                head = head.getparent()

    finished_leaves = []
    while leaves:
        next_leaves = []
        skips = set()
        for leaf in leaves:
            if leaf in skips:
                continue
            if leaf.pointer.getparent() is None:
                finished_leaves.append(leaf)
                continue

            if len(descendants[leaf.pointer]) > 1:
                group_targets = descendants[leaf.pointer]
                if any(target.pointer != leaf.pointer for target in group_targets):
                    continue

                new_leaves = combine_columns(group_targets)

                for desc_leaf in descendants[leaf.pointer]:
                    for k, desc_leaves in descendants.items():
                        if k != leaf.pointer:
                            desc_leaves.discard(desc_leaf)
                    skips.add(desc_leaf)
                descendants[leaf.pointer] = set()
                head = leaf.pointer.getparent()
                while head is not None:
                    descendants[head].update(new_leaves)
                    head = head.getparent()

                next_leaves = [nl for nl in next_leaves if nl not in group_targets]
                next_leaves.extend(new_leaves)
            else:
                leaf.pointer = leaf.pointer.getparent()
                next_leaves.append(leaf)
        leaves = next_leaves
    for leaf in finished_leaves:
        while leaf.column['object']:
            combine_columns([leaf])
    return create_data(finished_leaves)
