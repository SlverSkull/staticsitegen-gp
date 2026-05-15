class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if not self.props:
            return ""
        final = ""
        for key in self.props.keys():
            final = final + f' {key}="{self.props[key]}"'
        return final

    def __repr__(self):
        return f"HTMLNode(Tag:{self.tag}, Value:{self.value}, Children:{self.children}, Props:{self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
    
    def to_html(self):
        if self.value is None:
            raise ValueError("Missing value attribute...")
        if self.tag is None:
            return str(self.value)
        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'
    
    def __repr__(self):
        return f"LeafNode(Tag:{self.tag}, Value:{self.value}, Props:{self.props})"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("Missing tag attribute...")
        if self.children is None:
            raise ValueError(f"Missing children attribute...")
        final = f"<{self.tag}{self.props_to_html()}>"
        for i in self.children:
            final = final + f"{i.to_html()}"
        return final + f"</{self.tag}>"