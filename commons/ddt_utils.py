""" ddt参数解析，所有yaml用例读取 """
import os
import re
from commons.extract_utils import read_yaml
from configs import setting
from copy import deepcopy

# =============== 测试数据ddt读取 ====================
def resolve_ddt(data, row_values):
    """
    递归遍历数据结构，将 $ddt{key} 替换为 parametrize 数据行中对应的值。
    如果整个字符串就是 $ddt{key}，则返回原始类型（支持 None）。
    """
    if isinstance(data, str):
        # 情况1：整个字符串就是一个 $ddt{} 引用 → 返回原始类型
        full_match = re.match(r'^\$ddt\{(\w+)\}$', data)
        if full_match:
            key = full_match.group(1)
            if key not in row_values:
                raise KeyError(f"parametrize 中未定义列名: {key}")
            return row_values[key]

        # 情况2：字符串中部分包含 $ddt{} → 字符串内插
        def replace_ddt(match):
            key = match.group(1)
            if key not in row_values:
                raise KeyError(f"parametrize 中未定义列名: {key}")
            val = row_values[key]
            return str(val) if val is not None else ""
        return re.sub(r'\$ddt\{(\w+)\}', replace_ddt, data)
    elif isinstance(data, dict):
        return {k: resolve_ddt(v, row_values) for k, v in data.items()}
    elif isinstance(data, list):
        return [resolve_ddt(item, row_values) for item in data]

    else:
        return data


# =============== 读取所有测试用例数据yaml ===================
def read_all_testcase(root_dir=setting.test_yaml_path):
    """递归遍历目录，读取所有test_*.yaml用例，合并成列表返回"""
    login_cases = []
    business_cases = []
    # 遍历根目录下所有文件
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # 只读取test_开头、后缀yaml的用例文件
            if filename.startswith("test_") and filename.endswith(".yaml"):
                file_path = os.path.join(dirpath, filename)
                case_data = read_yaml(file_path)
                # 兼容单用例（dict）/ 多用例（list）格式
                case_list = case_data if isinstance(case_data, list) else [case_data]
                for case_template in case_list:
                    # 取出 parametrize 数据驱动表
                    parametrize_rows = case_template.pop("parametrize", None)

                    if not parametrize_rows:
                        # 没有数据驱动 → 原样添加
                        target = login_cases if "login" in filename.lower() else business_cases
                        target.append(case_template)
                    else:
                        # 有数据驱动 → 按行展开
                        headers = parametrize_rows[0]
                        for row in parametrize_rows[1:]:
                            row_values = dict(zip(headers, row))
                            new_case = resolve_ddt(deepcopy(case_template), row_values)
                            target = login_cases if "login" in filename.lower() else business_cases
                            target.append(new_case)
    # 先登录用例，再业务用例，保证登录最先执行
    return login_cases + business_cases