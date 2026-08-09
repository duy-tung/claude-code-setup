"""Hidden structural contract for the discount-refactor task."""
import ast
import unittest
from pathlib import Path


REQUIRED_TIERS = {"regular", "member", "vip", "staff"}


def assigned_name(node):
    target = node.targets[0] if isinstance(node, ast.Assign) else node.target
    return target.id if isinstance(target, ast.Name) else None


def mapping_keys(value):
    if isinstance(value, ast.Dict):
        return {
            key.value for key in value.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
    if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
            and value.func.id == "dict"):
        return {keyword.arg for keyword in value.keywords if keyword.arg}
    return set()


class TestDiscountRefactorStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(Path("pricing.py").read_text(encoding="utf-8"))
        cls.function = next(
            node for node in cls.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "final_price"
        )

    def test_uses_one_mapping_for_all_customer_tiers(self):
        candidates = set()
        for node in ast.walk(self.tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            name = assigned_name(node)
            if name and REQUIRED_TIERS <= mapping_keys(value):
                candidates.add(name)

        loaded_names = {
            node.id for node in ast.walk(self.function)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        self.assertTrue(
            candidates & loaded_names,
            "final_price must use one data-driven mapping containing all tiers",
        )

    def test_removes_if_elif_dispatch_chain(self):
        chained = [
            node for node in ast.walk(self.function)
            if isinstance(node, ast.If)
            and len(node.orelse) == 1
            and isinstance(node.orelse[0], ast.If)
        ]
        self.assertFalse(
            chained,
            "final_price must not retain an if/elif customer-type chain",
        )


if __name__ == "__main__":
    unittest.main()
