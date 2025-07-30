import ast
import re

def is_more_informative_type(type1: ast.expr | None, type2: ast.expr | None):
    # Returns True if type1 is more informative than type2
    # For simplicity, treat 'Any' or None as less informative
    placeholder = re.compile(r'^(Any|Incomplete)$')
    match type1, type2:
        case None, _:
            return False
        case _, None:
            return True
        case _:
            # If type1 is a placeholder, it is not more informative
            for child in ast.walk(type1):
                if isinstance(child, ast.Name) and placeholder.match(child.id):
                    return False
            return True

class AnnotationOverrideTransformer(ast.NodeTransformer):
    def __init__(self, annotation_ast: ast.AST):
        self.annotation_ast = annotation_ast
        # Build lookup tables for functions and classes by name
        self.func_annots: dict[str, ast.FunctionDef] = {node.name: node for node in ast.walk(annotation_ast) if isinstance(node, ast.FunctionDef)}
        self.class_annots: dict[str, ast.ClassDef] = {node.name: node for node in ast.walk(annotation_ast) if isinstance(node, ast.ClassDef)}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        annot_node = self.func_annots.get(node.name)
        if annot_node:
            # Override argument annotations
            for arg, annot_arg in zip(node.args.args, annot_node.args.args):
                if is_more_informative_type(annot_arg.annotation, arg.annotation):
                    arg.annotation = annot_arg.annotation
            # Override return annotation
            if is_more_informative_type(annot_node.returns, node.returns):
                node.returns = annot_node.returns
        return self.generic_visit(node)

    # def visit_ClassDef(self, node: ast.ClassDef):
    #     annot_node = self.class_annots.get(node.name)
    #     if annot_node:
    #         # Override base classes if more informative
    #         # (You can customize this logic as needed)
    #         pass
    #     return self.generic_visit(node)

def merge_annotations(source_ast: ast.Module, annotation_ast: ast.Module) -> ast.Module:
    """
    Merges annotations from annotation_ast into source_ast.
    Returns a new AST with the merged annotations.
    """
    transformer = AnnotationOverrideTransformer(annotation_ast)
    return transformer.visit(source_ast)
